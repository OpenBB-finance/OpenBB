"""气象公报下载标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field, field_validator


class WeatherBulletinDownloadQueryParams(QueryParams):
    """气象公报查询。"""

    urls: str | dict | list = Field(
        kw_only=True,
        description="要下载的报告的 URL。",
    )

    @field_validator("urls", mode="before", check_fields=False)
    @classmethod
    def _validate_urls(cls, v):
        """验证 URL 输入。"""
        if isinstance(v, str):
            if "," in v:
                return v.split(",")
            return [v]
        if isinstance(v, dict) and "urls" in v:
            return v["urls"]
        if isinstance(v, list):
            return v
        raise ValueError("URL 格式无效。必须是字符串、字典或列表。")


class WeatherBulletinDownloadData(Data):
    """气象公报数据。"""

    content: str = Field(
        description="气象公报文档的 Base64 编码内容。",
    )
