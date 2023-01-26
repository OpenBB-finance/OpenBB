from dataclasses import dataclass
import jwt
import openbb_terminal.feature_flags as obbff
from openbb_terminal.rich_config import console


@dataclass
class User:
    _TOKEN_TYPE: str = ""
    _TOKEN: str = ""
    _EMAIL: str = ""
    _UUID: str = ""
    _SYNC_ENABLED: bool = True

    @classmethod
    def load_user_info(cls, session: dict):
        """Load user info from login info.

        Parameters
        ----------
        session : dict
            The login info.
        """
        User._TOKEN_TYPE = session.get("token_type", "")
        User._TOKEN = session.get("access_token", "")
        User._UUID = session.get("uuid", "")

        if User._TOKEN:
            decoded_info = jwt.decode(User._TOKEN, options={"verify_signature": False})
            User._EMAIL = decoded_info.get("sub", "")

            MAX_FLAIR_LEN = 20

            if obbff.USE_FLAIR == ":openbb":
                username = User._EMAIL[: User._EMAIL.find("@")]
                if User._SYNC_ENABLED:
                    flair = "[" + username[:MAX_FLAIR_LEN] + "] 🟢"
                else:
                    flair = "[" + username[:MAX_FLAIR_LEN] + "] 🔴"
                setattr(obbff, "USE_FLAIR", flair)

    @classmethod
    def whoami(cls):
        """Display user info."""
        if User._UUID:
            console.print(f"[info]email:[/info] {User._EMAIL}")
            console.print(f"[info]uuid:[/info] {User._UUID}")
            if User._SYNC_ENABLED:
                sync = "enabled"
            else:
                sync = "disabled"
            console.print(f"[info]sync:[/info] {sync}\n")
        else:
            console.print("[info]Only you know...[/info]\n")

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
        return User._SYNC_ENABLED

    @classmethod
    def toggle_sync(cls):
        """Toggle sync."""
        User._SYNC_ENABLED = not User._SYNC_ENABLED

    @classmethod
    def get_token(cls):
        """Get token."""
        return f"{User._TOKEN_TYPE.title()} {User._TOKEN}"
