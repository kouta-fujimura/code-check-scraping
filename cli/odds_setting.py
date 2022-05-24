import sys
from itertools import starmap
from typing import NamedTuple

from keiba.base import Base
from keiba.utils.date_utils import yyyymmdd_to_jra_date
from keiba.utils.file_utils import dict_to_json
from keiba.utils.keiba_utils import get_jra_soup_object, get_page_param


class KaisaiParam(NamedTuple):
    name: str
    param: str


class OddsSetting(Base):
    """Setup to get odds data.

    Generate params file to jump each odds page.

    file structure:
        output(BASE_PATH)/kaisai_date/(each kaisai_name)/

        (each kaisai_name)/odds_params.json:
            key: race number
            value: page parameter(to jump each odds page)
    """

    def __init__(self, yyyymmdd: str) -> None:
        super().__init__()
        self.kaisai_date = yyyymmdd_to_jra_date(yyyymmdd)

        return None

    def setup_odds(self) -> None:
        result_ = list(starmap(self.func_stream, self.kaisai_params))

        print(f"========{len(result_)} files created========")

        return None

    @property
    def kaisai_params(self) -> list[NamedTuple]:
        """Params to jump odds_kaisai_page from kaisai_list_page.
        This contains self.kaisai_date's params only.

        Returns
        -------
        list
            KaisaiParam: NamedTuple

        Examples
        --------
            [
                KaisaiParam(
                    name: '1回中山1日',
                    param: 'aa01bbl00000000000000000000/AA'
                ),
                KaisaiParam(
                    name: '1回中京1日',
                    param: 'aa01bbl00000000000000000000/AB'
                ),
                ...
            ]
        """
        param = self.ODDS_PAGE_PARAM

        kaisai_params = []

        kaisai_soup = get_jra_soup_object(self.BASE_URL, param)
        panel_list = (
            kaisai_soup.find(id="main").find(class_="thisweek").find_all(class_="panel")
        )

        # filter target date
        target_panel = list(filter(
            lambda x: x.find("h3").text == self.kaisai_date, panel_list
        ))
        if not (len(target_panel) == 1):
            raise ValueError
        else:
            target_panel = target_panel[0]

        a_tag_list = target_panel.find(class_="link_list")("a")
        for a_tag in a_tag_list:
            name = a_tag.text
            param = get_page_param(a_tag)

            kaisai_params.append(
                KaisaiParam(name=name, param=param)
            )

        return kaisai_params

    def func_stream(self, name: str, param: str) -> None:
        """For itertools.starmap, gather methods to use KaisaiParam.
        Params name, param are KaisaiParam's field names.

        Function stream:
            make odds_params,
            get total race num,
            genearete odds_params file.
        """

        odds_params = self._get_odds_params(param)
        total_race = len(odds_params.keys())

        dir_path = self.BASE_PATH / f"{self.kaisai_date}/{name}"
        dict_to_json(dir_path / "odds_params.json", odds_params)

        print(f"{name} created, {total_race}races")

        return None

    def _get_odds_params(self, kaisai_param: NamedTuple) -> dict[str, str]:
        """Get params to jump odds page from kaisai page.

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

        odds_page_dict = {}

        kaisai_soup = get_jra_soup_object(self.BASE_URL, kaisai_param)
        tr_list = kaisai_soup.find(id="race_list").find("tbody").find_all("tr")

        for tr in tr_list:
            race_num = tr.find(class_="race_num").find("img").get("alt")
            race_num = str(race_num.strip("レース"))

            odds_page_param = get_page_param(tr.find(class_="race_num").find("a"))
            odds_page_dict[race_num] = odds_page_param

        return odds_page_dict


if __name__ == "__main__":
    a = OddsSetting(sys.argv[1])
    a.setup_odds()
