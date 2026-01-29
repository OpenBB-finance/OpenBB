"""Settings model."""

from enum import Enum
from typing import Any, Literal

from dotenv import dotenv_values, set_key
from openbb_cli.config.constants import AVAILABLE_FLAIRS, ENV_FILE_SETTINGS
from openbb_core.app.version import get_package_version
from pydantic import BaseModel, ConfigDict, Field, model_validator
from pytz import all_timezones

VERSION = get_package_version("openbb-cli")


class SettingGroups(Enum):
    """Setting types."""

    feature_flags = "feature_flag"
    preferences = "preference"


class Settings(BaseModel):
    """Settings model."""

    # Platform CLI version
    VERSION: str = VERSION

    # DEVELOPMENT FLAGS
    TEST_MODE: bool = False
    DEBUG_MODE: bool = False
    DEV_BACKEND: bool = False

    # OPENBB
    HUB_URL: str = "https://my.openbb.co"
    BASE_URL: str = "https://payments.openbb.co"

    # GENERAL
    PREVIOUS_USE: bool = False

    # FEATURE FLAGS
    FILE_OVERWRITE: bool = Field(
        default=False,
        description="是否覆盖现有的 Excel 文件",
        command="overwrite",
        group=SettingGroups.feature_flags,
    )
    SHOW_VERSION: bool = Field(
        default=True,
        description="是否在右下角显示版本",
        command="version",
        group=SettingGroups.feature_flags,
    )
    USE_INTERACTIVE_DF: bool = Field(
        default=True,
        description="在交互式窗口中显示表格",
        command="interactive",
        group=SettingGroups.feature_flags,
    )
    USE_CLEAR_AFTER_CMD: bool = Field(
        default=False,
        description="每次命令后清除控制台",
        command="cls",
        group=SettingGroups.feature_flags,
    )
    USE_DATETIME: bool = Field(
        default=True,
        description="是否在 flair 之前显示日期和时间",
        command="datetime",
        group=SettingGroups.feature_flags,
    )
    USE_PROMPT_TOOLKIT: bool = Field(
        default=True,
        description="启用 prompt toolkit（自动完成和历史记录）",
        command="promptkit",
        group=SettingGroups.feature_flags,
    )
    ENABLE_EXIT_AUTO_HELP: bool = Field(
        default=True,
        description="退出菜单时自动打印帮助",
        command="exithelp",
        group=SettingGroups.feature_flags,
    )
    ENABLE_RICH_PANEL: bool = Field(
        default=True,
        description="启用多彩的 rich CLI 面板",
        command="richpanel",
        group=SettingGroups.feature_flags,
    )
    TOOLBAR_HINT: bool = Field(
        default=True,
        description="在底部工具栏显示使用提示",
        command="tbhint",
        group=SettingGroups.feature_flags,
    )
    SHOW_MSG_OBBJECT_REGISTRY: bool = Field(
        default=False,
        description="添加新结果后显示 obbject 注册表消息",
        command="obbject_msg",
        group=SettingGroups.feature_flags,
    )

    # PREFERENCES
    TIMEZONE: Literal[tuple(all_timezones)] = Field(  # type: ignore[valid-type]
        default="America/New_York",
        description="选择时区",
        command="timezone",
        group=SettingGroups.preferences,
    )
    FLAIR: Literal[tuple(AVAILABLE_FLAIRS)] = Field(  # type: ignore[valid-type]
        default=":openbb",
        description="选择 flair 图标",
        command="flair",
        group=SettingGroups.preferences,
    )
    N_TO_KEEP_OBBJECT_REGISTRY: int = Field(
        default=10,
        description="定义注册表中允许的最大 obbject 数量",
        command="obbject_res",
        group=SettingGroups.preferences,
    )
    N_TO_DISPLAY_OBBJECT_REGISTRY: int = Field(
        default=5,
        description="定义帮助菜单上显示的最大缓存结果数量",
        command="obbject_display",
        group=SettingGroups.preferences,
    )
    RICH_STYLE: str = Field(
        default="dark",
        description="将自定义 rich 样式应用于 CLI",
        command="console_style",
        group=SettingGroups.preferences,
    )
    ALLOWED_NUMBER_OF_ROWS: int = Field(
        default=20,
        description="要显示的行数（不使用交互式表格时）。",
        command="n_rows",
        group=SettingGroups.preferences,
    )
    ALLOWED_NUMBER_OF_COLUMNS: int = Field(
        default=5,
        description="要显示的列数（不使用交互式表格时）。",
        command="n_cols",
        group=SettingGroups.preferences,
    )

    model_config = ConfigDict(validate_assignment=True)

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    @model_validator(mode="before")
    @classmethod
    def from_env(cls, values: dict) -> dict:
        """Load settings from .env."""
        settings = {}
        settings.update(dotenv_values(ENV_FILE_SETTINGS))
        settings.update(values)
        filtered = {k.replace("OPENBB_", ""): v for k, v in settings.items()}
        return filtered

    def set_item(self, key: str, value: Any) -> None:
        """Set an item in the model and save to .env."""
        setattr(self, key, value)
        set_key(str(ENV_FILE_SETTINGS), "OPENBB_" + key, str(value))
