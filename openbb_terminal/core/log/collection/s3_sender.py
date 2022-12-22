# IMPORTATION STANDARD
from pathlib import Path
from shutil import copyfile
from typing import Any, Dict

# IMPORTATION THIRDPARTY
import requests

try:
    import boto3
except ImportError:
    WITH_BOTO3 = False
else:
    WITH_BOTO3 = True

# IMPORTATION INTERNAL
from openbb_terminal.core.log.constants import DEFAULT_API_URL, DEFAULT_BUCKET
from openbb_terminal.core.log.generation.settings import AWSSettings

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
    raw_response = requests.put(
        json={"object_key": object_key},
        timeout=3,
        url=api_url,
    )
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
            data=presigned_info["fields"],
            files=files,  # type: ignore
            timeout=3,
            url=presigned_info["url"],
        )

    raw_response.raise_for_status()

    # SUCCESS IF STATUS_CODE == 204


def send_to_s3(
    archives_file: Path,
    aws_settings: AWSSettings,
    file: Path,
    object_key: str,
    tmp_file: Path,
    last: bool = False,
):
    """Send a file into a s3 bucket.

    Args:
        archives_file (Path):
            Destination Path after processing.
        aws_settings (AWSSettings):
            AWS settings.
        file (Path):
            Path of the file to process.
        object_key (str): _description_
            File location inside the s3 bucket.
        tmp_file (Path):
            Temporary Path in which to put the file during processing.
        last (bool, optional):
            Whether or not this is the last sending before program exit.
            Defaults to False.

    Raises:
        AttributeError:
            If `file` is empty.
    """

    api_url = DEFAULT_API_URL
    bucket = DEFAULT_BUCKET

    if file.stat().st_size <= 0:
        file.unlink(missing_ok=True)
        raise AttributeError(f"File is empty : {file}")

    tmp_file.parent.mkdir(exist_ok=True)

    if last:
        copyfile(file, tmp_file)
    else:
        file.rename(tmp_file)

    if (
        not last
        and aws_settings.aws_access_key_id != "REPLACE_ME"
        and aws_settings.aws_secret_access_key != "REPLACE_ME"
    ):
        send_to_s3_directly(
            aws_access_key_id=aws_settings.aws_access_key_id,
            aws_secret_access_key=aws_settings.aws_secret_access_key,
            bucket=bucket,
            file=tmp_file,
            object_key=object_key,
        )
    else:
        send_to_s3_using_presigned_url(
            api_url=api_url,
            file=tmp_file,
            object_key=object_key,
        )

    archives_file.parent.mkdir(exist_ok=True)
    tmp_file.rename(archives_file)
