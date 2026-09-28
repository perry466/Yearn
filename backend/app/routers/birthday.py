"""
生日管理 API 路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..schemas.birthday import BirthdayCreate, BirthdayUpdate, BirthdayResponse, StatsResponse
from ..services import birthday as birthday_service

router = APIRouter(prefix="/api/birthdays", tags=["生日管理"])


# ========== 生日记录 CRUD ==========

@router.get("", response_model=List[BirthdayResponse])
def list_birthdays(
    keyword: Optional[str] = Query(None, description="搜索关键词（姓名/备注）"),
    category: Optional[str] = Query(None, description="按分类筛选"),
    db: Session = Depends(get_db),
):
    """获取所有生日记录（支持搜索和分类筛选）"""
    if keyword:
        birthdays = birthday_service.search_birthdays(db, keyword)
    elif category:
        birthdays = birthday_service.get_birthdays_by_category(db, category)
    else:
        birthdays = birthday_service.get_all_birthdays(db)

    # 补充 upcoming_date 和 days_until
    from ..services.lunar import days_until_birthday, get_upcoming_birthday_date

    result = []
    for b in birthdays:
        days_left = days_until_birthday(b.solar_date, b.lunar_date, b.is_lunar, b.is_leap_month)
        upcoming_date = get_upcoming_birthday_date(b.solar_date, b.lunar_date, b.is_lunar, b.is_leap_month)
        result.append(BirthdayResponse(
            id=b.id,
            name=b.name,
            solar_date=b.solar_date,
            lunar_date=b.lunar_date,
            is_lunar=b.is_lunar,
            is_leap_month=b.is_leap_month,
            category=b.category,
            remark=b.remark,
            is_enabled=b.is_enabled,
            upcoming_date=upcoming_date.isoformat() if upcoming_date else None,
            days_until=days_left,
            created_at=b.created_at,
            updated_at=b.updated_at,
        ))
    return result


@router.get("/upcoming", response_model=List[BirthdayResponse])
def list_upcoming(
    days: int = Query(30, ge=1, le=365, description="提前天数，默认30天"),
    db: Session = Depends(get_db),
):
    """获取即将到来的生日"""
    upcoming = birthday_service.get_upcoming_birthdays(db, days)
    return [BirthdayResponse(**b) for b in upcoming]


@router.get("/stats", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)):
    """获取统计概览"""
    return birthday_service.get_statistics(db)


@router.get("/calendar", response_model=List[BirthdayResponse])
def get_calendar_birthdays(
    year: int = Query(None, description="年份，默认当前年"),
    month: int = Query(None, ge=1, le=12, description="月份 1-12"),
    db: Session = Depends(get_db),
):
    """获取日历视图数据（某年/月的生日）"""
    from datetime import date
    import calendar as cal

    if year is None:
        year = date.today().year
    if month is None:
        month = date.today().month

    # 获取当月天数
    _, days_in_month = cal.monthrange(year, month)
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{days_in_month:02d}"

    birthdays = birthday_service.get_all_birthdays(db)
    from ..services.lunar import get_upcoming_birthday_date

    result = []
    for b in birthdays:
        upcoming_date = get_upcoming_birthday_date(b.solar_date, b.lunar_date, b.is_lunar, b.is_leap_month)
        if upcoming_date and upcoming_date.year == year and upcoming_date.month == month:
            days_left = (upcoming_date - date.today()).days
            result.append(BirthdayResponse(
                id=b.id,
                name=b.name,
                solar_date=b.solar_date,
                lunar_date=b.lunar_date,
                is_lunar=b.is_lunar,
                is_leap_month=b.is_leap_month,
                category=b.category,
                remark=b.remark,
                is_enabled=b.is_enabled,
                upcoming_date=upcoming_date.isoformat(),
                days_until=days_left,
                created_at=b.created_at,
                updated_at=b.updated_at,
            ))

    result.sort(key=lambda x: x.upcoming_date or "")
    return result


@router.get("/{birthday_id}", response_model=BirthdayResponse)
def get_birthday(birthday_id: int, db: Session = Depends(get_db)):
    """获取单条生日记录"""
    b = birthday_service.get_birthday(db, birthday_id)
    if not b:
        raise HTTPException(status_code=404, detail="记录不存在")
    from ..services.lunar import days_until_birthday, get_upcoming_birthday_date
    days_left = days_until_birthday(b.solar_date, b.lunar_date, b.is_lunar, b.is_leap_month)
    upcoming_date = get_upcoming_birthday_date(b.solar_date, b.lunar_date, b.is_lunar, b.is_leap_month)
    return BirthdayResponse(
        id=b.id,
        name=b.name,
        solar_date=b.solar_date,
        lunar_date=b.lunar_date,
        is_lunar=b.is_lunar,
        is_leap_month=b.is_leap_month,
        category=b.category,
        remark=b.remark,
        is_enabled=b.is_enabled,
        upcoming_date=upcoming_date.isoformat() if upcoming_date else None,
        days_until=days_left,
        created_at=b.created_at,
        updated_at=b.updated_at,
    )


@router.post("", response_model=BirthdayResponse, status_code=201)
def create_birthday(data: BirthdayCreate, db: Session = Depends(get_db)):
    """添加新生日记录"""
    birthday = birthday_service.create_birthday(db, data)
    from ..services.lunar import days_until_birthday, get_upcoming_birthday_date
    days_left = days_until_birthday(birthday.solar_date, birthday.lunar_date, birthday.is_lunar, birthday.is_leap_month)
    upcoming_date = get_upcoming_birthday_date(birthday.solar_date, birthday.lunar_date, birthday.is_lunar, birthday.is_leap_month)
    return BirthdayResponse(
        id=birthday.id,
        name=birthday.name,
        solar_date=birthday.solar_date,
        lunar_date=birthday.lunar_date,
        is_lunar=birthday.is_lunar,
        is_leap_month=birthday.is_leap_month,
        category=birthday.category,
        remark=birthday.remark,
        is_enabled=birthday.is_enabled,
        upcoming_date=upcoming_date.isoformat() if upcoming_date else None,
        days_until=days_left,
        created_at=birthday.created_at,
        updated_at=birthday.updated_at,
    )


@router.put("/{birthday_id}", response_model=BirthdayResponse)
def update_birthday(
    birthday_id: int,
    data: BirthdayUpdate,
    db: Session = Depends(get_db),
):
    """更新生日记录"""
    birthday = birthday_service.update_birthday(db, birthday_id, data)
    if not birthday:
        raise HTTPException(status_code=404, detail="记录不存在")
    from ..services.lunar import days_until_birthday, get_upcoming_birthday_date
    days_left = days_until_birthday(birthday.solar_date, birthday.lunar_date, birthday.is_lunar, birthday.is_leap_month)
    upcoming_date = get_upcoming_birthday_date(birthday.solar_date, birthday.lunar_date, birthday.is_lunar, birthday.is_leap_month)
    return BirthdayResponse(
        id=birthday.id,
        name=birthday.name,
        solar_date=birthday.solar_date,
        lunar_date=birthday.lunar_date,
        is_lunar=birthday.is_lunar,
        is_leap_month=birthday.is_leap_month,
        category=birthday.category,
        remark=birthday.remark,
        is_enabled=birthday.is_enabled,
        upcoming_date=upcoming_date.isoformat() if upcoming_date else None,
        days_until=days_left,
        created_at=birthday.created_at,
        updated_at=birthday.updated_at,
    )


@router.delete("/{birthday_id}", status_code=204)
def delete_birthday(birthday_id: int, db: Session = Depends(get_db)):
    """删除生日记录"""
    success = birthday_service.delete_birthday(db, birthday_id)
    if not success:
        raise HTTPException(status_code=404, detail="记录不存在")
    return None
