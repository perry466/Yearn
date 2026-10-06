"""提醒发送记录（持久化去重）

原先的去重是 reminder.py 里的进程内字典 `_reminded`，有两个问题：
  1. 进程一退出就清空 → 同一天重启两次会重复推送同一条提醒；
  2. 无法跨天生效 → 「今天已提醒过」这件事第二天就忘了。

这里用 (birthday_id, days_until, target_date) 唯一约束落到数据库。
target_date 是这一次生日的具体公历日期，保证明年同一人同一阈值还能正常再推，
而不是一辈子只推一次。
"""
from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint

from ..core.database import Base


class ReminderLog(Base):
    __tablename__ = "reminder_log"

    id = Column(Integer, primary_key=True)
    birthday_id = Column(Integer, nullable=False, index=True)
    days_until = Column(Integer, nullable=False)
    # 这次生日对应的公历日期（YYYY-MM-DD），用于区分不同年份的同一条记录
    target_date = Column(String(10), nullable=False, default="")
    sent_at = Column(DateTime, default=datetime.now, nullable=False)

    __table_args__ = (
        UniqueConstraint("birthday_id", "days_until", "target_date",
                         name="uq_reminder_once"),
    )
