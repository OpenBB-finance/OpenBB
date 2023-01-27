from openbb_terminal.rich_config import console


def show_diff(configs: dict) -> bool:
    """Show the diff between the local and remote configs.

    Parameters
    ----------
    configs : dict
        The configs.

    Returns
    -------
    bool
        True if configs are found, False otherwise.
    """
    settings = configs.get("features_settings", {})
    keys = configs.get("features_keys", {})

    if settings or keys:
        if settings:
            console.print("Settings:", style="info")
            for k, v in sorted(settings.items()):
                console.print(f"[menu]{k}[/menu]: {v}")

        if keys:
            if settings:
                console.print("")

            console.print("Keys:", style="info")
            for k, v in sorted(keys.items()):
                console.print(f"[menu]{k}[/menu]: {v}")

        return True
    console.print("No configurations found.", style="info")
    return False
