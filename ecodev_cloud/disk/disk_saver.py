"""
Module implementing all disk saving methods
"""
from pathlib import Path
from typing import Callable

from ecodev_core import logger_get
from ecodev_core import make_dir

from ecodev_cloud.constants import CSV_EXT
from ecodev_cloud.constants import JSON_EXT
from ecodev_cloud.constants import LATEX_EXT
from ecodev_cloud.constants import NPY_EXT
from ecodev_cloud.constants import NPZ_EXT
from ecodev_cloud.constants import PNG_EXT
from ecodev_cloud.constants import SHP_EXT
from ecodev_cloud.constants import TXT_EXT
from ecodev_cloud.constants import XLSX_EXT
from ecodev_cloud.constants import ZIP_EXT
from ecodev_cloud.disk.disk_loader import DATA_TYPE
from ecodev_cloud.file_processing.basic_file_processing import save_folder
from ecodev_cloud.file_processing.basic_file_processing import save_xlsx
from ecodev_cloud.file_processing.basic_file_processing import write_json_file
from ecodev_cloud.file_processing.basic_file_processing import write_png_file
from ecodev_cloud.file_processing.basic_file_processing import write_text_file
from ecodev_cloud.file_processing.numpy_processing import save_numpy_compressed_data
from ecodev_cloud.file_processing.numpy_processing import save_numpy_data
from ecodev_cloud.file_processing.shapely_processing import save_polygon


log = logger_get(__name__)
"""
All saving mechanism implemented should be reference here
"""
DISK_SAVERS: dict[str, Callable] = {
    NPZ_EXT: save_numpy_compressed_data,
    NPY_EXT: save_numpy_data,
    JSON_EXT: write_json_file,
    CSV_EXT: lambda fp, x: x.to_csv(fp, index=False),
    XLSX_EXT: save_xlsx,
    TXT_EXT: write_text_file,
    LATEX_EXT: write_text_file,
    SHP_EXT: save_polygon,
    ZIP_EXT: save_folder,
    PNG_EXT: write_png_file
}


def disk_save(file_path: Path, data: DATA_TYPE) -> None:
    """
    Store data at disk file_path location.
    Pick the correct saving method thanks to file_path file extension.
    """
    if not (saver := DISK_SAVERS.get(file_path.suffix)):
        raise AttributeError(f'{file_path.suffix} extension of {file_path.name=} is not supported')

    try:
        make_dir(file_path.parent)
        return saver(file_path, data)
    except Exception as error:
        log.crtical(f'saving failed: {error} happened')
