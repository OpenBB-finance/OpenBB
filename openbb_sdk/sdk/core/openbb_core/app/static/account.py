# pylint: disable=W0212:protected-access
import json
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from openbb_core.app.command_runner import CommandRunnerSession
from openbb_core.app.hub.hub_manager import HubManager
from openbb_core.app.hub.model.hub_session import HubSession
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.service.user_service import UserService

if TYPE_CHECKING:
    from openbb_core.app.static.command_runner_wrapper import CommandRunnerWrapper


class OpenBBError(Exception):
    pass


class Account:
    def __init__(self, wrapper: "CommandRunnerWrapper"):
        self._wrapper = wrapper

    def create_hub_manager(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        sdk_token: Optional[str] = None,
    ) -> HubManager:
        if email is None and password is None and sdk_token is None:
            session_file = Path(
                self._wrapper.system.openbb_directory, ".sdk_hub_session.json"
            )
            if not session_file.exists():
                raise OpenBBError("Session not found.")

            with open(session_file) as f:
                session_dict = json.load(f)

            hub_session = HubSession(**session_dict)
            hm = HubManager(hub_session)
        else:
            hm = HubManager()
            hm.connect(email, password, sdk_token)
        return hm

    def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        sdk_token: Optional[str] = None,
        remember_me: bool = False,
    ) -> UserSettings:
        """Login to hub.

        Parameters
        ----------
        email : Optional[str], optional
            Email address, by default None
        password : Optional[str], optional
            Password, by default None
        sdk_token : Optional[str], optional
            SDK token, by default None
        remember_me : bool, optional
            Remember me, by default False

        Returns
        -------
        UserSettings
            User settings: profile, credentials, preferences
        """
        hm = self.create_hub_manager(email, password, sdk_token)
        incoming = hm.pull()
        self._wrapper._command_runner_session = CommandRunnerSession(
            user_settings=incoming
        )
        if remember_me:
            Path(self._wrapper.system.openbb_directory).mkdir(
                parents=False, exist_ok=True
            )
            session_file = Path(
                self._wrapper.system.openbb_directory, ".sdk_hub_session.json"
            )
            with open(session_file, "w") as f:
                if not hm.session:
                    raise OpenBBError("Not connected to hub.")

                json.dump(hm.session.dict(), f, indent=4)

        return self._wrapper._command_runner_session.user_settings

    def save(self) -> UserSettings:
        """Save user settings.

        Returns
        -------
        UserSettings
            User settings: profile, credentials, preferences
        """
        hub_session = (
            self._wrapper._command_runner_session.user_settings.profile.hub_session
        )
        if not hub_session:
            UserService.write_default_user_settings(
                self._wrapper._command_runner_session.user_settings
            )
        else:
            hm = HubManager(hub_session)
            hm.push(self._wrapper._command_runner_session.user_settings)
        return self._wrapper._command_runner_session.user_settings

    def refresh(self) -> UserSettings:
        """Refresh user settings.

        Returns
        -------
        UserSettings
            User settings: profile, credentials, preferences
        """
        hub_session = (
            self._wrapper._command_runner_session.user_settings.profile.hub_session
        )
        if not hub_session:
            self._wrapper._command_runner_session = CommandRunnerSession()
        else:
            hm = HubManager(hub_session)
            user_settings = hm.pull()
            user_settings.id = self._wrapper._command_runner_session.user_settings.id
            self._wrapper._command_runner_session = CommandRunnerSession(
                user_settings=user_settings
            )
        return self._wrapper._command_runner_session.user_settings

    def logout(self) -> UserSettings:
        """Logout from hub.

        Returns
        -------
        UserSettings
            User settings: profile, credentials, preferences
        """
        hub_session = (
            self._wrapper._command_runner_session.user_settings.profile.hub_session
        )
        if not hub_session:
            raise OpenBBError("Not connected to hub.")

        hm = HubManager(hub_session)
        hm.disconnect()

        session_file = Path(
            self._wrapper.system.openbb_directory, ".sdk_hub_session.json"
        )
        if session_file.exists():
            session_file.unlink()

        self._wrapper._command_runner_session = CommandRunnerSession()
        return self._wrapper._command_runner_session.user_settings
