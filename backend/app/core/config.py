"""
配置文件 - 请根据实际情况修改以下配置项
"""
import os
from pathlib import Path

# ========== 路径配置 ==========
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/birthday.db"

# ========== 服务器配置 ==========
HOST = "0.0.0.0"
PORT = 8000

# ========== 邮件提醒配置 ==========
# 请替换为你的邮箱 SMTP 信息
EMAIL_CONFIG = {
    "enabled": False,  # True 开启邮件提醒
    "smtp_host": "smtp.gmail.com",       # 如: smtp.163.com / smtp.qq.com
    "smtp_port": 587,
    "smtp_user": "your_email@example.com",
    "smtp_password": "your_app_password",  # 不是登录密码，是应用专用密码
    "from_name": "🎂 生日提醒",
    "to_email": "notify@example.com",      # 接收提醒的邮箱
}

# ========== Server酱配置 ==========
# 访问 http://sc.ftqq.com/3.version 注册并获取 SCKEY
SERVERCHAN_CONFIG = {
    "enabled": False,  # True 开启 Server酱推送
    "sckey": "your_sckey_here",
}

# ========== 提醒提前天数 ==========
# 到达这些天数时发送提醒（单位：天）
REMIND_AHEAD_DAYS = [30, 15, 7, 1]
