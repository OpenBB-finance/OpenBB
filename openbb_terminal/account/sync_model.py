from typing import Union
import requests
from openbb_terminal.base_helpers import strtobool
from openbb_terminal.rich_config import console
from openbb_terminal import feature_flags as obbff
from openbb_terminal.account.statics import BASE_URL, Failure
from openbb_terminal.account import user
from openbb_terminal import config_terminal as cfg


def fetch_user_configs(login_info: dict) -> Union[requests.Response, Failure]:
    """Fetch user configurations."""

    token_type = login_info.get("token_type", "")
    token = login_info.get("access_token", "")

    try:
        response = requests.get(
            url=BASE_URL + "terminal/user",
            headers={"Authorization": f"{token_type.title()} {token}"},
        )
        if response.status_code == 200:
            console.print("[green]\nFetched user configurations.[/green]")
        else:
            console.print("[red]\nFailed to fetch configurations.[/red]")
        return response
    except requests.exceptions.ConnectionError:
        return Failure("[red]\nConnection error.[/red]")
    except Exception:
        return Failure("[red]\nFailed to fetch configurations.[/red]")


def apply_configs(configs: dict):
    """Apply configurations."""
    console.print(configs, style="red")
    if configs:
        settings = configs.get("features_settings", {})
        for k, v in settings.items():
            if hasattr(obbff, k):
                if isinstance(getattr(obbff, k), int):
                    setattr(obbff, k, strtobool(v))
                else:
                    setattr(obbff, k, v)

        keys = configs.get("features_keys", {})
        for k, v in keys.items():
            if hasattr(cfg, k):
                if isinstance(getattr(cfg, k), int):
                    setattr(cfg, k, strtobool(v))
                else:
                    setattr(cfg, k, v)


def patch_user_configs(data: dict) -> Union[requests.Response, Failure]:
    """Patch user configurations."""
    # When available on the server just need to send the changed configs, not all of them.
    # Adapt this to Colin implementation.
    pass


def put_user_configs(data: dict) -> Union[int, Failure]:
    """Push user configurations to the server."""
    try:
        response = requests.put(
            url=BASE_URL + "terminal/user",
            headers={"Authorization": f"{user.TOKEN_TYPE.title()} {user.TOKEN}"},
            json=data,
        )
        if response.status_code == 200:
            console.print("[green]\nPushed user configurations.[/green]")
        else:
            console.print("[red]\nFailed to push configurations.[/red]")
        return response.status_code
    except requests.exceptions.ConnectionError:
        return Failure("[red]\nConnection error.[/red]")
    except Exception:
        return Failure("[red]\nFailed to push configurations.[/red]")
