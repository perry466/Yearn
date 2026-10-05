"""农历查询 API。

- GET /api/lunar/calendar?year=1977   某农历年的月份表（含闰月、每月天数）
- GET /api/lunar/month-days?year=1977&month=8&is_leap=false  单月天数

存在的意义：农历每月是 29 天（小月）还是 30 天（大月）**每年都不同**，
没有规律可循。前端不能靠硬编码猜天数（比如"八月一定有三十"是错的），
必须由后端用 lunardate 查表后返回，才能和生日换算用同一套数据、不出偏差。

lunardate 支持范围为农历 1900–2099 年，越界返回 400。
"""
from fastapi import APIRouter, HTTPException, Query

from ..services.lunar import lunar_year_calendar, lunar_days_in_month

router = APIRouter(prefix="/api/lunar", tags=["农历"])

MIN_YEAR = 1900
MAX_YEAR = 2099


def _check_year(year: int):
    if year < MIN_YEAR or year > MAX_YEAR:
        raise HTTPException(
            status_code=400,
            detail=f"year out of range [{MIN_YEAR}, {MAX_YEAR}]",
        )


@router.get("/calendar")
def get_lunar_calendar(year: int = Query(..., description="农历年份")):
    """返回该农历年每月天数及闰月位置，供前端生成「日」下拉框。"""
    _check_year(year)
    return lunar_year_calendar(year)


@router.get("/month-days")
def get_month_days(
    year: int = Query(..., description="农历年份"),
    month: int = Query(..., ge=1, le=12, description="农历月份 1-12"),
    is_leap: bool = Query(False, description="是否闰月"),
):
    """返回某农历年某月的天数（29 / 30）。0 表示该年没有这个闰月。"""
    _check_year(year)
    return {"year": year, "month": month, "is_leap": is_leap,
            "days": lunar_days_in_month(year, month, is_leap)}
