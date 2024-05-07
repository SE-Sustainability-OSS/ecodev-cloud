from io import BytesIO
from pathlib import Path
from typing import Iterator

from botocore.errorfactory import ClientError
from botocore.response import StreamingBody

from ecodev_cloud.cloud.s3.s3_bucket import BUCKET
from ecodev_cloud.cloud.s3.s3_bucket import s3
from ecodev_cloud.file_processing.basic_file_processing import get_common_ancestor
from ecodev_cloud.path_utils import forge_key
from ecodev_cloud.path_utils import ROOT_DIRECTORY


PAGINATOR = s3().meta.client.get_paginator('list_objects_v2')


def s3_upload(source_path: Path, dest_path: Path, location: str = BUCKET) -> None:
    """
    Upload content of source_path to dest_path on s3 bucket
    """
    s3().meta.client.upload_file(str(source_path), location, forge_key(dest_path))


def get_s3_object(fp: Path,
                  byte: bool = True,
                  location: str = BUCKET
                  ) -> bytes | StreamingBody:
    """
    Retrieves byte content stored on a S3 at file_path key location
    """
    s3_object = s3().Object(bucket_name=location, key=forge_key(fp)).get()['Body'].read()
    return BytesIO(s3_object) if byte else s3_object


def s3_move_folder(origin: Path,
                   dest: Path,
                   dist_origin: bool = False,
                   delete_file: bool = True,
                   location: str = BUCKET) -> None:
    """
    Move all files in the origin folder (either present locally or already on the S3,
     depending on dist_origin) to either another local folder dest, or a s3 dest.

        Attributes are:
        - origin: folder to move
        - dest: where to move origin
        - dist_origin: whether the origin folder is already on the blob or on a local filesystem
        - delete_file: whether to delete or not the origin folder. If false, amount to cp and not mv
        - location: bucket name inside the s3 storage on which to move
    """
    for origin_path in s3_rglob(origin):
        s3_move_file(origin_path, dest / origin_path.relative_to(origin),
                     dist_origin=dist_origin, delete_file=delete_file, location=location)


def s3_copy_file(origin: Path,
                 dest: Path,
                 location: str = BUCKET,
                 dist_origin: bool = False) -> None:
    """
    Move an origin path (either present locally or already on the S3, depending on dist_origin)
     to either another local dest, or a s3 dest.

    Attributes are:
        - origin: folder to copy
        - dest: where to copy origin
        - location: bucket name inside the s3 storage on which to move
        - dist_origin: whether the origin folder is already on the blob or on a local filesystem
    """
    s3_move_file(origin, dest, location=location, dist_origin=dist_origin, delete_file=False)


def s3_move_file(origin: Path,
                 dest: Path,
                 location: str = BUCKET,
                 dist_origin: bool = False,
                 delete_file: bool = True) -> None:
    """
    Move an origin path (either present locally or already on the S3, depending on dist_origin)
     to either another local dest, or a s3 dest.

     Attributes are:
        - origin: file to move
        - dest: where to move origin
        - location: bucket name inside the s3 storage on which to move
        - dist_origin: whether the origin file is already on the blob or on a local filesystem
        - delete_file: whether to delete or not the origin file. If false, amount to cp and not mv
    """
    if dist_origin:
        source = {'Bucket': location, 'Key': forge_key(origin)}
        s3().meta.client.copy(source, location, forge_key(dest))
        if delete_file:
            delete_s3_content(origin, location)
    else:
        s3().meta.client.upload_file(str(origin), location, forge_key(dest))
        if delete_file:
            origin.unlink()


def get_s3_url(fp: Path, timeout: int = 3600, location: str = BUCKET) -> str | None:
    """
    Generate a pre-signed URL to share an S3 object (the one stored at file_path location).
    Expiration is the time in seconds for the pre-signed URL to remain valid.
    https://boto3.amazonaws.com/v1/documentation/api/latest/guide/s3-presigned-urls.html
    """
    try:
        return s3().meta.client.generate_presigned_url('get_object', Params={
            'Bucket': location, 'Key': forge_key(fp)}, ExpiresIn=timeout)
    except ClientError:
        return None


def s3_rglob(fp: Path, pattern: str | None = None, location: str = BUCKET) -> Iterator[Path]:
    """
    Rglob functionality: recursively find all S3 keys in the file_path S3 key
    """
    yield from _s3_keys(fp, location, pattern.replace('*', '') if pattern else None)


def s3_iterdir(file_path: Path, location: str = BUCKET) -> Iterator[Path]:
    """
    iterdir functionality: list all files and folders directly in the file_path folder.
     Does so either locally or on a S3
    """
    files = {file_path / get_common_ancestor(elt, file_path) for elt in
             _s3_keys(file_path, location) if elt != file_path}
    yield from sorted(list(files))


def s3_exists(file_path: Path, location: str = BUCKET) -> bool:
    """
    Check if a file_path exists, either locally or on a S3
    """
    try:
        s3().meta.client.head_object(Bucket=location, Key=forge_key(file_path))
        return True
    except ClientError:
        return False


def download_s3_object(file_path: Path, local_path: Path, location: str = BUCKET) -> None:
    """
    Download on disk at local_path location the content of bucket at file_path key location.
    """
    s3().Bucket(location).download_file(forge_key(file_path), local_path)


def delete_s3_content(file_path: Path, location: str = BUCKET) -> None:
    """
    Delete content from a S3 at file_path key location
    """
    s3().Object(bucket_name=location, key=forge_key(file_path)).delete()


def _s3_keys(file_path: Path, location: str, pattern: str | None = None) -> Iterator[Path]:
    """
    Retrieves all S3 keys starting with file_path having the passed pattern
    """
    for page in PAGINATOR.paginate(Bucket=location, Prefix=forge_key(file_path)):
        for content in page.get('Contents', ()):
            if not pattern or pattern in content['Key']:
                yield ROOT_DIRECTORY / content['Key']
