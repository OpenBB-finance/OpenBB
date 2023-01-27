from dataclasses import dataclass
import openbb_terminal.feature_flags as obbff
from openbb_terminal.rich_config import console


@dataclass
class User:
    _TOKEN_TYPE: str = ""
    _TOKEN: str = ""
    _EMAIL: str = ""
    _UUID: str = ""

    @classmethod
    def load_user_info(cls, session: dict, email: str):
        """Load user info from login info.

        Parameters
        ----------
        session : dict
            The login info.
        """
        User._TOKEN_TYPE = session.get("token_type", "")
        User._TOKEN = session.get("access_token", "")
        User._UUID = session.get("uuid", "")
        User._EMAIL = email
        if User._EMAIL:
            User.update_flair()

    @classmethod
    def get_session(cls):
        """Get session info."""
        return {
            "token_type": User._TOKEN_TYPE,
            "access_token": User._TOKEN,
            "uuid": User._UUID,
        }

    @staticmethod
    def update_flair():
        MAX_FLAIR_LEN = 20
        username = User._EMAIL[: User._EMAIL.find("@")]
        username = "[" + username[:MAX_FLAIR_LEN] + "]"

        if obbff.USE_FLAIR == ":openbb" or username in obbff.USE_FLAIR:
            setattr(obbff, "USE_FLAIR", username + " 🦋")

    @classmethod
    def get_uuid(cls):
        """Get uuid."""
        return User._UUID

    @classmethod
    def get_email(cls):
        """Get email."""
        return User._EMAIL

    @classmethod
    def whoami(cls):
        """Display user info."""
        if User._UUID:
            console.print(f"[info]email:[/info] {User._EMAIL}")
            console.print(f"[info]uuid:[/info] {User._UUID}")
            if obbff.SYNC_ENABLED:
                sync = "ON"
            else:
                sync = "OFF"
            console.print(f"[info]sync:[/info] {sync}\n")
        else:
            console.print(
                "[info]You are currently logged as a guest.\n"
                "Create an account here https://my.openbb.co/register.[/info]\n"
            )

    @classmethod
    def clear(cls):
        """Clear user info."""
        User._TOKEN_TYPE = ""
        User._TOKEN = ""
        User._EMAIL = ""
        User._UUID = ""
        obbff.USE_FLAIR = ":openbb"

    @classmethod
    def is_guest(cls):
        """Check if user is guest."""
        return not bool(User._TOKEN)

    @classmethod
    def is_sync_enabled(cls):
        """Check if sync is enabled."""
        return obbff.SYNC_ENABLED

    @classmethod
    def get_token(cls):
        """Get token."""
        return f"{User._TOKEN_TYPE.title()} {User._TOKEN}"
