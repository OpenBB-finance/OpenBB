import json

from openbb_terminal.session import local_model as Local
from openbb_terminal.session import hub_model as Hub
from openbb_terminal.session.user import User
from openbb_terminal.session.session_controller import create_session


def get_session(email: str, password: str, save: bool):
    session = create_session(email, password, save)
    if not (isinstance(session, dict) and session):
        raise Exception("Failed to create session")
    return session


def login(email: str = "", password: str = "", save: bool = ""):
    local_session = Local.get_session()

    if not local_session:
        session = get_session(email, password, save)

    User.load_user_info(session)
    response = Hub.fetch_user_configs(session)
    if response:
        if response.status_code == 200:
            Local.apply_configs(configs=json.loads(response.content))
        else:
            raise Exception("Failed to fetch user configs")
    else:
        raise Exception("Failed to fetch user configs")
