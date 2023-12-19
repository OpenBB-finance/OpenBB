# IMPORTATION STANDARD
from pathlib import Path

# IMPORTATION THIRDPARTY
import pytest

from openbb_terminal.core.log.collection import s3_sender
from openbb_terminal.core.log.constants import DEFAULT_API_URL

# IMPORTATION INTERNAL
from openbb_terminal.core.log.generation.settings import AWSSettings

# pylint: disable=W0611


@pytest.mark.vcr(record_mode="none")
def test_send_to_s3_directly(mocker):
    s3_sender.boto3 = mocker.Mock()
    mocker.patch.object(
        target=s3_sender,
        attribute="WITH_BOTO3",
        new=True,
    )

    aws_access_key_id = "MOCK_ACCESS_KEY_ID"
    aws_secret_access_key = "MOCK_ACCESS_SECRET_KEY"  # noqa: S105
    bucket = "MOCK_BUCKET"
    file = Path(__file__)
    object_key = "MOCK_S3/OBJECT_KEY"

    s3_sender.send_to_s3_directly(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        bucket=bucket,
        file=file,
        object_key=object_key,
    )


@pytest.mark.vcr(record_mode="none")
def test_send_to_s3_directly_exception(mocker):
    s3_sender.boto3 = mocker.Mock()
    mocker.patch.object(
        target=s3_sender,
        attribute="WITH_BOTO3",
        new=False,
    )

    aws_access_key_id = "MOCK_ACCESS_KEY_ID"
    aws_secret_access_key = "MOCK_ACCESS_SECRET_KEY"  # noqa: S105
    bucket = "MOCK_BUCKET"
    file = Path(__file__)
    object_key = "MOCK_S3/OBJECT_KEY"

    with pytest.raises(ModuleNotFoundError):
        s3_sender.send_to_s3_directly(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            bucket=bucket,
            file=file,
            object_key=object_key,
        )


@pytest.mark.vcr
def test_fetch_presigned_url():
    object_key = "gst-app/logs/MOCK_OBJECT_KEY"
    s3_sender.fetch_presigned_url(api_url=DEFAULT_API_URL, object_key=object_key)


@pytest.mark.vcr(record_mode="none")
def test_send_to_s3_using_presigned_url(mocker, tmp_path):
    mocker.patch(
        "openbb_terminal.core.log.collection.s3_sender.fetch_presigned_url",
        return_value={"fields": [1, 2, 3], "url": "http://"},
    )
    mocker.patch("openbb_terminal.core.log.collection.s3_sender.requests")

    api_url = DEFAULT_API_URL
    file = tmp_path.joinpath("mock_log_file")
    object_key = "MOCK_S3/OBJECT_KEY"

    with open(file, "w", encoding="utf-8", newline="\n") as f:
        f.write("Mocking a log file to send to s3.")

    s3_sender.send_to_s3_using_presigned_url(
        api_url=api_url,
        file=file,
        object_key=object_key,
    )


@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "aws_settings, last",
    [
        (
            AWSSettings(
                aws_access_key_id="MOCK_AWS_ACCESS_KEY_ID",
                aws_secret_access_key="MOCK_AWS_ACCESS_KEY",  # noqa: S106
            ),
            False,
        ),
        (
            AWSSettings(
                aws_access_key_id="REPLACE_ME",
                aws_secret_access_key="REPLACE_ME",  # noqa: S106
            ),
            True,
        ),
    ],
)
def test_send_to_s3(aws_settings, mocker, last, tmp_path):
    mocker.patch("openbb_terminal.core.log.collection.s3_sender.send_to_s3_directly")
    mocker.patch(
        "openbb_terminal.core.log.collection.s3_sender.send_to_s3_using_presigned_url"
    )

    archives_file = tmp_path.joinpath("archives").joinpath("mock_log_file")
    tmp_file = tmp_path.joinpath("tmp").joinpath("mock_log_file")
    file = tmp_path.joinpath("mock_log_file")
    object_key = "MOCK_S3/OBJECT_KEY"

    with open(file, "w", encoding="utf-8", newline="\n") as f:
        f.write("Mocking a log file to send to s3.")

    assert file.exists()
    assert not archives_file.exists()
    assert not tmp_file.exists()

    s3_sender.send_to_s3(
        archives_file=archives_file,
        aws_settings=aws_settings,
        file=file,
        object_key=object_key,
        tmp_file=tmp_file,
        last=last,
    )

    assert last or not file.exists()
    assert archives_file.exists()
    assert not tmp_file.exists()


@pytest.mark.vcr(record_mode="none")
def test_send_to_s3_exception(mocker, tmp_path):
    mocker.patch("openbb_terminal.core.log.collection.s3_sender.send_to_s3_directly")
    mocker.patch(
        "openbb_terminal.core.log.collection.s3_sender.send_to_s3_using_presigned_url"
    )

    archives_file = tmp_path.joinpath("archives").joinpath("mock_log_file")
    tmp_file = tmp_path.joinpath("tmp").joinpath("mock_log_file")
    file = tmp_path.joinpath("mock_log_file")
    file.touch()
    object_key = "MOCK_S3/OBJECT_KEY"

    with pytest.raises(AttributeError):
        s3_sender.send_to_s3(
            archives_file=archives_file,
            aws_settings=AWSSettings(
                aws_access_key_id="REPLACE_ME",
                aws_secret_access_key="REPLACE_ME",  # noqa: S106
            ),
            file=file,
            object_key=object_key,
            tmp_file=tmp_file,
            last=False,
        )
