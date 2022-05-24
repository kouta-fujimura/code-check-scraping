from dataclasses import dataclass
from pathlib import Path


@dataclass
class Base:

    # JRAサイトデフォルトURL、ここから遷移ページパラメータを指定してpostを投げる
    BASE_URL: str = "https://jra.jp/JRADB/accessO.html"
    SCHEDULE_PAGE_PARAM: str = "pw01dli00/F3"
    ODDS_PAGE_PARAM: str = "pw15oli00/6D"
    RESULT_PAGE_PARAM: str = "pw01sli00/AF"

    # 取得オッズ保管dir親パス
    BASE_PATH: Path = Path.home() / "keiba-saiko/output/jra/"
    ARCHIVE_PATH: Path = Path.home() / "keiba-saiko/archive"
