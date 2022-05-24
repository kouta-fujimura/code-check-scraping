import sys

import boto3
from keiba.base import Base
from keiba.utils.date_utils import yyyymmdd_to_jra_date
from keiba.utils.file_utils import dict_to_json, read_json
from keiba.utils.keiba_utils import get_jra_soup_object, get_page_param


class RaceResults(Base):
    """Generate race result files."""

    def __init__(self, yyyymmdd: str) -> None:
        super().__init__()
        self.kaisai_date = yyyymmdd_to_jra_date(yyyymmdd)
        self.dir_path = self.BASE_PATH / self.kaisai_date

    def generate_results(self):
        print("Create result files")
        for kaisai_path in self.dir_path.iterdir():
            kaisai_name = kaisai_path.name
            kaisai_dict = {}

            race_page_params = read_json(kaisai_path / "race_params.json")

            for race_num, param in race_page_params.items():
                result_param = self._get_result_param(param)

                place_dict = self._make_place_dict(result_param)
                kaisai_dict[race_num] = place_dict

            dict_to_json(
                kaisai_path / "race_result.json", kaisai_dict, ensure_ascii=False
            )
            print(f"{kaisai_name} done")

        print("======All Results created======")

        return None

    def _get_result_param(self, race_page_param: str) -> str:
        """Get jra result page's params from race_card_page.
        To jump to jra race_card_page, use each kaisai's race_params.json.
        """

        race_card_soup = get_jra_soup_object(self.BASE_URL, race_page_param)
        result_a_tag = (
            race_card_soup.find(class_="race_header").find(class_="result").find("a")
        )
        result_param = get_page_param(result_a_tag)

        return result_param

    def _make_place_dict(self, result_param: str) -> dict[str, str]:
        """Generate each race's place dict from jra race_result_page.

        Returns
        -------
        dict
            key: horse_name
            values: place

        Examples
        --------
            {
            'ダイバナナダイスキ': 1,
            'プリンニシテヤルノ': 2,
            'マヒルタイヨウ': 3,
            ...
            }
        """

        results_dict = {}

        result_soup = get_jra_soup_object(Base.BASE_URL, result_param)
        tr_list = (
            result_soup.find(class_="race_result_unit").find("tbody").find_all("tr")
        )

        for tr in tr_list:
            horse_name = tr.find(class_="horse").text.strip("\n")
            place_ = tr.find(class_="place").text
            results_dict[horse_name] = place_

        return results_dict


class FileArchive(Base):
    """Archive keiba files to s3."""

    def __init__(self, yyyymmdd: str) -> None:
        super().__init__()
        self.yyyymmdd = yyyymmdd
        self.kaisai_date = yyyymmdd_to_jra_date(yyyymmdd)
        self.dir_path = self.BASE_PATH / self.kaisai_date

    def execute(self):

        self.delete_files()
        self.upload_files()

        return None

    def delete_files(self):
        print("Delete times, odds_params")

        # Delete times.json, race_params.json, and odds_params.json if exists
        files = ["times.json", "odds_params.json"]
        for kaisai_name_path in self.dir_path.iterdir():
            for f in kaisai_name_path.iterdir():
                if f.name in files:
                    f.unlink(missing_ok=True)
                    print(f"{f.name} deleted")
                else:
                    pass

        print("Files deleted")
        return None

    def upload_files(self):
        """Upload race files to aws s3 bucket.
        """

        s3 = boto3.resource("s3")
        archive_bucket = s3.Bucket(self.ARCHIVE_BUCKET)

        for kaisai_name_path in self.dir_path.iterdir():
            kaisai_name = kaisai_name_path.name
            for f in kaisai_name_path.iterdir():
                file_name = "/".join([self.yyyymmdd, kaisai_name, f.name])
                archive_bucket.upload_file(str(f), file_name)
            print(f"{kaisai_name} files uploaded.")

        print("======All files uploaded to S3 bucket======")

        return None


if __name__ == "__main__":
    yyyymmdd = sys.argv[1]

    results = RaceResults(yyyymmdd)
    results.generate_results()

    archive = FileArchive(yyyymmdd)
    archive.execute()
