"""
Module regrouping all netcdf reading and writing methods
"""
from pathlib import Path

from netCDF4 import Dataset
from typing_extensions import TypeAlias


NETCDF_DATASET: TypeAlias = Dataset


def read_netcdf(file_path: Path) -> NETCDF_DATASET:
    """
    Read the netcdf content of the given filename
    """
    return NETCDF_DATASET(str(file_path))


def read_data_netcdf(data: bytes) -> NETCDF_DATASET:
    """
    Read the netcdf content of the given filename
    """
    return NETCDF_DATASET('memory', memory=data)
