from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from sqlalchemy.sql import func
from ..core.database import Base


class Birthday(Base):
    """生日记录模型"""

    __tablename__ = "birthdays"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True, comment="姓名")
    # 公历日期（YYYY-MM-DD 格式存储）
    solar_date = Column(String(10), nullable=False, comment="公历生日")
    # 农历日期（YYYY-MM-DD 格式存储，用于农历生日）
    lunar_date = Column(String(20), nullable=True, comment="农历生日，如2026-08-15")
    is_lunar = Column(Boolean, default=False, comment="是否为农历生日")
    is_leap_month = Column(Boolean, default=False, comment="农历是否闰月")
    category = Column(String(50), default="朋友", comment="分类：朋友/家人/同事/客户/其他")
    remark = Column(String(500), default="", comment="备注")
    is_enabled = Column(Boolean, default=True, comment="提醒是否启用")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Birthday(id={self.id}, name={self.name}, date={self.lunar_date if self.is_lunar else self.solar_date})>"
