""" Screener View Module """
__docformat__ = "numpy"

import configparser

from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
)
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.screener import finviz_model

PRESETS_PATH = (
    get_current_user().preferences.USER_PRESETS_DIRECTORY / "stocks" / "screener"
)
PRESETS_PATH_DEFAULT = MISCELLANEOUS_DIRECTORY / "stocks" / "screener"
preset_choices = {}

if PRESETS_PATH.exists():
    preset_choices.update(
        {
            filepath.name.strip(".ini"): filepath
            for filepath in PRESETS_PATH.iterdir()
            if filepath.suffix == ".ini"
        }
    )

if PRESETS_PATH_DEFAULT.exists():
    preset_choices.update(
        {
            filepath.name.strip(".ini"): filepath
            for filepath in PRESETS_PATH_DEFAULT.iterdir()
            if filepath.suffix == ".ini"
        }
    )


def display_presets(preset: str):
    if preset:
        preset_filter = configparser.RawConfigParser()
        preset_filter.optionxform = str  # type: ignore
        preset_filter.read(preset_choices[preset])

        filters_headers = ["General", "Descriptive", "Fundamental", "Technical"]

        for i, filter_header in enumerate(filters_headers):
            console.print(f" - {filter_header} -")
            d_filters = {**preset_filter[filter_header]}
            d_filters = {k: v for k, v in d_filters.items() if v}

            if d_filters:
                max_len = len(max(d_filters, key=len))
                for key, value in d_filters.items():
                    console.print(f"{key}{(max_len-len(key))*' '}: {value}")

            if i < len(filters_headers) - 1:
                console.print("\n")

    else:
        console.print("\nCustom Presets:")
        for item, path in preset_choices.items():
            with open(
                path,
                encoding="utf8",
            ) as f:
                description = ""
                for line in f:
                    if line.strip() == "[General]":
                        break
                    description += line.strip()
            console.print(
                f"   {item}{(50-len(item)) * ' '}"
                f"{description.split('Description: ')[1].replace('#', '')}"
            )

        console.print("\nDefault Presets:")
        for signame, sigdesc in finviz_model.d_signals_desc.items():
            console.print(f"   {signame}{(50-len(signame)) * ' '}{sigdesc}")
