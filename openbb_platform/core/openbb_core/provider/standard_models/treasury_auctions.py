"""美国国债拍卖标准模型。"""

from datetime import (
    date as dateType,
    datetime,
    timedelta,
)
from typing import Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from pydantic import Field, model_validator


class USTreasuryAuctionsQueryParams(QueryParams):
    """美国国债拍卖查询。"""

    __json_schema_extra__ = {
        "security_type": {
            "choices": ["bill", "note", "bond", "cmb", "tips", "frn"],
        }
    }

    security_type: Literal["bill", "note", "bond", "cmb", "tips", "frn"] | None = Field(
        default=None,
        description="用于仅返回特定类型的证券。",
    )
    cusip: str | None = Field(
        default=None,
        description="按 CUSIP 筛选证券。",
    )
    page_size: int | None = Field(
        default=None,
        description="要返回的最大结果数；使用 pagesize 时还必须包含 pagenum。",
    )
    page_num: int | None = Field(
        default=None,
        description="显示结果的第一页页码；与每页大小结合使用。",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " 默认为 90 天前。",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "") + " 默认为今天。",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_dates(cls, values) -> dict:
        """验证查询参数。"""
        if not isinstance(values, dict):
            return values

        if values.get("start_date") is None:
            values["start_date"] = (datetime.now() - timedelta(days=90)).strftime(
                "%Y-%m-%d"
            )
        if values.get("end_date") is None:
            values["end_date"] = datetime.now().strftime("%Y-%m-%d")
        return values


class USTreasuryAuctionsData(Data):
    """美国国债拍卖数据。"""

    cusip: str = Field(description="证券的 CUSIP。")
    issue_date: dateType = Field(
        description="证券的出票日期。",
    )
    security_type: Literal["Bill", "Note", "Bond", "CMB", "TIPS", "FRN"] = Field(
        description="证券类型。",
    )
    security_term: str = Field(
        description="证券期限。",
    )
    maturity_date: dateType = Field(
        description="证券的到期日期。",
    )
    interest_rate: float | None = Field(
        default=None,
        description="证券利率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    cpi_on_issue_date: float | None = Field(
        default=None,
        description="证券出票日期的参考物价指数 (CPI) 利率。",
    )
    cpi_on_dated_date: float | None = Field(
        default=None,
        description="证券计息起始日期的参考物价指数 (CPI) 利率。",
    )
    announcement_date: dateType | None = Field(
        default=None,
        description="证券的公告日期。",
    )
    auction_date: dateType | None = Field(
        default=None,
        description="证券的拍卖日期。",
    )
    auction_date_year: int | None = Field(
        default=None,
        description="证券的拍卖年份。",
    )
    dated_date: dateType | None = Field(
        default=None,
        description="证券的计息起始日期。",
    )
    first_payment_date: dateType | None = Field(
        default=None,
        description="证券的首次付款日期。",
    )
    accrued_interest_per_100: float | None = Field(
        default=None,
        description="每 100 美元的应计利息。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    accrued_interest_per_1000: float | None = Field(
        default=None,
        description="每 1000 美元的应计利息。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    adjusted_accrued_interest_per_100: float | None = Field(
        default=None,
        description="调整后的每 100 美元应计利息。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    adjusted_accrued_interest_per_1000: float | None = Field(
        default=None,
        description="调整后的每 1000 美元应计利息。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    adjusted_price: float | None = Field(
        default=None,
        description="调整后价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    allocation_percentage: float | None = Field(
        default=None,
        description="分配百分比，作为归一化百分点。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    allocation_percentage_decimals: float | None = Field(
        default=None,
        description="分配百分比的小数位数。",
    )
    announced_cusip: str | None = Field(
        default=None,
        description="证券公布的 CUSIP。",
    )
    auction_format: str | None = Field(
        default=None,
        description="证券的拍卖形式。",
    )
    avg_median_discount_rate: float | None = Field(
        default=None,
        description="证券的平均中位贴现率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    avg_median_investment_rate: float | None = Field(
        default=None,
        description="证券的平均中位投资率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    avg_median_price: float | None = Field(
        default=None,
        description="为证券支付的平均中位价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    avg_median_discount_margin: float | None = Field(
        default=None,
        description="证券的平均中位贴现边际。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    avg_median_yield: float | None = Field(
        default=None,
        description="证券的平均中位收益率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    back_dated: Literal["Yes", "No"] | None = Field(
        default=None,
        description="证券是否为追溯日期。",
    )
    back_dated_date: dateType | None = Field(
        default=None,
        description="证券的追溯日期。",
    )
    bid_to_cover_ratio: float | None = Field(
        default=None,
        description="证券的认购倍数 (BTC Ratio)。",
    )
    call_date: dateType | None = Field(
        default=None,
        description="证券的赎回日期。",
    )
    callable: Literal["Yes", "No"] | None = Field(
        default=None,
        description="证券是否可赎回。",
    )
    called_date: dateType | None = Field(
        default=None,
        description="证券的被赎回日期。",
    )
    cash_management_bill: Literal["Yes", "No"] | None = Field(
        default=None,
        description="证券是否为现金管理国库券。",
    )
    closing_time_competitive: str | None = Field(
        default=None,
        description="证券竞争性投标的截止时间。",
    )
    closing_time_non_competitive: str | None = Field(
        default=None,
        description="证券非竞争性投标的截止时间。",
    )
    competitive_accepted: int | None = Field(
        default=None,
        description="证券竞争性投标的接受价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    competitive_accepted_decimals: int | None = Field(
        default=None,
        description="竞争性投标接受值的小数位数。",
    )
    competitive_tendered: int | None = Field(
        default=None,
        description="证券竞争性投标的投标价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    competitive_tenders_accepted: Literal["Yes", "No"] | None = Field(
        default=None,
        description="证券是否接受竞争性投标。",
    )
    corp_us_cusip: str | None = Field(
        default=None,
        description="证券的 CUSIP。",
    )
    cpi_base_reference_period: str | None = Field(
        default=None,
        description="证券的物价指数 (CPI) 基准参考期。",
    )
    currently_outstanding: int | None = Field(
        default=None,
        description="证券当前未偿还的金额。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    direct_bidder_accepted: int | None = Field(
        default=None,
        description="证券直接投标人的接受价值。",
    )
    direct_bidder_tendered: int | None = Field(
        default=None,
        description="证券直接投标人的投标价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    est_amount_of_publicly_held_maturing_security: int | None = Field(
        default=None,
        description="证券中由公众持有的到期证券的估计金额。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    fima_included: Literal["Yes", "No"] | None = Field(
        default=None,
        description="证券是否包含在 FIMA（外国和国际货币当局）中。",
    )
    fima_non_competitive_accepted: int | None = Field(
        default=None,
        description="来自 FIMA 的非竞争性投标接受价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    fima_non_competitive_tendered: int | None = Field(
        default=None,
        description="来自 FIMA 的非竞争性投标价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    first_interest_period: str | None = Field(
        default=None,
        description="证券的首个计息期。",
    )
    first_interest_payment_date: dateType | None = Field(
        default=None,
        description="证券的首次利息支付日期。",
    )
    floating_rate: Literal["Yes", "No"] | None = Field(
        default=None,
        description="证券是否为浮动利率。",
    )
    frn_index_determination_date: dateType | None = Field(
        default=None,
        description="证券的浮动利率债指数确定日期。",
    )
    frn_index_determination_rate: float | None = Field(
        default=None,
        description="证券的浮动利率债指数确定利率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    high_discount_rate: float | None = Field(
        default=None,
        description="证券的高贴现率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    high_investment_rate: float | None = Field(
        default=None,
        description="证券的高投资率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    high_price: float | None = Field(
        default=None,
        description="拍卖时证券的高价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    high_discount_margin: float | None = Field(
        default=None,
        description="证券的高贴现边际。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    high_yield: float | None = Field(
        default=None,
        description="拍卖时证券的高收益率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    index_ratio_on_issue_date: float | None = Field(
        default=None,
        description="证券出票日期的指数比率。",
    )
    indirect_bidder_accepted: int | None = Field(
        default=None,
        description="证券间接投标人的接受价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    indirect_bidder_tendered: int | None = Field(
        default=None,
        description="证券间接投标人的投标价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    interest_payment_frequency: str | None = Field(
        default=None,
        description="证券的利息支付频率。",
    )
    low_discount_rate: float | None = Field(
        default=None,
        description="证券的低贴现率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    low_investment_rate: float | None = Field(
        default=None,
        description="证券的低投资率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    low_price: float | None = Field(
        default=None,
        description="拍卖时证券的低价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    low_discount_margin: float | None = Field(
        default=None,
        description="证券的低贴现边际。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    low_yield: float | None = Field(
        default=None,
        description="拍卖时证券的低收益率。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    maturing_date: dateType | None = Field(
        default=None,
        description="证券的到期日期。",
    )
    max_competitive_award: int | None = Field(
        default=None,
        description="拍卖时的最大竞争性奖励。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    max_non_competitive_award: int | None = Field(
        default=None,
        description="拍卖时的最大非竞争性奖励。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    max_single_bid: int | None = Field(
        default=None,
        description="拍卖时的最大单笔投标。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    min_bid_amount: int | None = Field(
        default=None,
        description="拍卖时的最低投标金额。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    min_strip_amount: int | None = Field(
        default=None,
        description="拍卖时的最低剥离金额。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    min_to_issue: int | None = Field(
        default=None,
        description="拍卖时的最低发行量。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    multiples_to_bid: int | None = Field(
        default=None,
        description="拍卖时的投标倍数。",
    )
    multiples_to_issue: int | None = Field(
        default=None,
        description="拍卖时的发行倍数。",
    )
    nlp_exclusion_amount: int | None = Field(
        default=None,
        description="拍卖时的净多头头寸 (NLP) 排除金额。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    nlp_reporting_threshold: int | None = Field(
        default=None,
        description="拍卖时的净多头头寸 (NLP) 报告阈值。",
    )
    non_competitive_accepted: int | None = Field(
        default=None,
        description="证券非竞争性投标人的接受价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    non_competitive_tenders_accepted: Literal["Yes", "No"] | None = Field(
        default=None,
        description="拍卖是否接受非竞争性投标。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    offering_amount: int | None = Field(
        default=None,
        description="拍卖的发售金额。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    original_cusip: str | None = Field(
        default=None,
        description="证券的原始 CUSIP。",
    )
    original_dated_date: dateType | None = Field(
        default=None,
        description="证券的原始计息起始日期。",
    )
    original_issue_date: dateType | None = Field(
        default=None,
        description="证券的原始出票日期。",
    )
    original_security_term: str | None = Field(
        default=None,
        description="证券的原始期限。",
    )
    pdf_announcement: str | None = Field(
        default=None,
        description="证券公告的 PDF 文件名。",
    )
    pdf_competitive_results: str | None = Field(
        default=None,
        description="证券竞争性结果的 PDF 文件名。",
    )
    pdf_non_competitive_results: str | None = Field(
        default=None,
        description="证券非竞争性结果的 PDF 文件名。",
    )
    pdf_special_announcement: str | None = Field(
        default=None,
        description="特别公告的 PDF 文件名。",
    )
    price_per_100: float | None = Field(
        default=None,
        description="证券每 100 美元的价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    primary_dealer_accepted: int | None = Field(
        default=None,
        description="证券的一级交易商接受价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    primary_dealer_tendered: int | None = Field(
        default=None,
        description="证券的一级交易商投标价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    reopening: Literal["Yes", "No"] | None = Field(
        default=None,
        description="拍卖是否重新开启。",
    )
    security_term_day_month: str | None = Field(
        default=None,
        description="以天或月表示的证券期限。",
    )
    security_term_week_year: str | None = Field(
        default=None,
        description="以周或年表示的证券期限。",
    )
    series: str | None = Field(
        default=None,
        description="证券的系列名称。",
    )
    soma_accepted: int | None = Field(
        default=None,
        description="证券的 SOMA 接受价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    soma_holdings: int | None = Field(
        default=None,
        description="证券的 SOMA 持有量。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    soma_included: Literal["Yes", "No"] | None = Field(
        default=None,
        description="证券是否包含 SOMA（系统公开市场账户）。",
    )
    soma_tendered: int | None = Field(
        default=None,
        description="证券的 SOMA 投标价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    spread: float | None = Field(
        default=None,
        description="证券的利差。",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    standard_payment_per_1000: float | None = Field(
        default=None,
        description="证券每 1000 美元的标准付款。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    strippable: Literal["Yes", "No"] | None = Field(
        default=None,
        description="证券是否可剥离。",
    )
    term: str | None = Field(
        default=None,
        description="证券期限。",
    )
    tiin_conversion_factor_per_1000: float | None = Field(
        default=None,
        description="证券每 1000 美元的 TIIN 转换因子。",
    )
    tips: Literal["Yes", "No"] | None = Field(
        default=None,
        description="证券是否为通胀保值国债 (TIPS)。",
    )
    total_accepted: int | None = Field(
        default=None,
        description="拍卖时的总接受价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    total_tendered: int | None = Field(
        default=None,
        description="拍卖时的总投标价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    treasury_retail_accepted: int | None = Field(
        default=None,
        description="证券零售额部分的接受价值。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    treasury_retail_tenders_accepted: Literal["Yes", "No"] | None = Field(
        default=None,
        description="是否接受来自零售额部分的投标。",
    )
    type: str | None = Field(
        default=None,
        description="发行类型。这可能与证券类型不同。",
    )
    unadjusted_accrued_interest_per_1000: float | None = Field(
        default=None,
        description="证券每 1000 美元的未调整应计利息。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    unadjusted_price: float | None = Field(
        default=None,
        description="证券的未调整价格。",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    updated_timestamp: datetime | None = Field(
        default=None,
        description="证券的更新时间戳。",
    )
    xml_announcement: str | None = Field(
        default=None,
        description="证券公告的 XML 文件名。",
    )
    xml_competitive_results: str | None = Field(
        default=None,
        description="证券竞争性结果的 XML 文件名。",
    )
    xml_special_announcement: str | None = Field(
        default=None,
        description="特别公告的 XML 文件名。",
    )
    tint_cusip1: str | None = Field(
        default=None,
        description="Tint CUSIP 1.",
    )
    tint_cusip2: str | None = Field(
        default=None,
        description="Tint CUSIP 2.",
    )
