# IMPORTATION STANDARD
import os
import uuid
from pathlib import Path

# IMPORTATION THIRDPARTY


# IMPORTATION INTERNAL


def get_log_dir() -> Path:
    """Retrieve application's log directory."""

    file_path = Path(__file__)
    log_dir = file_path.parent.parent.parent.parent.absolute().joinpath("logs")

    if not os.path.isdir(log_dir.absolute()):
        os.mkdir(log_dir.absolute())

    log_id = log_dir.absolute().joinpath(".logid")

    if not os.path.isfile(log_id.absolute()):
        logging_id = f"{uuid.uuid4()}"
        with open(log_id.absolute(), "a") as a_file:
            a_file.write(f"{logging_id}\n")
    else:
        with open(log_id.absolute()) as a_file:
            logging_id = a_file.readline().rstrip()

    uuid_log_dir = log_dir.absolute().joinpath(logging_id)

    if not os.path.isdir(uuid_log_dir.absolute()):
        os.mkdir(uuid_log_dir.absolute())

    # print(uuid_log_dir)

    return uuid_log_dir


def get_log_sub_dir(name: str):
    log_dir = get_log_dir()

    sub_dir = log_dir / name

    return sub_dir
