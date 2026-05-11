"""Test the UserController class."""

from unittest.mock import MagicMock, patch

import pytest

MODULE = "openbb_cli.controllers.user_controller"


@pytest.fixture
def mock_user_session():
    """Create a mock session for UserController."""
    with patch(f"{MODULE}.session") as sess:
        sess.console = MagicMock()
        yield sess


@pytest.fixture
def mock_user_obb():
    """Mock obb.user.preferences with sample fields."""
    with patch(f"{MODULE}.obb") as obb_mock:
        obb_mock.user.preferences = MagicMock()
        obb_mock.user.preferences.__class__.model_fields = {}
        obb_mock.user.preferences.model_fields = {}
        yield obb_mock


class TestUserController:
    def test_generate_toggle_command(self, mock_user_session, mock_user_obb):
        from openbb_cli.controllers.user_controller import UserController

        ctrl = UserController.__new__(UserController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()

        field = {
            "command": "enable_feature",
            "field_name": "enable_feature",
            "description": "Enable a feature",
            "annotation": bool,
            "action": "toggle",
        }

        ns = MagicMock()
        ctrl.parse_simple_args = MagicMock(return_value=(ns, []))
        mock_user_obb.user.preferences.enable_feature = True

        ctrl._generate_command("enable_feature", field, "toggle")
        assert hasattr(ctrl, "call_enable_feature")

        ctrl.call_enable_feature([])
        assert True
        mock_user_session.console.print.assert_called()

    def test_generate_set_command_with_value(self, mock_user_session, mock_user_obb):
        from openbb_cli.controllers.user_controller import UserController

        ctrl = UserController.__new__(UserController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()

        field = {
            "command": "timezone",
            "field_name": "timezone",
            "description": "Set the timezone",
            "annotation": str,
            "action": "set",
        }

        ns = MagicMock()
        ns.value = "US/Eastern"
        ctrl.parse_simple_args = MagicMock(return_value=(ns, []))

        ctrl._generate_command("timezone", field, "set")
        assert hasattr(ctrl, "call_timezone")

        ctrl.call_timezone(["-v", "US/Eastern"])
        mock_user_session.console.print.assert_called()

    def test_generate_set_command_no_value_shows_current(
        self, mock_user_session, mock_user_obb
    ):
        from openbb_cli.controllers.user_controller import UserController

        ctrl = UserController.__new__(UserController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()

        field = {
            "command": "timezone",
            "field_name": "timezone",
            "description": "Set the timezone",
            "annotation": str,
            "action": "set",
        }

        ns = MagicMock()
        ns.value = None
        ctrl.parse_simple_args = MagicMock(return_value=(ns, []))
        mock_user_obb.user.preferences.timezone = "UTC"

        ctrl._generate_command("timezone", field, "set")
        ctrl.call_timezone([])
        mock_user_session.console.print.assert_called()
        args = mock_user_session.console.print.call_args[0][0]
        assert "timezone" in args

    def test_invalid_action_type(self, mock_user_session, mock_user_obb):
        from openbb_cli.controllers.user_controller import UserController

        ctrl = UserController.__new__(UserController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()

        field = {
            "command": "x",
            "field_name": "x",
            "description": "x",
            "annotation": str,
            "action": "bad",
        }

        with pytest.raises(ValueError, match="not allowed"):
            ctrl._generate_command("x", field, "bad")

    def test_call_credentials_loads_controller(self, mock_user_session, mock_user_obb):
        from openbb_cli.controllers.user_controller import UserController

        ctrl = UserController.__new__(UserController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()
        ctrl.load_class = MagicMock(return_value=[])

        ctrl.call_credentials(None)
        ctrl.load_class.assert_called_once()

    def test_init_runs_super_and_generates_commands(
        self, mock_user_session, mock_user_obb
    ):
        """Real ``__init__`` calls super, runs ``_generate_command`` per pref, updates completer."""
        from unittest.mock import PropertyMock

        from openbb_cli.controllers.user_controller import UserController

        with (
            patch(
                "openbb_cli.controllers.base_controller.BaseController.__init__",
                return_value=None,
            ) as super_init,
            patch.object(
                UserController,
                "choices_default",
                new_callable=PropertyMock,
                return_value={},
            ),
            patch.object(UserController, "_generate_command") as gen,
            patch.object(UserController, "update_completer") as update_completer,
        ):
            UserController(queue=["q"])
        super_init.assert_called_once_with(["q"])
        assert gen.call_count == len(UserController._PREF_COMMANDS)
        update_completer.assert_called_once()

    def test_set_command_literal_annotation_uses_choices(
        self, mock_user_session, mock_user_obb
    ):
        """``Literal[...]`` annotation populates argparse choices and keeps type as str."""
        from typing import Literal

        from openbb_cli.controllers.user_controller import UserController

        ctrl = UserController.__new__(UserController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()
        field = {
            "command": "theme",
            "field_name": "theme",
            "description": "Theme",
            "annotation": Literal["dark", "light"],
            "action": "set",
        }
        ns = MagicMock()
        ns.value = "dark"
        ctrl.parse_simple_args = MagicMock(return_value=(ns, []))

        ctrl._generate_command("theme", field, "set")
        ctrl.call_theme(["-v", "dark"])
        mock_user_session.console.print.assert_called()

    def test_set_command_int_annotation_uses_int_type(
        self, mock_user_session, mock_user_obb
    ):
        """``int`` annotation makes argparse coerce the value to int."""
        from openbb_cli.controllers.user_controller import UserController

        ctrl = UserController.__new__(UserController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()
        field = {
            "command": "limit",
            "field_name": "limit",
            "description": "Row limit",
            "annotation": int,
            "action": "set",
        }
        ns = MagicMock()
        ns.value = 10
        ctrl.parse_simple_args = MagicMock(return_value=(ns, []))

        ctrl._generate_command("limit", field, "set")
        ctrl.call_limit(["-v", "10"])
        mock_user_session.console.print.assert_called()

    def test_set_command_other_annotation_falls_back_to_str(
        self, mock_user_session, mock_user_obb
    ):
        """Unknown annotation (e.g. float) falls back to ``type_ = str`` branch."""
        from openbb_cli.controllers.user_controller import UserController

        ctrl = UserController.__new__(UserController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()
        field = {
            "command": "ratio",
            "field_name": "ratio",
            "description": "A ratio",
            "annotation": float,
            "action": "set",
        }
        ns = MagicMock()
        ns.value = "0.5"
        ctrl.parse_simple_args = MagicMock(return_value=(ns, []))

        ctrl._generate_command("ratio", field, "set")
        ctrl.call_ratio(["-v", "0.5"])
        mock_user_session.console.print.assert_called()

    def test_print_help(self, mock_user_session, mock_user_obb):
        from openbb_cli.controllers.user_controller import UserController

        ctrl = UserController.__new__(UserController)
        ctrl.queue = []
        ctrl.update_completer = MagicMock()
        ctrl._PREF_COMMANDS = {
            "enable_feature": {
                "command": "enable_feature",
                "field_name": "enable_feature",
                "description": "Enable a feature",
                "annotation": bool,
                "action": "toggle",
            },
            "timezone": {
                "command": "timezone",
                "field_name": "timezone",
                "description": "Set the timezone",
                "annotation": str,
                "action": "set",
            },
        }
        mock_user_obb.user.preferences.enable_feature = True
        mock_user_obb.user.preferences.timezone = "UTC"

        ctrl.print_help()
        mock_user_session.console.print.assert_called_once()
