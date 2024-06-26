"""Settings Controller Module."""

import argparse
from functools import partial, update_wrapper
from types import MethodType
from typing import List, Literal, Optional, get_origin

from openbb_cli.config.menu_text import MenuText
from openbb_cli.controllers.base_controller import BaseController
from openbb_cli.models.settings import SettingGroups
from openbb_cli.session import Session

session = Session()


class SettingsController(BaseController):
    """Settings Controller class."""

    _COMMANDS = {
        v.json_schema_extra.get("command"): {
            "command": (v.json_schema_extra or {}).get("command"),
            "group": (v.json_schema_extra or {}).get("group"),
            "description": v.description,
            "annotation": v.annotation,
            "field_name": k,
        }
        for k, v in sorted(
            session.settings.model_fields.items(),
            key=lambda item: (item[1].json_schema_extra or {}).get("command", ""),
        )
        if v.json_schema_extra
    }
    CHOICES_COMMANDS: List[str] = list(_COMMANDS.keys())
    PATH = "/settings/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Initialize the Constructor."""
        super().__init__(queue)
        for cmd, field in self._COMMANDS.items():
            group = field.get("group")
            if group == SettingGroups.feature_flags:
                self._generate_command(cmd, field, "toggle")
            elif group == SettingGroups.preferences:
                self._generate_command(cmd, field, "set")
        self.update_completer(self.choices_default)

    def print_help(self):
        """Print help."""
        mt = MenuText("settings/")
        mt.add_info("Feature Flags")
        for k, f in self._COMMANDS.items():
            if f.get("group") == SettingGroups.feature_flags:
                mt.add_setting(
                    name=k,
                    status=getattr(session.settings, f["field_name"]),
                    description=f["description"],
                )
        mt.add_raw("\n")
        mt.add_info("Preferences")
        for k, f in self._COMMANDS.items():
            if f.get("group") == SettingGroups.preferences:
                mt.add_cmd(
                    name=k,
                    description=f["description"],
                )
        session.console.print(text=mt.menu_text, menu="Settings")

    def _generate_command(
        self, cmd_name: str, field: dict, action_type: Literal["toggle", "set"]
    ):
        """Generate command call."""

        def _toggle(self, other_args: List[str], field=field) -> None:
            """Toggle setting value."""
            field_name = field["field_name"]
            parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog=field["command"],
                description=field["description"],
                add_help=False,
            )
            ns_parser, _ = self.parse_simple_args(parser, other_args)
            if ns_parser:
                session.settings.set_item(
                    field_name, not getattr(session.settings, field_name)
                )

        def _set(self, other_args: List[str], field=field) -> None:
            """Set preference value."""
            field_name = field["field_name"]
            annotation = field["annotation"]
            command = field["command"]
            type_ = str if get_origin(annotation) is Literal else annotation
            choices = None
            if get_origin(annotation) is Literal:
                choices = annotation.__args__
            elif command == "console_style":
                # To have updated choices for console style
                choices = session.style.available_styles
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
                type=type_,  # type: ignore[arg-type]
                choices=choices,
            )
            ns_parser, _ = self.parse_simple_args(parser, other_args)
            if ns_parser:
                if ns_parser.value:
                    # Console style is applied immediately
                    if command == "console_style":
                        session.style.apply(ns_parser.value)
                    session.settings.set_item(field_name, ns_parser.value)
                    session.console.print(
                        f"[info]Current value:[/info] {getattr(session.settings, field_name)}"
                    )
                elif not other_args:
                    session.console.print(
                        f"[info]Current value:[/info] {getattr(session.settings, field_name)}"
                    )

        action = None
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
