"""Tests for openbb_core.app.static.package_builder.file_lock."""

import importlib
import sys
from types import SimpleNamespace

import pytest

from openbb_core.app.static.package_builder import file_lock as file_lock_module
from openbb_core.app.static.package_builder.file_lock import _HAS_FCNTL, FileLock


@pytest.mark.skipif(not _HAS_FCNTL, reason="fcntl required")
def test_file_lock_acquire_and_release(tmp_path):
    p = tmp_path / "lock.txt"
    p.write_text("")
    with p.open("w") as f:
        lock = FileLock(f)
        lock.acquire()
        lock.release()


@pytest.mark.skipif(not _HAS_FCNTL, reason="fcntl required")
def test_file_lock_non_blocking(tmp_path):
    p = tmp_path / "lock.txt"
    p.write_text("")
    with p.open("w") as f:
        lock = FileLock(f)
        lock.acquire(blocking=False)
        lock.release()


def test_file_lock_release_swallows_errors():
    class Bad:
        def fileno(self):
            raise OSError("nope")

        def seek(self, _):
            raise OSError("nope")

    FileLock(Bad()).release()


@pytest.mark.skipif(not _HAS_FCNTL, reason="fcntl required")
def test_file_lock_second_acquire_non_blocking_raises(tmp_path):
    p = tmp_path / "lock.txt"
    p.write_text("")
    f1 = p.open("w")
    f2 = p.open("w")
    try:
        FileLock(f1).acquire()
        with pytest.raises(BlockingIOError):
            FileLock(f2).acquire(blocking=False)
    finally:
        FileLock(f1).release()
        f1.close()
        f2.close()


def test_file_lock_windows_non_blocking_error_is_normalized(monkeypatch):
    class _MSVCRT:
        LK_LOCK = 1
        LK_NBLCK = 2
        LK_UNLCK = 3

        @staticmethod
        def locking(_fd, _mode, _size):
            raise OSError("busy")

    class _File:
        def seek(self, _pos):
            return None

        def fileno(self):
            return 1

    monkeypatch.setattr(file_lock_module, "_HAS_FCNTL", False)
    monkeypatch.setattr(file_lock_module, "msvcrt", _MSVCRT, raising=False)

    with pytest.raises(BlockingIOError):
        FileLock(_File()).acquire(blocking=False)


def test_file_lock_windows_release_unlock_error_is_ignored(monkeypatch):
    class _MSVCRT:
        LK_LOCK = 1
        LK_NBLCK = 2
        LK_UNLCK = 3

        @staticmethod
        def locking(_fd, _mode, _size):
            raise OSError("unlock failed")

    class _File:
        def seek(self, _pos):
            return None

        def fileno(self):
            return 1

    monkeypatch.setattr(file_lock_module, "_HAS_FCNTL", False)
    monkeypatch.setattr(file_lock_module, "msvcrt", _MSVCRT, raising=False)

    FileLock(_File()).release()


def test_file_lock_windows_blocking_mode_branch(monkeypatch):
    calls = []

    class _MSVCRT:
        LK_LOCK = 1
        LK_NBLCK = 2
        LK_UNLCK = 3

        @staticmethod
        def locking(_fd, mode, _size):
            calls.append(mode)

    class _File:
        def seek(self, _pos):
            return None

        def fileno(self):
            return 1

    monkeypatch.setattr(file_lock_module, "_HAS_FCNTL", False)
    monkeypatch.setattr(file_lock_module, "msvcrt", _MSVCRT, raising=False)

    FileLock(_File()).acquire(blocking=True)
    assert calls == [_MSVCRT.LK_LOCK]


def test_file_lock_forced_fcntl_branch_via_reload(monkeypatch):
    calls = []

    def _flock(fd, flags):
        calls.append((fd, flags))

    fake_fcntl = SimpleNamespace(LOCK_EX=1, LOCK_NB=2, LOCK_UN=4, flock=_flock)

    monkeypatch.setitem(sys.modules, "fcntl", fake_fcntl)
    reloaded = importlib.reload(file_lock_module)

    class _File:
        def fileno(self):
            return 11

    lock = reloaded.FileLock(_File())
    lock.acquire(blocking=False)
    lock.release()

    assert reloaded._HAS_FCNTL is True
    assert calls == [
        (11, fake_fcntl.LOCK_EX | fake_fcntl.LOCK_NB),
        (11, fake_fcntl.LOCK_UN),
    ]

    monkeypatch.delitem(sys.modules, "fcntl", raising=False)
    importlib.reload(file_lock_module)


def test_file_lock_forced_fcntl_release_outer_exception(monkeypatch):
    def _flock(_fd, _flags):
        return None

    fake_fcntl = SimpleNamespace(LOCK_EX=1, LOCK_NB=2, LOCK_UN=4, flock=_flock)
    monkeypatch.setattr(file_lock_module, "_HAS_FCNTL", True)
    monkeypatch.setattr(file_lock_module, "fcntl", fake_fcntl, raising=False)

    class _Bad:
        def fileno(self):
            raise RuntimeError("boom")

    FileLock(_Bad()).release()
