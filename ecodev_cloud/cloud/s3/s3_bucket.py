"""
Module implementing the S3 connection logic
"""
from typing import Any

import boto3
from pydantic_settings import BaseSettings


class S3Configuration(BaseSettings):
    """
    S3 Configuration (filled thanks to the local .env):
    """
    s3_access_key_id: str = ''
    s3_secret_access_key: str = ''
    s3_region_name: str = ''
    s3_endpoint_url: str = ''
    s3_bucket_name: str = ''
    aws_use: bool = False


S3_CONF = S3Configuration()
S3_SESSION = boto3.session.Session()
S3_STR = 's3'
S3: Any | None = None
BUCKET = S3_CONF.s3_bucket_name
TEST_BUCKET = 'testbucket'


def s3() -> Any:
    """
    Singleton to retrieve the connection to the s3 resource.
    """
    global S3
    if not S3:
        S3 = S3_SESSION.resource(S3_STR) if S3_CONF.aws_use else S3_SESSION.resource(
            service_name=S3_STR,
            aws_access_key_id=S3_CONF.s3_access_key_id,
            aws_secret_access_key=S3_CONF.s3_secret_access_key,
            endpoint_url=S3_CONF.s3_endpoint_url,
            region_name=S3_CONF.s3_region_name,
            use_ssl=True,
            verify=True
        )

    return S3
