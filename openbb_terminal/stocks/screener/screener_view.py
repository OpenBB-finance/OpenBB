""" Screener View Module """
__docformat__ = "numpy"

import os
from os import path
import configparser

from openbb_terminal.rich_config import console
from openbb_terminal.stocks.screener import finviz_model

presets_path = path.join(path.abspath(path.dirname(__file__)), "presets/")

preset_choices = [
    preset.split(".")[0] for preset in os.listdir(presets_path) if preset[-4:] == ".ini"
]


def display_presets(preset: str = ""):
    if preset:
        preset_filter = configparser.RawConfigParser()
        preset_filter.optionxform = str  # type: ignore
        preset_filter.read(presets_path + preset + ".ini")

        filters_headers = ["General", "Descriptive", "Fundamental", "Technical"]

        console.print("")
        for filter_header in filters_headers:
            console.print(f" - {filter_header} -")
            d_filters = {**preset_filter[filter_header]}
            d_filters = {k: v for k, v in d_filters.items() if v}
            if d_filters:
                max_len = len(max(d_filters, key=len))
                for key, value in d_filters.items():
                    console.print(f"{key}{(max_len-len(key))*' '}: {value}")
            console.print("")

    else:
        console.print("\nCustom Presets:")
        for item in preset_choices:
            with open(
                presets_path + item + ".ini",
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
