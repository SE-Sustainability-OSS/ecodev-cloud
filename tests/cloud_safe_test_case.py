"""
Unittest wrapper ensuring safe setUp / tearDown of all tests.
This boilerplate code is not to be touched under any circumstances.
"""
import contextlib

from ecodev_core import logger_get
from ecodev_core import SafeTestCase

from ecodev_cloud.cloud.blob.blob_container import container
from ecodev_cloud.cloud.blob.blob_container import create_container
from ecodev_cloud.cloud.blob.blob_container import TEST_CONTAINER
from ecodev_cloud.cloud.s3.s3_bucket import BUCKET
from ecodev_cloud.cloud.s3.s3_bucket import s3
from ecodev_cloud.cloud.s3.s3_bucket import TEST_BUCKET


log = logger_get(__name__)


def _create_test_bucket() -> None:
    """
    Create prod bucket in an idempotent way.
    """
    with contextlib.suppress(Exception):
        s3().meta.client.create_bucket(Bucket=BUCKET)


class CloudSafeTestCase(SafeTestCase):
    """
    SafeTestCase makes sure that setUp / tearDown methods are always run when they should be.
    This boilerplate code is not to be touched under any circumstances.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Class set up, prompt class name and set files and folders to be suppressed at tearDownClass
        """
        log.info(f'Running test module: {cls.__module__.upper()}')
        super().setUpClass()
        _create_test_bucket()
        create_container(TEST_CONTAINER)
        s3().meta.client.create_bucket(Bucket=TEST_BUCKET)

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Safely suppress all files and directories used for this class
        """
        super().tearDownClass()
        s3().Bucket(TEST_BUCKET).objects.all().delete()
        s3().meta.client.delete_bucket(Bucket=TEST_BUCKET)
        with contextlib.suppress(Exception):
            container(TEST_CONTAINER).delete_container()
