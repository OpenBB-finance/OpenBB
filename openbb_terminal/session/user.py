import openbb_terminal.feature_flags as obbff
from openbb_terminal.rich_config import console
from openbb_terminal.session.hub_model import REGISTER_URL


class User:
    _token_type: str = ""
    _token: str = ""
    _uuid: str = ""
    _email: str = ""

    @classmethod
    def load_user_info(cls, session: dict, email: str):
        """Load user info from login info.

        Parameters
        ----------
        session : dict
            The login info.
        """
        cls._token_type = session.get("token_type", "")
        cls._token = session.get("access_token", "")
        cls._uuid = session.get("uuid", "")
        cls._email = email

    @classmethod
    def get_session(cls):
        """Get session info."""
        return {
            "token_type": cls._token_type,
            "access_token": cls._token,
            "uuid": cls._uuid,
        }

    @staticmethod
    def update_flair(flair: str):
        """Update flair if user has not changed it."""
        if flair is None:
            MAX_FLAIR_LEN = 20
            username = User._email[: User._email.find("@")]
            username = "[" + username[:MAX_FLAIR_LEN] + "]"
            setattr(obbff, "USE_FLAIR", username + " 🦋")

    @classmethod
    def get_uuid(cls):
        """Get uuid."""
        return cls._uuid

    @classmethod
    def whoami(cls):
        """Display user info."""
        if not User.is_guest():
            console.print(f"[info]email:[/info] {cls._email}")
            console.print(f"[info]uuid:[/info] {cls._uuid}")
            sync = "ON" if obbff.SYNC_ENABLED is True else "OFF"
            console.print(f"[info]sync:[/info] {sync}")
        else:
            User.print_guest_message()

    @classmethod
    def clear(cls):
        """Clear user info."""
        cls._token_type = ""
        cls._token = ""
        cls._email = ""
        cls._uuid = ""
        obbff.USE_FLAIR = ":openbb"

    @classmethod
    def is_guest(cls):
        """Check if user is guest."""
        return not bool(cls._token)

    @classmethod
    def is_sync_enabled(cls):
        """Check if sync is enabled."""
        return obbff.SYNC_ENABLED

    @classmethod
    def get_auth_header(cls):
        """Get token."""
        return f"{cls._token_type.title()} {cls._token}"

    @classmethod
    def get_token(cls):
        """Get token."""
        return cls._token

    @classmethod
    def print_guest_message(cls):
        """Print guest message."""
        console.print(
            "[info]You are currently logged as a guest.\n"
            f"[info]Register: [/info][cmds]{REGISTER_URL}\n[/cmds]"
        )
