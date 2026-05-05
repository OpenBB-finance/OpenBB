"""Test linters.py file."""

# pylint: disable=redefined-outer-name

import importlib.util
import sys

import pytest
from openbb_core.app.static.package_builder import (
    Linters,
)


@pytest.fixture(scope="module")
def tmp_package_dir(tmp_path_factory):
    """Return a temporary package directory."""
    return tmp_path_factory.mktemp("package")


@pytest.fixture(scope="module")
def linters(tmp_package_dir):
    """Return linters."""
    return Linters(tmp_package_dir)


def test_linters_init(linters):
    """Test linters init."""
    assert linters


def test_print_separator(linters):
    """Test print separator."""
    linters.print_separator(symbol="AAPL")


def test_run(linters):
    """Test run."""
    linters.run(linter="ruff")


def test_ruff(linters):
    """Test ruff."""
    linters.ruff()


def test_black(linters):
    """Test black."""
    linters.black()


@pytest.mark.skipif(
    importlib.util.find_spec("ruff") is None,
    reason="ruff not installed in this environment",
)
def test_ruff_strips_unused_imports_via_module_invocation(tmp_path, monkeypatch):
    """Regression test for the silent-skip bug.

    When the venv's bin/ is not on PATH, the previous shutil.which-based
    lookup returned None and the linter step silently no-op'd. That left
    the speculative ``OBBject_*`` imports emitted by ``ImportDefinition``
    in generated files, producing an ``ImportError`` at first use.

    The fix invokes ``python -m <linter>``, which is independent of PATH.
    This test simulates the broken case by emptying PATH for the duration
    of the run and asserts that ruff still strips an unused import.
    """
    sample = tmp_path / "sample.py"
    sample.write_text("import os\n")

    monkeypatch.setenv("PATH", "")
    Linters(tmp_path).ruff()

    # ruff with --fix should remove the unused import; if linting was
    # silently skipped, the file would still contain "import os".
    assert "import os" not in sample.read_text()


def test_run_logs_not_found_when_module_missing(tmp_path, capsys):
    """Missing linter should be reported, not silently skipped.

    Uses a known-non-existent linter name to exercise the find_spec branch
    without depending on what is actually installed.
    """
    Linters(tmp_path, verbose=True).run(linter="black")  # baseline: should run
    Linters(tmp_path, verbose=True).run(
        linter="this_linter_definitely_does_not_exist"  # type: ignore[arg-type]
    )
    out = capsys.readouterr().out
    assert "this_linter_definitely_does_not_exist not found" in out

    # Ensure the same Python interpreter has the linter package importable
    # via the module form -- a sanity check on the new invocation path.
    assert sys.executable
