import boto3
from boto3.session import Session as s3_session
from fastapi import UploadFile

from setting import is_local


class S3():

    def __init__(self):
        s3_attrs = {
            "endpoint_url": "http://minio:9000",
            "aws_access_key_id": "minio",
            "aws_secret_access_key": "minio123"
        } if is_local else {}

        self.s3: s3_session = boto3.client(
            "s3",
            **s3_attrs
        )

    def upload_file(self, filekey: str, file: UploadFile):
        # ファイルキーの生成ロジック
        if file is None:
            return None
        # S3にファイルをアップロード
        bucket_name="upload" if is_local else "house-keeper-pro"
        self.s3.put_object(Bucket=bucket_name, Key=filekey, Body=file)

        return filekey
