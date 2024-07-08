"""Account."""

# pylint: disable=W0212:protected-access
import json
from functools import wraps
from pathlib import Path
from sys import exc_info
from typing import TYPE_CHECKING, Optional

from openbb_core.app.logs.logging_service import LoggingService
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.app.model.hub.hub_session import HubSession
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.service.hub_service import HubService
from openbb_core.app.service.user_service import UserService

if TYPE_CHECKING:
    from openbb_core.app.static.app_factory import BaseApp


class Account:  # noqa: D205, D400
    """/account
    login
    logout
    save
    refresh
    """

    SESSION_FILE = ".hub_session.json"

    def __init__(self, base_app: "BaseApp"):
        """Initialize account service."""
        self._base_app = base_app
        self._openbb_directory = (
            base_app._command_runner.system_settings.openbb_directory
        )
        self._hub_service: Optional[HubService] = None

    def __repr__(self) -> str:
        """Human readable representation of the object."""
        return self.__doc__ or ""

    def _log_account_command(func):  # pylint: disable=E0213
        """Log account command."""

        @wraps(func)  # type: ignore[arg-type]
        def wrapped(self, *args, **kwargs):
            try:
                # pylint: disable=E1102
                result = func(self, *args, **kwargs)  # type: ignore[operator]
            except Exception as e:
                raise OpenBBError(e) from e
            finally:
                user_settings = self._base_app._command_runner.user_settings
                system_settings = self._base_app._command_runner.system_settings
                ls = LoggingService(
                    user_settings=user_settings, system_settings=system_settings
                )
                ls.log(
                    user_settings=user_settings,
                    system_settings=system_settings,
                    # pylint: disable=E1101
                    route=f"/account/{func.__name__}",  # type: ignore[attr-defined]
                    func=func,  # type: ignore[arg-type]
                    kwargs={},  # don't want any credentials being logged by accident
                    exec_info=exc_info(),
                )

            return result

        return wrapped

    def _create_hub_service(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        pat: Optional[str] = None,
    ) -> HubService:
        """Create hub service to handle connection."""
        if email is None and password is None and pat is None:
            session_file = Path(self._openbb_directory, self.SESSION_FILE)
            if not session_file.exists():
                raise OpenBBError("Session not found.")

            with open(session_file) as f:
                session_dict = json.load(f)

            hub_session = HubSession(**session_dict)
            hs = HubService(hub_session)
        else:
            hs = HubService()
            hs.connect(email, password, pat)
        return hs

    @_log_account_command  # type: ignore
    def login(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        pat: Optional[str] = None,
        remember_me: bool = False,
        return_settings: bool = False,
    ) -> Optional[UserSettings]:
        """Login to hub.

        Parameters
        ----------
        email : Optional[str], optional
            Email address, by default None
        password : Optional[str], optional
            Password, by default None
        pat : Optional[str], optional
            Personal access token, by default None
        remember_me : bool, optional
            Remember me, by default False
        return_settings : bool, optional
            Return user settings, by default False

        Returns
        -------
        Optional[UserSettings]
            User settings: profile, credentials, preferences
        """
        self._hub_service = self._create_hub_service(email, password, pat)
        incoming = self._hub_service.pull()
        self._base_app.user.profile = incoming.profile
        self._base_app.user.credentials.update(incoming.credentials)
        self._base_app.user.defaults.update(incoming.defaults)
        if remember_me:
            Path(self._openbb_directory).mkdir(parents=False, exist_ok=True)
            session_file = Path(self._openbb_directory, self.SESSION_FILE)
            with open(session_file, "w") as f:
                if not self._hub_service.session:
                    raise OpenBBError("Not connected to hub.")

                json.dump(
                    self._hub_service.session.model_dump(mode="json"), f, indent=4
                )

        if return_settings:
            return self._base_app._command_runner.user_settings
        return None

    @_log_account_command  # type: ignore
    def save(self, return_settings: bool = False) -> Optional[UserSettings]:
        """Save user settings.

        Parameters
        ----------
        return_settings : bool, optional
            Return user settings, by default False

        Returns
        -------
        Optional[UserSettings]
            User settings: profile, credentials, preferences
        """
        if not self._hub_service:
            UserService.write_to_file(self._base_app._command_runner.user_settings)
        else:
            self._hub_service.push(self._base_app._command_runner.user_settings)

        if return_settings:
            return self._base_app._command_runner.user_settings
        return None

    @_log_account_command  # type: ignore
    def refresh(self, return_settings: bool = False) -> Optional[UserSettings]:
        """Refresh user settings.

        Parameters
        ----------
        return_settings : bool, optional
            Return user settings, by default False

        Returns
        -------
        Optional[UserSettings]
            User settings: profile, credentials, preferences
        """
        if not self._hub_service:
            self._base_app._command_runner.user_settings = UserService.read_from_file()
        else:
            incoming = self._hub_service.pull()
            self._base_app.user.profile = incoming.profile
            self._base_app.user.credentials.update(incoming.credentials)
            self._base_app.user.defaults.update(incoming.defaults)
        if return_settings:
            return self._base_app._command_runner.user_settings
        return None

    @_log_account_command  # type: ignore
    def logout(self, return_settings: bool = False) -> Optional[UserSettings]:
        """Logout from hub.

        Parameters
        ----------
        return_settings : bool, optional
            Return user settings, by default False

        Returns
        -------
        Optional[UserSettings]
            User settings: profile, credentials, preferences
        """
        if not self._hub_service:
            raise OpenBBError("Not connected to hub.")

        self._hub_service.disconnect()

        session_file = Path(self._openbb_directory, self.SESSION_FILE)
        if session_file.exists():
            session_file.unlink()

        self._base_app._command_runner.user_settings = UserService.read_from_file()

        if return_settings:
            return self._base_app._command_runner.user_settings
        return None
