"""
Module regrouping all methods treating tif files
"""
from pathlib import Path
from uuid import uuid4

from osgeo import gdal
from typing_extensions import TypeAlias


GDAL_DATASET: TypeAlias = gdal.Dataset


def get_tif_tile(file_path: Path) -> GDAL_DATASET:
    """
    Read tif file from local disk storage and return a gdal Dataset
    """
    return gdal.Open(str(file_path))


def get_in_memory_tile(in_memory_data: bytes) -> GDAL_DATASET:
    """
    Form a gdal Dataset out of in memory byte information (presumably fetched from a s3)
    """
    filename = _in_memory_filename()
    gdal.FileFromMemBuffer(filename, in_memory_data)
    tile = gdal.Open(filename)
    gdal.Unlink(filename)
    return tile


def _in_memory_filename():
    """
    Generate a random filename tu put in gdal vsimem memory.
    """
    return f'/vsimem/{_get_new_uuid()}'


def _get_new_uuid() -> str:
    """
    Generate uuid4 strings
    """
    return str(uuid4())
