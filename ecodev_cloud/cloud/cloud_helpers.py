"""
Module implementing cloud helper methods centered around pathlib like behaviours
"""
from pathlib import Path
from typing import Iterator

from ecodev_cloud.cloud.blob.blob_helpers import blob_copy_file
from ecodev_cloud.cloud.blob.blob_helpers import blob_exists
from ecodev_cloud.cloud.blob.blob_helpers import blob_iterdir
from ecodev_cloud.cloud.blob.blob_helpers import blob_move_file
from ecodev_cloud.cloud.blob.blob_helpers import blob_move_folder
from ecodev_cloud.cloud.blob.blob_helpers import blob_rglob
from ecodev_cloud.cloud.blob.blob_helpers import CONTAINER
from ecodev_cloud.cloud.blob.blob_helpers import delete_blob_content
from ecodev_cloud.cloud.blob.blob_helpers import download_blob_object
from ecodev_cloud.cloud.blob.blob_helpers import get_blob_url
from ecodev_cloud.cloud.cloud import CLOUD
from ecodev_cloud.cloud.cloud import Cloud
from ecodev_cloud.cloud.s3.s3_helpers import BUCKET
from ecodev_cloud.cloud.s3.s3_helpers import delete_s3_content
from ecodev_cloud.cloud.s3.s3_helpers import download_s3_object
from ecodev_cloud.cloud.s3.s3_helpers import get_s3_url
from ecodev_cloud.cloud.s3.s3_helpers import s3_copy_file
from ecodev_cloud.cloud.s3.s3_helpers import s3_exists
from ecodev_cloud.cloud.s3.s3_helpers import s3_iterdir
from ecodev_cloud.cloud.s3.s3_helpers import s3_move_file
from ecodev_cloud.cloud.s3.s3_helpers import s3_move_folder
from ecodev_cloud.cloud.s3.s3_helpers import s3_rglob
from ecodev_cloud.constants import FILE_EXTENSIONS


def cloud_move_folder(origin: Path,
                      dest: Path,
                      dist_origin: bool = False,
                      delete_file: bool = True,
                      cloud: Cloud = CLOUD
                      ) -> None:
    """
    Move all files in the origin folder (either present locally or already on the cloud,
     depending on dist_origin) to cloud storage

    Attributes are:
        - origin: folder to move
        - dest: where to move origin
        - dist_origin: whether the origin folder is already on the blob or on a local filesystem
        - delete_file: whether to delete or not the origin folder. If false, amount to cp and not mv
        - cloud: cloud provider to use for the move
    """
    if cloud == Cloud.AZURE:
        return blob_move_folder(origin, dest, dist_origin=dist_origin, delete_file=delete_file)
    return s3_move_folder(origin, dest, dist_origin=dist_origin, delete_file=delete_file)


def cloud_copy_file(origin: Path,
                    dest: Path,
                    dist_origin: bool = False,
                    cloud: Cloud = CLOUD,
                    location: str | None = None
                    ) -> None:
    """
    Copy origin either present locally or already on the cloud (depending on dist_origin) to cloud.

    Attributes are:
        - origin: folder to copy
        - dest: where to copy origin
        - dist_origin: whether the origin folder is already on the blob or on a local filesystem
        - location: container/buket name inside the azure/s3 storage on which to move
        - cloud: cloud provider to use for the move
    """
    if cloud == Cloud.AZURE:
        return blob_copy_file(origin, dest, dist_origin=dist_origin, location=location or CONTAINER)
    return s3_copy_file(origin, dest, dist_origin=dist_origin, location=location or BUCKET)


def cloud_move_file(origin: Path,
                    dest: Path,
                    dist_origin: bool = False,
                    delete_file: bool = True,
                    cloud: Cloud = CLOUD
                    ) -> None:
    """
    Move origin either present locally or already on the cloud (depending on dist_origin) to cloud.

    Attributes are:
        - origin: file to move
        - dest: where to move origin
        - dist_origin: whether the origin file is already on the blob or on a local filesystem
        - delete_file: whether to delete or not the origin file. If false, amount to cp and not mv
        - cloud: cloud provider to use for the move
    """
    if cloud == Cloud.AZURE:
        return blob_move_file(origin, dest, dist_origin=dist_origin, delete_file=delete_file)
    return s3_move_file(origin, dest, dist_origin=dist_origin, delete_file=delete_file)


def get_cloud_url(file_path: Path, timeout: int = 3600, cloud: Cloud = CLOUD) -> str | None:
    """
    Generate a cloud_url.
    Expiration is the time in seconds for the URL to remain valid.
    """
    if cloud == Cloud.AZURE:
        return get_blob_url(file_path, timeout=timeout)
    return get_s3_url(file_path, timeout=timeout)


def cloud_is_dir(file_path: Path) -> bool:
    """
    Check if a cloud file_path is a folder or not
    """
    return file_path.suffix not in FILE_EXTENSIONS


def cloud_rglob(file_path: Path,
                pattern: str | None = None,
                cloud: Cloud = CLOUD
                ) -> Iterator[Path]:
    """
    Rglob functionality: recursively find all files in the file_path folder having passed pattern
    """
    if cloud == Cloud.AZURE:
        return blob_rglob(file_path, pattern=pattern)
    return s3_rglob(file_path, pattern=pattern)


def cloud_iterdir(file_path: Path, cloud: Cloud = CLOUD) -> Iterator[Path]:
    """
    list all files and folders directly in the cloud file_path folder.
    """
    if cloud == Cloud.AZURE:
        return blob_iterdir(file_path)
    return s3_iterdir(file_path)


def cloud_exists(file_path: Path, cloud: Cloud = CLOUD) -> bool:
    """
    Check if a file_path exists, either locally or on a cloud
    """
    if cloud == Cloud.AZURE:
        return blob_exists(file_path)
    return s3_exists(file_path)


def download_cloud_object(file_path: Path, local_path: Path, cloud: Cloud = CLOUD) -> None:
    """
    Download on disk at local_path location the content of location at file_path cloud location.
    """
    if cloud == Cloud.AZURE:
        return download_blob_object(file_path, local_path)
    return download_s3_object(file_path, local_path)


def delete_cloud_content(file_path: Path,  cloud: Cloud = CLOUD) -> None:
    """
    Delete content from a cloud at file_path location
    """
    if cloud == Cloud.AZURE:
        return delete_blob_content(file_path)
    return delete_s3_content(file_path)
