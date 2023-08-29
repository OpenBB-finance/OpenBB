"""Terminal helper"""
__docformat__ = "numpy"

import hashlib
import logging
import os
import subprocess  # nosec
import sys
import webbrowser

# IMPORTATION STANDARD
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt

# IMPORTATION THIRDPARTY
from packaging import version

# IMPORTATION INTERNAL
import openbb_terminal.core.session.local_model as Local
from openbb_terminal import thought_of_the_day as thought
from openbb_terminal.base_helpers import load_env_files
from openbb_terminal.core.config.paths import HIST_FILE_PATH, SETTINGS_ENV_FILE
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.constants import BackendEnvironment
from openbb_terminal.core.session.current_system import get_current_system
from openbb_terminal.core.session.current_user import (
    get_current_user,
    is_local,
    set_preference,
)
from openbb_terminal.core.session.env_handler import write_to_dotenv
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

# pylint: disable=too-many-statements,no-member,too-many-branches,C0302

try:
    __import__("git")
except ImportError:
    WITH_GIT = False
else:
    WITH_GIT = True
logger = logging.getLogger(__name__)


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

    console.print(
        "[param]The OpenBB Terminal is the result of a strong community building an "
        "investment research platform for everyone, anywhere.[/param]\n"
    )

    console.print(
        "We are always eager to welcome new contributors and you can find our open jobs here:\n"
        "[cmds]https://www.openbb.co/company/careers#open-roles[/cmds]\n"
    )

    console.print(
        "Join us           : [cmds]https://openbb.co/discord[/cmds]\n"
        "Follow us         : [cmds]https://openbb.co/twitter[/cmds]\n"
        "Ask support       : [cmds]https://openbb.co/support[/cmds]\n"
        "Request a feature : [cmds]https://openbb.co/request-a-feature[/cmds]\n"
    )

    console.print(
        "[bold]Fill in our 2-minute survey so we better understand how we can improve the OpenBB Terminal "
        "at [cmds]https://openbb.co/survey[/cmds][/bold]\n"
    )

    console.print(
        "[param]In the meantime access investment research from your chatting platform using the OpenBB Bot[/param]\n"
        "Try it today, for FREE: [cmds]https://openbb.co/products/bot[/cmds]\n"
    )
    logger.info("END")


def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def update_terminal():
    """Updates the terminal by running git pull in the directory.
    Runs poetry install if needed.
    """
    if not WITH_GIT or get_current_system().LOGGING_COMMIT_HASH != "REPLACE_ME":
        console.print("This feature is not available: Git dependencies not installed.")
        return 0

    poetry_hash = sha256sum("poetry.lock")

    completed_process = subprocess.run(  # nosec
        "git pull", shell=True, check=False  # noqa: S607,S602
    )
    if completed_process.returncode != 0:
        return completed_process.returncode

    new_poetry_hash = sha256sum("poetry.lock")

    if poetry_hash == new_poetry_hash:
        console.print("Great, seems like poetry hasn't been updated!")
        return completed_process.returncode
    console.print(
        "Seems like more modules have been added, grab a coke, this may take a while."
    )

    completed_process = subprocess.run(  # nosec
        "poetry install", shell=True, check=False  # noqa: S607,S602
    )
    if completed_process.returncode != 0:
        return completed_process.returncode

    return 0


def open_openbb_documentation(
    path,
    url="https://my.openbb.co/app/terminal",
    command=None,
    arg_type="",
):
    """Opens the documentation page based on your current location within the terminal. Make exceptions for menus
    that are considered 'common' by adjusting the path accordingly."""
    if path == "/" and command is None:
        path = "/usage?path=/usage/basics"
        command = ""
    elif "keys" in path:
        path = "/usage?path=/usage/guides/api-keys"
        command = ""
    elif "settings" in path:
        path = "/usage?path=/usage/guides/customizing-the-terminal"
        command = ""
    elif "featflags" in path:
        path = "/usage?path=/usage/guides/customizing-the-terminal#using-the-feature-flags-menu"
        command = ""
    elif "sources" in path:
        path = "/usage?path=/usage/guides/changing-sources"
        command = ""
    elif "account" in path:
        path = "/usage?path=/usage/guides/basics"
        command = ""
    elif arg_type == "command":  # user passed a command name
        if command in ["settings", "featflags"]:
            path = "/usage?path=/usage/guides/customizing-the-terminal"
            command = ""
        else:
            path = f"/commands?path={path}"
    elif arg_type == "menu":  # user passed a menu name
        if command in ["ta", "ba", "qa"]:
            menu = path.split("/")[-2]
            path = f"/usage?path=/usage/intros/common/{menu}"
        elif command == "forecast":
            command = ""
            path = "/usage?path=/usage/intros/forecast"
        else:
            path = f"/usage?path=/usage/intros/{path}"
    else:  # user didn't pass argument and is in a menu
        menu = path.split("/")[-2]
        path = (
            f"/usage?path=/usage/intros/common/{menu}"
            if menu in ["ta", "ba", "qa"]
            else f"/usage?path=/usage/intros/{path}"
        )

    if command:
        if command == "keys":
            path = "/usage?path=/usage/guides/api-keys"
            command = ""
        elif "settings" in path or "featflags" in path:
            path = "/usage?path=/usage/guides/customizing-the-terminal"
            command = ""
        elif "sources" in path:
            path = "/usage?path=/usage/guides/changing-sources"
            command = ""
        elif command in ["record", "stop", "exe"]:
            path = "/usage?path=/usage/guides/scripts-and-routines"
            command = ""
        elif command == "sources":
            path = "/usage?path=/usage/guides/changing-sources"
            command = ""
        elif command in [
            "intro",
            "about",
            "support",
            "survey",
            "update",
            "wiki",
            "news",
            "account",
        ]:
            path = "/usage"
            command = ""
        elif command in ["ta", "ba", "qa"]:
            path = f"/usage?path=/usage/intros/common/{command}"
            command = ""

        path += command

    full_url = f"{url}{path.replace('//', '/')}"

    if full_url[-1] == "/":
        full_url = full_url[:-1]

    webbrowser.open(full_url)


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
        logger.info(e)


def is_auth_enabled() -> bool:
    """Tell whether or not authentication is enabled.

    Returns
    -------
    bool
        If authentication is enabled
    """
    # TODO: This function is a temporary way to block authentication
    return get_current_system().ENABLE_AUTHENTICATION


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
        logger.exception("Exception: %s", str(e))
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

    if r is not None and r.status_code == 200:
        latest_tag_name = r.json()["tag_name"]
        latest_version = version.parse(latest_tag_name)
        current_version = version.parse(get_current_system().VERSION)

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
    console.print(f"\nWelcome to OpenBB Terminal v{get_current_system().VERSION}")

    if get_current_user().preferences.ENABLE_THOUGHTS_DAY:
        console.print("---------------------------------")
        try:
            thought.get_thought_of_the_day()
        except Exception as e:
            logger.exception("Exception: %s", str(e))
            console.print(e)


def reset(queue: Optional[List[str]] = None):
    """Resets the terminal.  Allows for checking code without quitting"""
    console.print("resetting...")
    logger.info("resetting")
    plt.close("all")
    plots_backend().close(reset=True)
    load_env_files()
    debug = get_current_system().DEBUG_MODE
    dev = get_current_system().DEV_BACKEND

    try:
        # save the current user
        user_profile = get_current_user().profile
        session: Dict[str, Any] = {
            "access_token": user_profile.token,
            "token_type": user_profile.token_type,
            "uuid": user_profile.uuid,
            "username": user_profile.username,
            "remember": user_profile.remember,
        }

        # remove the hub routines
        if not is_local():
            Local.remove(get_current_user().preferences.USER_ROUTINES_DIRECTORY / "hub")
            if not get_current_user().profile.remember:
                Local.remove(HIST_FILE_PATH)

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

            session_controller.main(session, queue=queue_list)

    except Exception as e:
        logger.exception("Exception: %s", str(e))
        console.print("Unfortunately, resetting wasn't possible!\n")
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
        set_preference("PREVIOUS_USE", True)
        write_to_dotenv("OPENBB_PREVIOUS_USE", "True")
        return True
    return False
