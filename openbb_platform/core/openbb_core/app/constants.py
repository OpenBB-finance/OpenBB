"""OpenBB 平台的常量。"""

from pathlib import Path

HOME_DIRECTORY = Path.home()
OPENBB_DIRECTORY = Path(HOME_DIRECTORY, ".openbb_platform")
USER_SETTINGS_PATH = Path(OPENBB_DIRECTORY, "user_settings.json")
SYSTEM_SETTINGS_PATH = Path(OPENBB_DIRECTORY, "system_settings.json")
