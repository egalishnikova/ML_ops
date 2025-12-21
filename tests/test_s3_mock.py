import boto3
import pytest
from moto import mock_aws

from app.s3_utils import download_bytes, upload_bytes


@pytest.fixture()
def s3_client():
    # mock_aws покрывает s3 (универсально для moto)
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket="test-bucket")
        yield client


def test_s3_upload_and_download_bytes(s3_client):
    upload_bytes(s3_client, "test-bucket", "folder/file.txt", b"hello")
    data = download_bytes(s3_client, "test-bucket", "folder/file.txt")
    assert data == b"hello"
