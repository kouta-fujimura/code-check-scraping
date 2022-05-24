import csv
import json
from pathlib import Path


def create_folders(dir_path, parents=True, exist_ok=True):
    """Create folders in target dir, defined as dir_path."""
    dir_path.mkdir(parents=parents, exist_ok=exist_ok)

    return None


def dict_to_json(file_path: Path, dict_: dict, ensure_ascii: bool = True) -> None:
    """write dict(key: value format) into json file.
    if not exists, touch from file_path.
    """
    if not file_path.exists():
        file_path.touch()
    else:
        pass

    with file_path.open(mode="w") as f:
        json.dump(dict_, f, ensure_ascii=ensure_ascii)

    return None


def read_json(file_path: Path) -> dict:
    """ read data from json file, and return new dict.
    """
    with file_path.open(mode="r") as f:
        dict_ = json.load(f)

    return dict_


def generate_csv(file_path: Path, header_: list) -> None:
    """Touch csv, and write header.
    """
    with file_path.open(mode="w", newline="") as f:
        writer_ = csv.DictWriter(f, fieldnames=header_)
        writer_.writeheader()

    return None


def append_to_csv(file_path: Path, header_: list, data: list) -> None:
    """Append data to the end of target csv file.
    """
    with file_path.open(mode="a", newline="") as f:
        writer_ = csv.DictWriter(f, fieldnames=header_)
        writer_.writerows(data)

    return None
