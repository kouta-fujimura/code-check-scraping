from datetime import datetime
import os
import time

JA_DOW = (
    "月",
    "火",
    "水",
    "木",
    "金",
    "土",
    "日",
)


def yyyymmdd_to_jra_date(yyyymmdd: str):
    """Convert yyyymmdd to jra date string.
    Converted string has month, day, and day of the week(dow).
    (ex. 20220123 -> '1月23日（土曜）')
    """
    format_ = "%Y%m%d"
    yyyymmdd_ = datetime.strptime(yyyymmdd, format_)

    month_str = yyyymmdd_.month
    day_str = yyyymmdd_.day

    dow = yyyymmdd_.weekday()
    youbi_str = JA_DOW[dow]

    jra_date = f"{month_str}月{day_str}日（{youbi_str}曜）"

    return jra_date


def jihun_to_hhmm(jihun: str):
    """Convert ~時~分 to hhmm string."""

    jihun_split_list = jihun.rstrip("分").split("時")
    hhmm = "".join(jihun_split_list).zfill(4)

    return hhmm


def nengappi_to_yyyymmdd(nengappi: str):
    """Convert ~年~月~日 to yyyymmdd string."""

    year_str = nengappi.split("年")[0]
    month_str = nengappi.removeprefix(f"{year_str}年").split("月")[0]
    day_str = nengappi.removeprefix(f"{year_str}年{month_str}月").rstrip("日")

    month_str = month_str.zfill(2)
    day_str = day_str.zfill(2)

    yyyymmdd = "".join([year_str, month_str, day_str])

    return yyyymmdd


def is_jst_timezone():
    current_tz = time.localtime().tm_zone
    is_jst = (current_tz == "JST")

    return is_jst


def set_jst_timezone():
    os.environ["TZ"] = "Japan"
    time.tzset()

    print(f"set timezone to {time.localtime().tm_zone}")

    return None
