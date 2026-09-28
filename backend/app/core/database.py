from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import DATABASE_URL

# 创建引擎（SQLite 启用外键约束）
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# 启用 SQLite 外键约束
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """获取数据库会话，每次请求后自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
