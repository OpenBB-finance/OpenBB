import openbb_terminal.feature_flags as obbff
from openbb_terminal.rich_config import console


class User:
    token_type: str = ""
    token: str = ""
    uuid: str = ""
    email: str = ""

    @classmethod
    def load_user_info(cls, session: dict, email: str):
        """Load user info from login info.

        Parameters
        ----------
        session : dict
            The login info.
        """
        User.token_type = session.get("token_type", "")
        User.token = session.get("access_token", "")
        User.uuid = session.get("uuid", "")
        User.email = email

    @classmethod
    def get_session(cls):
        """Get session info."""
        return {
            "token_type": User.token_type,
            "access_token": User.token,
            "uuid": User.uuid,
        }

    @staticmethod
    def update_flair(flair: str):
        """Update flair if user has not changed it."""
        if flair is None:
            MAX_FLAIR_LEN = 20
            username = User.email[: User.email.find("@")]
            username = "[" + username[:MAX_FLAIR_LEN] + "]"
            setattr(obbff, "USE_FLAIR", username + " 🦋")

    @classmethod
    def get_uuid(cls):
        """Get uuid."""
        return User.uuid

    @classmethod
    def whoami(cls):
        """Display user info."""
        if User.uuid:
            console.print(f"[info]email:[/info] {User.email}")
            console.print(f"[info]uuid:[/info] {User.uuid}")
            if obbff.SYNC_ENABLED:
                sync = "ON"
            else:
                sync = "OFF"
            console.print(f"[info]sync:[/info] {sync}")
        else:
            console.print(
                "[info]You are currently logged as a guest.\n"
                "Create an account here https://my.openbb.co/register.[/info]\n"
            )

    @classmethod
    def clear(cls):
        """Clear user info."""
        User.token_type = ""
        User.token = ""
        User.email = ""
        User.uuid = ""
        obbff.USE_FLAIR = ":openbb"

    @classmethod
    def is_guest(cls):
        """Check if user is guest."""
        return not bool(User.token)

    @classmethod
    def is_sync_enabled(cls):
        """Check if sync is enabled."""
        return obbff.SYNC_ENABLED

    @classmethod
    def get_auth_header(cls):
        """Get token."""
        return f"{User.token_type.title()} {User.token}"

    @classmethod
    def get_token(cls):
        """Get token."""
        return User.token
