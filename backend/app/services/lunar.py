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


def _build_lunar(year: int, month: int, day: int, is_leap: bool) -> Optional[LunarDate]:
    """尽力构造一个合法的 LunarDate。

    农历每月可能是 29 天（小月）或 30 天（大月），**哪个月是大月每年都不同**，
    所以「八月三十」在有些年份根本不存在。这里按以下顺序降级：

    1. 原样构造（闰月则先按闰月试，再按非闰月试）
    2. 该月没这天（如三十但只有廿九）→ 回退到该月最后一天（三十→廿九）

    仍失败才返回 None。这样保证「每年都能算出生日」，而不会让某一年凭空消失。
    注意：`LunarDate(...)` 构造函数**不做校验**，只有 `to_solar_date()` 才会抛
    ValueError。所以每次构造后必须转换一次才能真正验证日期是否合法。
    """
    flags = [is_leap, False] if is_leap else [False]
    for leap_flag in flags:
        try:
            lunar = LunarDate(year, month, day, leap_flag)
            lunar.to_solar_date()  # 触发校验
            return lunar
        except ValueError:
            # 该月没有这一天，或该年没有这个闰月 → 回退到该月最后一天
            days = lunar_days_in_month(year, month, leap_flag)
            if not days:
                continue
            try:
                lunar = LunarDate(year, month, days, leap_flag)
                lunar.to_solar_date()
                return lunar
            except ValueError:
                continue
    return None


def lunar_days_in_month(year: int, month: int, is_leap: bool = False) -> int:
    """查询某农历年某月有多少天（29 或 30）。

    农历的大小月由天文定朔决定，没有固定规律，**必须查表**。
    返回 0 表示查询失败（年份越界 / 该年没有这个闰月）。

    >>> lunar_days_in_month(1977, 8)   # 1977 年八月是大月
    30
    >>> lunar_days_in_month(2026, 8)   # 2026 年八月是小月
    29
    """
    try:
        LunarDate(year, month, 30, is_leap).to_solar_date()
        return 30
    except ValueError:
        try:
            LunarDate(year, month, 29, is_leap).to_solar_date()
            return 29
        except ValueError:
            return 0
    except Exception:
        return 0


def lunar_year_calendar(year: int) -> dict:
    """返回某农历年完整的月份表（含闰月），供前端渲染日期下拉框。

    返回: {"year": 1977, "leap_month": 7|None,
           "months": [{"month": 1, "is_leap": False, "days": 30}, ...]}
    闰月存在时，months 里闰月紧跟在同名月份之后。
    """
    leap_month = None
    try:
        leap_month = LunarDate.leap_month_for_year(year)
    except Exception:
        leap_month = None

    months = []
    for m in range(1, 13):
        days = lunar_days_in_month(year, m, False)
        if days:
            months.append({"month": m, "is_leap": False, "days": days})
        if leap_month == m:
            leap_days = lunar_days_in_month(year, m, True)
            if leap_days:
                months.append({"month": m, "is_leap": True, "days": leap_days})

    return {"year": year, "leap_month": leap_month, "months": months}


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

        lunar = _build_lunar(target_year, lunar_month, lunar_day, is_leap)
        if lunar is None:
            return None

        solar = lunar.to_solar_date()
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
