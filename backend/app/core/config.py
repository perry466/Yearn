"""
配置文件 - 敏感信息从 .env 读取（勿将 .env 提交到 GitHub）
参考 .env.example 填写你的真实值
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件（项目根目录）
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

# ========== 路径配置 ==========
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/birthday.db"

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
