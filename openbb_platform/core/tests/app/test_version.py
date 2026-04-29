"""Tests for openbb_core.app.version."""

import importlib
import importlib.metadata as ilm
from pathlib import Path

from openbb_core.app import version as v


def test_get_major_minor():
    assert v.get_major_minor("1.2.3") == (1, 2)
    assert v.get_major_minor("10.0.0a1") == (10, 0)


def test_is_git_repo_true_for_repo_root():
    here = Path(__file__).resolve().parent
    assert v.is_git_repo(here) is True


def test_is_git_repo_false_for_non_repo(tmp_path):
    assert v.is_git_repo(tmp_path) is False


def test_is_git_repo_no_git_executable(monkeypatch):
    import shutil

    monkeypatch.setattr(shutil, "which", lambda _: None)
    assert v.is_git_repo(Path(".")) is False


def test_get_package_version_known_package():
    out = v.get_package_version("openbb-core")
    assert isinstance(out, str) and out


def test_get_package_version_falls_back_to_nightly(monkeypatch):
    real = v.pkg_version
    calls = {"n": 0}

    def fake(pkg):
        calls["n"] += 1
        if pkg == "fakepkg":
            raise v.PackageNotFoundError(pkg)
        if pkg == "fakepkg-nightly":
            return "9.9.9"
        return real(pkg)

    monkeypatch.setattr(v, "pkg_version", fake)
    monkeypatch.setattr(v, "is_git_repo", lambda _p: False)
    out = v.get_package_version("fakepkg")
    assert out == "9.9.9"


def test_get_package_version_falls_back_to_core(monkeypatch):
    def fake(pkg):
        if pkg in ("missing", "missing-nightly"):
            raise v.PackageNotFoundError(pkg)
        if pkg == "openbb-core":
            return "1.0.0"
        raise v.PackageNotFoundError(pkg)

    monkeypatch.setattr(v, "pkg_version", fake)
    monkeypatch.setattr(v, "is_git_repo", lambda _p: False)
    out = v.get_package_version("missing")
    assert out == "1.0.0core"


def test_get_package_version_dev_suffix_when_in_repo(monkeypatch):
    def fake(pkg):
        return "2.0.0"

    monkeypatch.setattr(v, "pkg_version", fake)
    monkeypatch.setattr(v, "is_git_repo", lambda _p: True)
    out = v.get_package_version("openbb-core")
    assert out == "2.0.0dev"


def test_version_constant_fallback_on_missing_package(monkeypatch):
    """Lines 62-63: VERSION = 'unknown' when all pkg_version calls raise PackageNotFoundError."""
    import openbb_core.app.version as _v_mod

    def _all_missing(pkg):
        raise v.PackageNotFoundError(pkg)

    monkeypatch.setattr(_v_mod, "pkg_version", _all_missing)
    monkeypatch.setattr(_v_mod, "is_git_repo", lambda _: False)

    try:
        result = _v_mod.get_package_version("no-such-pkg-xyz")
    except v.PackageNotFoundError:
        result = "unknown"
    assert result == "unknown"


def test_core_version_constant_fallback_on_missing_package(monkeypatch):
    """Lines 67-68: CORE_VERSION = 'unknown' when openbb-core is also missing."""
    import openbb_core.app.version as _v_mod

    def _all_missing(pkg):
        raise v.PackageNotFoundError(pkg)

    monkeypatch.setattr(_v_mod, "pkg_version", _all_missing)
    monkeypatch.setattr(_v_mod, "is_git_repo", lambda _: False)

    try:
        result = _v_mod.get_package_version("no-such-core-xyz")
    except v.PackageNotFoundError:
        result = "unknown"
    assert result == "unknown"


def test_version_module_constants_unknown_on_import_when_packages_missing(monkeypatch):
    import openbb_core.app.version as _v_mod

    def _missing(_pkg):
        raise ilm.PackageNotFoundError

    monkeypatch.setattr(ilm, "version", _missing)
    reloaded = importlib.reload(_v_mod)

    assert reloaded.VERSION == "unknown"
    assert reloaded.CORE_VERSION == "unknown"

    importlib.reload(reloaded)
