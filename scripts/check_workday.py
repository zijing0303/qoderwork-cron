"""
中国工作日判断模块
基于 chinese_calendar 库，支持法定节假日和调休
"""
import sys
from datetime import date

try:
    from chinese_calendar import is_workday, is_holiday
    HAS_CHINESE_CALENDAR = True
except ImportError:
    HAS_CHINESE_CALENDAR = False


def check_workday(d=None):
    """
    判断给定日期是否为工作日
    d: date 对象，默认今天
    返回: (is_workday: bool, reason: str)
    """
    if d is None:
        d = date.today()

    weekday = d.weekday()  # 0=Monday, 6=Sunday
    day_name_cn = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]

    if HAS_CHINESE_CALENDAR:
        if is_workday(d):
            if weekday >= 5:
                return True, f"{d} 是{day_name_cn[weekday]}（调休补班），是工作日"
            return True, f"{d} 是{day_name_cn[weekday]}，正常工作日"
        else:
            if weekday < 5:
                return False, f"{d} 是{day_name_cn[weekday]}（法定节假日/调休放假），非工作日"
            return False, f"{d} 是{day_name_cn[weekday]}，正常周末"
    else:
        # fallback: 仅按周一~周五判断，不考虑节假日
        if weekday < 5:
            return True, f"{d} 是{day_name_cn[weekday]}（无 chinese_calendar 库，仅按周末判断）"
        return False, f"{d} 是{day_name_cn[weekday]}，周末"


if __name__ == "__main__":
    d = date.today()
    if len(sys.argv) > 1:
        d = date.fromisoformat(sys.argv[1])

    is_wd, reason = check_workday(d)
    print(reason)
    sys.exit(0 if is_wd else 1)
