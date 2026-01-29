"""环境变量。"""

import os
from pathlib import Path

import dotenv
from openbb_core.app.constants import OPENBB_DIRECTORY
from openbb_core.app.model.abstract.singleton import SingletonMeta


class Env(metaclass=SingletonMeta):
    """环境变量。"""

    _environ: dict[str, str]

    def __init__(self) -> None:
        """初始化环境。"""
        dotenv.load_dotenv(Path(OPENBB_DIRECTORY, ".env"))
        self._environ = os.environ.copy()

    @property
    def API_AUTH(self) -> bool:
        """API 身份验证：启用 API 端点身份验证。"""
        return self.str2bool(self._environ.get("OPENBB_API_AUTH", False))

    @property
    def API_USERNAME(self) -> str | None:
        """API 用户名：设置 API 用户名。"""
        return self._environ.get("OPENBB_API_USERNAME", None)

    @property
    def API_PASSWORD(self) -> str | None:
        """API 密码：设置 API 密码。"""
        return self._environ.get("OPENBB_API_PASSWORD", None)

    @property
    def API_AUTH_EXTENSION(self) -> str | None:
        """身份验证扩展：指定要使用的身份验证扩展。"""
        return self._environ.get("OPENBB_API_AUTH_EXTENSION", None)

    @property
    def AUTO_BUILD(self) -> bool:
        """自动构建：启用导入时的自动包构建。"""
        return self.str2bool(self._environ.get("OPENBB_AUTO_BUILD", True))

    @property
    def DEBUG_MODE(self) -> bool:
        """调试模式：启用调试模式。"""
        return self.str2bool(self._environ.get("OPENBB_DEBUG_MODE", False))

    @property
    def DEV_MODE(self) -> bool:
        """开发模式：启用开发模式。"""
        return self.str2bool(self._environ.get("OPENBB_DEV_MODE", False))

    @property
    def ALLOW_MUTABLE_EXTENSIONS(self) -> bool:
        """允许可变扩展：启用修改 OBBject 输出的扩展。"""
        return self.str2bool(
            self._environ.get("OPENBB_ALLOW_MUTABLE_EXTENSIONS", False)
        )

    @property
    def ALLOW_ON_COMMAND_OUTPUT(self) -> bool:
        """允许命令输出：启用在命令输出上起作用的扩展。"""
        return self.str2bool(self._environ.get("OPENBB_ALLOW_ON_COMMAND_OUTPUT", False))

    @staticmethod
    def str2bool(value) -> bool:
        """将值与其对应的布尔值匹配。"""
        if isinstance(value, bool):
            return value
        if value.lower() in {"false", "f", "0", "no", "n"}:
            return False
        if value.lower() in {"true", "t", "1", "yes", "y"}:
            return True
        raise ValueError(f"无法将 {value} 转换为 bool。")
