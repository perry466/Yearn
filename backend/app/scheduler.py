"""
生日提醒调度器
每天定时检查生日，提前 30/15/7/1 天发送提醒

启动方式：
    cd backend
    python -m app.scheduler

建议配合 nohup / screen / systemd 实现后台常驻
"""
import logging
import sys
from datetime import date, datetime
from pathlib import Path

# 将 backend 目录加入路径，以便直接 python -m app.scheduler 运行
sys.path.insert(0, str(Path(__file__).parent.parent))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.database import SessionLocal
from app.core.config import REMIND_AHEAD_DAYS
from app.services.birthday import get_upcoming_birthdays
from app.services.reminder import send_reminders

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("scheduler.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)

# 已提醒记录：{(birthday_id, days_until): True}，避免同一天重复发送
_reminded: dict[tuple[int, int], bool] = {}


def check_and_send_reminders():
    """
    检查即将到来的生日并发送提醒
    每天执行一次
    """
    logger.info("=" * 40)
    logger.info(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始检查生日提醒...")

    db = SessionLocal()
    try:
        today = date.today()
        all_upcoming = get_upcoming_birthdays(db, days=60)  # 拉取60天内的

        sent_count = 0
        for b in all_upcoming:
            days_left = b.get("days_until")
            if days_left is None:
                continue

            # 是否在提醒列表中
            if days_left in REMIND_AHEAD_DAYS:
                birthday_id = b["id"]

                # 避免同一天重复提醒（每天只发一次）
                key = (birthday_id, days_left)
                if _reminded.get(key):
                    logger.info(f"[跳过] {b['name']} - {days_left}天 (今日已提醒)")
                    continue

                # 获取原始生日日期显示
                display_date = b["lunar_date"] if b["is_lunar"] else b["solar_date"]
                if b["is_lunar"]:
                    display_date = f"农历 {b['lunar_date']}"
                else:
                    display_date = f"公历 {b['solar_date']}"

                logger.info(f"[提醒] {b['name']} - {days_left}天后 - {display_date}")

                results = send_reminders(
                    birthday_name=b["name"],
                    birthday_date=display_date,
                    days_left=days_left,
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
                    logger.warning(f"[失败] {b['name']} 所有渠道发送失败")

        logger.info(f"本次检查完成，新增发送 {sent_count} 条提醒")

    except Exception as e:
        logger.error(f"调度器异常: {e}", exc_info=True)
    finally:
        db.close()


def main():
    """启动调度器"""
    logger.info("🎂 生日提醒调度器启动")
    logger.info(f"提醒策略：提前 {REMIND_AHEAD_DAYS} 天发送提醒")

    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

    # 每天早上 9:00 执行（可改为其他时间）
    scheduler.add_job(
        check_and_send_reminders,
        CronTrigger(hour=9, minute=0, timezone="Asia/Shanghai"),
        id="daily_reminder",
        name="每日生日提醒检查",
        replace_existing=True,
    )

    # 也可以每6小时检查一次（更及时）
    # scheduler.add_job(
    #     check_and_send_reminders,
    #     CronTrigger(hour="0,6,12,18", minute=0, timezone="Asia/Shanghai"),
    #     id="six_hour_reminder",
    #     name="每6小时生日提醒检查",
    #     replace_existing=True,
    # )

    scheduler.start()
    logger.info("调度器已启动，等待定时任务...")

    # 立即执行一次（启动时检查）
    check_and_send_reminders()

    # 保持进程运行
    try:
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("调度器关闭")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
