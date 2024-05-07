"""
Module testing cloud helper methods
"""
from io import BytesIO

import pandas as pd
import requests
from azure.storage.blob import BlobClient

from ecodev_cloud.cloud.blob.blob_container import TEST_CONTAINER
from ecodev_cloud.cloud.blob.blob_helpers import blob_copy_file
from ecodev_cloud.cloud.blob.blob_helpers import blob_exists
from ecodev_cloud.cloud.blob.blob_helpers import blob_iterdir
from ecodev_cloud.cloud.blob.blob_helpers import blob_rglob
from ecodev_cloud.cloud.blob.blob_helpers import get_blob_url
from ecodev_cloud.cloud.cloud_helpers import cloud_is_dir
from ecodev_cloud.cloud.cloud_loaders import load_blob_data
from ecodev_cloud.cloud.cloud_loaders import load_s3_data
from ecodev_cloud.cloud.s3.s3_bucket import TEST_BUCKET
from ecodev_cloud.cloud.s3.s3_helpers import get_s3_url
from ecodev_cloud.cloud.s3.s3_helpers import s3_copy_file
from ecodev_cloud.cloud.s3.s3_helpers import s3_exists
from ecodev_cloud.cloud.s3.s3_helpers import s3_iterdir
from ecodev_cloud.cloud.s3.s3_helpers import s3_rglob
from ecodev_cloud.path_utils import ROOT_DIRECTORY
from tests.cloud_safe_test_case import CloudSafeTestCase


DATA_DIRECTORY = ROOT_DIRECTORY / 'tests/unitary/data'
LOCAL_PATH_1 = DATA_DIRECTORY / 'example.csv'
LOCAL_PATH_2 = DATA_DIRECTORY / 'example.json'


class CloudHelpersTest(CloudSafeTestCase):
    """
    Class testing blob helper methods
    """

    def test_blob_helpers(self):
        """
        Test blob helper methods.

        Tests that:
        - copy on blob works as expected
        - blob_iterdir works as expected
        - cloud_is_dir is able to identify files/folders
        - get_blob_url can produce a tmp url from which the data can be downloaded
        """
        blob_copy_file(LOCAL_PATH_1, LOCAL_PATH_1, location=TEST_CONTAINER)
        blob_copy_file(LOCAL_PATH_2, LOCAL_PATH_2 / LOCAL_PATH_2.name, location=TEST_CONTAINER)
        self.assertTrue(len(list(blob_rglob(DATA_DIRECTORY, location=TEST_CONTAINER))), 1)
        iterdir_1 = list(blob_iterdir(DATA_DIRECTORY.parent, location=TEST_CONTAINER))
        self.assertTrue(len(iterdir_1), 1)
        self.assertTrue(cloud_is_dir(iterdir_1[0]))
        iterdir_2 = list(blob_iterdir(DATA_DIRECTORY, location=TEST_CONTAINER))
        self.assertTrue(len(iterdir_2), 1)
        self.assertFalse(cloud_is_dir(iterdir_2[0]))
        self.assertTrue(cloud_is_dir(DATA_DIRECTORY))
        self.assertFalse(cloud_is_dir(LOCAL_PATH_1))
        self.assertTrue(blob_exists(LOCAL_PATH_1))
        blob_url = get_blob_url(LOCAL_PATH_1, location=TEST_CONTAINER)
        gt_df = load_blob_data(LOCAL_PATH_1, location=TEST_CONTAINER)
        prod_sas = BlobClient.from_blob_url(blob_url=blob_url)
        sas_df = pd.read_csv(BytesIO(prod_sas.download_blob().readall()))
        self.assertTrue(gt_df.equals(sas_df))

    def test_s3_helpers(self):
        """
        Test s3 helper methods

          Tests that:
        - copy on s3 works as expected
        - s3_iterdir works as expected
        - cloud_is_dir is able to identify files/folders
        - get_s3_url can produce a tmp url from which the data can be downloaded
        """
        s3_copy_file(LOCAL_PATH_1, LOCAL_PATH_1, location=TEST_BUCKET)
        s3_copy_file(LOCAL_PATH_2, LOCAL_PATH_2 / LOCAL_PATH_2.name, location=TEST_BUCKET)
        self.assertTrue(len(list(s3_rglob(DATA_DIRECTORY, location=TEST_BUCKET))), 1)
        iterdir_1 = list(s3_iterdir(DATA_DIRECTORY.parent, location=TEST_BUCKET))
        self.assertTrue(len(iterdir_1), 1)
        self.assertTrue(cloud_is_dir(iterdir_1[0]))
        iterdir_2 = list(s3_iterdir(DATA_DIRECTORY, location=TEST_BUCKET))
        self.assertTrue(len(iterdir_2), 1)
        self.assertFalse(cloud_is_dir(iterdir_2[0]))
        self.assertTrue(cloud_is_dir(DATA_DIRECTORY))
        self.assertFalse(cloud_is_dir(LOCAL_PATH_1))
        self.assertTrue(s3_exists(LOCAL_PATH_1, location=TEST_BUCKET))
        s3_url = get_s3_url(LOCAL_PATH_2 / LOCAL_PATH_2.name, location=TEST_BUCKET)
        gt_json = load_s3_data(LOCAL_PATH_2 / LOCAL_PATH_2.name, location=TEST_BUCKET)
        prod_sas = requests.get(s3_url).json()
        self.assertCountEqual(gt_json, prod_sas)
