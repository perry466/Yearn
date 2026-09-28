"""
农历生日服务
使用 lunardate 库进行公历/农历互转
"""
from datetime import date, datetime
from typing import Optional
from lunardate import LunarDate


def solar_to_lunar(solar_date: str) -> str:
    """
    将公历日期转换为农历日期
    输入: "2000-07-15" (YYYY-MM-DD)
    输出: "2000-06-14" (YYYY-MM-DD，农历)
    """
    try:
        d = datetime.strptime(solar_date, "%Y-%m-%d")
        lunar = LunarDate.fromSolarDate(d.year, d.month, d.day)
        return f"{lunar.year}-{lunar.month:02d}-{lunar.day:02d}"
    except Exception:
        return ""


def lunar_to_solar_this_year(lunar_date_str: str, year: Optional[int] = None, is_leap: bool = False) -> Optional[date]:
    """
    将农历日期转换为对应公历日期。
    输入: "2000-06-14" (农历 YYYY-MM-DD), is_leap=True 表示闰月
    - 如果传了 year 参数：转换为该公历年的对应日期（用于显示今年生日）
    - 如果 year=None：转换为农历同年的公历日期（用于存储原始出生公历）
    返回: date 对象或 None
    """
    try:
        parts = lunar_date_str.split("-")
        lunar_year = int(parts[0])
        lunar_month = int(parts[1])
        lunar_day = int(parts[2])

        # 用指定年份的农历月份来计算公历日期
        target_year = year if year is not None else lunar_year

        try:
            lunar = LunarDate(target_year, lunar_month, lunar_day, is_leap)
        except ValueError:
            # 如果指定闰月无效，尝试非闰月
            if is_leap:
                try:
                    lunar = LunarDate(target_year, lunar_month, lunar_day, False)
                except Exception:
                    return None
            else:
                return None

        solar = lunar.toSolarDate()
        return date(solar.year, solar.month, solar.day)

    except Exception:
        return None


def get_upcoming_birthday_date(solar_date: str, lunar_date: Optional[str], is_lunar: bool, is_leap: bool = False) -> Optional[date]:
    """
    获取即将到来的生日日期（公历 date 对象）
    对于农历生日，计算今年（或明年）对应的公历日期
    """
    today = date.today()
    current_year = today.year

    if is_lunar and lunar_date:
        # 农历生日：先尝试今年
        upcoming = lunar_to_solar_this_year(lunar_date, current_year, is_leap)
        if upcoming is None:
            return None
        # 今年已过，则用明年
        if upcoming < today:
            upcoming = lunar_to_solar_this_year(lunar_date, current_year + 1, is_leap)
        return upcoming
    else:
        # 公历生日
        try:
            parts = solar_date.split("-")
            month, day = int(parts[1]), int(parts[2])
            birthday = date(current_year, month, day)
            if birthday < today:
                birthday = date(current_year + 1, month, day)
            return birthday
        except Exception:
            return None


def days_until_birthday(solar_date: str, lunar_date: Optional[str], is_lunar: bool, is_leap: bool = False) -> Optional[int]:
    """
    计算距离生日还有多少天（今天=0 表示今天生日）
    """
    upcoming = get_upcoming_birthday_date(solar_date, lunar_date, is_lunar, is_leap)
    if upcoming is None:
        return None
    delta = upcoming - date.today()
    return delta.days
