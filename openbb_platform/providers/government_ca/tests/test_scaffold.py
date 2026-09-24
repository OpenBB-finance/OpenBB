"""Government of Canada scaffold smoke tests."""

from pathlib import Path


def test_import_succeeds():
    """The package imports without raising."""
    import openbb_government_ca  # noqa: F401


def test_scaffold_layout_exists():
    """The scaffold directories and the py.typed marker are in place."""
    import openbb_government_ca

    package = Path(openbb_government_ca.__file__).parent
    root = package.parent

    assert (package / "assets").is_dir()
    assert (package / "utils").is_dir()
    assert (root / "tests" / "record").is_dir()
    assert (package / "py.typed").is_file()
