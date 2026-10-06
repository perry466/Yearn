"""
生日提醒调度器（可选独立入口）

⚠️ 推荐：直接用 `uvicorn app.main:app` 单服务启动，调度器已自动集成（见 main.py lifespan）。
本文件仅作为「不想把调度放进 Web 进程」时的独立运行入口，二者不要同时跑，否则会重复推送。

启动方式：
    cd backend
    python -m app.scheduler

建议配合 nohup / screen / systemd 实现后台常驻。
"""
import logging
import sys
import time
from pathlib import Path

# 将 backend 目录加入路径，以便直接 python -m app.scheduler 运行
sys.path.insert(0, str(Path(__file__).parent.parent))

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.reminder import check_and_send_reminders

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


def main():
    """启动调度器"""
    logger.info("🎂 生日提醒调度器启动（独立模式）")
    scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

    # 每天早上 9:00 执行（北京时间）
    # misfire_grace_time=7200：允许任务迟到 2 小时仍补跑（默认 1 秒，休眠即丢）
    # coalesce=True：补跑只执行一次，不累积重复发送
    scheduler.add_job(
        check_and_send_reminders,
        CronTrigger(hour=9, minute=0, timezone="Asia/Shanghai"),
        id="daily_reminder",
        name="每日生日提醒检查",
        replace_existing=True,
        misfire_grace_time=7200,
        coalesce=True,
    )

    scheduler.start()
    logger.info("调度器已启动，等待定时任务...")

    # 立即执行一次（启动时检查）
    check_and_send_reminders()

    # 保持进程运行
    try:
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("调度器关闭")
        scheduler.shutdown()


if __name__ == "__main__":
    main()
