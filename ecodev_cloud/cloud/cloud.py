"""
Module listing all cloud object storage sources
"""
from enum import Enum
from enum import unique

from pydantic_settings import BaseSettings


@unique
class Cloud(str, Enum):
    """
    All cloud object storage sources
    """
    AZURE = 'Azure'
    AWS = 'Aws'


class CloudConfiguration(BaseSettings):
    """
    Simple authentication configuration class
    """
    cloud_provider: Cloud = Cloud.AWS


AUTH = CloudConfiguration()
CLOUD = AUTH.cloud_provider
