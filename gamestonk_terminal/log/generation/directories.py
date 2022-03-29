# IMPORTATION STANDARD
import uuid
from pathlib import Path

# IMPORTATION THIRDPARTY


# IMPORTATION INTERNAL


def get_log_dir() -> Path:
    """Retrieve application's log directory."""

    log_dir = Path(__file__).parent.parent.parent.parent.joinpath("logs")
    log_dir.mkdir(exist_ok=True)
    logid_file = log_dir.joinpath(".logid")

    if not logid_file.is_file():
        logid = str(uuid.uuid4())

        with open(logid_file, "w") as f:
            f.write(f"{logid}\n")
    else:
        with open(logid_file) as a_file:
            logid = a_file.readline().rstrip()

    logid_dir = log_dir.joinpath(logid)
    logid_dir.mkdir(exist_ok=True)

    return logid_dir


def get_log_sub_dir(name: str):
    log_dir = get_log_dir()

    sub_dir = log_dir / name

    return sub_dir
