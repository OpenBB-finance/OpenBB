import logging

from openbb_terminal.core.session import (
    local_model as Local,
    session_model,
)
from openbb_terminal.core.session.current_user import (
    get_current_user,
    is_local,
)
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.terminal_helper import print_guest_block_msg

logger = logging.getLogger(__name__)


def get_session(email: str, password: str, token: str, save: bool) -> dict:
    session = dict()

    if token:
        console.print("Creating session from token.")
        session = session_model.create_session_from_token(token, save)  # type: ignore

    if not session and email:
        console.print("Creating session from email and password.")
        session = session_model.create_session(email, password, save)  # type: ignore

    if not (isinstance(session, dict) and session):
        raise Exception("Failed to create session.")

    return session


@log_start_end(log=logger)
def login(
    email: str = "", password: str = "", token: str = "", keep_session: bool = False
):
    """
    Login and load user info.
    If there is a saved session it will be used (this can be achieved by `keep_session=True`).
    If there's not a local session,
    the user can use either email and password or the OpenBB Personal Access Token.

    Parameters
    ----------
    email : str
        The email.
    password : str
        The password.
    token : str
        The OpenBB Personal Access Token.
    keep_session : bool
        Keep the session, i.e., next time the user logs in,
        there is no need to enter the email and password or the token.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.login(email="your_email", password="your_password")
    """
    session = {}
    if not (email or token):
        session = Local.get_session()

    if not session:
        session = get_session(email, password, token, keep_session)
    else:
        console.print("Using local session to login.")

    status = session_model.login(session)
    if status != session_model.LoginStatus.SUCCESS:
        raise Exception(f"Login failed with status `{status.value}`.")

    console.print("[green]Login successful.[/green]")


@log_start_end(log=logger)
def logout():
    """
    Logout and clear session.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.logout()
    """
    current_user = get_current_user()
    session_model.logout(
        auth_header=current_user.profile.get_auth_header(),
        token=current_user.profile.token,
        guest=is_local(),
    )


@log_start_end(log=logger)
def whoami():
    """
    Display user info.

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.whoami()
    """
    current_user = get_current_user()
    local_user = is_local()
    if not local_user:
        console.print(f"[info]email:[/info] {current_user.profile.email}")
        console.print(f"[info]uuid:[/info] {current_user.profile.uuid}")
    else:
        print_guest_block_msg()
