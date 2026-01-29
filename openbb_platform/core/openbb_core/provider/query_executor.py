"""查询执行模块。"""

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.provider import Provider
from openbb_core.provider.registry import Registry, RegistryLoader
from pydantic import SecretStr


class QueryExecutor:
    """执行来自提供者查询的类。"""

    def __init__(self, registry: Registry | None = None) -> None:
        """初始化查询执行器。"""
        self.registry = registry or RegistryLoader.from_extensions()

    def get_provider(self, provider_name: str) -> Provider:
        """从注册表中获取提供者。"""
        name = provider_name.lower()
        if name not in self.registry.providers:
            raise OpenBBError(
                f"在注册表中未找到提供者 '{name}'。可用提供者：{list(self.registry.providers.keys())}"
            )
        return self.registry.providers[name]

    def get_fetcher(self, provider: Provider, model_name: str) -> type[Fetcher]:
        """从提供者获取获取器。"""
        if model_name not in provider.fetcher_dict:
            raise OpenBBError(
                f"在提供者 '{provider.name}' 中未找到模型 '{model_name}' 的获取器。"
            )
        return provider.fetcher_dict[model_name]

    @staticmethod
    def filter_credentials(
        credentials: dict[str, SecretStr] | None,
        provider: Provider,
        require_credentials: bool,
    ) -> dict[str, str]:
        """过滤凭据并检查它们是否符合提供者要求。"""
        filtered_credentials = {}

        if provider.credentials:
            if credentials is None:
                credentials = {}

            for c in provider.credentials:
                v = credentials.get(c)
                secret = v.get_secret_value() if v else None
                if c not in credentials or not secret:
                    if require_credentials:
                        website = provider.website or ""
                        extra_msg = f" 请查看 {website} 以获取。" if website else ""
                        raise OpenBBError(
                            f"缺少凭据 '{c}'。{extra_msg} 请参阅有关设置提供者凭据的文档 "
                            "credentials at https://docs.openbb.co/platform/settings/user_settings/api_keys."
                        )
                else:
                    filtered_credentials[c] = secret

        return filtered_credentials

    async def execute(
        self,
        provider_name: str,
        model_name: str,
        params: dict[str, Any],
        credentials: dict[str, SecretStr] | None = None,
        **kwargs: Any,
    ) -> Any:
        """执行查询。

        Parameters
        ----------
        provider_name : str
            提供者名称，例如："fmp"。
        model_name : str
            模型名称，例如："EquityHistorical"。
        params : Dict[str, Any]
            查询参数，例如：{"symbol": "AAPL"}
        credentials : Optional[Dict[str, SecretStr]], optional
            提供者的凭据，默认为 None
            例如，{"fmp_api_key": SecretStr("1234")}。

        Returns
        -------
        Any
            查询结果。
        """
        provider = self.get_provider(provider_name)
        fetcher = self.get_fetcher(provider, model_name)
        filtered_credentials = self.filter_credentials(
            credentials, provider, fetcher.require_credentials
        )
        return await fetcher.fetch_data(params, filtered_credentials, **kwargs)
