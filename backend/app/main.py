"""
FastAPI 主入口（单服务）

- 托管前端 build 产物：生产模式 `uvicorn app.main:app` 一条命令起全栈
- 自动启动提醒调度器：lifespan 内启动 BackgroundScheduler，无需手动 `python -m app.scheduler`
- 提醒配置（频道 / 频率 / 模板）存数据库，由网页设置页维护
"""
import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from .core.database import Base, engine, SessionLocal
from .routers import birthday, settings
from .models.settings import Settings
from .services.reminder import check_and_send_reminders

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建数据库表（含 settings 表）
Base.metadata.create_all(bind=engine)


def _migrate_gender_column():
    """如果 birthdays 表没有 gender 列则自动添加。"""
    from sqlalchemy import text
    db = SessionLocal()
    try:
        result = db.execute(text("PRAGMA table_info(birthdays)")).fetchall()
        columns = [row[1] for row in result]
        if "gender" not in columns:
            db.execute(text("ALTER TABLE birthdays ADD COLUMN gender TEXT DEFAULT 'unspecified'"))
            db.commit()
            logger.info("Migrated: added gender column to birthdays table")
        else:
            logger.info("Database already has gender column")
    except Exception as e:
        logger.warning(f"Gender column migration skipped: {e}")
    finally:
        db.close()


def _migrate_categories():
    """迁移英文/旧中文分类为统一值（配合 schema 白名单）。"""
    from sqlalchemy import text
    MAPPING = {
        "friend": "朋友",
        "family": "家人",
        "colleague": "同事",
        "classmate": "同学",
        "client": "客户",
        "其他": "other",
    }
    db = SessionLocal()
    try:
        for old_val, new_val in MAPPING.items():
            db.execute(
                text("UPDATE birthdays SET category=:new_val WHERE category=:old_val"),
                {"old_val": old_val, "new_val": new_val},
            )
        db.commit()
        logger.info(f"Category migration done: {len(MAPPING)} keys processed")
    except Exception as e:
        logger.warning(f"Category migration skipped: {e}")
    finally:
        db.close()


def _init_settings():
    """确保 settings 单例行存在（首次启动写入默认配置）。"""
    db = SessionLocal()
    try:
        if not db.query(Settings).filter(Settings.id == 1).first():
            db.add(Settings(id=1))
            db.commit()
            logger.info("Initialized default settings row")
    except Exception as e:
        logger.warning(f"Settings init skipped: {e}")
    finally:
        db.close()


# 调度器（单例，随应用生命周期启停）
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动期：迁移 + 初始化配置
    _migrate_gender_column()
    _migrate_categories()
    _init_settings()

    # 每天 09:00（北京时间）检查一次
    scheduler.add_job(
        check_and_send_reminders,
        CronTrigger(hour=9, minute=0, timezone="Asia/Shanghai"),
        id="daily_reminder",
        name="每日生日提醒检查",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("调度器已启动（每天 09:00 北京时间检查；频率/渠道可在网页设置页调整）")

    # 启动后立即跑一次（后台线程，避免阻塞服务启动）
    threading.Thread(target=check_and_send_reminders, daemon=True).start()

    try:
        yield
    finally:
        scheduler.shutdown()
        logger.info("调度器已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="🎂 生日提醒系统 API",
    description="支持公历/农历的生日记录与提醒工具（单服务版）",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(birthday.router)
app.include_router(settings.router)


@app.get("/health", tags=["健康检查"])
def health_check():
    """健康检查"""
    return {"status": "healthy"}


# ===== 前端托管 =====
# 生产：检测到前端构建产物时，托管静态文件并让 / 与前端路由返回 index.html，
#       实现「一条 uvicorn 起全栈」；健康检查仍走 /health。
# 开发：dist 不存在时，/ 返回健康提示（前端请用 vite dev）。
DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if DIST.exists():
    from fastapi.responses import FileResponse

    logger.info(f"检测到前端构建产物，将托管静态文件：{DIST}")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # API 与文档路由已由上面的具体路由优先匹配；此处仅兜底 SPA
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = DIST / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        # SPA fallback：未匹配到的前端路由一律返回 index.html
        return FileResponse(str(DIST / "index.html"))
else:
    @app.get("/", tags=["健康检查"])
    def root():
        return {
            "status": "ok",
            "message": "🎂 生日提醒系统运行中（前端未构建，请用 vite dev 或先 npm run build）",
        }
