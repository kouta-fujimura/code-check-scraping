from datetime import datetime

from keiba.base import Base
from keiba.utils.file_utils import append_to_csv, read_json
from keiba.utils.keiba_utils import get_jra_soup_object


class Odds(Base):
    """
    Generate odds getting job.
    Generated job gets each horses odds values in 1 race, from odds_page.
    And write it into stored file(race_{num}.csv).

    Parameters
    ----------
    kaisai_date: str
        Target date to execute.
        It's format should be jra_format.
        Ex: '1月23日（土曜）'

    kaisai_name: str
        Target name to execute.
        Ex: '1回小倉5日'

    race_num: str
        Target race number to execute.
    """

    def __init__(self, kaisai_date: str, kaisai_name: str, race_num: str) -> None:
        super().__init__()
        self.kaisai_date = kaisai_date
        self.kaisai_name = kaisai_name
        self.race_num = race_num
        self.dir_path = self.BASE_PATH / f"{self.kaisai_date}/{self.kaisai_name}"
        self.race_file_path = self.dir_path / f"race_{self.race_num}.csv"
        self.header = ["name", "odds", "time"]

        return None

    def job(self) -> None:
        """
        Main job to execute by scheduler.
        Get horse name, odds value, and current time, then append csv file.
        """

        odds_list = self._get_odds_values(self.odds_param)
        append_to_csv(self.race_file_path, self.header, odds_list)

        return None

    @property
    def odds_param(self) -> str:
        """
        jra odds page params read from 'odds_params.json',
        (generated by file_setteings.py) and return a target race's param only.

        Returns
        -------
        odds_param: str
            jra page parameter to jump odds page
        """
        params = read_json(self.dir_path / "odds_params.json")

        return params[self.race_num]

    def _get_odds_values(self, odds_param: str) -> list:
        """
        Get each horse's odds value from jra odds_page,
        and return it by list.

        Parameters
        ----------
        odds_param: str
            Use to jump jra odds_page.

        Returns
        -------
        odds_list: list
            contains odds_dict

            odds_dict: dict
                key: "name"
                value: horse name

                key: "odds"
                value: odds value

                key: "time"
                value: time to execute job

        Examples
        --------
            [
                {
                    "name": "ダイバナナダイスキ",
                    "odds": "7.7",
                    "time": 2022-03-04 22:41:18.786924
                },
                {
                    "name": "プリンニシテヤルノ",
                    "odds": "102.1",
                    "time": 2022-03-04 22:41:18.786924
                },
                {
                    "name": "マヒルタイヨウ",
                    "odds": "17.0",
                    "time": 2022-03-04 22:41:18.786924
                },
                ...
            ]
        """
        now_ = datetime.now()
        odds_list = []

        odds_soup = get_jra_soup_object(self.BASE_URL, odds_param)
        tr_list = odds_soup.find(id="odds_list").find("tbody").find_all("tr")

        for tr in tr_list:
            odds_dict = {}

            odds_dict["name"] = tr.find(class_="horse").text
            odds_dict["odds"] = tr.find(class_="odds_tan").text
            odds_dict["time"] = now_

            odds_list.append(odds_dict)

        return odds_list