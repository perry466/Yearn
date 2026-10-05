"""主题/外观设置模型。

- ThemeSetting ：主题状态 JSON（单行，id=1），含颜色模式/主题色/面板不透明度/自定义背景。
- BackgroundImage ：自定义背景图元数据，图片字节落在 DATA_DIR/images/<id>（见 routers/theme.py）。
"""
import datetime
from sqlalchemy import Column, Integer, Text, String, DateTime
from ..core.database import Base


class ThemeSetting(Base):
    __tablename__ = "theme_setting"

    id = Column(Integer, primary_key=True, default=1)  # 单例行
    data = Column(Text, default="")  # 主题状态 JSON
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class BackgroundImage(Base):
    __tablename__ = "background_image"

    id = Column(Integer, primary_key=True, autoincrement=True)
    mime = Column(String(64), default="image/jpeg")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
