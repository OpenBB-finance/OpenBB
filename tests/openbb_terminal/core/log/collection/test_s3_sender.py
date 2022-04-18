import os
from pathlib import Path
import pytest
from openbb_terminal.core.log.constants import S3_FOLDER_SUFFIX
from openbb_terminal.core.log.generation.settings import (
    Settings,
    AppSettings,
    AWSSettings,
    LogSettings,
)
from openbb_terminal.core.log.constants import DEFAULT_API_URL
from openbb_terminal.core.log.collection import s3_sender as s3s

# pylint: disable=W0611

try:
    import boto3  # noqa:F401
except ImportError:
    WITH_BOTO3 = False
else:
    WITH_BOTO3 = True

app_settings = AppSettings(
    commit_hash="MOCK_COMMIT_HASH",
    name="MOCK_COMMIT_HASH",
    identifier="MOCK_COMMIT_HASH",
    session_id="MOCK_SESSION_ID",
)
aws_settings = AWSSettings(
    aws_access_key_id="MOCK_AWS_ACCESS_KEY_ID",
    aws_secret_access_key="MOCK_AWS",  # pragma: allowlist secret
)
settings = Settings(
    app_settings=app_settings,
    aws_settings=aws_settings,
    log_settings=LogSettings(
        directory=Path("."),
        frequency="H",
        handler_list="file",
        rolling_clock=False,
        verbosity=20,
    ),
)

identifier = app_settings.identifier
app_name = app_settings.name
object_key = f"{app_name}{S3_FOLDER_SUFFIX}/logs/{identifier}/file.log"


def test_send_to_s3_directly(mocker):
    if WITH_BOTO3:
        mocker.patch("openbb_terminal.core.log.collection.s3_sender.boto3")
        s3s.send_to_s3_directly("access", "secret", "bucket", Path("."), "key")
    else:
        with pytest.raises(ModuleNotFoundError):
            s3s.send_to_s3_directly("access", "secret", "bucket", Path("."), "key")


def test_send_to_s3_directly_invalid(mocker):
    mocker.patch("openbb_terminal.core.log.collection.s3_sender.WITH_BOTO3", False)
    with pytest.raises(ModuleNotFoundError):
        s3s.send_to_s3_directly("access", "secret", "bucket", Path("."), "key")


@pytest.mark.vcr
def test_fetch_presigned_url():
    s3s.fetch_presigned_url(DEFAULT_API_URL, object_key)


def test_send_to_s3_using_presigned_url(mocker):
    mocker.patch(
        "openbb_terminal.core.log.collection.s3_sender.fetch_presigned_url",
        return_value={"fields": [1, 2, 3], "url": "http://"},
    )
    mocker.patch("openbb_terminal.core.log.collection.s3_sender.requests")
    with open("readme.txt", "w") as f:
        f.write("Create a new text file!")

    s3s.send_to_s3_using_presigned_url(DEFAULT_API_URL, "readme.txt", object_key)
    os.remove("readme.txt")


@pytest.mark.parametrize("last", [True, False])
def test_send_to_s3(mocker, last):
    mocker.patch(
        "openbb_terminal.core.log.collection.s3_sender.fetch_presigned_url",
        return_value={"fields": [1, 2, 3], "url": "http://"},
    )
    mocker.patch("openbb_terminal.core.log.collection.s3_sender.requests")
    if WITH_BOTO3:
        mocker.patch("openbb_terminal.core.log.collection.s3_sender.boto3")
    with open("readme.txt", "w") as f:
        f.write("Create a new text file!")
    with open("dontreadme.txt", "w") as f:
        f.write("Create a new text file!")
    file = Path("readme.txt")
    file2 = Path("dontreadme.txt")

    if WITH_BOTO3:
        s3s.send_to_s3(file, aws_settings, file, object_key, file2, last)
    elif last is False:
        with pytest.raises(ModuleNotFoundError):
            s3s.send_to_s3(file, aws_settings, file, object_key, file2, last)
    if file.is_file():
        os.remove(file)
