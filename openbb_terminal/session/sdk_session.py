from openbb_terminal.session import local_model as Local
from openbb_terminal.session import session_model
from openbb_terminal.rich_config import console


def get_session(email: str, password: str, save: bool):
    session = session_model.create_session(email, password, save)
    if not (isinstance(session, dict) and session):
        raise Exception("Failed to create session")
    return session


def login(email: str = "", password: str = "", save: bool = False):
    session = Local.get_session()

    if not session:
        session = get_session(email, password, save)

    if session_model.login(session) in [
        session_model.LoginStatus.FAILED,
        session_model.LoginStatus.NO_RESPONSE,
    ]:
        raise Exception("Login failed")

    console.print("[green]Login successful[/green]")
