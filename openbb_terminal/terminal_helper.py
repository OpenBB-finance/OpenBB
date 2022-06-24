"""Terminal helper"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
from contextlib import contextmanager
import hashlib
import logging
import os
import subprocess  # nosec
import sys
from typing import List

# IMPORTATION THIRDPARTY
import requests
import matplotlib.pyplot as plt

# IMPORTATION INTERNAL
from openbb_terminal import feature_flags as obbff
from openbb_terminal import thought_of_the_day as thought
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
        "OpenBB Terminal is the result of a strong community building an "
        "[param]investment research platform for everyone.[/param]\n\n"
        "Join us on [cmds]https://openbb.co/discord[/cmds], "
        "show your appreciation on [cmds]https://twitter.com/openbb_finance[/cmds],\n"
        "ask support on [cmds]https://openbb.co/support[/cmds], "
        "or even request a feature on [cmds]https://openbb.co/request-a-feature[/cmds]\n"
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

    if not WITH_GIT or obbff.LOGGING_COMMIT_HASH != "REPLACE_ME":
        console.print("This feature is not available : Git dependencies not installed.")
        return 0

    poetry_hash = sha256sum("poetry.lock")

    completed_process = subprocess.run("git pull", shell=True, check=False)  # nosec
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
        "poetry install", shell=True, check=False
    )
    if completed_process.returncode != 0:
        return completed_process.returncode

    return 0


def about_us():
    """Prints an about us section"""
    console.print(
        "\n[green]Thanks for using OpenBB Terminal. This is our way![/green]\n"
        + "\n"
        + "[cyan]Website: [/cyan]https://openbb.co\n"
        + "[cyan]Documentation: [/cyan]https://openbb.co/docs\n"
        + "\n"
        + "[cyan]Join our community on discord: [/cyan]https://openbb.co/discord\n"
        + "[cyan]Follow our twitter for updates: [/cyan]https://twitter.com/openbb_finance\n"
        + "\n"
        + "[yellow]Partnerships:[/yellow]\n"
        + "[cyan]FinBrain: [/cyan]https://finbrain.tech\n"
        + "[cyan]Quiver Quantitative: [/cyan]https://www.quiverquant.com\n"
        + "[cyan]SentimentInvestor: [/cyan]https://sentimentinvestor.com\n"
        + "\n[red]"
        + "DISCLAIMER: Trading in financial instruments involves high risks including the risk of losing some, "
        + "or all, of your investment amount, and may not be suitable for all investors. Before deciding to "
        + "trade in financial instrument you should be fully informed of the risks and costs associated with "
        + "trading the financial markets, carefully consider your investment objectives, level of experience, "
        + "and risk appetite, and seek professional advice where needed.\n"
        + "The data contained in OpenBB Terminal is not necessarily accurate. OpenBB and any provider "
        + "of the data contained in this software will not accept liability for any loss or damage "
        + "as a result of your trading, or your reliance on the information displayed.[/red]\n"
    )


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


def bootup():
    if sys.platform == "win32":
        # Enable VT100 Escape Sequence for WINDOWS 10 Ver. 1607
        os.system("")  # nosec
        # Hide splashscreen loader of the packaged app
        if obbff.PACKAGED_APPLICATION:
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

    Checks github for the latest release version and compares it to obbff.VERSION.
    """
    # The commit has was commented out because the terminal was crashing due to git import for multiple users
    # ({str(git.Repo('.').head.commit)[:7]})
    try:
        r = requests.get(
            "https://api.github.com/repos/openbb-finance/openbbterminal/releases/latest",
            timeout=1,
        )
    except Exception:
        r = None

    if r is not None and r.status_code == 200:
        release = r.json()["html_url"].split("/")[-1].replace("v", "")
        if obbff.VERSION == release:
            console.print("[green]You are using the latest version[/green]")
        else:
            console.print("[red]You are not using the latest version[/red]")
            console.print(
                "[yellow]Check for updates at https://openbb.co/products/terminal#get-started[/yellow]"
            )
    else:
        console.print(
            "[yellow]Unable to check for updates... "
            + "Check your internet connection and try again...[/yellow]"
        )
    console.print("")


def welcome_message():
    """Print the welcome message

    Prints first welcome message, help and a notification if updates are available.
    """
    console.print(f"\nWelcome to OpenBB Terminal v{obbff.VERSION}")

    if obbff.ENABLE_THOUGHTS_DAY:
        console.print("-------------------")
        try:
            thought.get_thought_of_the_day()
        except Exception as e:
            logger.exception("Exception: %s", str(e))
            console.print(e)
    console.print("")


def reset(queue: List[str] = None):
    """Resets the terminal.  Allows for checking code or keys without quitting"""
    console.print("resetting...")
    logger.info("resetting")
    plt.close("all")

    if queue and len(queue) > 0:
        completed_process = subprocess.run(  # nosec
            f"{sys.executable} terminal.py {'/'.join(queue) if len(queue) > 0 else ''}",
            shell=True,
            check=False,
        )
    else:
        completed_process = subprocess.run(  # nosec
            f"{sys.executable} terminal.py", shell=True, check=False
        )
    if completed_process.returncode != 0:
        console.print("Unfortunately, resetting wasn't possible!\n")

    return completed_process.returncode


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


def is_reset(command: str) -> bool:
    """Test whether a command is a reset command

    Parameters
    ----------
    command : str
        The command to test

    Returns
    ----------
    answer : bool
        Whether the command is a reset command
    """
    if "reset" in command:
        return True
    if command == "r":
        return True
    if command == "r\n":
        return True
    return False
