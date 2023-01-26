import json

from openbb_terminal.session import local_model as Local
from openbb_terminal.session import hub_model as Hub
from openbb_terminal.session.session_controller import create_session
from openbb_terminal.session.user import User
from openbb_terminal.rich_config import console


def get_session(email: str, password: str, save: bool):
    session = create_session(email, password, save)
    if not (isinstance(session, dict) and session):
        raise Exception("Failed to create session")
    return session


def login(email: str = "", password: str = "", save: bool = False):
    session = Local.get_session()

    if not session:
        session = get_session(email, password, save)

    User.load_user_info(session)
    response = Hub.fetch_user_configs(session)

    if not (response and response.status_code == 200):
        raise Exception("Failed to fetch user configs")

    Local.apply_configs(configs=json.loads(response.content))
    console.print("[green]Login successful[/green]")
