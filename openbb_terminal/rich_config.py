"""Rich Module"""
__docformat__ = "numpy"

import json
import os
from pathlib import Path
from typing import Iterable, Optional, Tuple, Union

import i18n
from rich import panel
from rich.console import Console, Theme
from rich.progress import track
from rich.text import Text

from openbb_terminal import (
    config_terminal as cfg,
    feature_flags as obbff,
)
from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY

# pylint: disable=no-member,c-extension-no-member


# https://rich.readthedocs.io/en/stable/appendix/colors.html#appendix-colors
# https://rich.readthedocs.io/en/latest/highlighting.html#custom-highlighters

CUSTOM_THEME = Theme(cfg.theme.console_style)

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


def translate(key: str):
    return i18n.t(key)


def no_panel(renderable, *args, **kwargs):  # pylint: disable=unused-argument
    return renderable


def get_ordered_list_sources(command_path: str):
    """
    Returns the preferred source for the given command. If a value is not available for the specific
    command, returns the most specific source, eventually returning the overall default source.

    Parameters
    ----------
    command_path: str
        The command to find the source for. Example would be "stocks/load" to return the value
        for stocks.load first, then stocks, then the default value.

    Returns
    -------
    list:
        list of sources
    """
    try:
        # Loading in both source files: default sources and user sources
        default_data_source = MISCELLANEOUS_DIRECTORY / "data_sources_default.json"
        user_data_source = Path(obbff.PREFERRED_DATA_SOURCE_FILE)

        # Opening default sources file from the repository root
        with open(str(default_data_source)) as json_file:
            json_doc = json.load(json_file)

        # If the user has added sources to their own sources file in OpenBBUserData, then use that
        if (
            not os.getenv("TEST_MODE")
            and user_data_source.exists()
            and user_data_source.stat().st_size > 0
        ):
            with open(str(user_data_source)) as json_file:
                json_doc = json.load(json_file)

        # We are going to iterate through each command as if it is broken up by period characters (.)
        path_objects = command_path.split("/")[1:]

        # Start iterating through the top-level JSON doc to start
        deepest_level = json_doc

        # If we still have entries in path_objects, continue to go deeper
        while len(path_objects) > 0:
            # Is this path object in the JSON doc? If so, go into that for our next iteration.
            if path_objects[0] in deepest_level:
                # We found the element, so go one level deeper
                deepest_level = deepest_level[path_objects[0]]

            else:
                # If we have not find the `load` on the deepest level it means we may be in a sub-menu
                # and we can use the load from the Base class
                if path_objects[0] == "load":
                    # Get the context associated with the sub-menu (e.g. stocks, crypto, ...)
                    context = command_path.split("/")[1]

                    # Grab the load source from that context if it exists, otherwise throws an error
                    if context in json_doc and "load" in json_doc[context]:
                        return json_doc[context]["load"]

                # We didn't find the next level, so flag that that command default source is missing
                # Which means that there aren't more than 1 source and therefore no selection is necessary
                return []

            # Go one level deeper into the path
            path_objects = path_objects[1:]

        # We got through all values, so return this as the final value
        return deepest_level

    except Exception as e:
        console.print(
            f"[red]Failed to load preferred source from file: "
            f"{obbff.PREFERRED_DATA_SOURCE_FILE}[/red]"
        )
        console.print(f"[red]{e}[/red]")
        return None


class MenuText:
    """Create menu text with rich colors to be displayed by terminal"""

    def __init__(self, path: str = "", column_sources: int = 100):
        """Initialize menu help

        Parameters
        ----------
        path : str
            path to the menu that is being created
        column_sources : int
            column width from which to start displaying sources
        """
        self.menu_text = ""
        self.menu_path = path
        self.col_src = column_sources

    def add_raw(self, raw_text: str):
        """Append raw text (no translation) to a menu

        Parameters
        ----------
        raw_text : str
            raw text to be appended to the menu
        """
        self.menu_text += raw_text

    def add_custom(self, key: str):
        """Append custom text (after translation from key) to a menu

        Parameters
        ----------
        key : str
            key to get translated text and add to the menu
        """
        self.menu_text += f"{i18n.t(self.menu_path + key)}"

    def add_info(self, key_info: str):
        """Append info text (after translation from key) to a menu

        Parameters
        ----------
        key_info : str
            key to get translated text and add to the menu as info
        """
        self.menu_text += f"[info]{i18n.t(self.menu_path + key_info)}:[/info]\n"

    def add_param(self, key_param: str, value: str, col_align: int = 0):
        """Append info text (after translation from key) to a menu

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

    def add_cmd(self, key_command: str, condition: bool = True):
        """Append command text (after translation from key) to a menu

        Parameters
        ----------
        key_command : str
            key command to be executed by user. It is also used as a key to get description of command.
        condition : bool
            condition in which command is available to user. I.e. displays command and description.
            If condition is false, the command line is greyed out.
        """
        spacing = (23 - (len(key_command) + 4)) * " "
        if condition:
            cmd = f"[cmds]    {key_command}{spacing}{i18n.t(self.menu_path + key_command)}[/cmds]"
        else:
            cmd = f"[unvl]    {key_command}{spacing}{i18n.t(self.menu_path + key_command)}[/unvl]"

        sources = get_ordered_list_sources(f"/{self.menu_path}{key_command}")

        if sources:
            space = (self.col_src - len(cmd)) * " " if self.col_src > len(cmd) else " "
            cmd += f"{space}[src][{', '.join(sources)}][/src]"

        self.menu_text += cmd + "\n"

    def add_menu(self, key_menu: str, condition: Optional[Union[bool, str]] = True):
        """Append menu text (after translation from key) to a menu

        Parameters
        ----------
        key_menu : str
            key menu to be executed by user. It is also used as a key to get description of menu.
        condition : bool
            condition in which menu is available to user. I.e. displays menu and description.
            If condition is false, the menu line is greyed out.
        """
        spacing = (23 - (len(key_menu) + 4)) * " "
        if condition:
            self.menu_text += f"[menu]>   {key_menu}{spacing}{i18n.t(self.menu_path + key_menu)}[/menu]\n"
        else:
            self.menu_text += f"[unvl]>   {key_menu}{spacing}{i18n.t(self.menu_path + key_menu)}[/unvl]\n"

    def add_setting(self, key_setting: str, status: bool = True):
        """Append menu text (after translation from key) to a menu

        Parameters
        ----------
        key_setting : str
            key setting to be set by user. It is also used as a key to get description of the setting.
        status : bool
            status of the current setting. If true the line will be green, otherwise red.
        """
        spacing = (23 - (len(key_setting) + 4)) * " "
        if status:
            self.menu_text += f"[green]    {key_setting}{spacing}{i18n.t(self.menu_path + key_setting)}[/green]\n"
        else:
            self.menu_text += f"[red]    {key_setting}{spacing}{i18n.t(self.menu_path + key_setting)}[/red]\n"


class ConsoleAndPanel:
    """Create a rich console to wrap the console print with a Panel"""

    def __init__(self):
        self.console = Console(theme=CUSTOM_THEME, highlight=False, soft_wrap=True)
        self.menu_text = ""
        self.menu_path = ""

    def capture(self):
        return self.console.capture()

    @staticmethod
    def filter_rich_tags(text):
        for val in RICH_TAGS:
            text = text.replace(val, "")

        return text

    @staticmethod
    def blend_text(
        message: str, color1: Tuple[int, int, int], color2: Tuple[int, int, int]
    ) -> Text:
        """Blend text from one color to another."""
        text = Text(message)
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        dr = r2 - r1
        dg = g2 - g1
        db = b2 - b1
        size = len(text) + 5
        for index in range(size):
            blend = index / size
            color = f"#{int(r1 + dr * blend):02X}{int(g1 + dg * blend):02X}{int(b1 + db * blend):02X}"
            text.stylize(color, index, index + 1)
        return text

    def print(self, *args, **kwargs):
        if kwargs and "text" in list(kwargs) and "menu" in list(kwargs):
            if not os.getenv("TEST_MODE"):
                if obbff.ENABLE_RICH_PANEL:
                    version = f"[param]OpenBB Terminal v{obbff.VERSION}[/param] (https://openbb.co)"
                    self.console.print(
                        panel.Panel(
                            "\n" + kwargs["text"],
                            title=kwargs["menu"],
                            subtitle_align="right",
                            subtitle=version,
                        )
                    )

                else:
                    self.console.print(kwargs["text"])
            else:
                print(self.filter_rich_tags(kwargs["text"]))
        else:
            if not os.getenv("TEST_MODE"):
                self.console.print(*args, **kwargs)
            else:
                print(*args, **kwargs)

    def input(self, *args, **kwargs):
        self.print(*args, **kwargs, end="")
        return input()


console = ConsoleAndPanel()


def optional_rich_track(
    inputs: Iterable,
    suppress_output: bool = False,
    desc: str = "",
    total: Optional[int] = None,
):
    """Generate a rich track progress bar if desired

    Parameters
    ----------
    inputs : Iterable
        The items to be looped through
    suppress_output : bool, optional
        Flag to suppress the output, by default False
    desc : str, optional
        String to describe the progress bar, by default ""
    total : Optional[int], optional
        Total number of items to be looped through, by default None
    """
    if suppress_output:
        return inputs
    return track(inputs, description=desc, total=total)
