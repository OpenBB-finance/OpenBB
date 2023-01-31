from openbb_terminal.rich_config import console
from openbb_terminal import feature_flags as obbff
from openbb_terminal import config_terminal as cfg
from openbb_terminal import config_plot as cfg_plot
from openbb_terminal.base_helpers import strtobool


def show_diff(configs: dict) -> bool:
    """Show the diff between the local and remote configs.

    Parameters
    ----------
    configs : dict
        The configs.

    Returns
    -------
    bool
        True if there is a diff.
    """
    diff_settings = get_diff_settings(configs)
    if diff_settings:
        console.print("Settings:", style="info")
        console.print("")
        for k, v in diff_settings.items():
            console.print(f"  [menu]{k}[/menu]: {v[0]} -> {v[1]}")

    diff_keys = get_diff_keys(configs)
    if diff_keys:
        console.print("Keys:", style="info")
        for k, v in diff_keys.items():
            console.print(f"  [menu]{k}[/menu]: {v[0]} -> {v[1]}")

    if diff_settings or diff_keys:
        return True
    return False


def get_diff_settings(configs: dict) -> dict:
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
    settings = configs.get("features_settings", {})
    diff = {}
    if settings:
        if settings:
            for k, v in sorted(settings.items()):
                if hasattr(obbff, k):
                    new, old = get_diff(obbff, k, v)
                    if new is not None:
                        diff[k] = (new, old)
                elif hasattr(cfg, k):
                    new, old = get_diff(cfg, k, v)
                    if new is not None:
                        diff[k] = (new, old)
                elif hasattr(cfg_plot, k):
                    new, old = get_diff(cfg_plot, k, v)
                    if new is not None:
                        diff[k] = (new, old)

    return diff


def get_diff_keys(configs: dict) -> dict:
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
    keys = configs.get("features_keys", {})
    diff = {}
    if keys:
        for k, v in sorted(keys.items()):
            new, old = get_diff(cfg, k, v)
            if new is not None:
                diff[k] = (new, old)

    return diff


def get_diff(obj, name, value):
    """Set attribute in object.

    Parameters
    ----------
    obj : object
        The object.
    name : str
        The attribute name.
    value : str
        The attribute value.
    """
    current_value = getattr(obj, name)

    if value.lower() in ["true", "false"]:
        cast_value = strtobool(value)
    elif isinstance(getattr(obj, name), int):
        cast_value = int(value)
    else:
        cast_value = value

    if current_value != cast_value:
        return current_value, cast_value

    return None, None
