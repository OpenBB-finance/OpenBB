"""日志记录的实用函数。"""

import time
import uuid
import warnings
from pathlib import Path, PosixPath


def get_session_id() -> str:
    """当前会话的 UUID。"""
    session_id = str(uuid.uuid4()) + "-" + str(int(time.time()))
    return session_id


def get_app_id(contextual_user_data_directory: str) -> str:
    """获取当前安装的 UUID。"""
    try:
        app_id = get_log_dir(contextual_user_data_directory).stem
    except OSError as e:
        if e.errno == 30:
            warnings.warn("请将应用程序移动到可写位置。")
            warnings.warn(
                "macOS 用户注意：将 `OpenBB Terminal` 文件夹复制到 DMG 之外。"
            )
        raise e
    except Exception as e:
        raise e

    return app_id


def get_log_dir(contextual_user_data_directory: str) -> PosixPath:
    """检索应用程序的日志目录。"""
    log_dir = create_log_dir_if_not_exists(contextual_user_data_directory)
    logging_uuid = create_log_uuid_if_not_exists(log_dir)
    uuid_log_dir = create_uuid_dir_if_not_exists(log_dir, logging_uuid)

    return uuid_log_dir


def create_log_dir_if_not_exists(contextual_user_data_directory: str) -> Path:
    """为当前安装创建日志目录。"""
    log_dir = Path(contextual_user_data_directory).joinpath("logs").absolute()
    if not log_dir.is_dir():
        log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir


def create_log_uuid_if_not_exists(log_dir: Path) -> str:
    """为当前日志会话创建日志 ID 文件。"""
    log_id = get_log_id(log_dir)
    if not log_id.is_file():
        logging_id = f"{uuid.uuid4()}"
        log_id.write_text(logging_id, encoding="utf-8")
    else:
        logging_id = log_id.read_text(encoding="utf-8").rstrip()

    return logging_id


def get_log_id(log_dir):
    """获取日志 ID 文件。"""
    return (log_dir / ".logid").absolute()


def create_uuid_dir_if_not_exists(log_dir, logging_id) -> PosixPath:
    """为当前日志会话创建目录。"""
    uuid_log_dir = (log_dir / logging_id).absolute()

    if not uuid_log_dir.is_dir():
        uuid_log_dir.mkdir(parents=True, exist_ok=True)

    return uuid_log_dir
