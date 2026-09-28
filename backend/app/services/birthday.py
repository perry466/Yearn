"""
生日业务逻辑服务
"""
from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.birthday import Birthday
from ..schemas.birthday import BirthdayCreate, BirthdayUpdate
from .lunar import get_upcoming_birthday_date, days_until_birthday, solar_to_lunar, lunar_to_solar_this_year


def create_birthday(db: Session, birthday_data: BirthdayCreate) -> Birthday:
    """创建生日记录
    - 公历模式：存 solar_date，自动算 lunar_date
    - 农历模式：存 lunar_date + is_leap_month，自动算 solar_date
    """
    data = birthday_data.model_dump()
    is_lunar = data.get("is_lunar", False)
    is_leap = data.get("is_leap_month", False)

    if is_lunar:
        # 农历模式：lunar_date 由前端传入（格式 YYYY-MM-DD）
        lunar_str = data.get("lunar_date") or ""
        # 计算对应的公历日期（用于 solar_date 字段，作为 fallback）
        solar = lunar_to_solar_this_year(lunar_str, is_leap=is_leap)
        solar_str = solar.isoformat() if solar else lunar_str  # fallback 用原值占位
    else:
        # 公历模式：前端传 solar_date
        solar_str = data.get("solar_date") or ""
        lunar_str = solar_to_lunar(solar_str)

    birthday = Birthday(
        name=data.get("name", "").strip(),
        solar_date=solar_str,
        lunar_date=lunar_str or None,
        is_lunar=is_lunar,
        is_leap_month=is_leap,
        category=data.get("category", "朋友"),
        remark=data.get("remark", "").strip(),
        is_enabled=data.get("is_enabled", True),
        gender=data.get("gender", "unspecified"),
    )

    db.add(birthday)
    db.commit()
    db.refresh(birthday)
    return birthday


def update_birthday(db: Session, birthday_id: int, data: BirthdayUpdate) -> Optional[Birthday]:
    """更新生日记录"""
    birthday = db.query(Birthday).filter(Birthday.id == birthday_id).first()
    if not birthday:
        return None

    update_data = data.model_dump(exclude_unset=True)

    # 处理日期字段：根据 is_lunar 联动更新
    new_is_lunar = update_data.get("is_lunar", birthday.is_lunar)
    new_is_leap = update_data.get("is_leap_month", birthday.is_leap_month)

    if new_is_lunar:
        # 农历模式：以前端 lunar_date 为准
        if "lunar_date" in update_data:
            lunar_str = update_data["lunar_date"]
            # 同步算出 solar_date
            solar = lunar_to_solar_this_year(lunar_str, is_leap=new_is_leap)
            if solar:
                update_data["solar_date"] = solar.isoformat()
    else:
        # 公历模式：以前端 solar_date 为准，自动算 lunar_date
        if "solar_date" in update_data:
            update_data["lunar_date"] = solar_to_lunar(update_data["solar_date"])

    for key, value in update_data.items():
        setattr(birthday, key, value)

    db.commit()
    db.refresh(birthday)
    return birthday


def delete_birthday(db: Session, birthday_id: int) -> bool:
    """删除生日记录"""
    birthday = db.query(Birthday).filter(Birthday.id == birthday_id).first()
    if not birthday:
        return False
    db.delete(birthday)
    db.commit()
    return True


def get_birthday(db: Session, birthday_id: int) -> Optional[Birthday]:
    """获取单条记录"""
    return db.query(Birthday).filter(Birthday.id == birthday_id).first()


def get_all_birthdays(db: Session) -> List[Birthday]:
    """获取所有生日记录"""
    return db.query(Birthday).order_by(Birthday.name).all()


def get_upcoming_birthdays(db: Session, days: int = 30) -> List[dict]:
    """
    获取即将到来的生日（未来N天内）
    返回带有 upcoming_date / days_until / gender / age 的列表
    """
    all_birthdays = db.query(Birthday).filter(Birthday.is_enabled == True).all()
    upcoming = []

    for b in all_birthdays:
        days_left = days_until_birthday(b.solar_date, b.lunar_date, b.is_lunar, b.is_leap_month)
        if days_left is not None and 0 <= days_left <= days:
            upcoming_date = get_upcoming_birthday_date(b.solar_date, b.lunar_date, b.is_lunar, b.is_leap_month)
            # 计算年龄：农历从 lunar_date 提取年份，公历从 solar_date
            try:
                from datetime import date
                today = date.today()
                if b.is_lunar and b.lunar_date:
                    birth_year = int(b.lunar_date.split('-')[0])
                else:
                    birth_year = date.fromisoformat(b.solar_date).year
                age = max(today.year - birth_year, 0)
            except Exception:
                age = None
            upcoming.append({
                "id": b.id,
                "name": b.name,
                "solar_date": b.solar_date,
                "lunar_date": b.lunar_date,
                "is_lunar": b.is_lunar,
                "is_leap_month": b.is_leap_month,
                "category": b.category,
                "remark": b.remark,
                "is_enabled": b.is_enabled,
                "gender": getattr(b, 'gender', 'unspecified'),
                "upcoming_date": upcoming_date.isoformat() if upcoming_date else None,
                "days_until": days_left,
                "age": age,
                "created_at": b.created_at,
                "updated_at": b.updated_at,
            })

    # 按天数排序（最近的最前面）
    upcoming.sort(key=lambda x: x["days_until"])
    return upcoming


def get_birthdays_by_category(db: Session, category: str) -> List[Birthday]:
    """按分类获取"""
    return db.query(Birthday).filter(Birthday.category == category).all()


def search_birthdays(db: Session, keyword: str) -> List[Birthday]:
    """搜索姓名或备注"""
    kw = f"%{keyword}%"
    return db.query(Birthday).filter(
        (Birthday.name.ilike(kw)) | (Birthday.remark.ilike(kw))
    ).all()


def get_statistics(db: Session) -> dict:
    """获取统计数据"""
    total = db.query(func.count(Birthday.id)).scalar()
    upcoming = get_upcoming_birthdays(db, days=30)

    # 按分类统计
    category_counts = db.query(
        Birthday.category,
        func.count(Birthday.id)
    ).group_by(Birthday.category).all()

    categories = {cat: count for cat, count in category_counts}

    return {
        "total": total or 0,
        "categories": categories,
        "upcoming_count": len(upcoming),
    }
