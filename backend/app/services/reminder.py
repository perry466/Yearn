"""
提醒服务：邮件 + Server酱 微信推送
配置（渠道开关 / key / 频率 / 模板）全部来自数据库 settings 表，
由网页设置页维护，改即生效，无需改 .env、无需重启。
"""
import json
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional

import httpx
from ..core.database import SessionLocal
from ..models.settings import Settings
from .birthday import get_upcoming_birthdays

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE = (
    "🎂 {name} 的生日还有 {days} 天！\n"
    "生日：{date}\n"
    "今年 {age} 岁，分类：{category}\n"
    "别忘了准备礼物哦！🎁"
)
DEFAULT_DAYS = [30, 15, 7, 1, 0]

# 已提醒记录：{(birthday_id, days_until): True}，避免同一天重复发送（进程内去重）
_reminded: dict = {}


class _SafeDict(dict):
    """未知占位符保留原样，避免 KeyError 导致整条推送失败。"""

    def __missing__(self, key):
        return '{' + key + '}'


def render_template(template: str, **kw) -> str:
    if not template:
        template = DEFAULT_TEMPLATE
    try:
        return template.format_map(_SafeDict(**kw))
    except Exception:
        return template


def _load_settings(db) -> Settings:
    s = db.query(Settings).filter(Settings.id == 1).first()
    if not s:
        s = Settings(id=1)
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


def _days_list(settings) -> list:
    try:
        days = json.loads(settings.remind_ahead_days or "[]")
        return [int(d) for d in days]
    except Exception:
        return list(DEFAULT_DAYS)


def send_serverchan(name, date_str, days_left, sckey, template, age=None, category=None) -> bool:
    """发送 Server酱微信推送。返回是否成功。"""
    if not sckey:
        logger.info(f"[Server酱] 未配置 SCKEY，跳过 {name}")
        return False
    try:
        url = f"https://sctapi.ftqq.com/{sckey}.send"
        desp = render_template(
            template,
            name=name,
            days=days_left,
            date=date_str,
            age=age if age is not None else "",
            category=category or "",
        )
        if days_left == 0:
            title = f"🎉 今天是 {name} 的生日！"
        elif days_left == 1:
            title = f"⏰ 明天是 {name} 的生日"
        else:
            title = f"🎂 {name} 的生日还有 {days_left} 天"
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, data={"title": title, "desp": desp})
        if resp.status_code == 200:
            logger.info(f"[Server酱] 推送成功: {name} - {days_left}天后")
            return True
        logger.error(f"[Server酱] 推送失败: {name} - {resp.status_code}: {resp.text}")
        return False
    except Exception as e:
        logger.error(f"[Server酱] 推送异常: {name} - {e}")
        return False


def send_email(name, date_str, days_left, cfg, template, age=None, category=None) -> bool:
    """发送邮件提醒。cfg: dict（来自 settings 的邮件字段）。返回是否成功。"""
    if not cfg.get("smtp_user") or not cfg.get("to_email"):
        logger.info(f"[邮件] 邮件未启用或配置不全，跳过 {name}")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🎂 生日提醒：{name} 还有 {days_left} 天！"
        msg["From"] = f"{cfg['from_name']} <{cfg['smtp_user']}>"
        msg["To"] = cfg["to_email"]
        body = render_template(
            template,
            name=name,
            days=days_left,
            date=date_str,
            age=age if age is not None else "",
            category=category or "",
        )
        msg.attach(MIMEText(body, "plain", "utf-8"))
        with smtplib.SMTP(cfg["smtp_host"], cfg["smtp_port"]) as server:
            server.ehlo()
            server.starttls()
            server.login(cfg["smtp_user"], cfg["smtp_password"])
            server.sendmail(cfg["smtp_user"], cfg["to_email"], msg.as_string())
        logger.info(f"[邮件] 发送成功: {name} - {days_left}天后")
        return True
    except Exception as e:
        logger.error(f"[邮件] 发送失败: {name} - {e}")
        return False


def send_reminder(name, date_str, days_left, settings, age=None, category=None) -> dict:
    """按 settings 中的启用渠道发送提醒，返回各渠道结果。"""
    template = settings.message_template or DEFAULT_TEMPLATE
    results = {"email": False, "serverchan": False}
    if settings.email_enabled:
        results["email"] = send_email(
            name, date_str, days_left,
            {
                "smtp_host": settings.email_smtp_host,
                "smtp_port": settings.email_smtp_port,
                "smtp_user": settings.email_smtp_user,
                "smtp_password": settings.email_smtp_password,
                "from_name": settings.email_from_name,
                "to_email": settings.email_to,
            },
            template, age, category,
        )
    if settings.serverchan_enabled:
        results["serverchan"] = send_serverchan(
            name, date_str, days_left, settings.serverchan_sckey, template, age, category
        )
    return results


def check_and_send_reminders():
    """
    检查即将到来的生日并发送提醒。
    由主程序 lifespan 每天的定时任务调用，也可手动 / 独立运行调用。
    频率（提前天数）与渠道配置均来自数据库 settings。
    """
    logger.info("=" * 40)
    logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查生日提醒...")
    db = SessionLocal()
    try:
        settings = _load_settings(db)
        days_list = _days_list(settings)
        logger.info(f"提醒策略：提前 {days_list} 天；Server酱={'开' if settings.serverchan_enabled else '关'}；邮件={'开' if settings.email_enabled else '关'}")

        all_upcoming = get_upcoming_birthdays(db, days=60)  # 拉取 60 天内
        sent_count = 0
        for b in all_upcoming:
            days_left = b.get("days_until")
            if days_left is None or days_left not in days_list:
                continue

            key = (b["id"], days_left)
            if _reminded.get(key):
                logger.info(f"[跳过] {b['name']} - {days_left}天 (今日已提醒)")
                continue

            display = f"农历 {b['lunar_date']}" if b["is_lunar"] else f"公历 {b['solar_date']}"
            logger.info(f"[提醒] {b['name']} - {days_left}天后 - {display}")

            results = send_reminder(
                b["name"], display, days_left, settings,
                b.get("age"), b.get("category"),
            )

            if results["email"] or results["serverchan"]:
                _reminded[key] = True
                sent_count += 1
                logger.info(
                    f"[成功] {b['name']}: "
                    f"邮件={'✓' if results['email'] else '✗'} "
                    f"Server酱={'✓' if results['serverchan'] else '✗'}"
                )
            else:
                logger.warning(f"[失败] {b['name']} 所有渠道发送失败（可能未启用或未配置 key/账号）")

        logger.info(f"本次检查完成，新增发送 {sent_count} 条提醒")
    except Exception as e:
        logger.error(f"调度器异常: {e}", exc_info=True)
    finally:
        db.close()


def send_test_reminder(db) -> dict:
    """测试发送：用第一条启用记录（或示例数据）渲染模板并推送，返回各渠道结果。"""
    settings = _load_settings(db)
    upcoming = get_upcoming_birthdays(db, days=60)
    if upcoming:
        b = upcoming[0]
        display = f"农历 {b['lunar_date']}" if b["is_lunar"] else f"公历 {b['solar_date']}"
        name, days_left = b["name"], b["days_until"]
        age, category = b.get("age"), b.get("category")
    else:
        name, days_left, display, age, category = "测试好友", 3, "公历 1995-08-15", 30, "朋友"

    results = send_reminder(name, display, days_left, settings, age, category)
    return {
        "name": name,
        "days_left": days_left,
        "email": results["email"],
        "serverchan": results["serverchan"],
        "note": "若两个渠道都为 false，请检查是否在设置页启用并填写了正确的 SCKEY / 邮箱账号",
    }
