"""Tests for the OpenBB mirror sync checker."""

from __future__ import annotations

from pathlib import Path

from openbb_platform.tools import check_openbb_sync


def _write_sync_fixtures(repo: Path, mirror_content: str = "shared-content") -> None:
    primary_assets = repo / "openbb_platform" / "core" / "openbb" / "assets"
    primary_package = repo / "openbb_platform" / "core" / "openbb" / "package"
    mirror_assets = repo / "OpenBB" / "openbb_platform" / "core" / "openbb" / "assets"
    mirror_package = repo / "OpenBB" / "openbb_platform" / "core" / "openbb" / "package"

    for path in (primary_assets, primary_package, mirror_assets, mirror_package):
        path.mkdir(parents=True, exist_ok=True)

    (primary_assets / "reference.json").write_text(mirror_content, encoding="utf-8")
    (mirror_assets / "reference.json").write_text(mirror_content, encoding="utf-8")
    (primary_package / "__extensions__.py").write_text(mirror_content, encoding="utf-8")
    (mirror_package / "__extensions__.py").write_text(mirror_content, encoding="utf-8")

    token_block = "\n".join(
        [
            'openbb-quant-ml = { version = "^0.1.0", optional = true }',
            'quant_ml = ["openbb-quant-ml"]',
            '"openbb-quant-ml"',
        ]
    )
    (repo / "openbb_platform" / "pyproject.toml").write_text(token_block, encoding="utf-8")
    (repo / "OpenBB" / "openbb_platform" / "pyproject.toml").write_text(
        token_block,
        encoding="utf-8",
    )


def test_main_skips_when_mirror_tree_is_absent(tmp_path: Path, monkeypatch, capsys) -> None:
    repo = tmp_path
    (repo / "openbb_platform").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(
        check_openbb_sync,
        "parse_args",
        lambda: type("Args", (), {"repo_root": str(repo)})(),
    )

    assert check_openbb_sync.main() == 0
    assert "SKIP mirror tree absent" in capsys.readouterr().out


def test_main_passes_when_primary_and_mirror_are_synced(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = tmp_path
    _write_sync_fixtures(repo)
    monkeypatch.setattr(
        check_openbb_sync,
        "parse_args",
        lambda: type("Args", (), {"repo_root": str(repo)})(),
    )

    assert check_openbb_sync.main() == 0
    assert "sync policy check passed" in capsys.readouterr().out


def test_main_fails_when_primary_and_mirror_diverge(
    tmp_path: Path,
    monkeypatch,
    capsys,
) -> None:
    repo = tmp_path
    _write_sync_fixtures(repo)
    (
        repo
        / "OpenBB"
        / "openbb_platform"
        / "core"
        / "openbb"
        / "package"
        / "__extensions__.py"
    ).write_text("different-content", encoding="utf-8")
    monkeypatch.setattr(
        check_openbb_sync,
        "parse_args",
        lambda: type("Args", (), {"repo_root": str(repo)})(),
    )

    assert check_openbb_sync.main() == 1
    assert "sync policy check failed" in capsys.readouterr().out
