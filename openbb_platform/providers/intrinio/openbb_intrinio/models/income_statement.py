"""Intrinio Income Statement Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Literal, Optional
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.income_statement import (
    IncomeStatementData,
    IncomeStatementQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.helpers import (
    ClientResponse,
    ClientSession,
    amake_requests,
)
from openbb_intrinio.utils.helpers import get_data_one
from pydantic import Field, field_validator


class IntrinioIncomeStatementQueryParams(IncomeStatementQueryParams):
    """Intrinio Income Statement Query.

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


class IntrinioIncomeStatementData(IncomeStatementData):
    """Intrinio Income Statement Data."""

    __alias_dict__ = {
        "amortization_expense": "amortizationexpense",
        "amortizationof_deferred_policy_acquisition_costs": "amortizationofdeferredpolicyacquisitioncosts",
        "basic_and_diluted_earnings_per_share": "basicdilutedeps",
        "basic_earnings_per_share": "basiceps",
        "capitalized_lease_obligations_interest_expense": "capitalizedleaseobligationinterestexpense",
        "cash_dividends_to_common_per_share": "cashdividendspershare",
        "current_and_future_benefits": "currentandfuturebenefits",
        "depletion_expense": "depletionexpense",
        "deposits_interest_expense": "depositsinterestexpense",
        "deposits_and_money_market_investments_interest_income": "depositsinterestincome",
        "depreciation_expense": "depreciationexpense",
        "diluted_earnings_per_share": "dilutedeps",
        "exploration_expense": "explorationexpense",
        "extraordinary_income": "extraordinaryincome",
        "federal_funds_purchased_and_securities_sold_interest_expense": "fedfundsandrepointerestexpense",
        "federal_funds_sold_and_securities_borrowed_interest_income": "fedfundsandrepointerestincome",
        "impairment_charge": "impairmentexpense",
        "income_tax_expense": "incometaxexpense",
        "pre_tax_income_margin": "pretaxincomemargin",
        "investment_banking_income": "investmentbankingincome",
        "investment_securities_interest_income": "investmentsecuritiesinterestincome",
        "loans_and_leases_interest_income": "loansandleaseinterestincome",
        "long_term_debt_interest_expense": "longtermdebtinterestexpense",
        "marketing_expense": "marketingexpense",
        "consolidated_net_income": "netincome",
        "net_income_continuing_operations": "netincomecontinuing",
        "net_income_discontinued_operations": "netincomediscontinued",
        "net_income_attributable_to_common_shareholders": "netincometocommon",
        "net_income_attributable_to_noncontrolling_interest": "netincometononcontrollinginterest",
        "net_interest_income": "netinterestincome",
        "net_occupancy_and_equipment_expense": "netoccupancyequipmentexpense",
        "net_realized_and_unrealized_capital_gains_on_investments": "netrealizedcapitalgains",
        "non_operating_income": "nonoperatingincome",
        "operating_revenue": "operatingrevenue",
        "operating_cost_of_revenue": "operatingcostofrevenue",
        "other_adjustments_to_consolidated_net_income": "otheradjustmentstoconsolidatednetincome",
        "other_adjustments_to_net_income_attributable_to_common_shareholders": "otheradjustmentstonetincometocommon",
        "other_adjustment_to_net_income_attributable_to_common_shareholders": "otheradjustmentstonetincometocommon",
        "other_cost_of_revenue": "othercostofrevenue",
        "other_gains": "othergains",
        "other_income": "otherincome",
        "other_interest_expense": "otherinterestexpense",
        "other_interest_income": "otherinterestincome",
        "other_non_interest_income": "othernoninterestincome",
        "other_operating_expenses": "otheroperatingexpenses",
        "other_revenue": "otherrevenue",
        "other_service_charges": "otherservicechargeincome",
        "other_special_charges": "otherspecialcharges",
        "insurance_policy_acquisition_costs": "policyacquisitioncosts",
        "preferred_stock_dividends_declared": "preferreddividends",
        "premiums_earned": "premiumsearned",
        "property_and_liability_insurance_claims": "propertyliabilityinsuranceclaims",
        "provision_for_credit_losses": "provisionforcreditlosses",
        "research_and_development_expense": "rdexpense",
        "restructuring_charge": "restructuringcharge",
        "salaries_and_employee_benefits": "salariesandemployeebenefitsexpense",
        "service_charges_on_deposit_accounts": "servicechargesondepositsincome",
        "selling_general_and_admin_expense": "sgaexpense",
        "short_term_borrowings_interest_expense": "shorttermborrowinginterestexpense",
        "cost_of_revenue": "totalcostofrevenue",
        "gross_profit": "totalgrossprofit",
        "gross_profit_margin": "grossmargin",
        "total_interest_expense": "totalinterestexpense",
        "interest_and_investment_income": "totalinterestincome",
        "total_non_interest_expense": "totalnoninterestexpense",
        "total_non_interest_income": "totalnoninterestincome",
        "total_operating_expenses": "totaloperatingexpenses",
        "total_operating_income": "totaloperatingincome",
        "total_other_income": "totalotherincome",
        "total_pre_tax_income": "totalpretaxincome",
        "revenue": "totalrevenue",
        "trading_account_interest_income": "tradingaccountinterestincome",
        "trust_fees_by_commissions": "trustfeeincome",
        "ebit": "ebit",
        "ebitda": "ebitda",
        "ebitda_margin": "ebitdamargin",
        "weighted_average_basic_and_diluted_shares_outstanding": "weightedavebasicdilutedsharesos",
        "weighted_average_basic_shares_outstanding": "weightedavebasicsharesos",
        "weighted_average_diluted_shares_outstanding": "weightedavedilutedsharesos",
    }

    reported_currency: Optional[str] = Field(
        description="The currency in which the balance sheet is reported.",
        default=None,
    )
    revenue: Optional[float] = Field(default=None, description="Total revenue")
    operating_revenue: Optional[float] = Field(
        default=None, description="Total operating revenue"
    )
    cost_of_revenue: Optional[float] = Field(
        default=None, description="Total cost of revenue"
    )
    operating_cost_of_revenue: Optional[float] = Field(
        default=None, description="Total operating cost of revenue"
    )
    gross_profit: Optional[float] = Field(
        default=None, description="Total gross profit"
    )
    gross_profit_margin: Optional[float] = Field(
        default=None,
        description="Gross margin ratio.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    provision_for_credit_losses: Optional[float] = Field(
        default=None,
        description="Provision for credit losses",
    )
    research_and_development_expense: Optional[float] = Field(
        default=None, description="Research and development expense"
    )
    selling_general_and_admin_expense: Optional[float] = Field(
        default=None, description="Selling, general, and admin expense"
    )
    salaries_and_employee_benefits: Optional[float] = Field(
        default=None, description="Salaries and employee benefits"
    )
    marketing_expense: Optional[float] = Field(
        default=None, description="Marketing expense"
    )
    net_occupancy_and_equipment_expense: Optional[float] = Field(
        default=None, description="Net occupancy and equipment expense"
    )
    other_operating_expenses: Optional[float] = Field(
        default=None, description="Other operating expenses"
    )
    depreciation_expense: Optional[float] = Field(
        default=None, description="Depreciation expense"
    )
    amortization_expense: Optional[float] = Field(
        default=None, description="Amortization expense"
    )
    amortization_of_deferred_policy_acquisition_costs: Optional[float] = Field(
        default=None, description="Amortization of deferred policy acquisition costs"
    )
    exploration_expense: Optional[float] = Field(
        default=None, description="Exploration expense"
    )
    depletion_expense: Optional[float] = Field(
        default=None, description="Depletion expense"
    )
    total_operating_expenses: Optional[float] = Field(
        default=None, description="Total operating expenses"
    )
    total_operating_income: Optional[float] = Field(
        default=None, description="Total operating income"
    )
    deposits_and_money_market_investments_interest_income: Optional[float] = Field(
        default=None,
        description="Deposits and money market investments interest income",
    )
    federal_funds_sold_and_securities_borrowed_interest_income: Optional[float] = Field(
        default=None,
        description="Federal funds sold and securities borrowed interest income",
    )
    investment_securities_interest_income: Optional[float] = Field(
        default=None, description="Investment securities interest income"
    )
    loans_and_leases_interest_income: Optional[float] = Field(
        default=None, description="Loans and leases interest income"
    )
    trading_account_interest_income: Optional[float] = Field(
        default=None, description="Trading account interest income"
    )
    other_interest_income: Optional[float] = Field(
        default=None, description="Other interest income"
    )
    total_non_interest_income: Optional[float] = Field(
        default=None, description="Total non-interest income"
    )
    interest_and_investment_income: Optional[float] = Field(
        default=None, description="Interest and investment income"
    )
    short_term_borrowings_interest_expense: Optional[float] = Field(
        default=None, description="Short-term borrowings interest expense"
    )
    long_term_debt_interest_expense: Optional[float] = Field(
        default=None, description="Long-term debt interest expense"
    )
    capitalized_lease_obligations_interest_expense: Optional[float] = Field(
        default=None, description="Capitalized lease obligations interest expense"
    )
    deposits_interest_expense: Optional[float] = Field(
        default=None, description="Deposits interest expense"
    )
    federal_funds_purchased_and_securities_sold_interest_expense: Optional[float] = (
        Field(
            default=None,
            description="Federal funds purchased and securities sold interest expense",
        )
    )
    other_interest_expense: Optional[float] = Field(
        default=None, description="Other interest expense"
    )
    total_interest_expense: Optional[float] = Field(
        default=None, description="Total interest expense"
    )
    net_interest_income: Optional[float] = Field(
        default=None, description="Net interest income"
    )
    other_non_interest_income: Optional[float] = Field(
        default=None, description="Other non-interest income"
    )
    investment_banking_income: Optional[float] = Field(
        default=None, description="Investment banking income"
    )
    trust_fees_by_commissions: Optional[float] = Field(
        default=None, description="Trust fees by commissions"
    )
    premiums_earned: Optional[float] = Field(
        default=None, description="Premiums earned"
    )
    insurance_policy_acquisition_costs: Optional[float] = Field(
        default=None, description="Insurance policy acquisition costs"
    )
    current_and_future_benefits: Optional[float] = Field(
        default=None, description="Current and future benefits"
    )
    property_and_liability_insurance_claims: Optional[float] = Field(
        default=None, description="Property and liability insurance claims"
    )
    total_non_interest_expense: Optional[float] = Field(
        default=None, description="Total non-interest expense"
    )
    net_realized_and_unrealized_capital_gains_on_investments: Optional[float] = Field(
        default=None,
        description="Net realized and unrealized capital gains on investments",
    )
    other_gains: Optional[float] = Field(default=None, description="Other gains")
    non_operating_income: Optional[float] = Field(
        default=None, description="Non-operating income"
    )
    other_income: Optional[float] = Field(default=None, description="Other income")
    other_revenue: Optional[float] = Field(default=None, description="Other revenue")

    extraordinary_income: Optional[float] = Field(
        default=None, description="Extraordinary income"
    )
    total_other_income: Optional[float] = Field(
        default=None, description="Total other income"
    )
    ebitda: Optional[float] = Field(
        default=None,
        description="Earnings Before Interest, Taxes, Depreciation and Amortization.",
    )
    ebitda_margin: Optional[float] = Field(
        default=None,
        description="Margin on Earnings Before Interest, Taxes, Depreciation and Amortization.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    total_pre_tax_income: Optional[float] = Field(
        default=None, description="Total pre-tax income"
    )
    ebit: Optional[float] = Field(
        default=None, description="Earnings Before Interest and Taxes."
    )
    pre_tax_income_margin: Optional[float] = Field(
        default=None,
        description="Pre-Tax Income Margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    income_tax_expense: Optional[float] = Field(
        default=None, description="Income tax expense"
    )
    impairment_charge: Optional[float] = Field(
        default=None, description="Impairment charge"
    )
    restructuring_charge: Optional[float] = Field(
        default=None, description="Restructuring charge"
    )
    service_charges_on_deposit_accounts: Optional[float] = Field(
        default=None, description="Service charges on deposit accounts"
    )
    other_service_charges: Optional[float] = Field(
        default=None, description="Other service charges"
    )
    other_special_charges: Optional[float] = Field(
        default=None, description="Other special charges"
    )
    other_cost_of_revenue: Optional[float] = Field(
        default=None, description="Other cost of revenue"
    )
    net_income_continuing_operations: Optional[float] = Field(
        default=None, description="Net income (continuing operations)"
    )
    net_income_discontinued_operations: Optional[float] = Field(
        default=None, description="Net income (discontinued operations)"
    )
    consolidated_net_income: Optional[float] = Field(
        default=None, description="Consolidated net income"
    )
    other_adjustments_to_consolidated_net_income: Optional[float] = Field(
        default=None, description="Other adjustments to consolidated net income"
    )
    other_adjustment_to_net_income_attributable_to_common_shareholders: Optional[
        float
    ] = Field(
        default=None,
        description="Other adjustment to net income attributable to common shareholders",
    )
    net_income_attributable_to_noncontrolling_interest: Optional[float] = Field(
        default=None, description="Net income attributable to noncontrolling interest"
    )
    net_income_attributable_to_common_shareholders: Optional[float] = Field(
        default=None, description="Net income attributable to common shareholders"
    )
    basic_earnings_per_share: Optional[float] = Field(
        default=None, description="Basic earnings per share"
    )
    diluted_earnings_per_share: Optional[float] = Field(
        default=None, description="Diluted earnings per share"
    )
    basic_and_diluted_earnings_per_share: Optional[float] = Field(
        default=None, description="Basic and diluted earnings per share"
    )
    cash_dividends_to_common_per_share: Optional[float] = Field(
        default=None, description="Cash dividends to common per share"
    )
    preferred_stock_dividends_declared: Optional[float] = Field(
        default=None, description="Preferred stock dividends declared"
    )
    weighted_average_basic_shares_outstanding: Optional[float] = Field(
        default=None, description="Weighted average basic shares outstanding"
    )
    weighted_average_diluted_shares_outstanding: Optional[float] = Field(
        default=None, description="Weighted average diluted shares outstanding"
    )
    weighted_average_basic_and_diluted_shares_outstanding: Optional[float] = Field(
        default=None,
        description="Weighted average basic and diluted shares outstanding",
    )


class IntrinioIncomeStatementFetcher(
    Fetcher[
        IntrinioIncomeStatementQueryParams,
        List[IntrinioIncomeStatementData],
    ]
):
    """Transform the query, extract and transform the data from the Intrinio endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> IntrinioIncomeStatementQueryParams:
        """Transform the query params."""
        return IntrinioIncomeStatementQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: IntrinioIncomeStatementQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Intrinio endpoint."""
        api_key = credentials.get("intrinio_api_key") if credentials else ""
        statement_code = "income_statement"
        if query.period in ["quarter", "annual"]:
            period_type = "FY" if query.period == "annual" else "QTR"
        elif query.period in ["ttm", "ytd"]:
            period_type = query.period.upper()
        else:
            raise OpenBBError(f"Period '{query.period}' not supported.")

        data_tags = [
            "ebit",
            "ebitda",
            "ebitdamargin",
            "pretaxincomemargin",
            "grossmargin",
        ]

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

        fiscal_periods = [
            f"{item['fiscal_year']}-{item['fiscal_period']}"
            for item in fundamentals_data
        ]
        fiscal_periods = fiscal_periods[: query.limit]

        async def callback(response: ClientResponse, session: ClientSession) -> Dict:
            """Return the response."""
            intrinio_id = response.url.parts[-2].replace(statement_code, "calculations")

            statement_data = await response.json()

            calculations_url = f"{base_url}/fundamentals/{intrinio_id}/standardized_financials?api_key={api_key}"
            calculations_data = await session.get_json(calculations_url)

            calculations_data = [
                item
                for item in calculations_data.get("standardized_financials", [])  # type: ignore
                if item["data_tag"]["tag"] in data_tags
            ]

            return {
                "period_ending": statement_data["fundamental"]["end_date"],  # type: ignore
                "fiscal_period": statement_data["fundamental"]["fiscal_period"],  # type: ignore
                "fiscal_year": statement_data["fundamental"]["fiscal_year"],  # type: ignore
                "financials": statement_data["standardized_financials"]  # type: ignore
                + calculations_data,
            }

        intrinio_id = f"{query.symbol}-{statement_code}"
        urls = [
            f"{base_url}/fundamentals/{intrinio_id}-{period}/standardized_financials?api_key={api_key}"
            for period in fiscal_periods
        ]

        return await amake_requests(urls, callback, **kwargs)

    @staticmethod
    def transform_data(
        query: IntrinioIncomeStatementQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[IntrinioIncomeStatementData]:
        """Return the transformed data."""
        transformed_data: List[IntrinioIncomeStatementData] = []
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

            transformed_data.append(IntrinioIncomeStatementData(**sub_dict))

        return transformed_data
