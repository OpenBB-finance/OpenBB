"""Additional tests for openbb_core.app.logs.utils.utils covering create_* helpers."""

from pathlib import Path

from openbb_core.app.logs.utils.utils import (
    create_log_dir_if_not_exists,
    create_log_uuid_if_not_exists,
    create_uuid_dir_if_not_exists,
    get_log_id,
)


def test_create_log_dir_if_not_exists_creates_and_is_idempotent(tmp_path):
    log_dir = create_log_dir_if_not_exists(str(tmp_path))
    assert log_dir.is_dir()
    assert log_dir == (tmp_path / "logs").absolute()
    again = create_log_dir_if_not_exists(str(tmp_path))
    assert again == log_dir


def test_create_log_uuid_writes_then_reads(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    first = create_log_uuid_if_not_exists(log_dir)
    second = create_log_uuid_if_not_exists(log_dir)
    assert first == second
    assert get_log_id(log_dir).read_text(encoding="utf-8").rstrip() == first


def test_create_uuid_dir_if_not_exists(tmp_path):
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    out = create_uuid_dir_if_not_exists(log_dir, "abc-123")
    assert out.is_dir()
    assert out.name == "abc-123"


def test_get_log_id_returns_logid_path(tmp_path):
    p = get_log_id(tmp_path)
    assert isinstance(p, Path)
    assert p.name == ".logid"
