"""User Controller Module."""

import argparse
from functools import partial, update_wrapper
from types import MethodType
from typing import Annotated, Any, Literal, cast, get_args, get_origin

from openbb import obb as _obb_container

obb = cast(Any, _obb_container)

from openbb_cli.config.menu_text import MenuText
from openbb_cli.controllers.base_controller import BaseController
from openbb_cli.session import Session

session = Session()


class UserController(BaseController):
    """User Controller class."""

    PATH = "/user/"
    CHOICES_GENERATION = True

    _PREF_COMMANDS: dict[str, dict[str, Any]] = {}
    for _fname, _finfo in sorted(obb.user.preferences.__class__.model_fields.items()):
        _annotation = _finfo.annotation
        _is_bool = _annotation is bool
        _PREF_COMMANDS[_fname] = {
            "command": _fname,
            "field_name": _fname,
            "description": _finfo.description or _fname.replace("_", " "),
            "annotation": _annotation,
            "action": "toggle" if _is_bool else "set",
        }

    CHOICES_COMMANDS: list[str] = list(_PREF_COMMANDS.keys())
    CHOICES_MENUS: list[str] = ["credentials"]

    def __init__(self, queue: list[str] | None = None):
        """Initialize the Constructor."""
        super().__init__(queue)
        for cmd, field in self._PREF_COMMANDS.items():
            self._generate_command(cmd, field, field["action"])
        self.update_completer(self.choices_default)

    def print_help(self):
        """Print help."""
        mt = MenuText("user/")
        mt.add_info("Session-level platform user settings (not persisted)")

        mt.add_raw("\n")
        mt.add_info("Toggles")
        for cmd, f in self._PREF_COMMANDS.items():
            if f["action"] == "toggle":
                mt.add_setting(
                    name=cmd,
                    status=getattr(obb.user.preferences, f["field_name"]),
                    description=f["description"],
                )

        mt.add_raw("\n")
        mt.add_info("Preferences")
        for cmd, f in self._PREF_COMMANDS.items():
            if f["action"] == "set":
                current = getattr(obb.user.preferences, f["field_name"])
                mt.add_cmd(
                    name=cmd,
                    description=f"{f['description']} [dim](current: {current})[/dim]",
                )

        mt.add_raw("\n")
        mt.add_menu(
            "credentials",
            description="view and set API keys and tokens for the session",
        )

        session.console.print(text=mt.menu_text, menu="User")

    def call_credentials(self, _):
        """Process credentials command."""
        from openbb_cli.controllers.credentials_controller import (
            CredentialsController,
        )

        self.queue = self.load_class(CredentialsController, self.queue)

    def _generate_command(
        self, cmd_name: str, field: dict, action_type: Literal["toggle", "set"]
    ):
        """Generate a toggle or set command bound to obb.user.preferences."""

        def _toggle(self, other_args: list[str], field=field) -> None:
            """Toggle a boolean preference."""
            field_name = field["field_name"]
            parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog=field["command"],
                description=field["description"],
                add_help=False,
            )
            ns_parser, _ = self.parse_simple_args(parser, other_args)
            if ns_parser:
                current = getattr(obb.user.preferences, field_name)
                setattr(obb.user.preferences, field_name, not current)
                session.console.print(f"[info]{field_name}:[/info] {not current}")

        def _set(self, other_args: list[str], field=field) -> None:
            """Set a preference value."""
            field_name = field["field_name"]
            annotation = field["annotation"]
            command = field["command"]

            type_: type = str
            choices = None
            if get_origin(annotation) is Literal:
                choices = list(get_args(annotation))
                type_ = str
            elif annotation is int or (
                get_origin(annotation) is Annotated
                and get_args(annotation)
                and get_args(annotation)[0] is int
            ):
                type_ = int
            elif annotation is not str:
                type_ = str

            parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog=command,
                description=field["description"],
                add_help=False,
            )
            parser.add_argument(
                "-v",
                "--value",
                dest="value",
                action="store",
                required=False,
                type=type_,
                choices=choices,
            )
            ns_parser, _ = self.parse_simple_args(parser, other_args)
            if ns_parser:
                if ns_parser.value is not None:
                    setattr(obb.user.preferences, field_name, ns_parser.value)
                    session.console.print(
                        f"[info]{field_name}:[/info] {getattr(obb.user.preferences, field_name)}"
                    )
                elif not other_args:
                    current = getattr(obb.user.preferences, field_name)
                    session.console.print(f"[info]{field_name}:[/info] {current}")

        if action_type == "toggle":
            action = _toggle
        elif action_type == "set":
            action = _set
        else:
            raise ValueError(f"Action type '{action_type}' not allowed.")

        bound_method = update_wrapper(
            wrapper=partial(MethodType(action, self), field=field), wrapped=action
        )
        setattr(self, f"call_{cmd_name}", bound_method)
