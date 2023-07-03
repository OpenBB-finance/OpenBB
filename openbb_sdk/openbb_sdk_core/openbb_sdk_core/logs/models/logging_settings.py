from pathlib import Path
from typing import List, Optional

from openbb_sdk_core.app.model.system_settings import SystemSettings
from openbb_sdk_core.app.model.user_settings import UserSettings
from openbb_sdk_core.logs.utils.utils import get_app_id, get_log_dir, get_session_id


class LoggingSettings:
    def __init__(self, user_settings: UserSettings, system_settings: SystemSettings):
        user_data_directory = (
            str(Path.home() / "OpenBBUserData")
            if not user_settings.preferences
            else user_settings.preferences.user_data_directory
        )
        hub_session = (
            user_settings.profile.hub_session if user_settings.profile else None
        )
        if hub_session:
            user_id = hub_session.user_uuid
            user_email = hub_session.email
            user_primary_usage = hub_session.primary_usage
        else:
            user_id, user_email, user_primary_usage = None, None, None

        # System
        self.commit_hash: Optional[str] = system_settings.logging_commit_hash
        self.branch: Optional[str] = system_settings.logging_branch
        self.app_name: str = system_settings.logging_app_name
        self.app_id: str = get_app_id(user_data_directory)
        self.session_id: str = get_session_id()
        self.frequency: str = system_settings.logging_frequency
        self.handler_list: List[str] = system_settings.logging_handlers
        self.rolling_clock: bool = system_settings.logging_rolling_clock
        self.verbosity: int = system_settings.logging_verbosity
        self.platform: str = system_settings.platform
        self.python_version: str = system_settings.python_version
        self.terminal_version: str = system_settings.version
        # User
        self.user_id: Optional[str] = user_id
        self.user_logs_directory: Path = get_log_dir(user_data_directory)
        self.user_email: Optional[str] = user_email
        self.user_primary_usage: Optional[str] = user_primary_usage
