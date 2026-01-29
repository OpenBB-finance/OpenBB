"""OBBject 扩展的 Extension 类。"""

import warnings
from collections.abc import Callable


class Extension:
    """
    充当 OBBject 扩展入口点，并且必须由每个扩展包创建。

    有关更多信息，请参阅 https://docs.openbb.co/developer/extension_types/obbject。
    """

    # pylint: disable=R0917
    def __init__(
        self,
        name: str,
        credentials: list[str] | None = None,
        description: str | None = None,
        on_command_output: bool = False,
        command_output_paths: list[str] | None = None,
        immutable: bool = True,
        results_only: bool = False,
    ) -> None:
        """初始化扩展。

        Parameters
        ----------
        name : str
            扩展名称。
        credentials : list[str], optional
            所需要的凭据列表，默认为 None
        description: Optional[str]
            扩展描述。
        on_command_output : bool, optional
            扩展是否有命令输出，默认为 False
        command_output_paths : list[str], optional
            扩展作用的端点路径列表，其中 None 表示全部，默认为 None。
        immutable : bool, optional
            函数输出是否不可变，默认为 True。
        results_only : bool, optional
            扩展是否仅返回结果而不是 OBBject，默认为 False。
        """
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.service.system_service import SystemService

        self.name = name
        self.credentials = credentials or []
        self.description = description
        self.on_command_output = on_command_output
        self.command_output_paths = command_output_paths or []
        self.immutable = immutable
        self.results_only = results_only

        # 必须显式启用此功能。
        if self.on_command_output is False and (
            self.command_output_paths
            or self.results_only is True
            or self.immutable is False
        ):
            raise ValueError(
                "OBBject Extension Error -> 当设置了 'command_output_paths'、'results_only' 或 'immutable' 时，"
                + "必须将 'on_command_output' 设置为 True。",
            )

        # 用户必须显式启用作用于命令输出的 OBBject 扩展。
        if (
            self.on_command_output
            and not SystemService().system_settings.allow_on_command_output
        ):
            raise RuntimeError(
                "OBBject Extension Error -> \n\n"
                + "已安装作用于命令输出的 OBBject 扩展，"
                + "但尚未在 `system_settings.json` 中启用。\n\n"
                + "将 `allow_on_command_output` 设置为 True 以启用它。\n"
                + "或者，将环境变量 `OPENBB_ALLOW_ON_COMMAND_OUTPUT` 设置为 True。"
                + "\n\n请谨慎操作，因为这可能会产生安全隐患。\n\n"
                + "确保扩展是从受信任的来源安装的。\n\n",
            )

        # 用户必须显式启用修改输出的 OBBject 扩展。
        if (
            self.on_command_output
            and self.immutable is False
            and not SystemService().system_settings.allow_mutable_extensions
        ):
            raise RuntimeError(
                "OBBject Extension Error -> \n\n"
                + "已安装修改输出的 OBBject 扩展，"
                + "但尚未在 `system_settings.json` 中启用。\n\n"
                + "将 `allow_mutable_extensions` 设置为 True 以启用它。\n"
                + "或者，将环境变量 `OPENBB_ALLOW_MUTABLE_EXTENSIONS` 设置为 True。"
                + "\n\n请谨慎操作，因为这可能会产生安全隐患。\n\n"
                + "确保扩展是从受信任的来源安装的。\n\n",
            )

    @property
    def obbject_accessor(self) -> Callable:
        """扩展 OBBject，灵感来自 pandas。"""
        # pylint: disable=import-outside-toplevel

        from openbb_core.app.model.obbject import OBBject

        return self.register_accessor(self.name, OBBject)

    @staticmethod
    def register_accessor(name, cls) -> Callable:
        """注册自定义访问器。"""

        def decorator(accessor):
            if hasattr(cls, name):
                warnings.warn(
                    f"在名称 '{repr(name)}' 下为类型 '{repr(cls)}' 注册访问器 '{repr(accessor)}' "
                    f"正在覆盖具有相同名称的预先存在的属性。",
                    UserWarning,
                )
            setattr(cls, name, CachedAccessor(name, accessor))
            cls.accessors.add(name)

            return accessor

        return decorator


class CachedAccessor:
    """CachedAccessor。"""

    def __init__(self, name: str, accessor) -> None:
        """初始化缓存访问器。"""
        self._name = name
        self._accessor = accessor

    def __get__(self, obj, cls):
        """获取缓存访问器。"""
        if obj is None:
            return self._accessor
        accessor_obj = self._accessor(obj)
        object.__setattr__(obj, self._name, accessor_obj)
        return accessor_obj
