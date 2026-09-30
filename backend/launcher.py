"""Yearn 打包入口（PyInstaller 生成 exe 时使用的主脚本）。

与 run.py 的分工：
- run.py      ：源码开发用，监听 0.0.0.0，方便局域网 / 服务器访问
- launcher.py ：打包成 exe 用，只监听 127.0.0.1，无控制台，右下角托盘常驻

开发时不需要执行本文件，照常 `python run.py` 即可，两者互不影响。
"""
import logging
import os
import socket
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

# 关键修复：GUI 模式（console=False）没有控制台，sys.stdout / sys.stderr 是无效句柄。
# 而 logging.basicConfig()（app.main 里）和 uvicorn 的 configure_logging() 都会创建
# 写 stderr 的 handler，一写就崩 —— 表现为服务线程静默死亡、浏览器打开后拒绝连接。
# 这里把它们重定向到黑洞，真正的日志走下面的 FileHandler 写文件。
if getattr(sys, "frozen", False):
    try:
        _devnull = open(os.devnull, "w", encoding="utf-8")
        sys.stdout = _devnull
        sys.stderr = _devnull
    except Exception:
        pass

# 确保能 import app 包（无论从哪个目录启动本脚本）
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import DATA_DIR

# 数据目录在打包后是 exe 同级的 data/，开发时仍是 backend/，由 config.py 决定
DATA_DIR.mkdir(parents=True, exist_ok=True)

# 配置日志文件：没有控制台后，日志是排查问题的唯一依据。
# 不依赖 basicConfig（它只在 root logger 无 handler 时生效，而 app 内部可能已配置），
# 直接给 root logger 添加一个 FileHandler，确保所有日志都落盘。
_log_handler = logging.FileHandler(DATA_DIR / "yearn.log", encoding="utf-8")
_log_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(_log_handler)

# 只监听本机：避免 Windows 防火墙弹出「是否允许访问网络」吓到普通用户
HOST = "127.0.0.1"
DEFAULT_PORT = 8000
SERVER_CONTAINER: dict = {}

# Windows 单例锁名称
_MUTEX_NAME = "Yearn_Single_Instance_Mutex_v1"


def _ensure_single_instance() -> bool:
    """Windows 命名互斥体，保证同时只有一个实例运行。"""
    if sys.platform != "win32":
        return True
    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.windll.kernel32
        kernel32.CreateMutexW.argtypes = [
            wintypes.LPVOID,
            wintypes.BOOL,
            wintypes.LPCWSTR,
        ]
        kernel32.CreateMutexW.restype = wintypes.HANDLE
        kernel32.GetLastError.restype = wintypes.DWORD

        handle = kernel32.CreateMutexW(None, False, _MUTEX_NAME)
        if not handle:
            return False
        if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            kernel32.CloseHandle(handle)
            return False
        # 保持 handle 不被回收；程序退出时系统自动释放
        SERVER_CONTAINER["mutex_handle"] = handle
        return True
    except Exception as exc:
        logging.warning("单例锁创建失败：%s", exc)
        return True


def _pick_port(start: int = DEFAULT_PORT, tries: int = 20) -> int:
    """从 start 开始找第一个未被占用的端口，避免端口冲突直接崩溃。"""
    for port in range(start, start + tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex((HOST, port)) != 0:
                return port
    return start


def _create_tray_icon():
    """在内存里生成一个简单的托盘图标，避免依赖外部 .ico 文件。"""
    from PIL import Image, ImageDraw, ImageFont

    size = 64
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # 蓝色圆形背景
    draw.ellipse((0, 0, size, size), fill=(59, 130, 246, 255))

    # 尝试画一个白色的 Y
    try:
        font = ImageFont.truetype("segoeui.ttf", 32)
    except Exception:
        font = ImageFont.load_default()

    text = "Y"
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    except Exception:
        tw, th = 16, 16

    draw.text(
        ((size - tw) / 2, (size - th) / 2 - 2),
        text,
        font=font,
        fill=(255, 255, 255, 255),
    )
    return image


def _wait_for_server(url: str, timeout: float = 15.0) -> bool:
    """轮询 health 接口，等服务真正 ready。"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def _notify_error() -> None:
    """托盘气泡提示启动失败（失败也不影响主流程）。"""
    try:
        icon = SERVER_CONTAINER.get("icon")
        if icon:
            icon.notify("服务未能启动，请查看 data/yearn.log", "Yearn 岁岁念")
    except Exception:
        pass


def _open_browser_when_ready(url: str) -> None:
    """等服务 ready 后再打开浏览器；服务起不来则不开（避免用户看到拒绝连接页）。"""
    health_url = f"{url}/health"
    if _wait_for_server(health_url, timeout=30.0):
        webbrowser.open(url)
        logging.info("Browser opened after server ready: %s", url)
    else:
        logging.error("Server did not start within 30s, skipping browser open")
        _notify_error()


def _run_server(host: str, port: int) -> None:
    """在后台线程运行 uvicorn。延迟导入，让托盘图标先显示。"""
    try:
        import uvicorn
        from app.main import app

        # log_config=None：不让 uvicorn 再建一套写 stdout/stderr 的 handler
        # （GUI 程序无控制台，dictConfig 建 console handler 会失败）
        # 日志统一走 launcher 配置的 FileHandler
        config = uvicorn.Config(
            app,
            host=host,
            port=port,
            log_level="warning",
            log_config=None,
            access_log=False,
        )
        server = uvicorn.Server(config)
        SERVER_CONTAINER["server"] = server
        logging.info("Yearn server starting on http://%s:%s", host, port)
        server.run()
        logging.info("Yearn server stopped")
    except BaseException:
        # 服务线程异常默认只打到 stderr（GUI 模式下看不到），必须落盘到日志文件
        logging.exception("Yearn server crashed")
        raise


def _on_open(icon, item):
    """托盘菜单：打开网页。若服务尚未 ready，则等待后打开。"""
    url = SERVER_CONTAINER.get("url")
    if url:
        threading.Thread(target=_open_browser_when_ready, args=(url,), daemon=True).start()


def _on_exit(icon, item):
    """托盘菜单：退出程序。"""
    logging.info("User requested exit from tray")
    server = SERVER_CONTAINER.get("server")
    if server:
        server.should_exit = True
    icon.stop()


def main() -> None:
    import pystray

    if not _ensure_single_instance():
        logging.info("Another Yearn instance is already running, exiting.")
        return

    port = _pick_port()
    url = f"http://localhost:{port}"
    SERVER_CONTAINER["url"] = url

    # 创建托盘图标（先显示，用户立刻有反馈）
    menu = pystray.Menu(
        pystray.MenuItem("打开 Yearn", _on_open),
        pystray.MenuItem("退出", _on_exit),
    )
    icon = pystray.Icon(
        name="Yearn",
        icon=_create_tray_icon(),
        title="Yearn 岁岁念",
        menu=menu,
    )
    SERVER_CONTAINER["icon"] = icon

    # 后台启动 uvicorn（延迟导入放在这个线程里，不阻塞托盘显示）
    threading.Thread(target=_run_server, args=(HOST, port), daemon=True).start()

    # 等服务 ready 后再打开浏览器
    threading.Thread(target=_open_browser_when_ready, args=(url,), daemon=True).start()

    logging.info("Yearn tray icon started")
    icon.run()

    # 用户点了退出，icon.run() 返回
    logging.info("Tray loop ended, exiting")
    time.sleep(0.3)
    os._exit(0)


if __name__ == "__main__":
    main()
