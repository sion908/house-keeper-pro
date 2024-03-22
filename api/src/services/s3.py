import boto3
from fastapi import UploadFile

from setting.variable import STAGE_NAME, s3


def upload_file(filekey: str,file: UploadFile):
    # ファイルキーの生成ロジック
    if file is None:
        return None
    # S3にファイルをアップロード
    bucket_name="upload" if STAGE_NAME=="local" else "house-keeper-pro"
    s3.put_object(Bucket=bucket_name, Key=filekey, Body=file)

    return filekey
