import sched
import sys
import time

from keiba.base import Base
from keiba.utils.date_utils import (
    is_jst_timezone,
    set_jst_timezone,
    yyyymmdd_to_jra_date,
)
from keiba.utils.file_utils import read_json

from odds import Odds
from scheduling import Scheduling


def check_timezone() -> None:
    # Check timezone is jst or not, and if not, convert it.
    if not (is_jst_timezone()):
        set_jst_timezone()
    else:
        pass

    return None


if __name__ == "__main__":

    check_timezone()

    s = sched.scheduler(time.time, time.sleep)

    kaisai_date = yyyymmdd_to_jra_date(sys.argv[1])
    kaisai_path = Base.BASE_PATH / kaisai_date

    for kaisai_name_path in kaisai_path.iterdir():
        kaisai_name = kaisai_name_path.name

        race_times = read_json(kaisai_name_path / "times.json")
        for race_num, race_time in race_times.items():
            o = Odds(kaisai_date, kaisai_name, race_num)
            a = Scheduling(race_time, s, o.job)
            a.setup_scheduler()

    s.run()
