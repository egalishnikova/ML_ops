from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import boto3


@dataclass(frozen=True)
class S3Config:
    endpoint_url: Optional[str]
    access_key: str
    secret_key: str
    region_name: str = "us-east-1"


def make_s3_client(cfg: S3Config):
    # endpoint_url может быть None (например для AWS), для MinIO будет http://minio:9000
    return boto3.client(
        "s3",
        endpoint_url=cfg.endpoint_url,
        aws_access_key_id=cfg.access_key,
        aws_secret_access_key=cfg.secret_key,
        region_name=cfg.region_name,
    )


def ensure_bucket(client, bucket: str) -> None:
    # Для тестов и MinIO обычно достаточно простого create_bucket
    client.create_bucket(Bucket=bucket)


def upload_bytes(client, bucket: str, key: str, data: bytes) -> None:
    client.put_object(Bucket=bucket, Key=key, Body=data)


def download_bytes(client, bucket: str, key: str) -> bytes:
    resp = client.get_object(Bucket=bucket, Key=key)
    return resp["Body"].read()
