"""Terminal helper"""

__docformat__ = "numpy"

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional

from packaging import version

from openbb_terminal.core.config.paths import SETTINGS_ENV_FILE
from openbb_terminal.core.session.constants import BackendEnvironment
from openbb_terminal.core.session.current_settings import (
    get_current_settings,
    set_settings,
)
from openbb_terminal.core.session.current_user import (
    get_platform_user,
    is_local,
)
from openbb_terminal.core.session.env_handler import load_env_files, write_to_dotenv
from openbb_terminal.core.session.utils import remove
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

# pylint: disable=too-many-statements,no-member,too-many-branches,C0302


def print_goodbye():
    """Prints a goodbye message when quitting the terminal"""
    # LEGACY GOODBYE MESSAGES - You'll live in our hearts forever.
    # "An informed ape, is a strong ape."
    # "Remember that stonks only go up."
    # "Diamond hands."
    # "Apes together strong."
    # "This is our way."
    # "Keep the spacesuit ape, we haven't reached the moon yet."
    # "I am not a cat. I'm an ape."
    # "We like the terminal."
    # "...when offered a flight to the moon, nobody asks about what seat."

    text = """
[param]Thank you for using the OpenBB Platform CLI and being part of this journey.[/param]

We hope you'll find the new CLI as valuable as this. To stay tuned, sign up for our newsletter: [cmds]https://openbb.co/newsletter.[/]

In the meantime, check out our other products:

[bold]OpenBB Terminal Pro[/]: [cmds]https://openbb.co/products/pro[/cmds]
[bold]OpenBB Platform:[/]     [cmds]https://openbb.co/products/platform[/cmds]
[bold]OpenBB Bot[/]:          [cmds]https://openbb.co/products/bot[/cmds]
    """
    console.print(text)


def hide_splashscreen():
    """Hide the splashscreen on Windows bundles.

    `pyi_splash` is a PyInstaller "fake-package" that's used to communicate
    with the splashscreen on Windows.
    Sending the `close` signal to the splash screen is required.
    The splash screen remains open until this function is called or the Python
    program is terminated.
    """
    try:
        import pyi_splash  # type: ignore  # pylint: disable=import-outside-toplevel

        pyi_splash.update_text("Terminal Loaded!")
        pyi_splash.close()
    except Exception as e:
        console.print(f"Error: Unable to hide splashscreen: {e}")


def print_guest_block_msg():
    """Block guest users from using the terminal."""
    if is_local():
        console.print(
            "[info]You are currently logged as a guest.[/info]\n"
            "[info]Login to use this feature.[/info]\n\n"
            "[info]If you don't have an account, you can create one here: [/info]"
            f"[cmds]{BackendEnvironment.HUB_URL + 'register'}\n[/cmds]"
        )


def is_installer() -> bool:
    """Tell whether or not it is a packaged version (Windows or Mac installer"""
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def bootup():
    if sys.platform == "win32":
        # Enable VT100 Escape Sequence for WINDOWS 10 Ver. 1607
        os.system("")  # nosec # noqa: S605,S607
        # Hide splashscreen loader of the packaged app
        if is_installer():
            hide_splashscreen()

    try:
        if os.name == "nt":
            # pylint: disable=E1101
            sys.stdin.reconfigure(encoding="utf-8")
            # pylint: disable=E1101
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception as e:
        console.print(e, "\n")


def check_for_updates() -> None:
    """Check if the latest version is running.

    Checks github for the latest release version and compares it to cfg.VERSION.
    """
    # The commit has was commented out because the terminal was crashing due to git import for multiple users
    # ({str(git.Repo('.').head.commit)[:7]})
    try:
        r = request(
            "https://api.github.com/repos/openbb-finance/openbbterminal/releases/latest"
        )
    except Exception:
        r = None

    if r and r.status_code == 200:
        latest_tag_name = r.json()["tag_name"]
        latest_version = version.parse(latest_tag_name)
        current_version = version.parse(get_current_settings().VERSION)

        if check_valid_versions(latest_version, current_version):
            if current_version == latest_version:
                console.print("[green]You are using the latest stable version[/green]")
            else:
                console.print(
                    "[yellow]You are not using the latest stable version[/yellow]"
                )
                if current_version < latest_version:
                    console.print(
                        "[yellow]Check for updates at https://my.openbb.co/app/terminal/download[/yellow]"
                    )

                else:
                    console.print(
                        "[yellow]You are using an unreleased version[/yellow]"
                    )

        else:
            console.print("[red]You are using an unrecognized version.[/red]")
    else:
        console.print(
            "[yellow]Unable to check for updates... "
            + "Check your internet connection and try again...[/yellow]"
        )
    console.print("\n")


def check_valid_versions(
    latest_version: version.Version,
    current_version: version.Version,
) -> bool:
    if (
        not latest_version
        or not current_version
        or not isinstance(latest_version, version.Version)
        or not isinstance(current_version, version.Version)
    ):
        return False
    return True


def welcome_message():
    """Print the welcome message

    Prints first welcome message, help and a notification if updates are available.
    """
    console.print(f"\nWelcome to OpenBB Platform CLI v{get_current_settings().VERSION}")


def reset(queue: Optional[List[str]] = None):
    """Resets the CLI.  Allows for checking code without quitting"""
    console.print("resetting...")
    load_env_files()
    debug = get_current_settings().DEBUG_MODE
    dev = get_current_settings().DEV_BACKEND

    try:
        # remove the hub routines
        if not is_local():
            user = get_platform_user()
            remove(Path(user.preferences.export_directory, "routines", "hub"))

            # if not get_current_user().profile.remember:
            #     Local.remove(HIST_FILE_PATH)

        # we clear all openbb_terminal modules from sys.modules
        for module in list(sys.modules.keys()):
            parts = module.split(".")
            if parts[0] == "openbb_terminal":
                del sys.modules[module]

        queue_list = ["/".join(queue) if len(queue) > 0 else ""]  # type: ignore
        # pylint: disable=import-outside-toplevel
        # we run the terminal again
        if is_local():
            from openbb_terminal.terminal_controller import main

            main(debug, dev, queue_list, module="")  # type: ignore
        else:
            from openbb_terminal.core.session import session_controller

            session_controller.launch_terminal(queue=queue_list)

    except Exception as e:
        console.print(f"Unfortunately, resetting wasn't possible: {e}\n")
        print_goodbye()


@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


def first_time_user() -> bool:
    """Whether a user is a first time user. A first time user is someone with an empty .env file.
    If this is true, it also adds an env variable to make sure this does not run again.

    Returns
    -------
    bool
        Whether or not the user is a first time user
    """
    if SETTINGS_ENV_FILE.stat().st_size == 0:
        set_settings("PREVIOUS_USE", True)
        write_to_dotenv("OPENBB_PREVIOUS_USE", "True")
        return True
    return False
