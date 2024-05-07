"""
Module implementing all disk loading methods
"""
from pathlib import Path
from typing import Any
from typing import Callable

import pandas as pd
from ecodev_core import logger_get

from ecodev_cloud.constants import CSV_EXT
from ecodev_cloud.constants import GPKG_EXT
from ecodev_cloud.constants import JSON_EXT
from ecodev_cloud.constants import LATEX_EXT
from ecodev_cloud.constants import NETCDF_EXT
from ecodev_cloud.constants import NPY_EXT
from ecodev_cloud.constants import NPZ_EXT
from ecodev_cloud.constants import SHP_EXT
from ecodev_cloud.constants import TIF_EXT
from ecodev_cloud.constants import TXT_EXT
from ecodev_cloud.constants import XLSX_EXT
from ecodev_cloud.file_processing.basic_file_processing import load_json_file
from ecodev_cloud.file_processing.basic_file_processing import load_text_file
from ecodev_cloud.file_processing.netcdf_processing import read_netcdf
from ecodev_cloud.file_processing.numpy_processing import get_npz_data
from ecodev_cloud.file_processing.numpy_processing import get_numpy_data
from ecodev_cloud.file_processing.shapely_processing import load_shp
from ecodev_cloud.file_processing.tif_processing import get_tif_tile


log = logger_get(__name__)
DATA_TYPE = Any
DISK_LOADERS: dict[str, Callable[[Path], DATA_TYPE]] = {
    NPZ_EXT: get_npz_data,
    NPY_EXT: get_numpy_data,
    NETCDF_EXT: read_netcdf,
    JSON_EXT: load_json_file,
    SHP_EXT: load_shp,
    GPKG_EXT: load_shp,
    TIF_EXT: get_tif_tile,
    CSV_EXT: pd.read_csv,
    TXT_EXT: load_text_file,
    LATEX_EXT: load_text_file,
    XLSX_EXT: pd.ExcelFile
}


def disk_load(file_path: Path) -> DATA_TYPE:
    """
    Load disk data from file_path location.

    Pick the correct loading method thanks to file_path file extension.
    """
    if not (loader := DISK_LOADERS.get(file_path.suffix)):
        raise AttributeError(f'{file_path.suffix} extension of {file_path.name=} is not supported')

    try:
        return loader(file_path)
    except Exception as error:
        log.crtical(f'loading failed: {error} happened')
