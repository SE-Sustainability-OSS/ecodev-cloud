"""
Module migrating all relevant files from S3 to Azure blob storage
"""
import tempfile
from functools import partial
from pathlib import Path

from ecodev_cloud.cloud.blob.blob_container import CONTAINER
from ecodev_cloud.cloud.blob.blob_helpers import blob_upload
from ecodev_cloud.cloud.cloud_helpers import cloud_is_dir
from ecodev_cloud.cloud.s3.s3_bucket import BUCKET
from ecodev_cloud.cloud.s3.s3_helpers import download_s3_object
from ecodev_cloud.cloud.s3.s3_helpers import s3_rglob
from ecodev_cloud.transfer.migration_helpers import to_blob


def transfer_s3_to_blob(folders: list[Path],
                        index_folder: Path,
                        bucket: str = BUCKET,
                        container: str = CONTAINER
                        ) -> None:
    """
    Robust migration from all s3 content (in folder keys) to Azure blob storage.
    """
    transferer = partial(_transfer_file, bucket=bucket, container=container)
    to_blob(folders, transferer, partial(s3_rglob, location=bucket), index_folder, cloud_is_dir)


def _transfer_file(file_path: Path, bucket: str, container: str) -> None:
    """
    Transfer file_path from S3 to Azure blob storage.
    """
    with tempfile.TemporaryDirectory() as folder:
        download_s3_object(file_path, Path(folder) / file_path.name, location=bucket)
        blob_upload(Path(folder) / file_path.name, file_path, location=container)
