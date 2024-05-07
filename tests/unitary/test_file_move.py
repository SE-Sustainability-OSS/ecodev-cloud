"""
Module testing that file moving methods are working properly
"""
from parameterized import parameterized

from ecodev_cloud.cloud.blob.blob_container import TEST_CONTAINER
from ecodev_cloud.cloud.blob.blob_helpers import blob_copy_file
from ecodev_cloud.cloud.blob.blob_helpers import blob_exists
from ecodev_cloud.cloud.blob.blob_helpers import blob_move_file
from ecodev_cloud.cloud.cloud_loaders import load_blob_data
from ecodev_cloud.cloud.cloud_loaders import load_s3_data
from ecodev_cloud.cloud.cloud_savers import save_blob_data
from ecodev_cloud.cloud.cloud_savers import save_s3_data
from ecodev_cloud.cloud.s3.s3_bucket import TEST_BUCKET
from ecodev_cloud.cloud.s3.s3_helpers import s3_copy_file
from ecodev_cloud.cloud.s3.s3_helpers import s3_exists
from ecodev_cloud.cloud.s3.s3_helpers import s3_move_file
from ecodev_cloud.disk.disk_helpers import disk_exists
from ecodev_cloud.disk.disk_loader import disk_load
from ecodev_cloud.path_utils import ROOT_DIRECTORY
from tests.cloud_safe_test_case import CloudSafeTestCase


DATA_DIR = ROOT_DIRECTORY / 'tests/unitary/data'


def method_provider() -> list[list]:
    """
    Provide config for tests
    """
    return [[save_s3_data, load_s3_data, s3_move_file, s3_copy_file, s3_exists, TEST_BUCKET],
            [save_blob_data, load_blob_data, blob_move_file, blob_copy_file, blob_exists,
             TEST_CONTAINER]]


class MoveFileTest(CloudSafeTestCase):
    """
    Class testing that file moving methods are working properly
    """

    @parameterized.expand(method_provider)
    def test_move_file(self, save, load, move, copy, exist, location):
        """
        Test that file moving methods are working properly
        """
        self.assertTrue(disk_exists(DATA_DIR / 'example.tex'))
        self.assertFalse(exist(DATA_DIR / 'example.tex', location=location))

        local_data = disk_load(DATA_DIR / 'example.tex')
        save(DATA_DIR / 'example.tex', local_data, location=location)
        self.assertTrue(exist(DATA_DIR / 'example.tex', location=location))

        move(DATA_DIR/'example.tex', DATA_DIR/'report2.tex', dist_origin=True, location=location)
        self.assertFalse(exist(DATA_DIR / 'example.tex', location=location))
        self.assertTrue(exist(DATA_DIR / 'report2.tex', location=location))

        copy(DATA_DIR/'report2.tex', DATA_DIR/'example.tex', dist_origin=True, location=location)
        self.assertTrue(exist(DATA_DIR / 'example.tex', location=location))
        self.assertTrue(exist(DATA_DIR / 'report2.tex', location=location))

        cloud_data = load(DATA_DIR / 'example.tex', location=location)
        cloud_data_2 = load(DATA_DIR / 'report2.tex', location=location)
        self.assertTrue(cloud_data == local_data)
        self.assertTrue(cloud_data_2 == local_data)
