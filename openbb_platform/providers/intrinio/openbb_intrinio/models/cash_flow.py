"""Intrinio Cash Flow Statement Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.cash_flow import (
    CashFlowStatementData,
    CashFlowStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import ClientResponse, amake_requests
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field, field_validator, model_validator


class IntrinioCashFlowStatementQueryParams(CashFlowStatementQueryParams):
    """Intrinio Cash Flow Statement Query.

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


class IntrinioCashFlowStatementData(CashFlowStatementData):
    """Intrinio Cash Flow Statement Data."""

    __alias_dict__ = {
        "cash_and_equivalents": "cashandequivalents",
        "acquisitions": "acquisitions",
        "amortization_expense": "amortizationexpense",
        "cash_income_taxes_paid": "cashincometaxespaid",
        "cash_interest_paid": "cashinterestpaid",
        "cash_interest_received": "cashinterestreceived",
        "depreciation_expense": "depreciationexpense",
        "divestitures": "divestitures",
        "effect_of_exchange_rate_changes": "effectofexchangeratechanges",
        "changes_in_operating_assets_and_liabilities": "increasedecreaseinoperatingcapital",
        "issuance_of_common_equity": "issuanceofcommonequity",
        "issuance_of_debt": "issuanceofdebt",
        "issuance_of_preferred_equity": "issuanceofpreferredequity",
        "loans_held_for_sale": "loansheldforsalenet",
        "net_cash_from_continuing_financing_activities": "netcashfromcontinuingfinancingactivities",
        "net_cash_from_continuing_investing_activities": "netcashfromcontinuinginvestingactivities",
        "net_cash_from_continuing_operating_activities": "netcashfromcontinuingoperatingactivities",
        "net_cash_from_discontinued_financing_activities": "netcashfromdiscontinuedfinancingactivities",
        "net_cash_from_discontinued_investing_activities": "netcashfromdiscontinuedinvestingactivities",
        "net_cash_from_discontinued_operating_activities": "netcashfromdiscontinuedoperatingactivities",
        "net_cash_from_financing_activities": "netcashfromfinancingactivities",
        "net_cash_from_investing_activities": "netcashfrominvestingactivities",
        "net_cash_from_operating_activities": "netcashfromoperatingactivities",
        "net_change_in_cash_and_equivalents": "netchangeincash",
        "net_change_in_deposits": "netchangeindeposits",
        "net_income": "netincome",
        "net_income_continuing_operations": "netincomecontinuing",
        "net_income_discontinued_operations": "netincomediscontinued",
        "net_increase_in_fed_funds_sold": "netincreaseinfedfundssold",
        "non_cash_adjustments_to_reconcile_net_income": "noncashadjustmentstonetincome",
        "other_financing_activities": "otherfinancingactivitiesnet",
        "other_investing_activities": "otherinvestingactivitiesnet",
        "other_net_changes_in_cash": "othernetchangesincash",
        "payment_of_dividends": "paymentofdividends",
        "provision_for_loan_losses": "provisionforloanlosses",
        "purchase_of_investments": "purchaseofinvestments",
        "purchase_of_investment_securities": "purchaseofinvestments",
        "purchase_of_property_plant_and_equipment": "purchaseofplantpropertyandequipment",
        "repayment_of_debt": "repaymentofdebt",
        "repurchase_of_common_equity": "repurchaseofcommonequity",
        "repurchase_of_preferred_equity": "repurchaseofpreferredequity",
        "sale_and_maturity_of_investments": "saleofinvestments",
        "sale_of_property_plant_and_equipment": "saleofplantpropertyandequipment",
    }

    reported_currency: Optional[str] = Field(
        description="The currency in which the balance sheet is reported.",
        default=None,
    )
    net_income_continuing_operations: Optional[float] = Field(
        default=None, description="Net Income (Continuing Operations)"
    )
    net_income_discontinued_operations: Optional[float] = Field(
        default=None, description="Net Income (Discontinued Operations)"
    )
    net_income: Optional[float] = Field(
        default=None, description="Consolidated Net Income."
    )
    provision_for_loan_losses: Optional[float] = Field(
        default=None, description="Provision for Loan Losses"
    )
    provision_for_credit_losses: Optional[float] = Field(
        default=None, description="Provision for credit losses"
    )
    depreciation_expense: Optional[float] = Field(
        default=None, description="Depreciation Expense."
    )
    amortization_expense: Optional[float] = Field(
        default=None, description="Amortization Expense."
    )
    share_based_compensation: Optional[float] = Field(
        default=None, description="Share-based compensation."
    )
    non_cash_adjustments_to_reconcile_net_income: Optional[float] = Field(
        default=None, description="Non-Cash Adjustments to Reconcile Net Income."
    )
    changes_in_operating_assets_and_liabilities: Optional[float] = Field(
        default=None, description="Changes in Operating Assets and Liabilities (Net)"
    )
    net_cash_from_continuing_operating_activities: Optional[float] = Field(
        default=None, description="Net Cash from Continuing Operating Activities"
    )
    net_cash_from_discontinued_operating_activities: Optional[float] = Field(
        default=None, description="Net Cash from Discontinued Operating Activities"
    )
    net_cash_from_operating_activities: Optional[float] = Field(
        default=None, description="Net Cash from Operating Activities"
    )
    divestitures: Optional[float] = Field(default=None, description="Divestitures")
    sale_of_property_plant_and_equipment: Optional[float] = Field(
        default=None, description="Sale of Property, Plant, and Equipment"
    )
    acquisitions: Optional[float] = Field(default=None, description="Acquisitions")
    purchase_of_investments: Optional[float] = Field(
        default=None, description="Purchase of Investments"
    )
    purchase_of_investment_securities: Optional[float] = Field(
        default=None, description="Purchase of Investment Securities"
    )
    sale_and_maturity_of_investments: Optional[float] = Field(
        default=None, description="Sale and Maturity of Investments"
    )
    loans_held_for_sale: Optional[float] = Field(
        default=None, description="Loans Held for Sale (Net)"
    )
    purchase_of_property_plant_and_equipment: Optional[float] = Field(
        default=None, description="Purchase of Property, Plant, and Equipment"
    )
    other_investing_activities: Optional[float] = Field(
        default=None, description="Other Investing Activities (Net)"
    )
    net_cash_from_continuing_investing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Continuing Investing Activities"
    )
    net_cash_from_discontinued_investing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Discontinued Investing Activities"
    )
    net_cash_from_investing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Investing Activities"
    )
    payment_of_dividends: Optional[float] = Field(
        default=None, description="Payment of Dividends"
    )
    repurchase_of_common_equity: Optional[float] = Field(
        default=None, description="Repurchase of Common Equity"
    )
    repurchase_of_preferred_equity: Optional[float] = Field(
        default=None, description="Repurchase of Preferred Equity"
    )
    issuance_of_common_equity: Optional[float] = Field(
        default=None, description="Issuance of Common Equity"
    )
    issuance_of_preferred_equity: Optional[float] = Field(
        default=None, description="Issuance of Preferred Equity"
    )
    issuance_of_debt: Optional[float] = Field(
        default=None, description="Issuance of Debt"
    )
    repayment_of_debt: Optional[float] = Field(
        default=None, description="Repayment of Debt"
    )
    other_financing_activities: Optional[float] = Field(
        default=None, description="Other Financing Activities (Net)"
    )
    cash_interest_received: Optional[float] = Field(
        default=None, description="Cash Interest Received"
    )
    net_change_in_deposits: Optional[float] = Field(
        default=None, description="Net Change in Deposits"
    )
    net_increase_in_fed_funds_sold: Optional[float] = Field(
        default=None, description="Net Increase in Fed Funds Sold"
    )
    net_cash_from_continuing_financing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Continuing Financing Activities"
    )
    net_cash_from_discontinued_financing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Discontinued Financing Activities"
    )
    net_cash_from_financing_activities: Optional[float] = Field(
        default=None, description="Net Cash from Financing Activities"
    )
    effect_of_exchange_rate_changes: Optional[float] = Field(
        default=None, description="Effect of Exchange Rate Changes"
    )
    other_net_changes_in_cash: Optional[float] = Field(
        default=None, description="Other Net Changes in Cash"
    )
    net_change_in_cash_and_equivalents: Optional[float] = Field(
        default=None, description="Net Change in Cash and Equivalents"
    )
    cash_income_taxes_paid: Optional[float] = Field(
        default=None, description="Cash Income Taxes Paid"
    )
    cash_interest_paid: Optional[float] = Field(
        default=None, description="Cash Interest Paid"
    )

    @model_validator(mode="before")
    @classmethod
    def replace_zero(cls, values):
        """Check for zero values and replace with None."""
        return (
            {k: None if v == 0 else v for k, v in values.items()}
            if isinstance(values, dict)
            else values
        )


class IntrinioCashFlowStatementFetcher(
    Fetcher[
        IntrinioCashFlowStatementQueryParams,
        List[IntrinioCashFlowStatementData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioCashFlowStatementQueryParams:
        """Transform the query params."""
        return IntrinioCashFlowStatementQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioCashFlowStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        statement_code = "cash_flow_statement"
        if query.period in ["quarter", "annual"]:
            period_type = "FY" if query.period == "annual" else "QTR"
        elif query.period in ["ttm", "ytd"]:
            period_type = query.period.upper()
        else:
            raise OpenBBError(f"Period '{query.period}' not supported.")

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

        fiscal_periods = [
            f"{item['fiscal_year']}-{item['fiscal_period']}"
            for item in fundamentals_data
        ]
        fiscal_periods = fiscal_periods[: query.limit]

        async def callback(response: ClientResponse, _: Any) -> Dict:
            """Return the response."""
            statement_data = await response.json()
            return {
                "period_ending": statement_data["fundamental"]["end_date"],  # type: ignore
                "fiscal_period": statement_data["fundamental"]["fiscal_period"],  # type: ignore
                "fiscal_year": statement_data["fundamental"]["fiscal_year"],  # type: ignore
                "financials": statement_data["standardized_financials"],  # type: ignore
            }

        intrinio_id = f"{query.symbol}-{statement_code}"
        urls = [
            f"{base_url}/fundamentals/{intrinio_id}-{period}/standardized_financials?api_key={api_key}"
            for period in fiscal_periods
        ]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioCashFlowStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioCashFlowStatementData]:
        """Return the transformed data."""
        transformed_data: List[IntrinioCashFlowStatementData] = []
        units = []
        for item in data:
            sub_dict: Dict[str, Any] = {}

            for sub_item in item["financials"]:
                unit = sub_item["data_tag"].get("unit", "")
                if unit and len(unit) == 3:
                    units.append(unit)
                field_name = sub_item["data_tag"]["tag"]
                sub_dict[field_name] = (
                    float(sub_item["value"])
                    if sub_item["value"] and sub_item["value"] != 0
                    else None
                )

            sub_dict["period_ending"] = item["period_ending"]
            sub_dict["fiscal_year"] = item["fiscal_year"]
            sub_dict["fiscal_period"] = item["fiscal_period"]
            sub_dict["reported_currency"] = list(set(units))[0]

            transformed_data.append(IntrinioCashFlowStatementData(**sub_dict))

        return transformed_data
