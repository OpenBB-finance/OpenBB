"""Intrinio Financial Ratios Model."""

import warnings
from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_ratios import (
    FinancialRatiosData,
    FinancialRatiosQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import ClientResponse, amake_requests
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field, field_validator

_warn = warnings.warn


class IntrinioFinancialRatiosQueryParams(FinancialRatiosQueryParams):
    """Intrinio Financial Ratios Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """

    period: Literal["annual", "quarter", "ttm", "ytd"] = Field(
        default="annual",
        description=QUERY_DESCRIPTIONS.get("period", ""),
    )
    fiscal_year: Optional[int] = Field(
        default=None,
        description="The specific fiscal year.  Reports do not go beyond 2008.",
    )

    @field_validator("symbol", mode="after", check_fields=False)
    @classmethod
    def handle_symbol(cls, v) -> str:
        """Handle symbols with a dash and replace it with a dot for Intrinio."""
        return v.replace("-", ".")


class IntrinioFinancialRatiosData(FinancialRatiosData):
    """Intrinio Financial Ratios Data."""

    __alias_dict__ = {
        "net_operating_profit_after_tax_margin": "nopatmargin",
        "invested_capital_turnover": "investedcapitalturnover",
        "book_value_per_share": "bookvaluepershare",
        "tangible_book_value_per_share": "tangiblebookvaluepershare",
        "price_to_book": "pricetobook",
        "price_to_tangible_book": "pricetotangiblebook",
        "price_to_revenue": "pricetorevenue",
        "price_to_earnings": "pricetoearnings",
        "dividend_yield": "dividendyield",
        "earnings_yield": "earningsyield",
        "ev_to_invested_capital": "evtoinvestedcapital",
        "ev_to_sales": "evtorevenue",
        "ev_to_ebitda": "evtoebitda",
        "ev_to_ebit": "evtoebit",
        "ev_to_nopat": "evtonopat",
        "ev_to_operating_cash_flow": "evtoocf",
        "ev_to_free_cash_flow": "evtofcff",
        "gross_margin": "grossmargin",
        "ebitda_margin": "ebitdamargin",
        "operating_margin": "operatingmargin",
        "ebit_margin": "ebitmargin",
        "net_profit_margin": "profitmargin",
        "cost_of_revenue_to_revenue": "costofrevtorevenue",
        "sga_expense_to_revenue": "sgaextorevenue",
        "rd_expense_to_revenue": "rdextorevenue",
        "op_expense_to_revenue": "opextorevenue",
        "tax_burden_percent": "taxburdenpct",
        "interest_burden_percent": "interestburdenpct",
        "effective_tax_rate": "efftaxrate",
        "asset_turnover": "assetturnover",
        "receivables_turnover": "arturnover",
        "inventory_turnover": "invturnover",
        "fixed_asset_turnover": "faturnover",
        "payables_turnover": "apturnover",
        "days_of_sales_outstanding": "dso",
        "days_of_inventory_outstanding": "dio",
        "days_payable_outstanding": "dpo",
        "cash_conversion_cycle": "ccc",
        "financial_leverage": "finleverage",
        "leverage_ratio": "leverageratio",
        "compound_leverage_factor": "compoundleveragefactor",
        "long_term_debt_to_equity": "ltdebttoequity",
        "debt_to_equity": "debttoequity",
        "return_on_invested_capital": "roic",
        "net_non_operating_expense_percent": "nnep",
        "roic_nnep_spread": "roicnnepspread",
        "return_on_net_non_operating_assets": "rnnoa",
        "return_on_equity": "roe",
        "cash_returned_on_invested_capital": "croic",
        "operating_return_on_assets": "oroa",
        "return_on_assets": "roa",
        "non_controlling_interest_sharing_ratio": "noncontrollinginterestsharingratio",
        "return_on_common_equity": "roce",
        "dividend_payout_ratio": "divpayoutratio",
        "augmented_payout_ratio": "augmentedpayoutratio",
        "operating_cash_flow_to_capex": "ocftocapex",
        "short_term_debt_to_capitalization": "stdebttocap",
        "long_term_debt_to_capitalization": "ltdebttocap",
        "debt_to_capitalization": "debttototalcapital",
        "preferred_equity_to_capitalization": "preferredtocap",
        "non_controlling_interest_to_capitalization": "noncontrolinttocap",
        "equity_to_capitalization": "commontocap",
        "debt_to_ebitda": "debttoebitda",
        "net_debt_to_ebitda": "netdebttoebitda",
        "long_term_debt_to_ebitda": "ltdebttoebitda",
        "debt_to_nopat": "debttonopat",
        "net_debt_to_nopat": "netdebttonopat",
        "long_term_debt_to_nopat": "ltdebttonopat",
        "altman_z_score": "altmanzscore",
        "ebit_to_interest_expense": "ebittointerestex",
        "nopat_to_interest_expense": "nopattointerestex",
        "ebit_less_capex_to_interest_expense": "ebitlesscapextointerestex",
        "nopat_less_capex_to_interest_expense": "nopatlesscapextointex",
        "operating_cash_flow_to_interest_expense": "ocftointerestex",
        "operating_cash_flow_less_capex_to_interest_expense": "ocflesscapextointerestex",
        "free_cash_flow_to_interest_expense": "fcfftointerestex",
        "current_ratio": "curratio",
        "quick_ratio": "quickratio",
        "debt_free_cash_and_free_nwc_to_revenue": "dfcfnwctorev",
        "debt_free_nwc_to_revenue": "dfnwctorev",
        "net_working_capital_to_revenue": "nwctorev",
        "normalized_nopat_margin": "normalizednopatmargin",
        "pre_tax_income_margin": "pretaxincomemargin",
        "adjusted_basic_eps": "adjbasiceps",
        "adjusted_diluted_eps": "adjdilutedeps",
        "adjusted_basic_and_diluted_eps": "adjbasicdilutedeps",
        "return_on_equity_simple": "roe_simple",
    }

    dividend_yield: Optional[float] = Field(
        default=None,
        description="Dividend yield, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    earnings_yield: Optional[float] = Field(
        default=None,
        description="Earnings yield, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    gross_margin: Optional[float] = Field(
        default=None,
        description="Gross margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    adjusted_basic_eps: Optional[float] = Field(
        default=None,
        description="Adjusted basic earnings per share",
    )
    adjusted_diluted_eps: Optional[float] = Field(
        default=None,
        description="Adjusted diluted earnings per share",
    )
    adjusted_basic_and_diluted_eps: Optional[float] = Field(
        default=None,
        description="Adjusted basic and diluted earnings per share",
    )
    book_value_per_share: Optional[float] = Field(
        default=None,
        description="Book value per share",
    )
    tangible_book_value_per_share: Optional[float] = Field(
        default=None,
        description="Tangible book value per share",
    )
    price_to_book: Optional[float] = Field(
        default=None,
    )
    price_to_tangible_book: Optional[float] = Field(
        default=None,
        description="Price to tangible book ratio",
    )
    price_to_revenue: Optional[float] = Field(
        default=None,
        description="Price to revenue",
    )
    price_to_earnings: Optional[float] = Field(
        default=None,
        description="Price to earnings",
    )
    ev_to_sales: Optional[float] = Field(
        default=None,
        description="Enterprise value to sales ratio",
    )
    ev_to_invested_capital: Optional[float] = Field(
        default=None,
        description="Enterprise value to invested capital ratio",
    )
    current_ratio: Optional[float] = Field(
        default=None,
        description="Current ratio",
    )
    quick_ratio: Optional[float] = Field(
        default=None,
        description="Quick ratio",
    )
    cash_conversion_cycle: Optional[float] = Field(
        default=None,
        description="Cash conversion cycle",
    )
    debt_free_nwc_to_revenue: Optional[float] = Field(
        default=None,
        description="Debt free net working capital to revenue ratio.",
    )
    debt_free_cash_and_free_nwc_to_revenue: Optional[float] = Field(
        default=None,
        description="Debt free cash and free net working capital to revenue ratio.",
    )
    net_working_capital_to_revenue: Optional[float] = Field(
        default=None,
        description="Net working capital to revenue ratio.",
    )
    debt_free_cash_and_free_nwc_to_revenue: Optional[float] = Field(
        default=None,
        description="Debt free cash and free net working capital to revenue ratio.",
    )
    cost_of_revenue_to_revenue: Optional[float] = Field(
        default=None,
        description="Cost of revenue to revenue ratio.",
    )
    sga_expense_to_revenue: Optional[float] = Field(
        default=None,
        description="SGA expense to revenue ratio.",
    )
    rd_expense_to_revenue: Optional[float] = Field(
        default=None,
    )
    op_expense_to_revenue: Optional[float] = Field(
        default=None,
    )
    days_of_sales_outstanding: Optional[float] = Field(
        default=None,
        description="Days of sales outstanding",
    )
    days_of_inventory_outstanding: Optional[float] = Field(
        default=None,
        description="Days of inventory outstanding",
    )
    days_payable_outstanding: Optional[float] = Field(
        default=None,
        description="Days payable outstanding",
    )
    asset_turnover: Optional[float] = Field(
        default=None,
        description="Asset turnover",
    )
    inventory_turnover: Optional[float] = Field(
        default=None,
        description="Inventory turnover",
    )
    fixed_asset_turnover: Optional[float] = Field(
        default=None,
        description="Fixed asset turnover",
    )
    invested_capital_turnover: Optional[float] = Field(
        default=None,
        description="Invested capital turnover",
    )
    receivables_turnover: Optional[float] = Field(
        default=None,
        description="Receivables turnover",
    )
    payables_turnover: Optional[float] = Field(
        default=None,
        description="Payables turnover",
    )
    leverage_ratio: Optional[float] = Field(
        default=None,
        description="Leverage ratio",
    )
    financial_leverage: Optional[float] = Field(
        default=None,
        description="Financial leverage",
    )
    compound_leverage_factor: Optional[float] = Field(
        default=None,
        description="Compound leverage factor",
    )
    debt_to_equity: Optional[float] = Field(
        default=None,
        description="Debt to equity ratio",
    )
    long_term_debt_to_equity: Optional[float] = Field(
        default=None,
        description="Long term debt to equity ratio",
    )
    short_term_debt_to_capitalization: Optional[float] = Field(
        default=None,
        description="Short term debt to capitalization ratio",
    )
    long_term_debt_to_capitalization: Optional[float] = Field(
        default=None,
        description="Long term debt to capitalization ratio",
    )
    debt_to_capitalization: Optional[float] = Field(
        default=None,
        description="Debt to capitalization ratio",
    )
    debt_to_ebitda: Optional[float] = Field(
        default=None,
        description="Debt to EBITDA ratio",
    )
    long_term_debt_to_ebitda: Optional[float] = Field(
        default=None,
        description="Long term debt to EBITDA ratio",
    )
    net_debt_to_ebitda: Optional[float] = Field(
        default=None,
        description="Net debt to EBITDA ratio",
    )
    ebitda_margin: Optional[float] = Field(
        default=None,
        description="EBITDA margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ev_to_ebitda: Optional[float] = Field(
        default=None,
        description="Enterprise value to EBITDA ratio",
    )
    ebit_margin: Optional[float] = Field(
        default=None,
        description="EBIT margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ev_to_ebit: Optional[float] = Field(
        default=None,
        description="Enterprise value to EBIT ratio",
    )
    interest_burden_percent: Optional[float] = Field(
        default=None,
        description="Interest burden percent (normalized)",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ebit_to_interest_expense: Optional[float] = Field(
        default=None,
        description="EBIT to interest expense ratio",
    )
    ebit_less_capex_to_interest_expense: Optional[float] = Field(
        default=None,
        description="EBIT less capital expenditure to interest expense ratio.",
    )
    pre_tax_income_margin: Optional[float] = Field(
        default=None,
        description="Pre tax income margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    tax_burden_percent: Optional[float] = Field(
        default=None,
        description="Tax burden percent (normalized)",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    effective_tax_rate: Optional[float] = Field(
        default=None,
        description="Effective tax rate, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    operating_margin: Optional[float] = Field(
        default=None,
        description="Operating margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ev_to_operating_cash_flow: Optional[float] = Field(
        default=None,
        description="Enterprise value to operating cash flow ratio.",
    )
    ev_to_invested_capital: Optional[float] = Field(
        default=None,
        description="Enterprise value to invested capital ratio.",
    )
    operating_cash_flow_to_capex: Optional[float] = Field(
        default=None,
        description="Operating cash flow to capital expenditure ratio.",
    )
    operating_cash_flow_to_interest_expense: Optional[float] = Field(
        default=None,
        description="Operating cash flow to interest expense ratio.",
    )
    operating_cash_flow_less_capex_to_interest_expense: Optional[float] = Field(
        default=None,
        description="Operating cash flow less capital expenditure to interest expense ratio",
    )
    net_operating_profit_after_tax_margin: Optional[float] = Field(
        default=None,
        description="Net operating profit after tax margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ev_to_nopat: Optional[float] = Field(
        default=None,
        description="Enterprise value to net operating profit after tax ratio",
    )
    debt_to_nopat: Optional[float] = Field(
        default=None,
        description="Debt to net operating profit after tax ratio",
    )
    long_term_debt_to_nopat: Optional[float] = Field(
        default=None,
        description="Long term debt to net operating profit after tax ratio",
    )
    net_debt_to_nopat: Optional[float] = Field(
        default=None,
        description="Net debt to net operating profit after tax ratio",
    )
    nopat_less_capex_to_interest_expense: Optional[float] = Field(
        default=None,
        description="Net operating profit after tax less capital expenditure to interest expense ratio",
    )
    nopat_to_interest_expense: Optional[float] = Field(
        default=None,
        description="Net operating profit after tax to interest expense ratio",
    )
    normalized_nopat_margin: Optional[float] = Field(
        default=None,
        description="Normalized net operating profit after tax margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    net_profit_margin: Optional[float] = Field(
        default=None,
        description="Net profit margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    free_cash_flow_to_interest_expense: Optional[float] = Field(
        default=None,
        description="Free cash flow to interest expense ratio.",
    )
    ev_to_free_cash_flow: Optional[float] = Field(
        default=None,
        description="Enterprise value to free cash flow ratio",
    )
    return_on_invested_capital: Optional[float] = Field(
        default=None,
        description="Return on invested capital, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    net_non_operating_expense_percent: Optional[float] = Field(
        default=None,
        description="Net non operating expense as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    roic_nnep_spread: Optional[float] = Field(
        default=None,
        description="The spread between ROIC and net non operating expense percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_net_non_operating_assets: Optional[float] = Field(
        default=None,
        description="Return on net non operating assets, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    operating_return_on_assets: Optional[float] = Field(
        default=None,
        description="Operating return on assets, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_assets: Optional[float] = Field(
        default=None,
        description="Return on assets, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    cash_returned_on_invested_capital: Optional[float] = Field(
        default=None,
        description="Cash returned on invested capital, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_equity_simple: Optional[float] = Field(
        default=None,
        description="Return on equity simple, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_common_equity: Optional[float] = Field(
        default=None,
        description="Return on common equity, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on equity, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    equity_to_capitalization: Optional[float] = Field(
        default=None,
        description="Equity to capitalization ratio",
    )
    preferred_equity_to_capitalization: Optional[float] = Field(
        default=None,
        description="Preferred equity to capitalization ratio",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    non_controlling_interest_to_capitalization: Optional[float] = Field(
        default=None,
        description="Non controlling interest to capitalization ratio",
    )
    non_controlling_interest_sharing_ratio: Optional[float] = Field(
        default=None,
        description="Non controlling interest sharing ratio",
    )
    dividend_payout_ratio: Optional[float] = Field(
        default=None,
        description="Dividend payout ratio",
    )
    augmented_payout_ratio: Optional[float] = Field(
        default=None,
        description="Augmented payout ratio",
    )
    altman_z_score: Optional[float] = Field(
        default=None,
    )


class IntrinioFinancialRatiosFetcher(
    Fetcher[
        IntrinioFinancialRatiosQueryParams,
        List[IntrinioFinancialRatiosData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioFinancialRatiosQueryParams:
        """Transform the query params."""
        return IntrinioFinancialRatiosQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioFinancialRatiosQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""

        api_key = credentials.get("intrinio_api_key") if credentials else ""
        statement_code = "calculations"
        if query.period in ["quarter", "annual"]:
            period_type = "FY" if query.period == "annual" else "QTR"
        if query.period in ["ttm", "ytd"]:
            period_type = query.period.upper()

        fundamentals_data: Dict = {}

        base_url = "https://api-v2.intrinio.com"
        fundamentals_url = (
            f"{base_url}/companies/{query.symbol}/fundamentals?"
            f"statement_code={statement_code}&type={period_type}"
        )
        if query.fiscal_year is not None:
            if query.fiscal_year < 2008:
                _warn("Financials data is only available from 2008 and later.")
                query.fiscal_year = 2008
            fundamentals_url = fundamentals_url + f"&fiscal_year={query.fiscal_year}"
        fundamentals_url = fundamentals_url + f"&api_key={api_key}"
        fundamentals_data = (await get_data_one(fundamentals_url, **kwargs)).get(
            "fundamentals", []
        )
        ids = [item["id"] for item in fundamentals_data]
        ids = ids[: query.limit]

        async def callback(response: ClientResponse, _: Any) -> Dict:
            """Return the response."""
            statement_data = await response.json()
            return {
                "period_ending": statement_data["fundamental"]["end_date"],
                "fiscal_year": statement_data["fundamental"]["fiscal_year"],
                "fiscal_period": statement_data["fundamental"]["fiscal_period"],
                "calculations": statement_data["standardized_financials"],
            }

        urls = [
            f"https://api-v2.intrinio.com/fundamentals/{id}/standardized_financials?api_key={api_key}"
            for id in ids
        ]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioFinancialRatiosQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioFinancialRatiosData]:
        """Return the transformed data."""
        transformed_data: List[IntrinioFinancialRatiosData] = []

        tags = [
            "nopatmargin",
            "investedcapitalturnover",
            "bookvaluepershare",
            "tangiblebookvaluepershare",
            "pricetobook",
            "pricetotangiblebook",
            "pricetorevenue",
            "pricetoearnings",
            "dividendyield",
            "earningsyield",
            "evtoinvestedcapital",
            "evtorevenue",
            "evtoebitda",
            "evtoebit",
            "evtonopat",
            "evtoocf",
            "evtofcff",
            "grossmargin",
            "ebitdamargin",
            "operatingmargin",
            "ebitmargin",
            "profitmargin",
            "costofrevtorevenue",
            "sgaextorevenue",
            "rdextorevenue",
            "opextorevenue",
            "taxburdenpct",
            "interestburdenpct",
            "efftaxrate",
            "assetturnover",
            "arturnover",
            "invturnover",
            "faturnover",
            "apturnover",
            "dso",
            "dio",
            "dpo",
            "ccc",
            "finleverage",
            "leverageratio",
            "compoundleveragefactor",
            "ltdebttoequity",
            "debttoequity",
            "roic",
            "nnep",
            "roicnnepspread",
            "rnnoa",
            "roe",
            "croic",
            "oroa",
            "roa",
            "noncontrollinginterestsharingratio",
            "roce",
            "divpayoutratio",
            "augmentedpayoutratio",
            "ocftocapex",
            "stdebttocap",
            "ltdebttocap",
            "debttototalcapital",
            "preferredtocap",
            "noncontrolinttocap",
            "commontocap",
            "debttoebitda",
            "netdebttoebitda",
            "ltdebttoebitda",
            "debttonopat",
            "netdebttonopat",
            "ltdebttonopat",
            "altmanzscore",
            "ebittointerestex",
            "nopattointerestex",
            "ebitlesscapextointerestex",
            "nopatlesscapextointex",
            "ocftointerestex",
            "ocflesscapextointerestex",
            "fcfftointerestex",
            "curratio",
            "quickratio",
            "dfcfnwctorev",
            "dfnwctorev",
            "nwctorev",
            "normalizednopatmargin",
            "pretaxincomemargin",
            "adjbasiceps",
            "adjdilutedeps",
            "adjbasicdilutedeps",
            "roe_simple",
        ]

        for item in data:
            sub_dict: Dict[str, Any] = {}

            for sub_item in item["calculations"]:
                field_name = sub_item["data_tag"]["tag"]
                if field_name in tags:
                    sub_dict[field_name] = (
                        float(sub_item["value"])
                        if sub_item["value"] and sub_item["value"] != 0
                        else None
                    )

            sub_dict["period_ending"] = item["period_ending"]
            sub_dict["fiscal_year"] = item["fiscal_year"]
            sub_dict["fiscal_period"] = item["fiscal_period"]

            transformed_data.append(IntrinioFinancialRatiosData(**sub_dict))

        return transformed_data
