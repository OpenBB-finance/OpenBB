"""Tests for the ``openbb_mcp_server.utils.app_import`` aliases."""

import pytest

from openbb_mcp_server.app import (
    args as args_mod,
    bootstrap as bootstrap_mod,
)
from openbb_mcp_server.utils import app_import as shim


class TestAppImportAliases:
    """Lazy re-exports of ``import_app``, ``parse_args``, and ``cl_doc``."""

    @pytest.mark.parametrize(
        ("name", "target"),
        [
            ("import_app", bootstrap_mod.import_app),
            ("parse_args", args_mod.parse_args),
            ("cl_doc", args_mod.LAUNCH_SCRIPT_DESCRIPTION),
        ],
    )
    def test_alias_resolves_to_source(self, name, target):
        """Each legacy name resolves to its current source object."""
        assert getattr(shim, name) is target

    def test_unknown_attribute_raises(self):
        """Unknown attribute access raises a clean ``AttributeError``."""
        with pytest.raises(AttributeError, match="no attribute 'no_such_thing'"):
            _ = shim.no_such_thing

    def test_dir_lists_lazy_targets(self):
        """``dir()`` lists exactly the lazy names, sorted."""
        assert dir(shim) == ["cl_doc", "import_app", "parse_args"]
