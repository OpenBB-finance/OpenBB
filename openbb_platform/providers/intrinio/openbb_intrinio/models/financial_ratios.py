"""Intrinio Financial Ratios Model."""

from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.financial_ratios import (
    FinancialRatiosData,
    FinancialRatiosQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import ClientResponse, amake_requests
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field, field_validator


class IntrinioFinancialRatiosQueryParams(FinancialRatiosQueryParams):
    """Intrinio Financial Ratios Query.

    Source: https://docs.intrinio.com/documentation/web_api/get_company_fundamentals_v2
    Source: https://docs.intrinio.com/documentation/web_api/get_fundamental_standardized_financials_v2
    """

    __json_schema_extra__ = {
        "period": {
            "choices": ["annual", "quarter", "ttm", "ytd"],
        }
    }
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
        "tangible_book_value": "tangiblebookvaluepershare",
        "price_to_book_ratio": "pricetobook",
        "price_to_tangible_book_ratio": "pricetotangiblebook",
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
        "cost_of_rev_to_revenue": "costofrevtorevenue",
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
        "long_term_debt_equity_ratio": "ltdebttoequity",
        "debt_equity_ratio": "debttoequity",
        "return_on_invested_capital": "roic",
        "net_non_operating_expense_percent": "nnep",
        "roic_nnep_spread": "roicnnepspread",
        "return_on_net_non_operating_assets": "rnnoa",
        "return_on_equity": "roe",
        "cash_returned_on_invested_capitals": "croic",
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
        "non_controlling_interests_to_capitalization": "noncontrolinttocap",
        "equity_to_capitalization": "commontocap",
        "debt_to_ebitda": "debttoebitda",
        "net_debt_to_ebitda": "netdebttoebitda",
        "long_term_debt_to_ebita": "ltdebttoebitda",
        "debt_to_nopat": "debttonopat",
        "net_debt_to_nopat": "netdebttonopat",
        "long_term_debt_to_nopat": "ltdebttonopat",
        "altman_z_score": "altmanzscore",
        "ebit_to_interest_expense": "ebittointerestex",
        "nopat_to_intersest_expense": "nopattointerestex",
        "ebit_less_capex_to_interest_expense": "ebitlesscapextointerestex",
        "nopat_less_capex_to_interest_expense": "nopatlesscapextointex",
        "operating_cash_flow_to_interest_expense": "ocftointerestex",
        "operating_cash_flow_less_capex_to_interest_expense": "ocflesscapextointerestex",
        "free_cash_flow_to_interest_expense": "fcfftointerestex",
        "current_ratio": "curratio",
        "quick_ratio": "quickratio",
        "debt_free_cash_free_nwc_to_revenue": "dfcfnwctorev",
        "debt_free_nwc_to_revenue": "dfnwctorev",
        "net_working_capital_to_revenue": "nwctorev",
        "normalized_nopat_margin": "normalizednopatmargin",
        "pre_tax_income_margin": "pretaxincomemargin",
        "adjusted_basic_eps": "adjbasiceps",
        "adjusted_diluted_eps": "adjdilutedeps",
        "adjusted_basic_diluted_eps": "adjbasicdilutedeps",
        "return_on_equity_simple": "roe_simple",
    }


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
        elif query.period in ["ttm", "ytd"]:
            period_type = query.period.upper()
        else:
            raise OpenBBError(f"Period '{query.period}' not supported.")

        fundamentals_data: Dict = {}

        base_url = "https://api-v2.intrinio.com"
        fundamentals_url = (
            f"{base_url}/companies/{query.symbol}/fundamentals?"
            f"statement_code={statement_code}&type={period_type}"
        )
        if query.fiscal_year is not None:
            if query.fiscal_year < 2008:
                warn("Financials data is only available from 2008 and later.")
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
                "period_ending": statement_data["fundamental"]["end_date"],  # type: ignore
                "fiscal_year": statement_data["fundamental"]["fiscal_year"],  # type: ignore
                "fiscal_period": statement_data["fundamental"]["fiscal_period"],  # type: ignore
                "calculations": statement_data["standardized_financials"],  # type: ignore
            }

        urls = [
            f"https://api-v2.intrinio.com/fundamentals/{id}/standardized_financials?api_key={api_key}"
            for id in ids
        ]

        return await amake_requests(urls, callback, **kwargs)  # type: ignore

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
