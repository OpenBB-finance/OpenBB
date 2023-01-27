from openbb_terminal.rich_config import console


def show_diff(configs: dict):
    """Show the diff between the local and remote configs.

    Parameters
    ----------
    configs : dict
        The configs.
    """
    if configs:
        settings = configs.get("features_settings", {})
        keys = configs.get("features_keys", {})

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
