from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ========== 基础 Schema ==========

class BirthdayBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="姓名")
    solar_date: str = Field(..., description="公历生日 YYYY-MM-DD")
    lunar_date: Optional[str] = Field(None, description="农历生日 YYYY-MM-DD")
    is_lunar: bool = Field(False, description="是否为农历生日")
    is_leap_month: bool = Field(False, description="农历是否闰月（仅农历模式有效）")
    category: str = Field("朋友", max_length=50, description="分类")
    remark: str = Field("", max_length=500, description="备注")
    is_enabled: bool = Field(True, description="提醒是否启用")


# ========== 创建 Schema ==========

class BirthdayCreate(BirthdayBase):
    pass


# ========== 更新 Schema ==========

class BirthdayUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    solar_date: Optional[str] = None
    lunar_date: Optional[str] = None
    is_lunar: Optional[bool] = None
    is_leap_month: Optional[bool] = None
    category: Optional[str] = Field(None, max_length=50)
    remark: Optional[str] = Field(None, max_length=500)
    is_enabled: Optional[bool] = None


# ========== 响应 Schema ==========

class BirthdayResponse(BirthdayBase):
    id: int
    # 转换后的公历生日（农历模式下为今年对应的公历日期）
    upcoming_date: Optional[str] = None
    # 距离生日天数（None 表示今年已过）
    days_until: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ========== 统计 Schema ==========

class StatsResponse(BaseModel):
    total: int
    categories: dict[str, int]
    upcoming_count: int  # 30天内过生日的人数
