"""过期文件管理实用程序。"""

import contextlib
from datetime import datetime
from pathlib import Path


def get_timestamp_from_x_days(x: int) -> float:
    """获取 x 天前的时间戳。"""
    timestamp_from_x_days = datetime.now().timestamp() - x * 86400
    return timestamp_from_x_days


def get_expired_file_list(directory: Path, before_timestamp: float) -> list[Path]:
    """获取目录中的过期文件列表。"""
    expired_files = []
    if directory.is_dir():  # 检查目录是否存在且为目录
        for file in directory.iterdir():
            if file.is_file() and file.lstat().st_mtime < before_timestamp:
                expired_files.append(file)

    return expired_files


def remove_file_list(file_list: list[Path]):
    """删除文件列表。"""
    for file in file_list:
        with contextlib.suppress(PermissionError):
            file.unlink(missing_ok=True)
