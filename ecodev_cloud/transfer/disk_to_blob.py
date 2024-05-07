"""
Module migrating all relevant files from Disk to Azure blob storage
"""
from functools import partial
from pathlib import Path

from ecodev_cloud.cloud.blob.blob_container import CONTAINER
from ecodev_cloud.cloud.blob.blob_helpers import blob_upload
from ecodev_cloud.disk.disk_helpers import disk_is_dir
from ecodev_cloud.disk.disk_helpers import disk_rglob
from ecodev_cloud.transfer.migration_helpers import to_blob


def transfer_disk_to_blob(folders: list[Path],
                          index_folder: Path,
                          container: str = CONTAINER
                          ) -> None:
    """
    Robust migration from all disk content to Azure blob storage
    """
    to_blob(folders, partial(_transfer_file, container=container), disk_rglob, index_folder,
            disk_is_dir)


def _transfer_file(file_path: Path, container: str) -> None:
    """
    Transfer file_path from disk to Azure blob storage.
    """
    blob_upload(file_path, file_path, location=container)
