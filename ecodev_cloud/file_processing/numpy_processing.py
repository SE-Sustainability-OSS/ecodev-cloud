"""
Module regrouping all methods treating numpy files
"""
from pathlib import Path

import numpy as np
from typing_extensions import TypeAlias


NP_ARRAY: TypeAlias = np.ndarray
INDICATOR_STR = 'indicator'


def get_npz_data(data, indicator: str = INDICATOR_STR) -> NP_ARRAY:
    """
    Retrieves numpy data (that has been compressed) out of the passed BytesIO/str data
    """
    return get_numpy_data(data).get(indicator)


def get_numpy_data(data) -> NP_ARRAY | dict[str, NP_ARRAY]:
    """
    Retrieves numpy data out of the passed BytesIO/str data
    """
    return np.load(str(data) if isinstance(data, Path) else data)


def save_numpy_data(file_path: Path, data: NP_ARRAY):
    """
    Save passed numpy array data into file_path
    """
    return np.save(str(file_path), data)


def save_numpy_compressed_data(file_path: Path, data: NP_ARRAY):
    """
    Save passed numpy array data into file_path at compressed format
    """
    np.savez_compressed(str(file_path), indicator=data)
