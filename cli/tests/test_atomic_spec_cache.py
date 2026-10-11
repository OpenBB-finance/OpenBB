"""Spec replacement failures preserve the last complete cache."""

import json

import pytest

from openbb_cli.dispatchers import spec


@pytest.mark.parametrize("failure", ["write", "fsync", "replace"])
def test_failed_spec_save_preserves_old_cache_without_temp_files(
    tmp_path, monkeypatch, failure
):
    target = tmp_path / "existing.spec"
    previous = {"version": spec.SPEC_VERSION, "commands": {"old": {"parameters": []}}}
    spec.write_spec(target, previous)
    original = target.read_bytes()

    def fail(*_args, **_kwargs):
        raise OSError("injected save failure")

    if failure == "write":

        def failed_dump(value, stream, **kwargs):
            stream.write('{"incomplete":')
            fail()

        monkeypatch.setattr(spec.json, "dump", failed_dump)
    else:
        monkeypatch.setattr("os." + failure, fail)
    with pytest.raises(OSError, match="injected save failure"):
        spec.write_spec(target, {"version": spec.SPEC_VERSION, "commands": {}})
    assert target.read_bytes() == original
    assert json.loads(target.read_text())["commands"] == previous["commands"]
    assert list(tmp_path.iterdir()) == [target]


def test_spec_save_replaces_with_complete_hashed_document(tmp_path):
    target = tmp_path / "existing.spec"
    target.write_text('{"old": true}')
    value = {"version": spec.SPEC_VERSION, "commands": {}, "label": "café"}
    spec.write_spec(target, value)
    loaded = json.loads(target.read_text())
    assert loaded == value
    assert loaded["content_sha256"] == spec._content_hash(loaded)
    assert "\n" not in target.read_text()
    assert list(tmp_path.iterdir()) == [target]
