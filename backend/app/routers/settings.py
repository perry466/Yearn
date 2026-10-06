"""系统设置 API：提醒渠道 / 频率 / 推送模板，均存数据库，网页改即存"""
import json
import logging
import threading
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..models.settings import Settings
from ..schemas.settings import SettingsResponse, SettingsUpdate
from ..services.reminder import send_test_reminder, check_and_send_reminders

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/settings", tags=["设置"])

DEFAULT_TEMPLATE = (
    "🎂 {name} 的生日还有 {days} 天！\n"
    "生日：{date}\n"
    "今年 {age} 岁，分类：{category}\n"
    "别忘了准备礼物哦！🎁"
)
DEFAULT_DAYS = [30, 15, 7, 1, 0]


def _ensure_row(db: Session) -> Settings:
    s = db.query(Settings).filter(Settings.id == 1).first()
    if not s:
        s = Settings(id=1)
        db.add(s)
        db.commit()
        db.refresh(s)
    return s


def _to_response(s: Settings) -> SettingsResponse:
    try:
        days = json.loads(s.remind_ahead_days or "[]")
    except Exception:
        days = list(DEFAULT_DAYS)
    return SettingsResponse(
        serverchan_enabled=bool(s.serverchan_enabled),
        serverchan_sckey=s.serverchan_sckey or "",
        email_enabled=bool(s.email_enabled),
        email_smtp_host=s.email_smtp_host or "",
        email_smtp_port=s.email_smtp_port or 587,
        email_smtp_user=s.email_smtp_user or "",
        email_smtp_password=s.email_smtp_password or "",
        email_from_name=s.email_from_name or "",
        email_to=s.email_to or "",
        remind_ahead_days=days,
        message_template=s.message_template or DEFAULT_TEMPLATE,
    )


@router.get("", response_model=SettingsResponse)
def get_settings(db: Session = Depends(get_db)):
    """获取当前系统设置"""
    return _to_response(_ensure_row(db))


@router.put("", response_model=SettingsResponse)
def update_settings(payload: SettingsUpdate, db: Session = Depends(get_db)):
    """更新系统设置（网页改即存，无需重启）"""
    s = _ensure_row(db)
    data = payload.model_dump(exclude_unset=True)
    if "remind_ahead_days" in data and data["remind_ahead_days"] is not None:
        data["remind_ahead_days"] = json.dumps(data["remind_ahead_days"])
    for k, v in data.items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)

    # 配置变更后立即重跑一次检查。
    # 不这样做的话：启动补检在启动时已跑完，用户之后才在页面上加阈值（比如补上 3 天），
    # 改动要等到第二天 09:00 才生效，看上去就像「推送坏了」。
    # 去重已持久化到 reminder_log 表，所以反复保存不会重复推送。
    try:
        threading.Thread(target=check_and_send_reminders, daemon=True).start()
        logger.info("设置已更新，已触发一次提醒检查")
    except Exception as e:
        logger.warning(f"设置更新后触发检查失败: {e}")

    return _to_response(s)


@router.post("/test")
def test_reminder(db: Session = Depends(get_db)):
    """测试发送：用第一条启用记录（或示例数据）渲染模板并推送，返回各渠道结果"""
    return send_test_reminder(db)
