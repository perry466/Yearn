"""
提醒服务：邮件 + Server酱 微信推送
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
import httpx
from ..core.config import EMAIL_CONFIG, SERVERCHAN_CONFIG

logger = logging.getLogger(__name__)


def send_reminder_email(birthday_name: str, birthday_date: str, days_left: int) -> bool:
    """发送邮件提醒"""
    if not EMAIL_CONFIG.get("enabled"):
        logger.info(f"[邮件] 邮件提醒未启用，跳过 {birthday_name}")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🎂 生日提醒：{birthday_name} 还有 {days_left} 天！"
        msg["From"] = f"{EMAIL_CONFIG['from_name']} <{EMAIL_CONFIG['smtp_user']}>"
        msg["To"] = EMAIL_CONFIG["to_email"]

        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #FF6B6B, #FFA07A); border-radius: 16px; padding: 30px; text-align: center;">
                <h1 style="color: white; margin: 0;">🎂 生日提醒</h1>
            </div>
            <div style="padding: 30px; background: #f9f9f9; border-radius: 16px; margin-top: 20px;">
                <p style="font-size: 18px;">
                    <strong>{birthday_name}</strong> 的生日还有
                    <span style="font-size: 24px; color: #FF6B6B; font-weight: bold;">{days_left} 天</span>
                </p>
                <p style="color: #666;">
                    生日日期：{birthday_date}<br>
                    别忘了准备礼物哦！🎁
                </p>
            </div>
            <p style="text-align: center; color: #999; font-size: 12px; margin-top: 20px;">
                由生日提醒系统自动发送
            </p>
        </body>
        </html>
        """
        msg.attach(MIMEText(body, "html", "utf-8"))

        with smtplib.SMTP(EMAIL_CONFIG["smtp_host"], EMAIL_CONFIG["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(EMAIL_CONFIG["smtp_user"], EMAIL_CONFIG["smtp_password"])
            server.sendmail(EMAIL_CONFIG["smtp_user"], EMAIL_CONFIG["to_email"], msg.as_string())

        logger.info(f"[邮件] 发送成功: {birthday_name} - {days_left}天后")
        return True

    except Exception as e:
        logger.error(f"[邮件] 发送失败: {birthday_name} - {e}")
        return False


def send_serverchan_reminder(birthday_name: str, birthday_date: str, days_left: int) -> bool:
    """发送 Server酱微信推送"""
    if not SERVERCHAN_CONFIG.get("enabled") or not SERVERCHAN_CONFIG.get("sckey"):
        logger.info(f"[Server酱] 未启用或未配置SCKEY，跳过 {birthday_name}")
        return False

    try:
        # Server酱 官方接口（新版 sctapi）
        url = f"https://sctapi.ftqq.com/{SERVERCHAN_CONFIG['sckey']}.send"

        # 计算 emoji
        cake = "🎂"
        if days_left == 30:
            cake = "🔔"
        elif days_left == 15:
            cake = "⏰"
        elif days_left == 7:
            cake = "🎉"
        elif days_left == 1:
            cake = "⚠️"

        title = f"{birthday_name} 的生日还有 {days_left} 天"
        desp = f"""{cake} **生日提醒**

**{birthday_name}** 的生日还有 **{days_left} 天**！

📅 生日日期：{birthday_date}

💡 别忘了准备礼物哦！
"""

        data = {
            "title": title,
            "desp": desp,
        }

        with httpx.Client(timeout=10) as client:
            response = client.post(url, data=data)

        if response.status_code == 200:
            logger.info(f"[Server酱] 推送成功: {birthday_name} - {days_left}天后")
            return True
        else:
            logger.error(f"[Server酱] 推送失败: {birthday_name} - {response.status_code}: {response.text}")
            return False

    except Exception as e:
        logger.error(f"[Server酱] 推送异常: {birthday_name} - {e}")
        return False


def send_reminders(birthday_name: str, birthday_date: str, days_left: int) -> dict:
    """
    同时发送邮件和 Server酱提醒
    返回各渠道发送结果
    """
    results = {
        "email": send_reminder_email(birthday_name, birthday_date, days_left),
        "serverchan": send_serverchan_reminder(birthday_name, birthday_date, days_left),
    }
    return results
