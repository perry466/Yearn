"""
配置文件 - 敏感信息从 .env 读取（勿将 .env 提交到 GitHub）
参考 .env.example 填写你的真实值
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


def _base_dir() -> Path:
    """应用根目录（数据库、.env 都放在这里）。

    - 源码运行：backend/ 目录 —— 与改造前完全一致，birthday.db 位置不变，
      已有数据不需要迁移。
    - 打包运行（PyInstaller）：exe 所在目录 —— 必须放在用户可见的持久位置。
      若沿用 __file__ 推算，会落进随机的临时解压目录（_MEIxxx），
      该目录退出即删，导致每次启动数据都被重置。
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent.parent


# ========== 路径配置 ==========
# 开发时 = backend/，打包后 = exe 同级目录
BASE_DIR = _base_dir()

# 加载 .env（可选；提醒配置主要存在数据库 settings 表中，由网页设置页维护）
load_dotenv(BASE_DIR / ".env")

# 打包后把数据集中到 data/ 子目录：目录整洁，用户备份时拷走整个文件夹即可
# 开发时沿用 backend/，birthday.db 位置与改造前完全一致
if getattr(sys, "frozen", False):
    DATA_DIR = BASE_DIR / "data"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
else:
    DATA_DIR = BASE_DIR

DATABASE_URL = f"sqlite:///{DATA_DIR}/birthday.db"

# ========== 服务器配置 ==========
HOST = os.getenv("YERN_HOST", "0.0.0.0")
PORT = int(os.getenv("YERN_PORT", "8000"))

# ========== 邮件提醒配置 ==========
# 请替换为你的邮箱 SMTP 信息
EMAIL_CONFIG = {
    "enabled": os.getenv("EMAIL_ENABLED", "false").lower() == "true",
    "smtp_host": os.getenv("EMAIL_SMTP_HOST", "smtp.gmail.com"),
    "smtp_port": int(os.getenv("EMAIL_SMTP_PORT", "587")),
    "smtp_user": os.getenv("EMAIL_USER", ""),
    "smtp_password": os.getenv("EMAIL_PASSWORD", ""),
    "from_name": os.getenv("EMAIL_FROM_NAME", "🎂 生日提醒"),
    "to_email": os.getenv("EMAIL_TO", ""),
}

# ========== Server酱配置 ==========
# 访问 http://sc.ftqq.com/3.version 注册并获取 SCKEY
SERVERCHAN_CONFIG = {
    "enabled": os.getenv("SERVERCHAN_ENABLED", "false").lower() == "true",
    "sckey": os.getenv("SERVERCHAN_SCKEY", ""),
}

# ========== 提醒提前天数 ==========
# 到达这些天数时发送提醒（单位：天）
REMIND_AHEAD_DAYS = [30, 15, 7, 1, 0]
