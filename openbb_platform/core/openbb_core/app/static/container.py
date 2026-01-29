"""容器类。"""

from typing import TYPE_CHECKING, Any

from openbb_core.app.model.abstract.error import OpenBBError

if TYPE_CHECKING:
    from openbb_core.app.command_runner import CommandRunner


class Container:
    """命令运行器会话的容器类。"""

    def __init__(self, command_runner: "CommandRunner") -> None:
        """初始化容器。"""
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.model.obbject import OBBject

        self._command_runner = command_runner
        OBBject._user_settings = command_runner.user_settings
        OBBject._system_settings = command_runner.system_settings

    def _run(self, *args, **kwargs) -> Any:
        """在容器中运行命令。"""
        endpoint = args[0][1:].replace("/", ".") if args else ""
        defaults = self._command_runner.user_settings.defaults.commands

        if endpoint and defaults and defaults.get(endpoint):
            default_params = {
                k: v for k, v in defaults[endpoint].items() if k != "provider"
            }
            for k, v in default_params.items():
                if k == "chart" and v is True:
                    kwargs["chart"] = True
                elif (
                    k in kwargs["standard_params"]
                    and kwargs["standard_params"][k] is None
                ):
                    kwargs["standard_params"][k] = v
                elif (
                    k in kwargs["extra_params"] and kwargs["extra_params"][k] is None
                ) or k not in kwargs["extra_params"]:
                    kwargs["extra_params"][k] = v

        obbject = self._command_runner.sync_run(*args, **kwargs)

        results_only = getattr(obbject, "_results_only", False)

        if results_only is True:
            content = obbject.model_dump(exclude_unset=True).get("results", [])
            return content

        output_type = self._command_runner.user_settings.preferences.output_type

        if output_type == "OBBject":
            return obbject

        return getattr(obbject, "to_" + output_type)()

    def _check_credentials(self, provider: str) -> bool | None:
        """检查所需凭据是否已填充。"""
        credentials = self._command_runner.user_settings.credentials
        if provider not in credentials.origins:
            return None
        required = credentials.origins.get(provider)
        return all(getattr(credentials, r, None) for r in required)

    def _get_provider(
        self, choice: str | None, command: str, default_priority: tuple[str, ...]
    ) -> str:
        """获取执行中使用的提供者。

        如果未指定选择，则使用配置的优先级列表。当提供者的所有必需凭据都已填充时，将使用该提供者。

        Parameters
        ----------
        choice: Optional[str]
            提供者选择，例如 'fmp'。
        command: str
            获取提供者的命令，例如 'equity.price.historical'
        default_priority: Tuple[str, ...]
            给定命令的可用提供者元组，用作默认优先级列表。

        Returns
        -------
        str
            命令中使用的提供者。

        Raises
        ------
        OpenBBError
            当优先级列表中的所有提供者都失败时引发错误。
        """
        if choice is None:
            commands = self._command_runner.user_settings.defaults.commands
            providers = (
                commands.get(command, {}).get("provider", []) or default_priority
            )
            tries = []
            if len(providers) == 1:
                return providers[0]
            for p in providers:
                result = self._check_credentials(p)
                if result:
                    return p
                if result is False:
                    tries.append((p, "missing credentials"))
                else:
                    tries.append((p, f"not installed, please install openbb-{p}"))

            msg = "\n  ".join([f"* '{pair[0]}' -> {pair[1]}" for pair in tries])
            raise OpenBBError(f"Provider fallback failed.\n[Providers]\n  {msg}")
        return choice
