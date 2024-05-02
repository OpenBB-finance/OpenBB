"""Rich Module."""

__docformat__ = "numpy"

from typing import Dict, List

import i18n
from openbb import obb

# https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
# https://rich.readthedocs.io/en/latest/highlighting.html#custom-highlighters


RICH_TAGS = [
    "[menu]",
    "[/menu]",
    "[cmds]",
    "[/cmds]",
    "[info]",
    "[/info]",
    "[param]",
    "[/param]",
    "[src]",
    "[/src]",
    "[help]",
    "[/help]",
]

USE_COLOR = True


def get_ordered_providers(command_path: str) -> List:
    """Return the preferred provider for the given command.

    Parameters
    ----------
    command_path: str
        The command to find the provider for. E.g. "/equity/price/historical

    Returns
    -------
    List
        The list of providers for the given command.
    """
    command_reference = obb.reference.get("paths", {}).get(command_path, {})  # type: ignore
    if command_reference:
        providers = list(command_reference["parameters"].keys())
        return [provider for provider in providers if provider != "standard"]
    return []


class MenuText:
    """Create menu text with rich colors to be displayed by CLI."""

    CMD_NAME_LENGTH = 18
    CMD_DESCRIPTION_LENGTH = 65
    CMD_PROVIDERS_LENGTH = 23
    SECTION_SPACING = 4

    def __init__(self, path: str = ""):
        """Initialize menu help.

        Parameters
        ----------
        path : str
            path to the menu that is being created
        column_sources : int
            column width from which to start displaying sources
        """
        self.menu_text = ""
        self.menu_path = path
        self.warnings: List[Dict[str, str]] = []

    def add_raw(self, raw_text: str):
        """Append raw text (no translation) to a menu.

        Parameters
        ----------
        raw_text : str
            raw text to be appended to the menu
        """
        self.menu_text += raw_text

    def add_custom(self, key: str):
        """Append custom text (after translation from key) to a menu.

        Parameters
        ----------
        key : str
            key to get translated text and add to the menu
        """
        self.menu_text += f"{i18n.t(self.menu_path + key)}"

    def add_info(self, key_info: str):
        """Append info text (after translation from key) to a menu.

        Parameters
        ----------
        key_info : str
            key to get translated text and add to the menu as info
        """
        self.menu_text += f"[info]{i18n.t(self.menu_path + key_info)}:[/info]\n"

    def add_param(self, key_param: str, value: str, col_align: int = 0):
        """Append info text (after translation from key) to a menu.

        Parameters
        ----------
        key_param : str
            key to get translated text and add to the menu as parameter
        value : str
            value to display in front of the parameter
        col_align : int
            column alignment for the value. This allows for a better UX experience.
        """
        parameter_translated = i18n.t(self.menu_path + key_param)
        space = (
            (col_align - len(parameter_translated)) * " "
            if col_align > len(parameter_translated)
            else ""
        )
        self.menu_text += f"[param]{parameter_translated}{space}:[/param] {value}\n"

    def _format_cmd_name(self, name: str) -> str:
        """Adjust the length of the command if it is too long.

        Parameters
        ----------
        name : str
            command to be formatted

        Returns
        -------
        str
            formatted command
        """
        if len(name) > self.CMD_NAME_LENGTH:
            new_name = name[
                : self.CMD_NAME_LENGTH
            ]  # Default to trimming to 18 characters

            if "_" in name:
                name_split = name.split("_")

                new_name = (
                    "_".join(name_split[:2]) if len(name_split) > 2 else name_split[0]
                )

                if len(new_name) > self.CMD_NAME_LENGTH:
                    new_name = new_name[: self.CMD_NAME_LENGTH]

            if new_name != name:
                self.warnings.append(
                    {
                        "warning": "Command name too long",
                        "command": name,
                        "trimmed_command": new_name,
                    }
                )
                name = new_name

        return name

    def _format_cmd_description(
        self, name: str, description: str, trim: bool = True
    ) -> str:
        """Handle the command description.

        Parameters
        ----------
        name : str
            command to be adjusted
        description : str
            description of the command
        trim : bool
            If true, the description will be trimmed to the maximum length

        Returns
        -------
        str
            adjusted command description
        """
        if not description:
            description = i18n.t(self.menu_path + name)
            if description == self.menu_path + name:
                description = ""
        return (
            description[: self.CMD_DESCRIPTION_LENGTH - 3] + "..."
            if len(description) > self.CMD_DESCRIPTION_LENGTH and trim
            else description
        )

    def add_cmd(self, name: str, description: str = "", disable: bool = False):
        """Append command text (after translation from key) to a menu.

        Parameters
        ----------
        name : str
            key command to be executed by user. It is also used as a key to get description of command.
        description : str
            description of the command
        disable : bool
            If disable is true, the command line is greyed out.
        """
        formatted_name = self._format_cmd_name(name)
        name_padding = (self.CMD_NAME_LENGTH - len(formatted_name)) * " "
        providers = get_ordered_providers(f"{self.menu_path}{name}")
        formatted_description = self._format_cmd_description(
            formatted_name,
            description,
            bool(providers),
        )
        description_padding = (
            self.CMD_DESCRIPTION_LENGTH - len(formatted_description)
        ) * " "
        spacing = self.SECTION_SPACING * " "
        description_padding = (
            self.CMD_DESCRIPTION_LENGTH - len(formatted_description)
        ) * " "
        cmd = f"{spacing}{formatted_name + name_padding}{spacing}{formatted_description+description_padding}"
        cmd = f"[unvl]{cmd}[/unvl]" if disable else f"[cmds]{cmd}[/cmds]"

        if providers:
            cmd += rf"{spacing}[src]\[{', '.join(providers)}][/src]"

        self.menu_text += cmd + "\n"

    def add_menu(
        self,
        name: str,
        description: str = "",
        disable: bool = False,
    ):
        """Append menu text (after translation from key) to a menu.

        Parameters
        ----------
        name : str
            key menu to be executed by user. It is also used as a key to get description of menu.
        disable : bool
            If disable is true, the menu line is greyed out.
        """
        spacing = (self.CMD_NAME_LENGTH - len(name) + self.SECTION_SPACING) * " "

        if description:
            menu = f"{name}{spacing}{description}"
        else:
            description = i18n.t(self.menu_path + name)
            if description == self.menu_path + name:
                description = ""
            menu = f"{name}{spacing}{description}"

        if disable:
            self.menu_text += f"[unvl]>   {menu}[/unvl]\n"
        else:
            self.menu_text += f"[menu]>   {menu}[/menu]\n"

    def add_setting(self, name: str, status: bool = True):
        """Append menu text (after translation from key) to a menu.

        Parameters
        ----------
        name : str
            key setting to be set by user. It is also used as a key to get description of the setting.
        status : bool
            status of the current setting. If true the line will be green, otherwise red.
        """
        spacing = (self.CMD_NAME_LENGTH - len(name) + self.SECTION_SPACING) * " "
        indentation = self.SECTION_SPACING * " "
        if status:
            self.menu_text += f"[green]{indentation}{name}{spacing}{i18n.t(self.menu_path + name)}[/green]\n"
        else:
            self.menu_text += f"[red]{indentation}{name}{spacing}{i18n.t(self.menu_path + name)}[/red]\n"
