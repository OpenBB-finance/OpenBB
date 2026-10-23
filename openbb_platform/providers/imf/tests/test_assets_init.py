"""Smoke test for the ``openbb_imf.assets`` package marker."""

# ruff: noqa: I001


def test_assets_package_importable():
    """The ``openbb_imf.assets`` package imports cleanly."""
    import openbb_imf.assets as assets_pkg

    assert assets_pkg is not None
