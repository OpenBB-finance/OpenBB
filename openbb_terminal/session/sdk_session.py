from openbb_terminal.rich_config import console
from openbb_terminal.session import local_model as Local
from openbb_terminal.session import session_model
from openbb_terminal.session.user import User


def get_session(email: str, password: str, token: str, save: bool):
    session = ""

    if token:
        console.print("Creating session from token.")
        session = session_model.create_session_from_token(token, save)

    if not session:
        console.print("Creating session from email and password.")
        session = session_model.create_session(email, password, save)

    if not (isinstance(session, dict) and session):
        raise Exception("Failed to create session.")

    return session


def login(
    email: str = "", password: str = "", token: str = "", keep_session: bool = False
):
    session = Local.get_session()

    if not session:
        session = get_session(email, password, token, keep_session)

    if session_model.login(session) in [
        session_model.LoginStatus.FAILED,
        session_model.LoginStatus.NO_RESPONSE,
    ]:
        raise Exception("Login failed.")

    console.print("[green]Login successful.[/green]")


def logout():
    session_model.logout(
        auth_header=User.get_auth_header(),
        token=User.get_token(),
        guest=User.is_guest(),
    )


def whoami():
    User.whoami()
