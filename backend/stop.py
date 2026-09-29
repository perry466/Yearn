"""Yearn 一键关闭服务。

关闭占用指定端口的进程（默认 8000，即 run.py 启动的单服务）。
也可指定多个端口，例如顺手把旧的 vite 也关掉：python stop.py 8000 5173

用法：
    python stop.py            # 关闭 8000（单服务）
    python stop.py 8000 5173  # 关闭 8000 和 5173
"""
import subprocess
import sys
import os
import signal

DEFAULT_PORTS = [8000]


def find_pids_on_port(port):
    pids = []
    if sys.platform.startswith("win"):
        try:
            out = subprocess.run(
                ["netstat", "-ano", "-p", "TCP"],
                capture_output=True, text=True, check=False,
            ).stdout
        except Exception:
            return pids
        for line in out.splitlines():
            cols = line.split()
            # TCP    0.0.0.0:8000    0.0.0.0:0    LISTENING    1234
            if (len(cols) >= 5 and cols[0] == "TCP"
                    and f":{port}" in cols[1] and cols[3] == "LISTENING"):
                try:
                    pids.append(int(cols[4]))
                except ValueError:
                    pass
    else:
        try:
            out = subprocess.run(
                ["lsof", f"-tiTCP:{port}", "-sTCP:LISTEN"],
                capture_output=True, text=True, check=False,
            ).stdout
            for line in out.splitlines():
                line = line.strip()
                if line.isdigit():
                    pids.append(int(line))
        except Exception:
            pass
    return pids


def kill_pid(pid):
    if sys.platform.startswith("win"):
        res = subprocess.run(
            ["taskkill", "/PID", str(pid), "/F", "/T"],
            capture_output=True, text=True, check=False,
        )
        return res.returncode == 0
    try:
        os.kill(pid, signal.SIGTERM)
        return True
    except ProcessLookupError:
        return False


def stop_port(port):
    pids = find_pids_on_port(port)
    if not pids:
        print(f"[端口 {port}] 没有进程在监听，无需关闭。")
        return
    for pid in set(pids):
        ok = kill_pid(pid)
        print(f"[端口 {port}] 进程 PID={pid} {'已关闭' if ok else '关闭失败'}")


if __name__ == "__main__":
    ports = [int(a) for a in sys.argv[1:]] if len(sys.argv) > 1 else DEFAULT_PORTS
    print("Yearn 关闭服务：")
    for p in ports:
        stop_port(p)
    print("完成。")
