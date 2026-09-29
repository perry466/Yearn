"""系统设置相关 Schema"""
from typing import Optional, List
from pydantic import BaseModel


class SettingsResponse(BaseModel):
    serverchan_enabled: bool
    serverchan_sckey: str
    email_enabled: bool
    email_smtp_host: str
    email_smtp_port: int
    email_smtp_user: str
    email_smtp_password: str
    email_from_name: str
    email_to: str
    remind_ahead_days: List[int]
    message_template: str


class SettingsUpdate(BaseModel):
    serverchan_enabled: Optional[bool] = None
    serverchan_sckey: Optional[str] = None
    email_enabled: Optional[bool] = None
    email_smtp_host: Optional[str] = None
    email_smtp_port: Optional[int] = None
    email_smtp_user: Optional[str] = None
    email_smtp_password: Optional[str] = None
    email_from_name: Optional[str] = None
    email_to: Optional[str] = None
    remind_ahead_days: Optional[List[int]] = None
    message_template: Optional[str] = None
