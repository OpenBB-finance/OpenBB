"""Test the CredentialsController class."""

from unittest.mock import MagicMock, patch

import pytest
from pydantic import SecretStr

MODULE = "openbb_cli.controllers.credentials_controller"


class TestCredentialStatus:
    """Test the _credential_status helper function."""

    def test_secret_str_with_value(self):
        from openbb_cli.controllers.credentials_controller import _credential_status

        result = _credential_status(SecretStr("abcdef12345"))
        assert "Set" in result
        assert "abcd" in result
        assert "green" in result

    def test_secret_str_empty(self):
        from openbb_cli.controllers.credentials_controller import _credential_status

        result = _credential_status(SecretStr(""))
        assert "Not set" in result
        assert "red" in result

    def test_non_secret_str(self):
        from openbb_cli.controllers.credentials_controller import _credential_status

        result = _credential_status(None)
        assert "Not set" in result
        assert "red" in result

    def test_plain_string(self):
        from openbb_cli.controllers.credentials_controller import _credential_status

        result = _credential_status("some_string")
        assert "Not set" in result


@pytest.fixture
def mock_cred_session():
    """Create a mock session for CredentialsController."""
    with patch(f"{MODULE}.session") as sess:
        sess.console = MagicMock()
        yield sess


@pytest.fixture
def mock_obb():
    """Mock the obb object with credentials."""
    with patch(f"{MODULE}.obb") as obb_mock:
        obb_mock.user.credentials = MagicMock()
        obb_mock.user.credentials.__class__.model_fields = {
            "test_api_key": MagicMock(description="test provider"),
        }
        obb_mock.user.credentials.test_api_key = SecretStr("mykey1234")
        yield obb_mock


class TestCredentialsController:
    def test_init_generates_commands(self, mock_cred_session, mock_obb):
        from openbb_cli.controllers.credentials_controller import (
            CredentialsController,
        )

        ctrl = CredentialsController.__new__(CredentialsController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()

        ctrl._CRED_COMMANDS = {
            "test_api_key": {
                "command": "test_api_key",
                "field_name": "test_api_key",
                "provider": "test provider",
            }
        }
        ctrl.CHOICES_COMMANDS = list(ctrl._CRED_COMMANDS.keys())
        ctrl.parse_simple_args = MagicMock()

        for cmd, field in ctrl._CRED_COMMANDS.items():
            ctrl._generate_credential_command(cmd, field)

        assert hasattr(ctrl, "call_test_api_key")

    def test_init_loop_runs_for_each_class_level_credential(
        self, mock_cred_session, mock_obb, monkeypatch
    ):
        """Real ``__init__`` path: when the class-level ``_CRED_COMMANDS`` is
        non-empty (the normal case for a populated install), the for-loop
        body runs once per credential and registers the dynamic
        ``call_<name>`` method. On Windows CI installs without provider
        credentials the class dict is empty, so the loop body is skipped —
        this test pins coverage by populating the class attribute itself."""
        from openbb_cli.controllers.credentials_controller import (
            CredentialsController,
        )

        # Patch the class attribute (not just the instance) so __init__ sees it.
        monkeypatch.setattr(
            CredentialsController,
            "_CRED_COMMANDS",
            {
                "covered_api_key": {
                    "command": "covered_api_key",
                    "field_name": "covered_api_key",
                    "provider": "covered",
                }
            },
        )
        with patch.object(CredentialsController, "update_completer"):
            ctrl = CredentialsController(queue=[])
        assert hasattr(ctrl, "call_covered_api_key")

    def test_print_help(self, mock_cred_session, mock_obb):
        from openbb_cli.controllers.credentials_controller import (
            CredentialsController,
        )

        ctrl = CredentialsController.__new__(CredentialsController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()
        ctrl._CRED_COMMANDS = {
            "test_api_key": {
                "command": "test_api_key",
                "field_name": "test_api_key",
                "provider": "test provider",
            }
        }
        ctrl.print_help()
        mock_cred_session.console.print.assert_called_once()
        call_kwargs = mock_cred_session.console.print.call_args[1]
        assert "Credentials" in call_kwargs.get("menu", "")

    def test_set_credential_via_value(self, mock_cred_session, mock_obb):
        from openbb_cli.controllers.credentials_controller import (
            CredentialsController,
        )

        ctrl = CredentialsController.__new__(CredentialsController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()
        ctrl._CRED_COMMANDS = {
            "test_api_key": {
                "command": "test_api_key",
                "field_name": "test_api_key",
                "provider": "test provider",
            }
        }

        ns = MagicMock()
        ns.value = "new_secret"
        ctrl.parse_simple_args = MagicMock(return_value=(ns, []))

        for cmd, field in ctrl._CRED_COMMANDS.items():
            ctrl._generate_credential_command(cmd, field)

        ctrl.call_test_api_key(["-v", "new_secret"])
        mock_cred_session.console.print.assert_called()
        args = mock_cred_session.console.print.call_args[0][0]
        assert "Set" in args

    def test_view_credential_no_args(self, mock_cred_session, mock_obb):
        from openbb_cli.controllers.credentials_controller import (
            CredentialsController,
        )

        ctrl = CredentialsController.__new__(CredentialsController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()
        ctrl._CRED_COMMANDS = {
            "test_api_key": {
                "command": "test_api_key",
                "field_name": "test_api_key",
                "provider": "test provider",
            }
        }

        ns = MagicMock()
        ns.value = None
        ctrl.parse_simple_args = MagicMock(return_value=(ns, []))

        for cmd, field in ctrl._CRED_COMMANDS.items():
            ctrl._generate_credential_command(cmd, field)

        ctrl.call_test_api_key([])
        mock_cred_session.console.print.assert_called()

    def test_init_runs_super_and_generates_all_commands(
        self, mock_cred_session, mock_obb
    ):
        """Real ``__init__`` runs ``super().__init__()`` and generates one ``call_*`` per credential."""
        from unittest.mock import PropertyMock

        from openbb_cli.controllers.credentials_controller import (
            CredentialsController,
        )

        with (
            patch(
                "openbb_cli.controllers.base_controller.BaseController.__init__",
                return_value=None,
            ) as super_init,
            patch.object(
                CredentialsController,
                "choices_default",
                new_callable=PropertyMock,
                return_value={},
            ),
            patch.object(CredentialsController, "update_completer") as update_completer,
            patch.object(CredentialsController, "_generate_credential_command") as gen,
        ):
            CredentialsController(queue=["x"])
        super_init.assert_called_once_with(["x"])
        assert gen.call_count == len(CredentialsController._CRED_COMMANDS)
        update_completer.assert_called_once()


def test_class_level_loop_builds_cred_commands_from_model_fields():
    """Re-import the module with a populated ``credentials.model_fields`` so the
    class-body loop (which derives ``_CRED_COMMANDS`` from the live credentials
    class) is exercised. Without this, environments where no provider extensions
    are installed leave the loop body uncovered.

    Covers both branches of the provider derivation:
    * ``description == name`` → suffix-stripping fallback
    * ``description != name`` → keep description as the provider label
    """
    import importlib
    import sys
    from unittest.mock import MagicMock

    import openbb

    fmp_field = MagicMock()
    fmp_field.description = "fmp_api_key"
    polygon_field = MagicMock()
    polygon_field.description = "Polygon API token"
    bare_token_field = MagicMock()
    bare_token_field.description = "tiingo_token"
    plain_key_field = MagicMock()
    plain_key_field.description = "alpaca_key"

    fake_creds_class = type(
        "FakeCredentials",
        (),
        {
            "model_fields": {
                "fmp_api_key": fmp_field,
                "polygon_token": polygon_field,
                "tiingo_token": bare_token_field,
                "alpaca_key": plain_key_field,
            }
        },
    )
    fake_creds_instance = MagicMock()
    fake_creds_instance.__class__ = fake_creds_class

    fake_obb = MagicMock()
    fake_obb.user.credentials = fake_creds_instance

    original_obb = openbb.obb
    openbb.obb = fake_obb
    sys.modules.pop("openbb_cli.controllers.credentials_controller", None)
    try:
        mod = importlib.import_module("openbb_cli.controllers.credentials_controller")
        cmds = mod.CredentialsController._CRED_COMMANDS
        assert cmds["fmp_api_key"]["provider"] == "fmp"
        assert cmds["polygon_token"]["provider"] == "Polygon API token"
        assert cmds["tiingo_token"]["provider"] == "tiingo"
        assert cmds["alpaca_key"]["provider"] == "alpaca"
    finally:
        openbb.obb = original_obb
        sys.modules.pop("openbb_cli.controllers.credentials_controller", None)
