"""
Module testing that all loading and saving method are working properly
"""
import itertools
from pathlib import Path
from typing import Any
from typing import Callable

import numpy as np
from ecodev_core import logger_get
from parameterized import parameterized

from ecodev_cloud import Cloud
from ecodev_cloud import cloud_copy_file
from ecodev_cloud import disk_save
from ecodev_cloud.cloud.blob.blob_container import TEST_CONTAINER
from ecodev_cloud.cloud.cloud_loaders import load_cloud_data
from ecodev_cloud.cloud.cloud_savers import save_cloud_data
from ecodev_cloud.cloud.s3.s3_bucket import TEST_BUCKET
from ecodev_cloud.constants import SHP_EXT
from ecodev_cloud.constants import ZIP_EXT
from ecodev_cloud.disk.disk_loader import disk_load
from ecodev_cloud.file_processing.shapely_processing import load_points
from ecodev_cloud.path_utils import ROOT_DIRECTORY
from tests.cloud_safe_test_case import CloudSafeTestCase

DATA_DIRECTORY = ROOT_DIRECTORY / 'tests/unitary/data'
BRITISH = 'UKofGreatBritainandNorthernIreland'
CLOUDS: dict[Cloud, str] = {
    Cloud.AWS: TEST_BUCKET,
    Cloud.AZURE: TEST_CONTAINER
}
SKOPS_FILE = DATA_DIRECTORY / 'example.skops'
log = logger_get(__name__)


def _equal(x, y): return x == y


def _np_equal(x, y): return np.allclose(x, y)


def _xlsx_equal(x, y): return all(x.parse(elt).equals(y.parse(elt))
                                  for elt in ['bla', 'bli'])


def _csv_equal(x, y): return x.equals(y)


def _gdal_equal(x, y): return all(x.ReadAsArray(j, i, 1, 1)[0, 0] == y.ReadAsArray(j, i, 1, 1)[0, 0]
                                  for j, i in itertools.product(
    range(0, 1440, 10), range(0, 720, 10)))


def _point_equal(x, y): return load_points(x) == load_points(y)


def _nc_equal(x, y): return np.allclose(x['tas'][:], y['tas'][:])


def file_provider() -> list[list]:
    """
    Provide config for tests
    """
    return [['example.npy.npz', _np_equal, True],
            ['example.tif', _gdal_equal, False],
            ['example.json', _equal, True],
            ['example.csv', _csv_equal, True],
            ['example.gpkg', _equal, False],
            ['example.shp', _equal, False],
            ['example_points.shp', _point_equal, False],
            ['example.txt', _equal, True],
            ['example.npy', _np_equal, True],
            ['example.tex', _equal, True],
            ['example.xlsx', _xlsx_equal, False],
            ['example.nc', _nc_equal, False]]


class LoadSaveTest(CloudSafeTestCase):
    """
    Class testing that all loading and saving method are working properly
    """

    @parameterized.expand(file_provider)
    def test_s3_save(self, filename: str, equality: Callable, should_save: bool):
        """
        Test s3 load save
        """
        self._load_save_helper(Cloud.AWS, filename, equality, should_save)

    @parameterized.expand(file_provider)
    def test_blob_save(self, filename: str, equality: Callable, should_save: bool):
        """
        Test blob load save
        """
        self._load_save_helper(Cloud.AZURE, filename, equality, should_save)

    def test_erroneous_s3_load_save(self):
        """
        Test erroneous s3 load save
        """
        return self._erroneous_load_save_helper(Cloud.AWS)

    def test_erroneous_blob_load_save(self):
        """
        Test erroneous blob load save
        """
        self._erroneous_load_save_helper(Cloud.AZURE)

    def _erroneous_load_save_helper(self, cloud: Cloud):
        """
        erroneous load save helper
        """
        with self.assertRaises(AttributeError):
            load_cloud_data(SKOPS_FILE, cloud=cloud)
        with self.assertRaises(AttributeError):
            disk_load(SKOPS_FILE)
        with self.assertRaises(AttributeError):
            save_cloud_data(SKOPS_FILE, data={}, cloud=cloud)
        with self.assertRaises(AttributeError):
            disk_save(SKOPS_FILE, data={})

    def _load_save_helper(self, cloud: Cloud, filename: str, equality: Callable, should_save: bool):
        """
        Generic load save test
        """
        log.info(f'testing for {CLOUDS[cloud]}')
        local_data = disk_load(DATA_DIRECTORY / filename)
        _save_file(cloud, local_data, DATA_DIRECTORY / filename, should_save)
        cloud_data = load_cloud_data(DATA_DIRECTORY / filename, location=CLOUDS[cloud], cloud=cloud)
        self.assertTrue(equality(cloud_data, local_data))


def _save_file(cloud: Cloud, local_data: Any, file_path: Path, should_save: bool) -> None:
    """
    Save test file (if no save method is implemented for this type of file, just copy it).
    """
    if should_save:
        save_cloud_data(file_path, local_data, location=CLOUDS[cloud], cloud=cloud)
        return

    store_path = file_path.with_suffix(ZIP_EXT) if file_path.suffix == SHP_EXT else file_path
    cloud_copy_file(store_path, store_path, location=CLOUDS[cloud], cloud=cloud)
