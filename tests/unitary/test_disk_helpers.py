"""
Module testing disk helper methods
"""
import tempfile
from pathlib import Path

from ecodev_cloud import disk_copy
from ecodev_cloud import disk_is_dir
from ecodev_cloud import disk_iterdir
from ecodev_cloud import disk_move
from ecodev_cloud.path_utils import ROOT_DIRECTORY
from tests.cloud_safe_test_case import CloudSafeTestCase


DATA_DIRECTORY = ROOT_DIRECTORY / 'tests/unitary/data'


class DiskHelpersTest(CloudSafeTestCase):
    """
    Class testing disk helper methods
    """

    def test_disk_helpers(self):
        """
        test disk helper methods
        """
        self.assertTrue((disk_is_dir(DATA_DIRECTORY)))
        self.assertEqual(len(list(disk_iterdir(DATA_DIRECTORY))), 20)
        with tempfile.TemporaryDirectory() as folder_name:
            disk_copy(DATA_DIRECTORY / 'example.csv', Path(folder_name) / 'example.csv')
            self.assertEqual(len(list(disk_iterdir(Path(folder_name)))), 1)
            disk_move(Path(folder_name) / 'example.csv', Path(folder_name) / 'toto.csv')
            self.assertEqual(len(list(disk_iterdir(Path(folder_name)))), 1)
            disk_copy(Path(folder_name) / 'toto.csv', Path(folder_name) / 'example.csv')
            self.assertEqual(len(list(disk_iterdir(Path(folder_name)))), 2)
