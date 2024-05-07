"""
Module regrouping all methods treating json files
"""
import json
import os
import zipfile
from pathlib import Path

import pandas as pd

from ecodev_cloud.constants import UTF8_STR
from ecodev_cloud.disk.disk_helpers import disk_rglob


def load_text_file(file_path: Path) -> str:
    """
    Read a text from a file
    """
    with open(file_path, 'r', encoding=UTF8_STR) as f_stream:
        text = f_stream.read()

    return text


def write_text_file(file_path: Path, data: str) -> None:
    """
    Save a text
    """
    with open(file_path, 'w', encoding=UTF8_STR) as f:
        f.write(data)


def write_png_file(file_path: Path, data: bytes) -> None:
    """
    Save a png image
    """
    with open(file_path, 'wb') as f:
        f.write(data)


def write_json_file(file_path: Path, json_data:  dict | list) -> None:
    """
    Write json_data at file_path location
    """
    os.umask(0)
    with open(file_path, 'w', encoding=UTF8_STR) as f:
        f.write(str(json.dumps(json_data, indent=4)))


def load_json_file(file_path: Path) -> dict | list:
    """
    Load a json file at file_path location
    """
    with open(file_path, 'r', encoding=UTF8_STR) as f:
        loaded_json = json.load(f)

    return loaded_json


def get_in_memory_json_data(data: bytes) -> dict | list:
    """
    Retrieve json data out of the passed data bytes
    """
    return json.loads(data)


def save_xlsx(file_path: Path, data: dict[str, pd.DataFrame]):
    """
    Save a Dict of (str, DataFrame) data at xlsx format
    """
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        for sheet_name, df in data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)


def save_folder(file_path: Path, data: Path):
    """
    Save a zipped folder
    """
    with zipfile.ZipFile(file_path.name, mode='w') as f:
        for fp in disk_rglob(data):
            f.write(fp, str(fp.relative_to(data)))


def get_common_ancestor(current_path: Path, folder: Path) -> Path:
    """
    Subtlety when the current path is a file directly into the folder we want to iterdir on
    """
    parents = list(current_path.relative_to(folder).parents)
    try:
        return parents[-2]
    except IndexError:
        return Path(current_path.name)
