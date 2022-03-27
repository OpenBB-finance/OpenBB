# IMPORTATION STANDARD
from pathlib import Path
from typing import Any, Dict

# IMPORTATION THIRDPARTY
import requests

try:
    import boto3
except ImportError:
    WITH_BOTO3 = False
finally:
    WITH_BOTO3 = True

# IMPORTATION INTERNAL
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal.log.constants import DEFAULT_API_URL, DEFAULT_BUCKET

# DO NOT USE THE FILE LOGGER IN THIS MODULE


def send_to_s3_directly(
    aws_access_key_id: str,
    aws_secret_access_key: str,
    bucket: str,
    file: Path,
    object_key: str,
):
    if not WITH_BOTO3:
        raise ModuleNotFoundError("Library `boto3` is required to directly access S3.")

    s3_client = boto3.client(
        service_name="s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
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


def send_to_s3(archives_file: Path, file: Path, object_key: str, tmp_file: Path):
    api_url = DEFAULT_API_URL
    aws_access_key_id = cfg.AWS_ACCESS_KEY_ID
    aws_secret_access_key = cfg.AWS_SECRET_ACCESS_KEY
    bucket = DEFAULT_BUCKET

    if file.stat().st_size <= 0:
        file.unlink(missing_ok=True)
        raise AttributeError(f"File is empty : {file}")

    tmp_file.parent.mkdir(exist_ok=True)
    file = file.rename(tmp_file)

    if aws_access_key_id != "REPLACE_ME" and aws_secret_access_key != "REPLACE_ME":
        send_to_s3_directly(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
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

    archives_file.parent.mkdir(exist_ok=True)
    file.rename(archives_file)
