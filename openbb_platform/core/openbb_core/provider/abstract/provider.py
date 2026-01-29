"""Provider 抽象类。"""

from openbb_core.provider.abstract.fetcher import Fetcher


class Provider:
    """充当提供者扩展入口点，必须由每个提供者创建。"""

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def __init__(
        self,
        name: str,
        description: str,
        website: str | None = None,
        credentials: list[str] | None = None,
        fetcher_dict: dict[str, type[Fetcher]] | None = None,
        repr_name: str | None = None,
        deprecated_credentials: dict[str, str | None] | None = None,
        instructions: str | None = None,
    ) -> None:
        """初始化提供者。

        Parameters
        ----------
        name : str
            提供者名称。
        description : str
            提供者描述。
        website : Optional[str]
            提供者网站，默认为 None。
        credentials : Optional[List[str]]
            所需凭据列表，默认为 None。
        fetcher_dict : Optional[Dict[str, Type[Fetcher]]]
            fetcher 字典，默认为 None。
        repr_name: Optional[str]
            提供者全名，默认为 None。
        deprecated_credentials: Optional[Dict[str, Optional[str]]]
            已弃用凭据到当前名称的映射，默认为 None。
        instructions: Optional[str]
            如何设置提供者的说明。例如，如何获取 API 密钥。
        """
        self.name = name
        self.description = description
        self.website = website
        self.fetcher_dict = fetcher_dict or {}
        if credentials is None:
            self.credentials: list = []
        else:
            self.credentials = []
            for c in credentials:
                self.credentials.append(f"{self.name.lower()}_{c}")
        self.repr_name = repr_name
        self.deprecated_credentials = deprecated_credentials
        self.instructions = instructions
