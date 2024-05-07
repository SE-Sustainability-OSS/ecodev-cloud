"""
Module implementing cloud loading methods
"""
from functools import partial
from pathlib import Path
from typing import Any
from typing import Callable

import pandas as pd
from ecodev_core import logger_get

from ecodev_cloud.cloud.blob.blob_container import CONTAINER
from ecodev_cloud.cloud.blob.blob_helpers import get_blob_object
from ecodev_cloud.cloud.cloud import CLOUD
from ecodev_cloud.cloud.cloud import Cloud
from ecodev_cloud.cloud.s3.s3_bucket import BUCKET
from ecodev_cloud.cloud.s3.s3_helpers import get_s3_object
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
from ecodev_cloud.constants import UTF8_STR
from ecodev_cloud.constants import XLSX_EXT
from ecodev_cloud.constants import ZIP_EXT
from ecodev_cloud.disk.disk_loader import DATA_TYPE
from ecodev_cloud.file_processing.basic_file_processing import get_in_memory_json_data
from ecodev_cloud.file_processing.netcdf_processing import read_data_netcdf
from ecodev_cloud.file_processing.numpy_processing import get_npz_data
from ecodev_cloud.file_processing.numpy_processing import get_numpy_data
from ecodev_cloud.file_processing.shapely_processing import load_memory_gpkg
from ecodev_cloud.file_processing.shapely_processing import load_zipped_shp
from ecodev_cloud.file_processing.tif_processing import get_in_memory_tile

log = logger_get(__name__)

CLOUD_LOADERS: dict[str, Callable[[Any], DATA_TYPE]] = {
    NPZ_EXT: get_npz_data,
    NPY_EXT: get_numpy_data,
    NETCDF_EXT: read_data_netcdf,
    JSON_EXT: get_in_memory_json_data,
    SHP_EXT: load_zipped_shp,
    GPKG_EXT: load_memory_gpkg,
    TIF_EXT: get_in_memory_tile,
    CSV_EXT: pd.read_csv,
    TXT_EXT: lambda x: x.decode(UTF8_STR),
    LATEX_EXT: lambda x: x.decode(UTF8_STR),
    XLSX_EXT: pd.ExcelFile
}


def load_cloud_data(file_path: Path,
                    cloud: Cloud = CLOUD,
                    location: str | None = None
                    ) -> DATA_TYPE:
    """
    Load cloud data from file_path location.
    """
    if cloud == Cloud.AZURE:
        return load_blob_data(file_path, location=location or CONTAINER)
    return load_s3_data(file_path, location=location or BUCKET)


def load_s3_data(file_path: Path, location: str = BUCKET) -> DATA_TYPE:
    """
    Load S3 data from file_path location.
    """
    return _cloud_load(file_path, partial(get_s3_object, location=location))


def load_blob_data(file_path: Path, location: str = CONTAINER) -> DATA_TYPE:
    """
    Load blob data from file_path location.
    """
    return _cloud_load(file_path, partial(get_blob_object, location=location))


def _cloud_load(file_path: Path, getter: Callable) -> DATA_TYPE:
    """
    Load cloud data from file_path location.

    Pick the correct loading method thanks to file_path file extension.
    """
    if not (loader := CLOUD_LOADERS.get(suffix := file_path.suffix)):
        raise AttributeError(f'{suffix} extension of {file_path.name=} is not supported')

    try:
        load_path = file_path.with_suffix(ZIP_EXT) if suffix == SHP_EXT else file_path
        return loader(getter(load_path, _is_byte(suffix)))
    except Exception as error:
        log.crtical(f'loading failed: {error} happened')


def _is_byte(suffix: str) -> bool:
    """
    Check if the file requires byte loading or not
    """
    return suffix in [NPY_EXT, NPZ_EXT, CSV_EXT, XLSX_EXT, SHP_EXT, GPKG_EXT]
