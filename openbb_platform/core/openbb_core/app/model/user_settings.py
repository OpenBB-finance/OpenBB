"""用户设置模型。"""

import json
import os
import warnings

from openbb_core.app.constants import USER_SETTINGS_PATH
from openbb_core.app.model.abstract.tagged import Tagged
from openbb_core.app.model.credentials import Credentials
from openbb_core.app.model.defaults import Defaults
from openbb_core.app.model.preferences import Preferences
from pydantic import Field


class UserSettings(Tagged):
    """用户设置。"""

    credentials: Credentials = Field(default_factory=Credentials)
    preferences: Preferences = Field(default_factory=Preferences)
    defaults: Defaults = Field(default_factory=Defaults)

    def __init__(self, **kwargs):
        """如果文件存在，则通过直接从文件加载来初始化用户设置。"""
        # 检查用户设置文件是否存在并从中加载
        if os.path.exists(USER_SETTINGS_PATH):
            try:
                with open(USER_SETTINGS_PATH) as f:
                    file_settings = json.load(f)
                # 使用文件中的设置进行初始化
                super().__init__(**{k: v for k, v in file_settings.items() if v})
            except (json.JSONDecodeError, OSError) as e:
                warnings.warn(
                    f"从文件加载用户设置时出错: {e}",
                    stacklevel=2,
                    category=UserWarning,
                )
                # 如果无法读取文件，则回退到默认值
                super().__init__(**kwargs)
        else:
            # 如果文件不存在，则使用默认值
            super().__init__(**kwargs)

    def __repr__(self) -> str:
        """对象的人类可读表示。"""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )
