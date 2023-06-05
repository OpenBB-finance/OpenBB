# IMPORTATION STANDARD
import uuid
from pathlib import Path

from openbb_terminal.core.session.current_user import get_current_user

# IMPORTATION THIRDPARTY


# IMPORTATION INTERNAL


def get_log_dir() -> Path:
    """Retrieve application's log directory."""

    log_dir = (
        get_current_user().preferences.USER_DATA_DIRECTORY.joinpath("logs").absolute()
    )

    if not log_dir.is_dir():
        log_dir.mkdir(parents=True, exist_ok=True)

    log_id = (log_dir / ".logid").absolute()

    if not log_id.is_file():
        logging_id = f"{uuid.uuid4()}"
        log_id.write_text(logging_id, encoding="utf-8")
    else:
        logging_id = log_id.read_text(encoding="utf-8").rstrip()

    uuid_log_dir = (log_dir / logging_id).absolute()

    if not uuid_log_dir.is_dir():
        uuid_log_dir.mkdir(parents=True, exist_ok=True)

    return uuid_log_dir


def get_log_sub_dir(name: str):
    log_dir = get_log_dir()

    sub_dir = log_dir / name

    return sub_dir
