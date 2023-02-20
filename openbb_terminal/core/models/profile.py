from typing import Dict, Optional
from pydantic.dataclasses import dataclass

from openbb_terminal.rich_config import console
from openbb_terminal.session.hub_model import REGISTER_URL


@dataclass(config=dict(validate_assignment=True))
class ProfileModel:
    """Data model for profile."""

    token_type: Optional[str]
    token: Optional[str]
    uuid: Optional[str]
    email: Optional[str]
    username: Optional[str]

    def load_user_info(self, session: dict, email: str):
        """Load user info from login info.

        Parameters
        ----------
        session : dict
            The login info.
        email : str
            The email.
        """
        self.token_type = session.get("token_type", "")
        self.token = session.get("access_token", "")
        self.uuid = session.get("uuid", "")
        self.email = email
        self.username = self.email[: self.email.find("@")]

    def get_uuid(self) -> Optional[str]:
        """Get uuid.

        Returns
        -------
        Optional[str]
            The uuid.
        """
        return self.uuid

    def get_token(self) -> Optional[str]:
        """Get token.

        Returns
        -------
        Optional[str]
            The token.
        """
        return self.token

    def get_session(self) -> Dict[str, Optional[str]]:
        """Get session info.

        Returns
        -------
        Dict[str, Optional[str]]
            The session info.
        """
        return {
            "token_type": self.token_type,
            "access_token": self.token,
            "uuid": self.uuid,
        }

    def get_auth_header(self) -> Optional[str]:
        """Get auth header."""
        if self.token_type is None or self.token is None:
            return None
        return f"{self.token_type.title()} {self.token}"

    def is_guest(self) -> bool:
        """Check if user is guest.

        Returns
        -------
        bool
            True if user is guest, False otherwise.
        """
        return not bool(self.token)

    def whoami(self):
        """Display user info."""
        if not self.is_guest():
            console.print(f"[info]email:[/info] {self.email}")
            console.print(f"[info]uuid:[/info] {self.uuid}")
        else:
            self.print_guest_message()

    @staticmethod
    def print_guest_message():
        """Print guest message."""
        console.print(
            "[info]You are currently logged as a guest.\n"
            f"[info]Register: [/info][cmds]{REGISTER_URL}\n[/cmds]"
        )


profile = ProfileModel(  # type: ignore
    token_type=None,
    token=None,
    uuid=None,
    email=None,
    username=None,
)
