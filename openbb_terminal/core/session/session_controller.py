from typing import Dict, List, Optional, Tuple

from prompt_toolkit import PromptSession

import openbb_terminal.core.session.local_model as Local
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.constants import BackendEnvironment
from openbb_terminal.core.session.current_system import (
    get_current_system,
    set_system_variable,
)
from openbb_terminal.core.session.session_model import (
    LoginStatus,
    create_session,
    login,
)
from openbb_terminal.rich_config import console
from openbb_terminal.terminal_helper import bootup, is_installer


def display_welcome_message(links: bool = True) -> None:
    """Display welcome message"""
    with open(PACKAGE_DIRECTORY / "core" / "session" / "banner.txt") as f:
        console.print(f"[menu]{f.read()}[/menu]\n")
        if links:
            console.print(
                f"Register : [cmds]{BackendEnvironment.HUB_URL + 'register'}[/cmds]"
            )
            console.print(
                f"Support  : [cmds]{BackendEnvironment.HUB_URL + 'app/terminal/support'}[/cmds]"
            )


def get_user_input() -> Tuple[str, str, bool]:
    """Get user input

    Returns
    -------
    Tuple[str, str, bool]
        The user email, password and save login option.
    """

    msg = "\nPlease enter your credentials"

    if not is_installer():
        msg += " or press <ENTER> for guest mode:"
    else:
        msg += ":"

    console.print("[info]" + msg + "[/info]")

    s: PromptSession = PromptSession()

    email = s.prompt(
        message="> Email/Username: ",
    )
    if not email:
        return "", "", False

    password = s.prompt(
        message="> Password: ",
        is_password=True,
    )
    remember = (
        s.prompt(message="> Remember me? (y/n): ", is_password=False).lower() == "y"
    )

    return email, password, remember


def pywry_login(welcome: bool = True):
    """Login using PyWry window and launch terminal if login is successful.

    Parameters
    ----------
    welcome : bool, optional
        Display welcome message, by default True
    """
    bootup()

    plots_backend().start(get_current_system().DEBUG_MODE)
    if plots_backend().isatty:
        if welcome:
            display_welcome_message(False)
        response = plots_backend().call_hub() or None
    else:
        return prompt_cli(welcome)

    if response is None:
        if is_installer():
            return prompt_cli(welcome=False)
        return launch_terminal()

    if isinstance(response, dict) and response:
        console.print("\n[info]Logging in... Please wait.[/info]\n")
        response["token_type"] = "bearer"  # noqa: S105

        for r_key, new_key in zip(
            ["status", "accessToken", "primaryUsage"],
            ["information_complete", "access_token", "primary_usage"],
        ):
            response[new_key] = response.pop(r_key, None)

        response["primary_usage"] = response.get("primary_usage", None) or "personal"

        if remember := (
            response.get("remember", False) or response.get("is_oauth", False)
        ):
            response["remember"] = remember
            Local.save_session(response)

        return login_and_launch(response, remember)

    return pywry_login(welcome=False)


def prompt_cli(welcome: bool = True):
    """Prompt and launch terminal if login is successful.

    Parameters
    ----------
    welcome : bool, optional
        Display welcome message, by default True
    """
    bootup()

    if welcome:
        display_welcome_message()

    while True:
        email, password, remember = get_user_input()
        if not email:
            return prompt_cli(welcome=False) if is_installer() else launch_terminal()

        session = create_session(email, password, remember)
        if isinstance(session, dict) and session:
            return login_and_launch(session, remember)


# pylint: disable=inconsistent-return-statements
def launch_terminal(
    debug: bool = False, dev: bool = False, queue: Optional[List[str]] = None
):
    """Launch terminal"""
    # pylint: disable=import-outside-toplevel
    from openbb_terminal import terminal_controller

    if queue:
        return terminal_controller.main(debug, dev, queue, module="")

    terminal_controller.parse_args_and_run()


def login_and_launch(session: dict, remember: bool = False):
    """Login and launch terminal.

    Parameters
    ----------
    session : dict
        The session info.
    remember : bool, optional
        Remember the session, by default False
    """
    status = login(session, remember)
    if status in [LoginStatus.SUCCESS, LoginStatus.NO_RESPONSE]:
        launch_terminal()
    elif status == LoginStatus.FAILED:
        pywry_login(welcome=False)
    else:
        pywry_login(welcome=True)


def main(
    session: Optional[Dict] = None,
    welcome: bool = True,
    prompt: bool = True,
    queue: Optional[List[str]] = None,
    dev: bool = False,
):
    """Main function"""
    if dev:
        set_system_variable("DEV_BACKEND", True)
        BackendEnvironment.BASE_URL = "https://payments.openbb.dev/"
        BackendEnvironment.HUB_URL = "https://my.openbb.dev/"

    local_session = Local.get_session() if session is None else session

    if not local_session and not prompt:
        launch_terminal(queue=queue)
    elif local_session:
        login_and_launch(session=local_session, remember=True)
    else:
        pywry_login(welcome)


if __name__ == "__main__":
    main()
