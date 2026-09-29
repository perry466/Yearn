"""系统设置模型（单例行，id 固定为 1）"""
from sqlalchemy import Column, Integer, Boolean, String, Text
from ..core.database import Base


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, default=1)
    # Server 酱
    serverchan_enabled = Column(Boolean, default=False)
    serverchan_sckey = Column(String(255), default="")
    # 邮件
    email_enabled = Column(Boolean, default=False)
    email_smtp_host = Column(String(255), default="smtp.gmail.com")
    email_smtp_port = Column(Integer, default=587)
    email_smtp_user = Column(String(255), default="")
    email_smtp_password = Column(String(255), default="")
    email_from_name = Column(String(255), default="🎂 生日提醒")
    email_to = Column(String(255), default="")
    # 提醒提前天数（JSON 数组文本），例如 [30, 15, 7, 1, 0]
    remind_ahead_days = Column(String(255), default="[30, 15, 7, 1, 0]")
    # 自定义推送消息模板，支持 {name}/{days}/{date}/{age}/{category}
    message_template = Column(Text, default="")
