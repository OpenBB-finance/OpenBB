"""查询类。"""

import warnings
from dataclasses import asdict
from typing import Any

from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    ProviderInterface,
    StandardParams,
)


class Query:
    """查询类。"""

    def __init__(
        self,
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> None:
        """初始化查询类。"""
        self.cc = cc
        original = asdict(provider_choices)
        self.provider = original.get("provider")
        self.standard_params = standard_params
        self.extra_params = extra_params
        self.name = self.standard_params.__class__.__name__
        self.provider_interface = ProviderInterface()

    def filter_extra_params(
        self,
        extra_params: ExtraParams,
        provider_name: str,
    ) -> dict[str, Any]:
        """根据提供者过滤额外参数，如果不支持则发出警告。"""
        original = asdict(extra_params)
        filtered = {}

        query = extra_params.__class__.__name__
        fields = asdict(self.provider_interface.params[query]["extra"]())  # type: ignore

        for k, v in original.items():
            f = fields[k]
            providers = f.title.split(",") if hasattr(f, "title") else []

            # 我们仅在值不是默认值时进行过滤/警告，因为 fastapi
            # Depends 总是发送默认值，即使它不在请求中。
            if v != f.default:
                if provider_name in providers:
                    filtered[k] = v
                else:
                    available = ", ".join(providers)
                    warnings.warn(
                        message=f"参数 '{k}' 不被 {provider_name} 支持。可用于：{available}。",
                        category=OpenBBWarning,
                    )

        return filtered

    async def execute(self) -> Any:
        """执行查询。"""
        standard_dict = asdict(self.standard_params)
        extra_dict = (
            self.filter_extra_params(self.extra_params, self.provider) if self.extra_params else {}  # type: ignore
        )
        query_executor = self.provider_interface.create_executor()

        return await query_executor.execute(
            provider_name=self.provider,
            model_name=self.name,
            params={**standard_dict, **extra_dict},
            credentials=self.cc.user_settings.credentials.model_dump(),
            preferences=self.cc.user_settings.preferences.model_dump(),
        )
