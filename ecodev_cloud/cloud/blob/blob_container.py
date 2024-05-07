"""
Module implementing the Azure blob connection logic
"""
from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from azure.storage.blob import ContainerClient
from ecodev_core import logger_get
from pydantic_settings import BaseSettings

log = logger_get(__name__)


class BlobConfiguration(BaseSettings):
    """
    Azure Blob Configuration (filled thanks to the local .env):
    """
    connection_string: str = ''
    container: str = ''


AZURE_SERVICE: BlobServiceClient | None = None
AZURE_BLOB: ContainerClient | None = None
BLOB_CONF = BlobConfiguration()
CONTAINER = BLOB_CONF.container
TEST_CONTAINER = 'testblob'


def container(name: str = CONTAINER) -> ContainerClient:
    """
    Singleton to retrieve the connection to the azure blob storage container.
    """
    global AZURE_BLOB
    if not AZURE_BLOB:
        AZURE_BLOB = _azure_service().get_container_client(name)
        _create_container(AZURE_BLOB, name)
    return AZURE_BLOB


def create_container(name: str = CONTAINER):
    """
    Safe container creation (creating the blob storage if not there)
    """
    global AZURE_BLOB
    if not AZURE_BLOB:
        container(name)
    else:
        _create_container(AZURE_BLOB, name)


def _create_container(blob: ContainerClient, name: str) -> None:
    """
    Safe container creation in passed blob storage
    """
    try:
        blob.create_container()
        log.info(f'creating azure {name} container')
    except ResourceExistsError:
        log.info(f'container {name} already exists')


def _azure_service() -> BlobServiceClient:
    """
    Singleton to retrieve the connection to the azure blob storage service.
    """
    global AZURE_SERVICE
    if not AZURE_SERVICE:
        AZURE_SERVICE = BlobServiceClient.from_connection_string(BLOB_CONF.connection_string)
    return AZURE_SERVICE
