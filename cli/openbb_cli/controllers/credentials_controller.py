"""Credentials Controller Module."""

import argparse
from functools import partial, update_wrapper
from types import MethodType
from typing import Any, cast

from openbb import obb as _obb_container
from pydantic import SecretStr

obb = cast(Any, _obb_container)

from openbb_cli.controllers.base_controller import BaseController
from openbb_cli.session import Session

session = Session()


def _credential_status(raw: object) -> str:
    """Return a display string for a credential value."""
    if isinstance(raw, SecretStr):
        secret = raw.get_secret_value()
        if secret:
            return f"[green]Set ({secret[:4]}****)[/green]"
    return "[red]Not set[/red]"


class CredentialsController(BaseController):
    """Credentials Controller class."""

    PATH = "/user/credentials/"
    CHOICES_GENERATION = True

    _CRED_COMMANDS: dict[str, dict[str, Any]] = {}
    for _fname, _finfo in sorted(obb.user.credentials.__class__.model_fields.items()):
        _provider = _finfo.description or ""
        if _provider == _fname:
            _provider = (
                _fname.rsplit("_api_key", 1)[0]
                .rsplit("_token", 1)[0]
                .rsplit("_key", 1)[0]
            )
        _CRED_COMMANDS[_fname] = {
            "command": _fname,
            "field_name": _fname,
            "provider": _provider,
        }

    CHOICES_COMMANDS: list[str] = list(_CRED_COMMANDS.keys())
    CHOICES_MENUS: list[str] = []

    def __init__(self, queue: list[str] | None = None):
        """Initialize the Constructor."""
        super().__init__(queue)
        for cmd, field in self._CRED_COMMANDS.items():
            self._generate_credential_command(cmd, field)
        self.update_completer(self.choices_default)

    def print_help(self):
        """Print help."""
        spacing = 4
        max_name = max((len(c) for c in self._CRED_COMMANDS), default=20)
        col_width = max_name + spacing

        lines: list[str] = []
        lines.append("[info]Session-level credentials (not persisted):[/info]")
        lines.append("[info]Use: <credential> -v <value>[/info]")
        lines.append("")

        for cmd, f in self._CRED_COMMANDS.items():
            raw = getattr(obb.user.credentials, f["field_name"], None)
            status = _credential_status(raw)
            provider = f["provider"]
            pad = " " * (col_width - len(cmd))
            lines.append(
                f"[cmds]{' ' * spacing}{cmd}{pad}{provider:<20s}[/cmds] {status}"
            )

        menu_text = "\n".join(lines) + "\n"
        session.console.print(text=menu_text, menu="Credentials")

    def _generate_credential_command(self, cmd_name: str, field: dict):
        """Generate a set command bound to obb.user.credentials."""

        def _set_credential(self, other_args: list[str], field=field) -> None:
            """Set a credential value."""
            field_name = field["field_name"]
            parser = argparse.ArgumentParser(
                formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                prog=field["command"],
                description=f"Set {field_name} credential",
                add_help=False,
            )
            parser.add_argument(
                "-v",
                "--value",
                dest="value",
                action="store",
                required=False,
                type=str,
            )
            ns_parser, _ = self.parse_simple_args(parser, other_args)
            if ns_parser:
                if ns_parser.value is not None:
                    setattr(obb.user.credentials, field_name, ns_parser.value)
                    session.console.print(
                        f"[info]{field_name}:[/info] [green]Set[/green]"
                    )
                elif not other_args:
                    raw = getattr(obb.user.credentials, field_name, None)
                    status = _credential_status(raw)
                    session.console.print(f"[info]{field_name}:[/info] {status}")

        bound_method = update_wrapper(
            wrapper=partial(MethodType(_set_credential, self), field=field),
            wrapped=_set_credential,
        )
        setattr(self, f"call_{cmd_name}", bound_method)
