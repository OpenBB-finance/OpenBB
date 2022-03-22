# IMPORTATION STANDARD
# import logging
from pathlib import Path
from typing import Any, Dict

# IMPORTATION THIRDPARTY
import requests

try:
    import boto3
except ImportError:
    WITH_BOTO3 = True
finally:
    WITH_BOTO3 = False

# IMPORTATION INTERNAL
from gamestonk_terminal import config_terminal as cfg

# DO NOT USE THE FILE LOGGER IN THIS MODULE

DEFAULT_BUCKET = "gst-restrictions"
DEFAULT_FOLDER_PATH = f"{cfg.LOGGING_APP_NAME}-app/logs"
DEFAULT_API_URL = "https://knaqi3sud7.execute-api.eu-west-3.amazonaws.com/log_api/logs"


def send_to_s3_directly(
    aws_access_key: str,
    aws_access_key_id: str,
    bucket: str,
    file: Path,
    object_key: str,
):
    if not WITH_BOTO3:
        raise ModuleNotFoundError("Library `boto3` is required to directly access S3.")

    s3_client = boto3.client(
        service_name="s3",
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_access_key_id,
    )
    s3_client.upload_file(str(file), bucket, object_key)


def fetch_presigned_url(api_url: str, object_key: str) -> Dict[str, Any]:
    raw_response = requests.put(url=api_url, json={"object_key": object_key})
    raw_response.raise_for_status()

    response = raw_response.json()

    return response


def send_to_s3_using_presigned_url(
    api_url: str,
    file: Path,
    object_key: str,
):
    presigned_info = fetch_presigned_url(api_url=api_url, object_key=object_key)

    with open(file, "rb") as f:
        files = {"file": f}

        raw_response = requests.post(
            presigned_info["url"],
            data=presigned_info["fields"],
            files=files,
        )

    raw_response.raise_for_status()

    if raw_response.status_code == 204:
        pass


def send_to_s3(file: Path, tmp_dir: Path, archives_dir: Path):
    api_url = DEFAULT_API_URL
    aws_access_key = cfg.AWS_ACCESS_KEY
    aws_access_key_id = cfg.AWS_ACCESS_KEY_ID
    bucket = DEFAULT_BUCKET
    object_key = f"{DEFAULT_FOLDER_PATH}/{file.stem}"

    if not file.stat().st_size > 0:
        raise AttributeError(f"File is empty : {file}")

    file = file.rename(tmp_dir / file.name)

    if aws_access_key != "REPLACE_ME" and aws_access_key_id != "REPLACE_ME":
        send_to_s3_directly(
            aws_access_key=aws_access_key_id,
            aws_access_key_id=aws_access_key_id,
            bucket=bucket,
            file=file,
            object_key=object_key,
        )
    else:
        send_to_s3_using_presigned_url(
            api_url=api_url,
            file=file,
            object_key=object_key,
        )

    file.rename(archives_dir / file.name)
