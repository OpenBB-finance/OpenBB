from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd

from openbb_terminal import (
    config_plot as cfg_plot,
    config_terminal as cfg,
    feature_flags as obbff,
)
from openbb_terminal.base_helpers import strtobool
from openbb_terminal.core.config import paths
from openbb_terminal.rich_config import console


def get_diff(configs: dict) -> dict:
    """Show the diff between the local and remote configs.

    Parameters
    ----------
    configs : dict
        The configs.

    Returns
    -------
    dict
        The diff.
    """
    SETTINGS = "features_settings"
    KEYS = "features_keys"
    configs_diff: Dict[str, Dict[str, Any]] = {SETTINGS: {}, KEYS: {}}

    diff_settings = get_diff_settings(configs.get(SETTINGS, {}))
    if diff_settings:
        console.print("[info]Settings:[/info]")
        for k, v in diff_settings.items():
            configs_diff[SETTINGS][k] = v[1]
            console.print(f"  [menu]{k}[/menu]: {v[0]} -> {v[1]}")

    diff_keys = get_diff_keys(configs.get(KEYS, {}))
    if diff_keys:
        console.print("[info]Keys:[/info]")
        for k, v in diff_keys.items():
            configs_diff[KEYS][k] = v[1]
            console.print(f"  [menu]{k}[/menu]: {v[0]} -> {v[1]}")

    if not configs_diff[SETTINGS]:
        configs_diff.pop(SETTINGS)

    if not configs_diff[KEYS]:
        configs_diff.pop(KEYS)

    return configs_diff


def get_diff_settings(settings: dict) -> dict:
    """Get the diff between the local and remote settings.

    Parameters
    ----------
    configs : dict
        The configs.

    Returns
    -------
    dict
        The diff.
    """
    diff = {}
    if settings:
        for k, v in sorted(settings.items()):
            if hasattr(obbff, k):
                old, new = get_var_diff(obbff, k, v)
                if new is not None:
                    diff[k] = (old, new)
            elif hasattr(cfg, k):
                old, new = get_var_diff(cfg, k, v)
                if new is not None:
                    diff[k] = (old, new)
            elif hasattr(cfg_plot, k):
                old, new = get_var_diff(cfg_plot, k, v)
                if new is not None:
                    diff[k] = (old, new)
            elif hasattr(paths, k):
                old, new = get_var_diff(paths, k, v)
                if new is not None:
                    diff[k] = (old, new)

    return diff


def get_diff_keys(keys: dict) -> dict:
    """Get the diff between the local and remote keys.

    Parameters
    ----------
    configs : dict
        The configs.

    Returns
    -------
    dict
        The diff.
    """
    diff = {}
    if keys:
        for k, v in sorted(keys.items()):
            if hasattr(cfg, k):
                old, new = get_var_diff(cfg, k, v)
                if new is not None:
                    diff[k] = (old, new)

    return diff


def get_var_diff(obj, name, value) -> Tuple[Any, Any]:
    """Set attribute in object.

    Parameters
    ----------
    obj : object
        The object.
    name : str
        The attribute name.
    value : str
        The attribute value.

    Returns
    -------
    Tuple[Any, Any]
        The old and new values.
    """
    current_value = getattr(obj, name)

    if str(value).lower() in ["true", "false"]:
        cast_value = strtobool(value)
    elif isinstance(getattr(obj, name), int):
        cast_value = int(value)
    elif isinstance(getattr(obj, name), float):
        cast_value = float(value)
    elif isinstance(getattr(obj, name), Path):
        cast_value = Path(value)
    else:
        cast_value = value

    if current_value != cast_value:
        return current_value, cast_value

    return None, None


def get_routines_info(response) -> Tuple[pd.DataFrame, int, int]:
    """Get the routines list.

    Parameters
    ----------
    response : requests.Response
        The response.

    Returns
    -------
    Tuple[pd.DataFrame, int, int]
        The routines list, the current page and the total number of pages.
    """
    df = pd.DataFrame()
    page = 1
    pages = 1
    if response and response.status_code == 200:
        data = response.json()
        page = data.get("page", 1)
        pages = data.get("pages", 1)
        items = data.get("items", [])
        if items:
            df = pd.DataFrame(items)
            df.index = np.arange(1, len(df) + 1)

    return df, page, pages
