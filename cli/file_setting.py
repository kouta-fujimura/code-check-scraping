from itertools import starmap
from pathlib import Path
from typing import NamedTuple

from bs4 import BeautifulSoup as bs
from keiba.base import Base
from keiba.utils.date_utils import jihun_to_hhmm, nengappi_to_yyyymmdd
from keiba.utils.file_utils import create_folders, dict_to_json, generate_csv, read_json
from keiba.utils.keiba_utils import get_jra_soup_object, get_page_param


class KaisaiParam(NamedTuple):
    date_: str
    name: str
    param: str


class RaceCardParam(NamedTuple):
    dir_: Path
    race_num: str
    param: str


class Settings(Base):
    """Create file structure, and Generate Race info files for storing odds.

    Create file structure:
        Make ouput folders to store files(race start time, odds).
        And touch race_params.json to jump each race_card page in JRA site.

        file structure:
            output(BASE_PATH)/kaisai_date/kaisai_name/

        race_params.json:
            key: race number
            value: page parameter(to jump each race_card page)


    Generate race info files:
        Each file is placed into 'output(BASE_PATH)/kaisai_date/kaisai_name/'
        To get race info, Use race_params.json to jump each race card page.
        (dir and json file are already created by FileStructure.setup_file_structure)

        race_{num}.csv:
            file for storing each time odds in each race.
            generated from 'self._generate_odds_storing_file'.
            if kaisai has 12races, 12 files are created(race_1.csv ~ race_12.csv).

            heaeder: name, odds, time

        times.json:
            file that contains each race's start time.
            this file is used to setup schedule .
            generated from self._generate_times_file.
            regardless of races, generate 1 file by 1 kaisai.

            key: race_num
            value: start_time(yyyymmddhhmm)
    """

    def __init__(self) -> None:
        super().__init__()

        return None

    def execute(self) -> None:

        if not self.BASE_PATH.exists():
            create_folders(self.BASE_PATH)
            print("output folder created")
        else:
            pass

        dirs = list(starmap(self.file_structure_stream, self.kaisai_params))

        print("========File structure created========")

        for dir_ in dirs:
            dir_path = self.BASE_PATH / dir_
            file_path = dir_path / "race_params.json"

            race_card_dict = read_json(file_path)
            race_card_params = [
                RaceCardParam(dir_=dir_path, race_num=race_num, param=param)
                for race_num, param in race_card_dict.items()
            ]

            times = dict(starmap(self.files_stream, race_card_params))
            dict_to_json(dir_path / "times.json", times)

            print(f"{dir_} {len(times.keys())} race created")

        print("======All Files created======")

        return None

    @property
    def kaisai_params(self) -> list[NamedTuple]:
        """Params to jump kaisai page from kaisai_list page.
        If kaisai name has '馬番確定', strip it.

        Returns
        -------
        list
            KaisaiParam: NamedTuple

        Examples
        --------
            [
                KaisaiParam(
                    date_: '1月5日（土曜）',
                    name: '1回中山1日',
                    param: 'aa01bbl00000000000000000000/AA'
                ),
                KaisaiParam(
                    date_: '1月5日（土曜）',
                    name: '1回中京2日',
                    param: 'aa01bbl00000000000000000000/AB'
                ),
                ...
            ]
        """
        param = self.SCHEDULE_PAGE_PARAM

        kaisai_params = []

        kaisai_soup = get_jra_soup_object(self.BASE_URL, param)
        panel_list = kaisai_soup.find(id="main").find_all(class_="panel")

        for panel in panel_list:
            date_str = panel.find("h3").text
            a_tag_list = panel.find(class_="link_list")("a")

            for a_tag in a_tag_list:
                name = a_tag.text.strip("馬番確定")
                param = get_page_param(a_tag)

                kaisai_params.append(
                    KaisaiParam(date_=date_str, name=name, param=param)
                )

        return kaisai_params

    def file_structure_stream(self, date_: str, name: str, param: str) -> str:
        """For itertools.starmap, gather methods to use KaisaiParam.
        Params date_, name, param are KaisaiParam's field names.

        Function stream:
            make race_card_params,
            create dir,
            genearete race_card_params file.

        """
        dir_path = self.BASE_PATH / f"{date_}/{name}"
        race_card_params = self._make_race_card_params(param)

        create_folders(dir_path)
        dict_to_json(dir_path / "race_params.json", race_card_params)

        print("".join([date_, name]))

        return "/".join([date_, name])

    def _make_race_card_params(self, kaisai_param: str) -> dict[str, str]:
        """Get params to jump race_card page from kaisai page.

        Returns
        -------
        dict
            key: race number
            value: page parameter

        Examples
        --------
            {
                '1': 'aa01bbl00000000000000000000/AA',
                '2': 'aa01bbl00000000000000000000/AB',
                '3': 'aa01bbl00000000000000000000/AC',
                ...
            }
        """

        race_card_dict = {}

        kaisai_soup = get_jra_soup_object(self.BASE_URL, kaisai_param)
        tr_list = kaisai_soup.find(id="race_list").find("tbody").find_all("tr")

        for tr in tr_list:
            race_num = tr.find(class_="race_num").find("img").get("alt")
            race_num = str(race_num.strip("レース"))

            race_card_param = get_page_param(tr.find(class_="syutsuba").find("a"))
            race_card_dict[race_num] = race_card_param

        return race_card_dict

    def files_stream(self, dir_path: Path, race_num: str, param: str) -> tuple:
        """For itertools.starmap, gather methods to use RaceCardParam.
        Params dir_path, race_num, param are RaceCardParam's field names.

        Function stream:
            generate odds_storing_file,
            make race_start_time tuple,
            and retrun it.
        """
        race_card_soup = get_jra_soup_object(self.BASE_URL, param)

        # generate race_{num}.csv
        header_ = ["name", "odds", "time"]
        generate_csv(dir_path / f"race_{race_num}.csv", header_)

        # make times_dict
        start_time = self._make_start_time(race_card_soup, race_num)

        return start_time

    def _make_start_time(self, race_card_soup: bs, race_num: str) -> tuple:
        """Get race's start time from race_card_soup.

        Returns
        -------

        tuple
            race_num: str
            start_time: str(yyyymmddhhmm format)
        """

        datetime_soup = race_card_soup.find(id="syutsuba").find(class_="date_line")

        # ex) yyyy年mm月dd日（～曜） n回阪神n日
        date_str = datetime_soup.find(class_="date").text.split(" ")[0]
        nengappi = date_str.split("（")[0]

        yyyymmdd = nengappi_to_yyyymmdd(nengappi)

        # ex) 発送時刻：h時mm分\n
        time_str = datetime_soup.find(class_="time").text
        time_str = time_str.split("：")[1].rstrip("\n")

        hhmm = jihun_to_hhmm(time_str)

        start_time = "".join(yyyymmdd + hhmm)

        return (race_num, start_time)


if __name__ == "__main__":
    settings = Settings()
    settings.execute()
