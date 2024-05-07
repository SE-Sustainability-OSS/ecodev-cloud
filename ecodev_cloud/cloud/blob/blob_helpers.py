"""
Module implementing blob helper methods centered around pathlib like behaviours
"""
import datetime
from io import BytesIO
from pathlib import Path
from typing import Iterator

from azure.storage.blob import BlobSasPermissions
from azure.storage.blob import generate_blob_sas

from ecodev_cloud.cloud.blob.blob_container import CONTAINER
from ecodev_cloud.cloud.blob.blob_container import container
from ecodev_cloud.file_processing.basic_file_processing import get_common_ancestor
from ecodev_cloud.path_utils import forge_key
from ecodev_cloud.path_utils import ROOT_DIRECTORY


def get_blob_object(file_path: Path,  byte: bool = False, location: str = CONTAINER):
    """
    Retrieve a blob object from Azure blob storage
    """
    data = container(location).get_blob_client(forge_key(file_path)).download_blob().readall()
    return BytesIO(data) if byte else data


def blob_upload(source_path: Path, dest_path: Path, location: str = CONTAINER):
    """
    Upload content of source_path to dest_path on Azure blob storage
    """
    with open(source_path, 'rb') as data:
        container(location).upload_blob(name=forge_key(dest_path), data=data, overwrite=True)


def blob_move_folder(origin: Path,
                     dest: Path,
                     dist_origin: bool = False,
                     delete_file: bool = True,
                     location: str = CONTAINER) -> None:
    """
    Move all files in the origin folder (either present locally or already on the blob,
     depending on dist_origin) to blob storage

    Attributes are:
        - origin: folder to move
        - dest: where to move origin
        - dist_origin: whether the origin folder is already on the blob or on a local filesystem
        - delete_file: whether to delete or not the origin folder. If false, amount to cp and not mv
        - location: container name inside the azure storage on which to move
    """
    for origin_path in blob_rglob(origin):
        blob_move_file(origin_path, dest / origin_path.relative_to(origin),
                       dist_origin=dist_origin, delete_file=delete_file, location=location)


def blob_copy_file(origin: Path,
                   dest: Path,
                   location: str = CONTAINER,
                   dist_origin: bool = False) -> None:
    """
    Copy origin either present locally or already on the blob (depending on dist_origin) to blob.

    Attributes are:
        - origin: folder to copy
        - dest: where to copy origin
        - location: container name inside the azure storage on which to move
        - dist_origin: whether the origin folder is already on the blob or on a local filesystem
    """
    blob_move_file(origin, dest, location=location, dist_origin=dist_origin, delete_file=False)


def blob_move_file(origin: Path,
                   dest: Path,
                   location: str = CONTAINER,
                   dist_origin: bool = False,
                   delete_file: bool = True) -> None:
    """
    Move origin either present locally or already on the blob (depending on dist_origin) to blob.

     Attributes are:
        - origin: file to move
        - dest: where to move origin
        - location: container name inside the azure storage on which to move
        - dist_origin: whether the origin file is already on the blob or on a local filesystem
        - delete_file: whether to delete or not the origin file. If false, amount to cp and not mv
    """
    if dist_origin:
        blob_client = container(location).get_blob_client(forge_key(origin))
        new_blob_client = container(location).get_blob_client(forge_key(dest))
        new_blob_client.start_copy_from_url(blob_client.url)
        if delete_file:
            blob_client.delete_blob()
    else:
        blob_upload(origin, dest, location)
        if delete_file:
            origin.unlink()


def get_blob_url(file_path: Path, timeout: int = 3600, location: str = CONTAINER) -> str:
    """
    Generate a sas token and then an URL to share a blob object
    Expiration is the time in seconds for the URL to remain valid.
    https://learn.microsoft.com/en-us/azure/storage/blobs/sas-service-create-python
    """
    start_time = datetime.datetime.now(datetime.timezone.utc)
    expiry_time = start_time + datetime.timedelta(seconds=timeout)
    data = container(location).get_blob_client(forge_key(file_path))
    sas_token = generate_blob_sas(
        account_name=data.account_name,
        container_name=data.container_name,
        blob_name=data.blob_name,
        account_key=data.credential.account_key,
        permission=BlobSasPermissions(read=True),
        expiry=expiry_time,
        start=start_time
    )
    url = data._hosts['primary']
    prefix = 'http' if 'azurite' in url else 'https'
    return f"{prefix}://{data._hosts['primary']}/{data.container_name}/{data.blob_name}?{sas_token}"


def blob_rglob(file_path: Path,
               pattern: str | None = None,
               location: str = CONTAINER) -> Iterator[Path]:
    """
    Rglob functionality: recursively find all files in the file_path folder having passed pattern
    """
    cleaned_pattern = pattern.replace('*', '') if pattern else None
    for fp in container(location).list_blob_names(name_starts_with=forge_key(file_path)):
        if not cleaned_pattern or cleaned_pattern in str(fp):
            yield ROOT_DIRECTORY / fp


def blob_iterdir(file_path: Path, location: str = CONTAINER) -> Iterator[Path]:
    """
    list all files and folders directly in the blob file_path folder.
    """
    files = {file_path / get_common_ancestor(ROOT_DIRECTORY / elt, file_path)
             for elt in container(location).list_blob_names(
        name_starts_with=str(forge_key(file_path)))
        if elt != file_path}
    yield from sorted(list(files))


def blob_exists(file_path: Path, location: str = CONTAINER) -> bool:
    """
    Check if a file_path exists, either locally or on a blob
    """
    return container(location).get_blob_client(forge_key(file_path)).exists()


def download_blob_object(file_path: Path, local_path: Path, location: str = CONTAINER) -> None:
    """
    Download on disk at local_path location the content of location at file_path blob location.
    """
    blob = container(location).get_blob_client(forge_key(file_path))
    with open(file=local_path, mode='wb') as sample_blob:
        download_stream = blob.download_blob()
        sample_blob.write(download_stream.readall())


def delete_blob_content(file_path: Path, location: str = CONTAINER) -> None:
    """
    Delete content from a blob at file_path location
    """
    container(location).get_blob_client(forge_key(file_path)).delete_blob()
