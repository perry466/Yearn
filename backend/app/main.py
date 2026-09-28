"""
FastAPI 主入口
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.database import Base, engine, SessionLocal
from .routers import birthday

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建数据库表
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


_migrate_gender_column()

# 创建 FastAPI 应用
app = FastAPI(
    title="🎂 生日提醒系统 API",
    description="支持公历/农历的生日记录与提醒工具",
    version="1.0.0",
)

# CORS 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # 生产环境建议限制为前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(birthday.router)


@app.get("/", tags=["健康检查"])
def root():
    """健康检查接口"""
    return {"status": "ok", "message": "🎂 生日提醒系统运行中"}


@app.get("/health", tags=["健康检查"])
def health_check():
    """健康检查"""
    return {"status": "healthy"}
