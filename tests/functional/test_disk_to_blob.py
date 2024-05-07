"""
Module testing End-to-end disk to azure blob storage migration.
"""
from io import BytesIO
from pathlib import Path

import pandas as pd
from ecodev_core import logger_get

from ecodev_cloud.cloud.blob.blob_container import container
from ecodev_cloud.cloud.blob.blob_container import TEST_CONTAINER
from ecodev_cloud.cloud.s3.s3_bucket import TEST_BUCKET
from ecodev_cloud.constants import CSV_EXT
from ecodev_cloud.disk.disk_loader import disk_load
from ecodev_cloud.path_utils import ROOT_DIRECTORY
from ecodev_cloud.transfer.disk_to_blob import transfer_disk_to_blob
from ecodev_cloud.transfer.migration_helpers import _load_index
from ecodev_cloud.transfer.migration_helpers import FAILED_IDX
from tests.cloud_safe_test_case import CloudSafeTestCase


log = logger_get(__name__)
ROOT_TEST = ROOT_DIRECTORY / 'tests/functional/mapping/root'
EXPECTED_DIR = ROOT_DIRECTORY / 'tests/functional/mapping/expected'


class DiskToAzureTest(CloudSafeTestCase):
    """
    Class testing End-to-end disk to azure blob storage migration.
    """

    def setUp(self) -> None:
        """
        Initialize all needed variables for the end-to-end test. Erase produced data at end test
        """

        self.client = EXPECTED_DIR
        self.ext = ROOT_TEST / 'tmp'
        self.directories_created.append(self.ext)

    def test_migrate_folder_from_disk_to_azure(self):
        """
        End-to-end test of disk to azure blob storage migration.
        """
        transfer_disk_to_blob([self.client], self.ext, TEST_BUCKET)
        for file_path in [Path(x['name']) for x in container(TEST_CONTAINER).list_blobs()]:
            if file_path.suffix == CSV_EXT:
                log.info(f'checking {file_path}')
                expected = disk_load(ROOT_DIRECTORY / file_path)
                data = container(TEST_CONTAINER).get_blob_client(str(file_path))
                pred = pd.read_csv(BytesIO(data.download_blob().readall()))
                self.assertTrue(pd.testing.assert_frame_equal(expected, pred) is None)
        self.assertTrue(len(_load_index(FAILED_IDX, self.ext)) == 0)
