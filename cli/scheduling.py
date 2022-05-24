import sched
import time
from datetime import datetime, timedelta
from typing import Callable


class Scheduling:
    """Scheduling job(get odds data) into scheduler instance.
    Scheduling job start 8 hours before to start race, and its interval is 5m.


    Ex: Race start at: 10:10
    ------------------------
        1- 2:10 (8 hours before)
        2- 2:15
        3- 2:20
        4- 2:25
        5- 2:30
        ...
        94- 10:00
        95- 10:05
        97- 10:10 (race time)

    """

    def __init__(
        self, race_time: str, scheduler: sched.scheduler, job: Callable
    ) -> None:
        self.race_time = race_time
        self.scheduler = scheduler
        self.job = job

        return None

    @property
    def times(self) -> list:
        """Generate times list to use scheduling."""
        format_ = "%Y%m%d%H%M"
        race_time_d = datetime.strptime(self.race_time, format_)

        times = []
        for i in reversed(range(0, 485, 5)):
            times.append(race_time_d - timedelta(minutes=i))

        return times

    def setup_scheduler(self) -> None:

        for time_ in self.times:
            delay_time = self._calc_delay_time(time_)
            self._set_scheduler(self.scheduler, delay_time, self.job)

        return None

    def _calc_delay_time(self, start_time: datetime) -> datetime:
        """Calc delay time to execute job."""
        delay_time = start_time.timestamp() - time.time()

        return delay_time

    def _set_scheduler(
        self, scheduler: sched.scheduler, delay_time: datetime, job: Callable
    ) -> None:
        """Set scheduling event into sched.scheduler."""
        priority_ = 1
        scheduler.enter(delay_time, priority_, job)

        return None
