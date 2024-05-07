"""
Module implementing all atomic saving methods
"""
import tempfile
from functools import partial
from pathlib import Path
from typing import Any
from typing import Callable

from ecodev_core import logger_get

from ecodev_cloud.cloud.blob.blob_container import CONTAINER
from ecodev_cloud.cloud.blob.blob_helpers import blob_upload
from ecodev_cloud.cloud.cloud import CLOUD
from ecodev_cloud.cloud.cloud import Cloud
from ecodev_cloud.cloud.s3.s3_bucket import BUCKET
from ecodev_cloud.cloud.s3.s3_helpers import s3_upload
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
from ecodev_cloud.file_processing.shapely_processing import save_shp

log = logger_get(__name__)

"""
All saving mechanism implemented should be reference here
"""
CLOUD_SAVERS: dict[str, Callable[[Path, Any], None]] = {
    NPZ_EXT: lambda fp, data: save_numpy_compressed_data(fp.parent / fp.stem, data),
    NPY_EXT: save_numpy_data,
    JSON_EXT: write_json_file,
    CSV_EXT: lambda fp, data:  data.to_csv(fp, index=False),
    XLSX_EXT: save_xlsx,
    TXT_EXT: write_text_file,
    LATEX_EXT: write_text_file,
    SHP_EXT: save_shp,
    ZIP_EXT: save_folder,
    PNG_EXT: write_png_file
}


def save_cloud_data(file_path: Path,
                    data: DATA_TYPE,
                    cloud: Cloud = CLOUD,
                    location: str | None = None
                    ) -> None:
    """
    Store data at cloud file_path location.
    """
    if cloud == Cloud.AZURE:
        return save_blob_data(file_path, data, location=location or CONTAINER)
    return save_s3_data(file_path, data, location=location or BUCKET)


def save_s3_data(file_path: Path, data: DATA_TYPE, location: str = BUCKET) -> None:
    """
    Store data at S3 file_path location.
    """
    _cloud_save(file_path, data, uploader=partial(s3_upload, location=location))


def save_blob_data(file_path: Path, data: DATA_TYPE, location: str = CONTAINER) -> None:
    """
    Store data at blob file_path location.
    """
    _cloud_save(file_path, data,  uploader=partial(blob_upload, location=location))


def _cloud_save(file_path: Path, data: DATA_TYPE, uploader: Callable) -> None:
    """
    Store data at blob file_path location.
    Pick the correct saving method thanks to file_path file extension..
    """
    if not (saver := CLOUD_SAVERS.get(suffix := file_path.suffix)):
        raise AttributeError(f'{suffix} extension of {file_path.name=} is not supported')

    try:
        with tempfile.TemporaryDirectory() as folder:
            saver(Path(folder) / file_path.name, data)
            store_path = file_path if suffix != SHP_EXT else file_path.with_suffix(ZIP_EXT)
            uploader(Path(folder) / store_path.name, store_path)
    except Exception as error:
        log.crtical(f'saving failed: {error} happened')
