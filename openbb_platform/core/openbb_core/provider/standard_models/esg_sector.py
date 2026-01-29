"""ESG 行业标准模型。"""

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams


class ESGSectorQueryParams(QueryParams):
    """ESG 行业查询。

    参数
    ---------
    year : int
        获取 ESG 信息的年份
    """

    year: int


class ESGSectorData(Data):
    """ESG 行业数据。

    返回
    -------
    year : int
        ESG 行业的年份。
    sector : str
        ESG 行业的行业。
    environmental_score : float
        ESG 行业的环境评分。
    social_score : float
        ESG 行业的社会评分。
    governance_score : float
        ESG 行业的治理评分。
    esg_score : float
        ESG 行业的 ESG 评分。
    """

    year: int
    sector: str
    environmental_score: float
    social_score: float
    governance_score: float
    esg_score: float
