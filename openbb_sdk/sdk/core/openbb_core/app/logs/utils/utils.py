# IMPORT STANDARD
import time
import uuid
from pathlib import Path

# IMPORT THIRD-PARTY
# IMPORT INTERNAL


def get_session_id() -> str:
    """UUID of the current session."""
    session_id = str(uuid.uuid4()) + "-" + str(int(time.time()))
    return session_id


def get_app_id(contextual_user_data_directory: str) -> str:
    """UUID of the current installation."""

    try:
        app_id = get_log_dir(contextual_user_data_directory).stem
    except OSError as e:
        if e.errno == 30:
            print("Please move the application into a writable location.")
            print(
                "Note for macOS users: copy `OpenBB Terminal` folder outside the DMG."
            )
        else:
            raise e
    except Exception as e:
        raise e

    return app_id


def get_log_dir(contextual_user_data_directory: str) -> Path:
    """Retrieve application's log directory."""

    log_dir = Path(contextual_user_data_directory).joinpath("logs").absolute()

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
