"""Cross-platform file lock used by the package builder."""

from typing import (
    TYPE_CHECKING,
    TypeVar,
)

if TYPE_CHECKING:
    from numpy import ndarray  # noqa
    from pandas import DataFrame, Series  # noqa
    from openbb_core.provider.abstract.data import Data  # noqa

from importlib.util import find_spec

CHARTING_INSTALLED = find_spec("openbb_charting") is not None

try:
    import fcntl

    _HAS_FCNTL = True
except Exception:  # noqa
    _HAS_FCNTL = False
    import msvcrt  # noqa

DataProcessingSupportedTypes = TypeVar(
    "DataProcessingSupportedTypes",
    list,
    dict,
    "DataFrame",
    list["DataFrame"],
    "Series",
    list["Series"],
    "ndarray",
    "Data",
)

from openbb_core.app.static.package_builder._indent import (  # noqa: F401
    TAB,
    create_indent,
)


class FileLock:
    """Simple cross-platform file lock wrapper used only for this module."""

    def __init__(self, file_obj):
        """Initialize the file lock."""
        self._file = file_obj

    def acquire(self, blocking: bool = True) -> None:
        """Acquire the file lock."""
        if _HAS_FCNTL:
            flags = fcntl.LOCK_EX | (0 if blocking else fcntl.LOCK_NB)
            fcntl.flock(self._file.fileno(), flags)
        else:  # Windows via msvcrt
            mode = msvcrt.LK_LOCK if blocking else msvcrt.LK_NBLCK  # type: ignore
            try:
                # lock 1 byte at file start; file.seek(0) to ensure position
                self._file.seek(0)
                msvcrt.locking(self._file.fileno(), mode, 1)  # type: ignore
            except OSError as exc:  # pragma: no cover - platform specific
                # Normalize to BlockingIOError for parity with fcntl non-blocking
                raise BlockingIOError from exc

    def release(self) -> None:
        """Release the file lock."""
        try:
            if _HAS_FCNTL:
                fcntl.flock(self._file.fileno(), fcntl.LOCK_UN)
            else:
                try:
                    self._file.seek(0)
                    msvcrt.locking(self._file.fileno(), msvcrt.LK_UNLCK, 1)  # type: ignore
                except OSError:
                    # If unlocking fails on Windows, ignore - file will be closed soon
                    pass
        except Exception:  # noqa
            pass
