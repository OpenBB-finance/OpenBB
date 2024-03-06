### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union
from warnings import simplefilter, warn

from annotated_types import Ge
from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated, deprecated


class ROUTER_equity_fundamental(Container):
    """/equity/fundamental
    balance
    balance_growth
    cash
    cash_growth
    dividends
    employee_count
    filings
    historical_attributes
    historical_eps
    historical_splits
    income
    income_growth
    latest_attributes
    management
    management_compensation
    metrics
    multiples
    overview
    ratios
    reported_financials
    revenue_per_geography
    revenue_per_segment
    search_attributes
    trailing_dividend_yield
    transcript
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def balance(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        period: Annotated[
            str, OpenBBCustomParameter(description="Time period of the data to return.")
        ] = "annual",
        limit: Annotated[
            Optional[Annotated[int, Ge(ge=0)]],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 5,
        provider: Optional[Literal["fmp", "intrinio", "polygon", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the balance sheet for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : str
            Time period of the data to return.
        limit : Optional[Annotated[int, Ge(ge=0)]]
            The number of data entries to return.
        provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        fiscal_year : Optional[int]
            The specific fiscal year.  Reports do not go beyond 2008. (provider: intrinio)
        filing_date : Optional[datetime.date]
            Filing date of the financial statement. (provider: polygon)
        filing_date_lt : Optional[datetime.date]
            Filing date less than the given date. (provider: polygon)
        filing_date_lte : Optional[datetime.date]
            Filing date less than or equal to the given date. (provider: polygon)
        filing_date_gt : Optional[datetime.date]
            Filing date greater than the given date. (provider: polygon)
        filing_date_gte : Optional[datetime.date]
            Filing date greater than or equal to the given date. (provider: polygon)
        period_of_report_date : Optional[datetime.date]
            Period of report date of the financial statement. (provider: polygon)
        period_of_report_date_lt : Optional[datetime.date]
            Period of report date less than the given date. (provider: polygon)
        period_of_report_date_lte : Optional[datetime.date]
            Period of report date less than or equal to the given date. (provider: polygon)
        period_of_report_date_gt : Optional[datetime.date]
            Period of report date greater than the given date. (provider: polygon)
        period_of_report_date_gte : Optional[datetime.date]
            Period of report date greater than or equal to the given date. (provider: polygon)
        include_sources : bool
            Whether to include the sources of the financial statement. (provider: polygon)
        order : Optional[Literal['asc', 'desc']]
            Order of the financial statement. (provider: polygon)
        sort : Optional[Literal['filing_date', 'period_of_report_date']]
            Sort of the financial statement. (provider: polygon)

        Returns
        -------
        OBBject
            results : List[BalanceSheet]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        BalanceSheet
        ------------
        period_ending : date
            The end date of the reporting period.
        fiscal_period : Optional[str]
            The fiscal period of the report.
        fiscal_year : Optional[int]
            The fiscal year of the fiscal period.
        filing_date : Optional[date]
            The date when the filing was made. (provider: fmp)
        accepted_date : Optional[datetime]
            The date and time when the filing was accepted. (provider: fmp)
        reported_currency : Optional[str]
            The currency in which the balance sheet was reported. (provider: fmp, intrinio)
        cash_and_cash_equivalents : Optional[float]
            Cash and cash equivalents. (provider: fmp, intrinio)
        short_term_investments : Optional[float]
            Short term investments. (provider: fmp, intrinio)
        cash_and_short_term_investments : Optional[float]
            Cash and short term investments. (provider: fmp)
        net_receivables : Optional[float]
            Net receivables. (provider: fmp)
        inventory : Optional[Union[float, int]]
            Inventory. (provider: fmp, polygon)
        other_current_assets : Optional[Union[float, int]]
            Other current assets. (provider: fmp, intrinio, polygon)
        total_current_assets : Optional[Union[float, int]]
            Total current assets. (provider: fmp, intrinio, polygon)
        plant_property_equipment_net : Optional[float]
            Plant property equipment net. (provider: fmp, intrinio)
        goodwill : Optional[float]
            Goodwill. (provider: fmp, intrinio)
        intangible_assets : Optional[Union[float, int]]
            Intangible assets. (provider: fmp, intrinio, polygon)
        goodwill_and_intangible_assets : Optional[float]
            Goodwill and intangible assets. (provider: fmp)
        long_term_investments : Optional[float]
            Long term investments. (provider: fmp, intrinio)
        tax_assets : Optional[float]
            Tax assets. (provider: fmp)
        other_non_current_assets : Optional[Union[float, int]]
            Other non current assets. (provider: fmp, polygon)
        non_current_assets : Optional[float]
            Total non current assets. (provider: fmp)
        other_assets : Optional[float]
            Other assets. (provider: fmp, intrinio)
        total_assets : Optional[Union[float, int]]
            Total assets. (provider: fmp, intrinio, polygon)
        accounts_payable : Optional[Union[float, int]]
            Accounts payable. (provider: fmp, intrinio, polygon)
        short_term_debt : Optional[float]
            Short term debt. (provider: fmp, intrinio)
        tax_payables : Optional[float]
            Tax payables. (provider: fmp)
        current_deferred_revenue : Optional[float]
            Current deferred revenue. (provider: fmp, intrinio)
        other_current_liabilities : Optional[Union[float, int]]
            Other current liabilities. (provider: fmp, intrinio, polygon)
        total_current_liabilities : Optional[Union[float, int]]
            Total current liabilities. (provider: fmp, intrinio, polygon)
        long_term_debt : Optional[Union[float, int]]
            Long term debt. (provider: fmp, intrinio, polygon)
        deferred_revenue_non_current : Optional[float]
            Non current deferred revenue. (provider: fmp)
        deferred_tax_liabilities_non_current : Optional[float]
            Deferred tax liabilities non current. (provider: fmp)
        other_non_current_liabilities : Optional[Union[float, int]]
            Other non current liabilities. (provider: fmp, polygon)
        total_non_current_liabilities : Optional[Union[float, int]]
            Total non current liabilities. (provider: fmp, intrinio, polygon)
        other_liabilities : Optional[float]
            Other liabilities. (provider: fmp)
        capital_lease_obligations : Optional[float]
            Capital lease obligations. (provider: fmp, intrinio)
        total_liabilities : Optional[Union[float, int]]
            Total liabilities. (provider: fmp, intrinio, polygon)
        preferred_stock : Optional[Union[float, int]]
            Preferred stock. (provider: fmp, intrinio, polygon)
        common_stock : Optional[float]
            Common stock. (provider: fmp, intrinio)
        retained_earnings : Optional[float]
            Retained earnings. (provider: fmp, intrinio)
        accumulated_other_comprehensive_income : Optional[float]
            Accumulated other comprehensive income (loss). (provider: fmp, intrinio)
        other_shareholders_equity : Optional[float]
            Other shareholders equity. (provider: fmp)
        other_total_shareholders_equity : Optional[float]
            Other total shareholders equity. (provider: fmp)
        total_common_equity : Optional[float]
            Total common equity. (provider: fmp, intrinio)
        total_equity_non_controlling_interests : Optional[float]
            Total equity non controlling interests. (provider: fmp, intrinio)
        total_liabilities_and_shareholders_equity : Optional[float]
            Total liabilities and shareholders equity. (provider: fmp)
        minority_interest : Optional[Union[float, int]]
            Minority interest. (provider: fmp, polygon)
        total_liabilities_and_total_equity : Optional[float]
            Total liabilities and total equity. (provider: fmp)
        total_investments : Optional[float]
            Total investments. (provider: fmp)
        total_debt : Optional[float]
            Total debt. (provider: fmp)
        net_debt : Optional[float]
            Net debt. (provider: fmp)
        link : Optional[str]
            Link to the filing. (provider: fmp)
        final_link : Optional[str]
            Link to the filing document. (provider: fmp)
        cash_and_due_from_banks : Optional[float]
            Cash and due from banks. (provider: intrinio)
        restricted_cash : Optional[float]
            Restricted cash. (provider: intrinio)
        federal_funds_sold : Optional[float]
            Federal funds sold. (provider: intrinio)
        accounts_receivable : Optional[Union[float, int]]
            Accounts receivable. (provider: intrinio, polygon)
        note_and_lease_receivable : Optional[float]
            Note and lease receivable. (Vendor non-trade receivables) (provider: intrinio)
        inventories : Optional[float]
            Net Inventories. (provider: intrinio)
        customer_and_other_receivables : Optional[float]
            Customer and other receivables. (provider: intrinio)
        interest_bearing_deposits_at_other_banks : Optional[float]
            Interest bearing deposits at other banks. (provider: intrinio)
        time_deposits_placed_and_other_short_term_investments : Optional[float]
            Time deposits placed and other short term investments. (provider: intrinio)
        trading_account_securities : Optional[float]
            Trading account securities. (provider: intrinio)
        loans_and_leases : Optional[float]
            Loans and leases. (provider: intrinio)
        allowance_for_loan_and_lease_losses : Optional[float]
            Allowance for loan and lease losses. (provider: intrinio)
        current_deferred_refundable_income_taxes : Optional[float]
            Current deferred refundable income taxes. (provider: intrinio)
        loans_and_leases_net_of_allowance : Optional[float]
            Loans and leases net of allowance. (provider: intrinio)
        accrued_investment_income : Optional[float]
            Accrued investment income. (provider: intrinio)
        other_current_non_operating_assets : Optional[float]
            Other current non-operating assets. (provider: intrinio)
        loans_held_for_sale : Optional[float]
            Loans held for sale. (provider: intrinio)
        prepaid_expenses : Optional[Union[float, int]]
            Prepaid expenses. (provider: intrinio, polygon)
        plant_property_equipment_gross : Optional[float]
            Plant property equipment gross. (provider: intrinio)
        accumulated_depreciation : Optional[float]
            Accumulated depreciation. (provider: intrinio)
        premises_and_equipment_net : Optional[float]
            Net premises and equipment. (provider: intrinio)
        mortgage_servicing_rights : Optional[float]
            Mortgage servicing rights. (provider: intrinio)
        unearned_premiums_asset : Optional[float]
            Unearned premiums asset. (provider: intrinio)
        non_current_note_lease_receivables : Optional[float]
            Non-current note lease receivables. (provider: intrinio)
        deferred_acquisition_cost : Optional[float]
            Deferred acquisition cost. (provider: intrinio)
        separate_account_business_assets : Optional[float]
            Separate account business assets. (provider: intrinio)
        non_current_deferred_refundable_income_taxes : Optional[float]
            Noncurrent deferred refundable income taxes. (provider: intrinio)
        employee_benefit_assets : Optional[float]
            Employee benefit assets. (provider: intrinio)
        other_non_current_operating_assets : Optional[float]
            Other noncurrent operating assets. (provider: intrinio)
        other_non_current_non_operating_assets : Optional[float]
            Other noncurrent non-operating assets. (provider: intrinio)
        interest_bearing_deposits : Optional[float]
            Interest bearing deposits. (provider: intrinio)
        total_non_current_assets : Optional[Union[float, int]]
            Total noncurrent assets. (provider: intrinio, polygon)
        non_interest_bearing_deposits : Optional[float]
            Non interest bearing deposits. (provider: intrinio)
        federal_funds_purchased_and_securities_sold : Optional[float]
            Federal funds purchased and securities sold. (provider: intrinio)
        bankers_acceptance_outstanding : Optional[float]
            Bankers acceptance outstanding. (provider: intrinio)
        current_deferred_payable_income_tax_liabilities : Optional[float]
            Current deferred payable income tax liabilities. (provider: intrinio)
        accrued_interest_payable : Optional[float]
            Accrued interest payable. (provider: intrinio)
        accrued_expenses : Optional[float]
            Accrued expenses. (provider: intrinio)
        other_short_term_payables : Optional[float]
            Other short term payables. (provider: intrinio)
        customer_deposits : Optional[float]
            Customer deposits. (provider: intrinio)
        dividends_payable : Optional[float]
            Dividends payable. (provider: intrinio)
        claims_and_claim_expense : Optional[float]
            Claims and claim expense. (provider: intrinio)
        future_policy_benefits : Optional[float]
            Future policy benefits. (provider: intrinio)
        current_employee_benefit_liabilities : Optional[float]
            Current employee benefit liabilities. (provider: intrinio)
        unearned_premiums_liability : Optional[float]
            Unearned premiums liability. (provider: intrinio)
        other_taxes_payable : Optional[float]
            Other taxes payable. (provider: intrinio)
        policy_holder_funds : Optional[float]
            Policy holder funds. (provider: intrinio)
        other_current_non_operating_liabilities : Optional[float]
            Other current non-operating liabilities. (provider: intrinio)
        separate_account_business_liabilities : Optional[float]
            Separate account business liabilities. (provider: intrinio)
        other_long_term_liabilities : Optional[float]
            Other long term liabilities. (provider: intrinio)
        non_current_deferred_revenue : Optional[float]
            Non-current deferred revenue. (provider: intrinio)
        non_current_deferred_payable_income_tax_liabilities : Optional[float]
            Non-current deferred payable income tax liabilities. (provider: intrinio)
        non_current_employee_benefit_liabilities : Optional[float]
            Non-current employee benefit liabilities. (provider: intrinio)
        other_non_current_operating_liabilities : Optional[float]
            Other non-current operating liabilities. (provider: intrinio)
        other_non_current_non_operating_liabilities : Optional[float]
            Other non-current, non-operating liabilities. (provider: intrinio)
        asset_retirement_reserve_litigation_obligation : Optional[float]
            Asset retirement reserve litigation obligation. (provider: intrinio)
        commitments_contingencies : Optional[float]
            Commitments contingencies. (provider: intrinio)
        redeemable_non_controlling_interest : Optional[Union[float, int]]
            Redeemable non-controlling interest. (provider: intrinio, polygon)
        treasury_stock : Optional[float]
            Treasury stock. (provider: intrinio)
        participating_policy_holder_equity : Optional[float]
            Participating policy holder equity. (provider: intrinio)
        other_equity_adjustments : Optional[float]
            Other equity adjustments. (provider: intrinio)
        total_preferred_common_equity : Optional[float]
            Total preferred common equity. (provider: intrinio)
        non_controlling_interest : Optional[float]
            Non-controlling interest. (provider: intrinio)
        total_liabilities_shareholders_equity : Optional[float]
            Total liabilities and shareholders equity. (provider: intrinio)
        marketable_securities : Optional[int]
            Marketable securities (provider: polygon)
        property_plant_equipment_net : Optional[int]
            Property plant and equipment net (provider: polygon)
        employee_wages : Optional[int]
            Employee wages (provider: polygon)
        temporary_equity_attributable_to_parent : Optional[int]
            Temporary equity attributable to parent (provider: polygon)
        equity_attributable_to_parent : Optional[int]
            Equity attributable to parent (provider: polygon)
        temporary_equity : Optional[int]
            Temporary equity (provider: polygon)
        redeemable_non_controlling_interest_other : Optional[int]
            Redeemable non-controlling interest other (provider: polygon)
        total_stock_holders_equity : Optional[int]
            Total stock holders equity (provider: polygon)
        total_liabilities_and_stock_holders_equity : Optional[int]
            Total liabilities and stockholders equity (provider: polygon)
        total_equity : Optional[int]
            Total equity (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.balance(symbol="AAPL", period="annual", limit=5)
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/balance",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/balance",
                        ("fmp", "intrinio", "polygon", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "period": period,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def balance_growth(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the growth of a company's balance sheet items over time.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[BalanceSheetGrowth]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        BalanceSheetGrowth
        ------------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        period : str
            Reporting period.
        growth_cash_and_cash_equivalents : float
            Growth rate of cash and cash equivalents.
        growth_short_term_investments : float
            Growth rate of short-term investments.
        growth_cash_and_short_term_investments : float
            Growth rate of cash and short-term investments.
        growth_net_receivables : float
            Growth rate of net receivables.
        growth_inventory : float
            Growth rate of inventory.
        growth_other_current_assets : float
            Growth rate of other current assets.
        growth_total_current_assets : float
            Growth rate of total current assets.
        growth_property_plant_equipment_net : float
            Growth rate of net property, plant, and equipment.
        growth_goodwill : float
            Growth rate of goodwill.
        growth_intangible_assets : float
            Growth rate of intangible assets.
        growth_goodwill_and_intangible_assets : float
            Growth rate of goodwill and intangible assets.
        growth_long_term_investments : float
            Growth rate of long-term investments.
        growth_tax_assets : float
            Growth rate of tax assets.
        growth_other_non_current_assets : float
            Growth rate of other non-current assets.
        growth_total_non_current_assets : float
            Growth rate of total non-current assets.
        growth_other_assets : float
            Growth rate of other assets.
        growth_total_assets : float
            Growth rate of total assets.
        growth_account_payables : float
            Growth rate of accounts payable.
        growth_short_term_debt : float
            Growth rate of short-term debt.
        growth_tax_payables : float
            Growth rate of tax payables.
        growth_deferred_revenue : float
            Growth rate of deferred revenue.
        growth_other_current_liabilities : float
            Growth rate of other current liabilities.
        growth_total_current_liabilities : float
            Growth rate of total current liabilities.
        growth_long_term_debt : float
            Growth rate of long-term debt.
        growth_deferred_revenue_non_current : float
            Growth rate of non-current deferred revenue.
        growth_deferrred_tax_liabilities_non_current : float
            Growth rate of non-current deferred tax liabilities.
        growth_other_non_current_liabilities : float
            Growth rate of other non-current liabilities.
        growth_total_non_current_liabilities : float
            Growth rate of total non-current liabilities.
        growth_other_liabilities : float
            Growth rate of other liabilities.
        growth_total_liabilities : float
            Growth rate of total liabilities.
        growth_common_stock : float
            Growth rate of common stock.
        growth_retained_earnings : float
            Growth rate of retained earnings.
        growth_accumulated_other_comprehensive_income_loss : float
            Growth rate of accumulated other comprehensive income/loss.
        growth_othertotal_stockholders_equity : float
            Growth rate of other total stockholders' equity.
        growth_total_stockholders_equity : float
            Growth rate of total stockholders' equity.
        growth_total_liabilities_and_stockholders_equity : float
            Growth rate of total liabilities and stockholders' equity.
        growth_total_investments : float
            Growth rate of total investments.
        growth_total_debt : float
            Growth rate of total debt.
        growth_net_debt : float
            Growth rate of net debt.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.balance_growth(symbol="AAPL", limit=10)
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/balance_growth",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/balance_growth",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def cash(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        period: Annotated[
            str, OpenBBCustomParameter(description="Time period of the data to return.")
        ] = "annual",
        limit: Annotated[
            Optional[Annotated[int, Ge(ge=0)]],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 5,
        provider: Optional[Literal["fmp", "intrinio", "polygon", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the cash flow statement for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : str
            Time period of the data to return.
        limit : Optional[Annotated[int, Ge(ge=0)]]
            The number of data entries to return.
        provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        fiscal_year : Optional[int]
            The specific fiscal year.  Reports do not go beyond 2008. (provider: intrinio)
        filing_date : Optional[datetime.date]
            Filing date of the financial statement. (provider: polygon)
        filing_date_lt : Optional[datetime.date]
            Filing date less than the given date. (provider: polygon)
        filing_date_lte : Optional[datetime.date]
            Filing date less than or equal to the given date. (provider: polygon)
        filing_date_gt : Optional[datetime.date]
            Filing date greater than the given date. (provider: polygon)
        filing_date_gte : Optional[datetime.date]
            Filing date greater than or equal to the given date. (provider: polygon)
        period_of_report_date : Optional[datetime.date]
            Period of report date of the financial statement. (provider: polygon)
        period_of_report_date_lt : Optional[datetime.date]
            Period of report date less than the given date. (provider: polygon)
        period_of_report_date_lte : Optional[datetime.date]
            Period of report date less than or equal to the given date. (provider: polygon)
        period_of_report_date_gt : Optional[datetime.date]
            Period of report date greater than the given date. (provider: polygon)
        period_of_report_date_gte : Optional[datetime.date]
            Period of report date greater than or equal to the given date. (provider: polygon)
        include_sources : bool
            Whether to include the sources of the financial statement. (provider: polygon)
        order : Literal[None, 'asc', 'desc']
            Order of the financial statement. (provider: polygon)
        sort : Literal[None, 'filing_date', 'period_of_report_date']
            Sort of the financial statement. (provider: polygon)

        Returns
        -------
        OBBject
            results : List[CashFlowStatement]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CashFlowStatement
        -----------------
        period_ending : date
            The end date of the reporting period.
        fiscal_period : Optional[str]
            The fiscal period of the report.
        fiscal_year : Optional[int]
            The fiscal year of the fiscal period.
        filing_date : Optional[date]
            The date of the filing. (provider: fmp)
        accepted_date : Optional[datetime]
            The date the filing was accepted. (provider: fmp)
        reported_currency : Optional[str]
            The currency in which the cash flow statement was reported. (provider: fmp);
            The currency in which the balance sheet is reported. (provider: intrinio)
        net_income : Optional[float]
            Net income. (provider: fmp);
            Consolidated Net Income. (provider: intrinio)
        depreciation_and_amortization : Optional[float]
            Depreciation and amortization. (provider: fmp)
        deferred_income_tax : Optional[float]
            Deferred income tax. (provider: fmp)
        stock_based_compensation : Optional[float]
            Stock-based compensation. (provider: fmp)
        change_in_working_capital : Optional[float]
            Change in working capital. (provider: fmp)
        change_in_account_receivables : Optional[float]
            Change in account receivables. (provider: fmp)
        change_in_inventory : Optional[float]
            Change in inventory. (provider: fmp)
        change_in_account_payable : Optional[float]
            Change in account payable. (provider: fmp)
        change_in_other_working_capital : Optional[float]
            Change in other working capital. (provider: fmp)
        change_in_other_non_cash_items : Optional[float]
            Change in other non-cash items. (provider: fmp)
        net_cash_from_operating_activities : Optional[float]
            Net cash from operating activities. (provider: fmp, intrinio)
        purchase_of_property_plant_and_equipment : Optional[float]
            Purchase of property, plant and equipment. (provider: fmp, intrinio)
        acquisitions : Optional[float]
            Acquisitions. (provider: fmp, intrinio)
        purchase_of_investment_securities : Optional[float]
            Purchase of investment securities. (provider: fmp, intrinio)
        sale_and_maturity_of_investments : Optional[float]
            Sale and maturity of investments. (provider: fmp, intrinio)
        other_investing_activities : Optional[float]
            Other investing activities. (provider: fmp, intrinio)
        net_cash_from_investing_activities : Optional[float]
            Net cash from investing activities. (provider: fmp, intrinio)
        repayment_of_debt : Optional[float]
            Repayment of debt. (provider: fmp, intrinio)
        issuance_of_common_equity : Optional[float]
            Issuance of common equity. (provider: fmp, intrinio)
        repurchase_of_common_equity : Optional[float]
            Repurchase of common equity. (provider: fmp, intrinio)
        payment_of_dividends : Optional[float]
            Payment of dividends. (provider: fmp, intrinio)
        other_financing_activities : Optional[float]
            Other financing activities. (provider: fmp, intrinio)
        net_cash_from_financing_activities : Optional[float]
            Net cash from financing activities. (provider: fmp, intrinio)
        effect_of_exchange_rate_changes_on_cash : Optional[float]
            Effect of exchange rate changes on cash. (provider: fmp)
        net_change_in_cash_and_equivalents : Optional[float]
            Net change in cash and equivalents. (provider: fmp, intrinio)
        cash_at_beginning_of_period : Optional[float]
            Cash at beginning of period. (provider: fmp)
        cash_at_end_of_period : Optional[float]
            Cash at end of period. (provider: fmp)
        operating_cash_flow : Optional[float]
            Operating cash flow. (provider: fmp)
        capital_expenditure : Optional[float]
            Capital expenditure. (provider: fmp)
        free_cash_flow : Optional[float]
            None
        link : Optional[str]
            Link to the filing. (provider: fmp)
        final_link : Optional[str]
            Link to the filing document. (provider: fmp)
        provision_for_loan_losses : Optional[float]
            Provision for Loan Losses (provider: intrinio)
        provision_for_credit_losses : Optional[float]
            Provision for credit losses (provider: intrinio)
        depreciation_expense : Optional[float]
            Depreciation Expense. (provider: intrinio)
        amortization_expense : Optional[float]
            Amortization Expense. (provider: intrinio)
        share_based_compensation : Optional[float]
            Share-based compensation. (provider: intrinio)
        non_cash_adjustments_to_reconcile_net_income : Optional[float]
            Non-Cash Adjustments to Reconcile Net Income. (provider: intrinio)
        changes_in_operating_assets_and_liabilities : Optional[float]
            Changes in Operating Assets and Liabilities (Net) (provider: intrinio)
        net_cash_from_continuing_operating_activities : Optional[float]
            Net Cash from Continuing Operating Activities (provider: intrinio)
        net_cash_from_discontinued_operating_activities : Optional[float]
            Net Cash from Discontinued Operating Activities (provider: intrinio)
        net_income_continuing_operations : Optional[float]
            Net Income (Continuing Operations) (provider: intrinio)
        net_income_discontinued_operations : Optional[float]
            Net Income (Discontinued Operations) (provider: intrinio)
        divestitures : Optional[float]
            Divestitures (provider: intrinio)
        sale_of_property_plant_and_equipment : Optional[float]
            Sale of Property, Plant, and Equipment (provider: intrinio)
        purchase_of_investments : Optional[float]
            Purchase of Investments (provider: intrinio)
        loans_held_for_sale : Optional[float]
            Loans Held for Sale (Net) (provider: intrinio)
        net_cash_from_continuing_investing_activities : Optional[float]
            Net Cash from Continuing Investing Activities (provider: intrinio)
        net_cash_from_discontinued_investing_activities : Optional[float]
            Net Cash from Discontinued Investing Activities (provider: intrinio)
        repurchase_of_preferred_equity : Optional[float]
            Repurchase of Preferred Equity (provider: intrinio)
        issuance_of_preferred_equity : Optional[float]
            Issuance of Preferred Equity (provider: intrinio)
        issuance_of_debt : Optional[float]
            Issuance of Debt (provider: intrinio)
        cash_interest_received : Optional[float]
            Cash Interest Received (provider: intrinio)
        net_change_in_deposits : Optional[float]
            Net Change in Deposits (provider: intrinio)
        net_increase_in_fed_funds_sold : Optional[float]
            Net Increase in Fed Funds Sold (provider: intrinio)
        net_cash_from_continuing_financing_activities : Optional[float]
            Net Cash from Continuing Financing Activities (provider: intrinio)
        net_cash_from_discontinued_financing_activities : Optional[float]
            Net Cash from Discontinued Financing Activities (provider: intrinio)
        effect_of_exchange_rate_changes : Optional[float]
            Effect of Exchange Rate Changes (provider: intrinio)
        other_net_changes_in_cash : Optional[float]
            Other Net Changes in Cash (provider: intrinio)
        cash_income_taxes_paid : Optional[float]
            Cash Income Taxes Paid (provider: intrinio)
        cash_interest_paid : Optional[float]
            Cash Interest Paid (provider: intrinio)
        net_cash_flow_from_operating_activities_continuing : Optional[int]
            Net cash flow from operating activities continuing. (provider: polygon)
        net_cash_flow_from_operating_activities_discontinued : Optional[int]
            Net cash flow from operating activities discontinued. (provider: polygon)
        net_cash_flow_from_operating_activities : Optional[int]
            Net cash flow from operating activities. (provider: polygon)
        net_cash_flow_from_investing_activities_continuing : Optional[int]
            Net cash flow from investing activities continuing. (provider: polygon)
        net_cash_flow_from_investing_activities_discontinued : Optional[int]
            Net cash flow from investing activities discontinued. (provider: polygon)
        net_cash_flow_from_investing_activities : Optional[int]
            Net cash flow from investing activities. (provider: polygon)
        net_cash_flow_from_financing_activities_continuing : Optional[int]
            Net cash flow from financing activities continuing. (provider: polygon)
        net_cash_flow_from_financing_activities_discontinued : Optional[int]
            Net cash flow from financing activities discontinued. (provider: polygon)
        net_cash_flow_from_financing_activities : Optional[int]
            Net cash flow from financing activities. (provider: polygon)
        net_cash_flow_continuing : Optional[int]
            Net cash flow continuing. (provider: polygon)
        net_cash_flow_discontinued : Optional[int]
            Net cash flow discontinued. (provider: polygon)
        exchange_gains_losses : Optional[int]
            Exchange gains losses. (provider: polygon)
        net_cash_flow : Optional[int]
            Net cash flow. (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.cash(symbol="AAPL", period="annual", limit=5)
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/cash",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/cash",
                        ("fmp", "intrinio", "polygon", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "period": period,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def cash_growth(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the growth of a company's cash flow statement items over time.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[CashFlowStatementGrowth]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CashFlowStatementGrowth
        -----------------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        period : str
            Period the statement is returned for.
        growth_net_income : float
            Growth rate of net income.
        growth_depreciation_and_amortization : float
            Growth rate of depreciation and amortization.
        growth_deferred_income_tax : float
            Growth rate of deferred income tax.
        growth_stock_based_compensation : float
            Growth rate of stock-based compensation.
        growth_change_in_working_capital : float
            Growth rate of change in working capital.
        growth_accounts_receivables : float
            Growth rate of accounts receivables.
        growth_inventory : float
            Growth rate of inventory.
        growth_accounts_payables : float
            Growth rate of accounts payables.
        growth_other_working_capital : float
            Growth rate of other working capital.
        growth_other_non_cash_items : float
            Growth rate of other non-cash items.
        growth_net_cash_provided_by_operating_activities : float
            Growth rate of net cash provided by operating activities.
        growth_investments_in_property_plant_and_equipment : float
            Growth rate of investments in property, plant, and equipment.
        growth_acquisitions_net : float
            Growth rate of net acquisitions.
        growth_purchases_of_investments : float
            Growth rate of purchases of investments.
        growth_sales_maturities_of_investments : float
            Growth rate of sales maturities of investments.
        growth_other_investing_activities : float
            Growth rate of other investing activities.
        growth_net_cash_used_for_investing_activities : float
            Growth rate of net cash used for investing activities.
        growth_debt_repayment : float
            Growth rate of debt repayment.
        growth_common_stock_issued : float
            Growth rate of common stock issued.
        growth_common_stock_repurchased : float
            Growth rate of common stock repurchased.
        growth_dividends_paid : float
            Growth rate of dividends paid.
        growth_other_financing_activities : float
            Growth rate of other financing activities.
        growth_net_cash_used_provided_by_financing_activities : float
            Growth rate of net cash used/provided by financing activities.
        growth_effect_of_forex_changes_on_cash : float
            Growth rate of the effect of foreign exchange changes on cash.
        growth_net_change_in_cash : float
            Growth rate of net change in cash.
        growth_cash_at_end_of_period : float
            Growth rate of cash at the end of the period.
        growth_cash_at_beginning_of_period : float
            Growth rate of cash at the beginning of the period.
        growth_operating_cash_flow : float
            Growth rate of operating cash flow.
        growth_capital_expenditure : float
            Growth rate of capital expenditure.
        growth_free_cash_flow : float
            Growth rate of free cash flow.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.cash_growth(symbol="AAPL", limit=10)
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/cash_growth",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/cash_growth",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def dividends(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        provider: Optional[Literal["fmp", "intrinio", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """Get historical dividend data for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        limit : Optional[int]
            The number of data entries to return. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[HistoricalDividends]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        HistoricalDividends
        -------------------
        ex_dividend_date : date
            The ex-dividend date - the date on which the stock begins trading without rights to the dividend.
        amount : float
            The dividend amount per share.
        label : Optional[str]
            Label of the historical dividends. (provider: fmp)
        adj_dividend : Optional[float]
            Adjusted dividend of the historical dividends. (provider: fmp)
        record_date : Optional[date]
            Record date of the historical dividends. (provider: fmp)
        payment_date : Optional[date]
            Payment date of the historical dividends. (provider: fmp)
        declaration_date : Optional[date]
            Declaration date of the historical dividends. (provider: fmp)
        factor : Optional[float]
            factor by which to multiply stock prices before this date, in order to calculate historically-adjusted stock prices. (provider: intrinio)
        currency : Optional[str]
            The currency in which the dividend is paid. (provider: intrinio)
        split_ratio : Optional[float]
            The ratio of the stock split, if a stock split occurred. (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.dividends(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/dividends",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/dividends",
                        ("fmp", "intrinio", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def employee_count(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get historical employee count data for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[HistoricalEmployees]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        HistoricalEmployees
        -------------------
        symbol : str
            Symbol representing the entity requested in the data.
        cik : int
            Central Index Key (CIK) for the requested entity.
        acceptance_time : datetime
            Time of acceptance of the company employee.
        period_of_report : date
            Date of reporting of the company employee.
        company_name : str
            Registered name of the company to retrieve the historical employees of.
        form_type : str
            Form type of the company employee.
        filing_date : date
            Filing date of the company employee
        employee_count : int
            Count of employees of the company.
        source : str
            Source URL which retrieves this data for the company.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.employee_count(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/employee_count",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/employee_count",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def filings(
        self,
        symbol: Annotated[
            Optional[str], OpenBBCustomParameter(description="Symbol to get data for.")
        ] = None,
        form_type: Annotated[
            Optional[str],
            OpenBBCustomParameter(
                description="Filter by form type. Check the data provider for available types."
            ),
        ] = None,
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Optional[Literal["fmp", "intrinio", "sec"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the URLs to SEC filings reported to EDGAR database, such as 10-K, 10-Q, 8-K, and more. SEC
        filings include Form 10-K, Form 10-Q, Form 8-K, the proxy statement, Forms 3, 4, and 5, Schedule 13, Form 114,
        Foreign Investment Disclosures and others. The annual 10-K report is required to be
        filed annually and includes the company's financial statements, management discussion and analysis,
        and audited financial statements.


        Parameters
        ----------
        symbol : Optional[str]
            Symbol to get data for.
        form_type : Optional[str]
            Filter by form type. Check the data provider for available types.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['fmp', 'intrinio', 'sec']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format. (provider: intrinio)
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format. (provider: intrinio)
        thea_enabled : Optional[bool]
            Return filings that have been read by Intrinio's Thea NLP. (provider: intrinio)
        cik : Optional[Union[int, str]]
            Lookup filings by Central Index Key (CIK) instead of by symbol. (provider: sec)
        type : Optional[Literal['1', '1-A', '1-A POS', '1-A-W', '1-E', '1-E AD', '1-K', '1-SA', '1-U', '1-Z', '1-Z-W', '10-12B', '10-12G', '10-D', '10-K', '10-KT', '10-Q', '10-QT', '11-K', '11-KT', '13F-HR', '13F-NT', '13FCONP', '144', '15-12B', '15-12G', '15-15D', '15F-12B', '15F-12G', '15F-15D', '18-12B', '18-K', '19B-4E', '2-A', '2-AF', '2-E', '20-F', '20FR12B', '20FR12G', '24F-2NT', '25', '25-NSE', '253G1', '253G2', '253G3', '253G4', '3', '305B2', '34-12H', '4', '40-17F1', '40-17F2', '40-17G', '40-17GCS', '40-202A', '40-203A', '40-206A', '40-24B2', '40-33', '40-6B', '40-8B25', '40-8F-2', '40-APP', '40-F', '40-OIP', '40FR12B', '40FR12G', '424A', '424B1', '424B2', '424B3', '424B4', '424B5', '424B7', '424B8', '424H', '425', '485APOS', '485BPOS', '485BXT', '486APOS', '486BPOS', '486BXT', '487', '497', '497AD', '497H2', '497J', '497K', '497VPI', '497VPU', '5', '6-K', '6B NTC', '6B ORDR', '8-A12B', '8-A12G', '8-K', '8-K12B', '8-K12G3', '8-K15D5', '8-M', '8F-2 NTC', '8F-2 ORDR', '9-M', 'ABS-15G', 'ABS-EE', 'ADN-MTL', 'ADV-E', 'ADV-H-C', 'ADV-H-T', 'ADV-NR', 'ANNLRPT', 'APP NTC', 'APP ORDR', 'APP WD', 'APP WDG', 'ARS', 'ATS-N', 'ATS-N-C', 'ATS-N/UA', 'AW', 'AW WD', 'C', 'C-AR', 'C-AR-W', 'C-TR', 'C-TR-W', 'C-U', 'C-U-W', 'C-W', 'CB', 'CERT', 'CERTARCA', 'CERTBATS', 'CERTCBO', 'CERTNAS', 'CERTNYS', 'CERTPAC', 'CFPORTAL', 'CFPORTAL-W', 'CORRESP', 'CT ORDER', 'D', 'DEF 14A', 'DEF 14C', 'DEFA14A', 'DEFA14C', 'DEFC14A', 'DEFC14C', 'DEFM14A', 'DEFM14C', 'DEFN14A', 'DEFR14A', 'DEFR14C', 'DEL AM', 'DFAN14A', 'DFRN14A', 'DOS', 'DOSLTR', 'DRS', 'DRSLTR', 'DSTRBRPT', 'EFFECT', 'F-1', 'F-10', 'F-10EF', 'F-10POS', 'F-1MEF', 'F-3', 'F-3ASR', 'F-3D', 'F-3DPOS', 'F-3MEF', 'F-4', 'F-4 POS', 'F-4MEF', 'F-6', 'F-6 POS', 'F-6EF', 'F-7', 'F-7 POS', 'F-8', 'F-8 POS', 'F-80', 'F-80POS', 'F-9', 'F-9 POS', 'F-N', 'F-X', 'FOCUSN', 'FWP', 'G-405', 'G-405N', 'G-FIN', 'G-FINW', 'IRANNOTICE', 'MA', 'MA-A', 'MA-I', 'MA-W', 'MSD', 'MSDCO', 'MSDW', 'N-1', 'N-14', 'N-14 8C', 'N-14MEF', 'N-18F1', 'N-1A', 'N-2', 'N-2 POSASR', 'N-23C-2', 'N-23C3A', 'N-23C3B', 'N-23C3C', 'N-2ASR', 'N-2MEF', 'N-30B-2', 'N-30D', 'N-4', 'N-5', 'N-54A', 'N-54C', 'N-6', 'N-6F', 'N-8A', 'N-8B-2', 'N-8F', 'N-8F NTC', 'N-8F ORDR', 'N-CEN', 'N-CR', 'N-CSR', 'N-CSRS', 'N-MFP', 'N-MFP1', 'N-MFP2', 'N-PX', 'N-Q', 'N-VP', 'N-VPFS', 'NO ACT', 'NPORT-EX', 'NPORT-NP', 'NPORT-P', 'NRSRO-CE', 'NRSRO-UPD', 'NSAR-A', 'NSAR-AT', 'NSAR-B', 'NSAR-BT', 'NSAR-U', 'NT 10-D', 'NT 10-K', 'NT 10-Q', 'NT 11-K', 'NT 20-F', 'NT N-CEN', 'NT N-MFP', 'NT N-MFP1', 'NT N-MFP2', 'NT NPORT-EX', 'NT NPORT-P', 'NT-NCEN', 'NT-NCSR', 'NT-NSAR', 'NTFNCEN', 'NTFNCSR', 'NTFNSAR', 'NTN 10D', 'NTN 10K', 'NTN 10Q', 'NTN 20F', 'OIP NTC', 'OIP ORDR', 'POS 8C', 'POS AM', 'POS AMI', 'POS EX', 'POS462B', 'POS462C', 'POSASR', 'PRE 14A', 'PRE 14C', 'PREC14A', 'PREC14C', 'PREM14A', 'PREM14C', 'PREN14A', 'PRER14A', 'PRER14C', 'PRRN14A', 'PX14A6G', 'PX14A6N', 'QRTLYRPT', 'QUALIF', 'REG-NR', 'REVOKED', 'RW', 'RW WD', 'S-1', 'S-11', 'S-11MEF', 'S-1MEF', 'S-20', 'S-3', 'S-3ASR', 'S-3D', 'S-3DPOS', 'S-3MEF', 'S-4', 'S-4 POS', 'S-4EF', 'S-4MEF', 'S-6', 'S-8', 'S-8 POS', 'S-B', 'S-BMEF', 'SBSE', 'SBSE-A', 'SBSE-BD', 'SBSE-C', 'SBSE-W', 'SC 13D', 'SC 13E1', 'SC 13E3', 'SC 13G', 'SC 14D9', 'SC 14F1', 'SC 14N', 'SC TO-C', 'SC TO-I', 'SC TO-T', 'SC13E4F', 'SC14D1F', 'SC14D9C', 'SC14D9F', 'SD', 'SDR', 'SE', 'SEC ACTION', 'SEC STAFF ACTION', 'SEC STAFF LETTER', 'SF-1', 'SF-3', 'SL', 'SP 15D2', 'STOP ORDER', 'SUPPL', 'T-3', 'TA-1', 'TA-2', 'TA-W', 'TACO', 'TH', 'TTW', 'UNDER', 'UPLOAD', 'WDL-REQ', 'X-17A-5']]
            Type of the SEC filing form. (provider: sec)
        use_cache : bool
            Whether or not to use cache.  If True, cache will store for one day. (provider: sec)

        Returns
        -------
        OBBject
            results : List[CompanyFilings]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'sec']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CompanyFilings
        --------------
        filing_date : date
            The date of the filing.
        accepted_date : Optional[datetime]
            Accepted date of the filing.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        cik : Optional[str]
            Central Index Key (CIK) for the requested entity.
        report_type : Optional[str]
            Type of filing.
        filing_url : Optional[str]
            URL to the filing page.
        report_url : str
            URL to the actual report.
        id : Optional[str]
            Intrinio ID of the filing. (provider: intrinio)
        period_end_date : Optional[date]
            Ending date of the fiscal period for the filing. (provider: intrinio)
        sec_unique_id : Optional[str]
            SEC unique ID of the filing. (provider: intrinio)
        instance_url : Optional[str]
            URL for the XBRL filing for the report. (provider: intrinio)
        industry_group : Optional[str]
            Industry group of the company. (provider: intrinio)
        industry_category : Optional[str]
            Industry category of the company. (provider: intrinio)
        report_date : Optional[date]
            The date of the filing. (provider: sec)
        act : Optional[Union[int, str]]
            The SEC Act number. (provider: sec)
        items : Optional[Union[str, float]]
            The SEC Item numbers. (provider: sec)
        primary_doc_description : Optional[str]
            The description of the primary document. (provider: sec)
        primary_doc : Optional[str]
            The filename of the primary document. (provider: sec)
        accession_number : Optional[Union[int, str]]
            The accession number. (provider: sec)
        file_number : Optional[Union[int, str]]
            The file number. (provider: sec)
        film_number : Optional[Union[int, str]]
            The film number. (provider: sec)
        is_inline_xbrl : Optional[Union[int, str]]
            Whether the filing is an inline XBRL filing. (provider: sec)
        is_xbrl : Optional[Union[int, str]]
            Whether the filing is an XBRL filing. (provider: sec)
        size : Optional[Union[int, str]]
            The size of the filing. (provider: sec)
        complete_submission_url : Optional[str]
            The URL to the complete filing submission. (provider: sec)
        filing_detail_url : Optional[str]
            The URL to the filing details. (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.filings(limit=100)
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/filings",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/filings",
                        ("fmp", "intrinio", "sec"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "form_type": form_type,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def historical_attributes(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed for provider(s): intrinio."
            ),
        ],
        tag: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio."
            ),
        ],
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        frequency: Annotated[
            Optional[Literal["daily", "weekly", "monthly", "quarterly", "yearly"]],
            OpenBBCustomParameter(description="The frequency of the data."),
        ] = "yearly",
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 1000,
        tag_type: Annotated[
            Optional[str],
            OpenBBCustomParameter(description="Filter by type, when applicable."),
        ] = None,
        sort: Annotated[
            Optional[Literal["asc", "desc"]],
            OpenBBCustomParameter(description="Sort order."),
        ] = "desc",
        provider: Optional[Literal["intrinio"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the historical values of a data tag from Intrinio.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed for provider(s): intrinio.
        tag : Union[str, List[str]]
            Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        frequency : Optional[Literal['daily', 'weekly', 'monthly', 'quarterly', 'year...
            The frequency of the data.
        limit : Optional[int]
            The number of data entries to return.
        tag_type : Optional[str]
            Filter by type, when applicable.
        sort : Optional[Literal['asc', 'desc']]
            Sort order.
        provider : Optional[Literal['intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[HistoricalAttributes]
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        HistoricalAttributes
        --------------------
        date : date
            The date of the data.
        symbol : str
            Symbol representing the entity requested in the data.
        tag : Optional[str]
            Tag name for the fetched data.
        value : Optional[float]
            The value of the data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.historical_attributes(tag='ebitda')
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/historical_attributes",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/historical_attributes",
                        ("intrinio",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "tag": tag,
                    "start_date": start_date,
                    "end_date": end_date,
                    "frequency": frequency,
                    "limit": limit,
                    "tag_type": tag_type,
                    "sort": sort,
                },
                extra_params=kwargs,
                extra_info={
                    "symbol": {"multiple_items_allowed": ["intrinio"]},
                    "tag": {"multiple_items_allowed": ["intrinio"]},
                },
            )
        )

    @exception_handler
    @validate
    def historical_eps(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get historical earnings per share data for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        limit : Optional[int]
            The number of data entries to return. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[HistoricalEps]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        HistoricalEps
        -------------
        date : Optional[date]
            The date of the data.
        symbol : str
            Symbol representing the entity requested in the data.
        announce_time : Optional[str]
            Timing of the earnings announcement.
        eps_actual : Optional[float]
            Actual EPS from the earnings date.
        eps_estimated : Optional[float]
            Estimated EPS for the earnings date.
        revenue_estimated : Optional[float]
            Estimated consensus revenue for the reporting period. (provider: fmp)
        revenue_actual : Optional[float]
            The actual reported revenue. (provider: fmp)
        reporting_time : Optional[str]
            The reporting time - e.g. after market close. (provider: fmp)
        updated_at : Optional[date]
            The date when the data was last updated. (provider: fmp)
        period_ending : Optional[date]
            The fiscal period end date. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.historical_eps(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/historical_eps",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/historical_eps",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def historical_splits(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get historical stock splits for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[HistoricalSplits]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        HistoricalSplits
        ----------------
        date : date
            The date of the data.
        label : str
            Label of the historical stock splits.
        numerator : float
            Numerator of the historical stock splits.
        denominator : float
            Denominator of the historical stock splits.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.historical_splits(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/historical_splits",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/historical_splits",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def income(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        period: Annotated[
            str, OpenBBCustomParameter(description="Time period of the data to return.")
        ] = "annual",
        limit: Annotated[
            Optional[Annotated[int, Ge(ge=0)]],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 5,
        provider: Optional[Literal["fmp", "intrinio", "polygon", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the income statement for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : str
            Time period of the data to return.
        limit : Optional[Annotated[int, Ge(ge=0)]]
            The number of data entries to return.
        provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        fiscal_year : Optional[int]
            The specific fiscal year.  Reports do not go beyond 2008. (provider: intrinio)
        filing_date : Optional[datetime.date]
            Filing date of the financial statement. (provider: polygon)
        filing_date_lt : Optional[datetime.date]
            Filing date less than the given date. (provider: polygon)
        filing_date_lte : Optional[datetime.date]
            Filing date less than or equal to the given date. (provider: polygon)
        filing_date_gt : Optional[datetime.date]
            Filing date greater than the given date. (provider: polygon)
        filing_date_gte : Optional[datetime.date]
            Filing date greater than or equal to the given date. (provider: polygon)
        period_of_report_date : Optional[datetime.date]
            Period of report date of the financial statement. (provider: polygon)
        period_of_report_date_lt : Optional[datetime.date]
            Period of report date less than the given date. (provider: polygon)
        period_of_report_date_lte : Optional[datetime.date]
            Period of report date less than or equal to the given date. (provider: polygon)
        period_of_report_date_gt : Optional[datetime.date]
            Period of report date greater than the given date. (provider: polygon)
        period_of_report_date_gte : Optional[datetime.date]
            Period of report date greater than or equal to the given date. (provider: polygon)
        include_sources : Optional[bool]
            Whether to include the sources of the financial statement. (provider: polygon)
        order : Optional[Literal['asc', 'desc']]
            Order of the financial statement. (provider: polygon)
        sort : Optional[Literal['filing_date', 'period_of_report_date']]
            Sort of the financial statement. (provider: polygon)

        Returns
        -------
        OBBject
            results : List[IncomeStatement]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'polygon', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        IncomeStatement
        ---------------
        period_ending : date
            The end date of the reporting period.
        fiscal_period : Optional[str]
            The fiscal period of the report.
        fiscal_year : Optional[int]
            The fiscal year of the fiscal period.
        filing_date : Optional[date]
            The date when the filing was made. (provider: fmp)
        accepted_date : Optional[datetime]
            The date and time when the filing was accepted. (provider: fmp)
        reported_currency : Optional[str]
            The currency in which the balance sheet was reported. (provider: fmp, intrinio)
        revenue : Optional[float]
            Total revenue. (provider: fmp, intrinio, polygon)
        cost_of_revenue : Optional[float]
            Cost of revenue. (provider: fmp, intrinio, polygon)
        gross_profit : Optional[float]
            Gross profit. (provider: fmp, intrinio, polygon)
        gross_profit_margin : Optional[float]
            Gross profit margin. (provider: fmp);
            Gross margin ratio. (provider: intrinio)
        general_and_admin_expense : Optional[float]
            General and administrative expenses. (provider: fmp)
        research_and_development_expense : Optional[float]
            Research and development expenses. (provider: fmp, intrinio)
        selling_and_marketing_expense : Optional[float]
            Selling and marketing expenses. (provider: fmp)
        selling_general_and_admin_expense : Optional[float]
            Selling, general and administrative expenses. (provider: fmp, intrinio)
        other_expenses : Optional[float]
            Other expenses. (provider: fmp)
        total_operating_expenses : Optional[float]
            Total operating expenses. (provider: fmp, intrinio)
        cost_and_expenses : Optional[float]
            Cost and expenses. (provider: fmp)
        interest_income : Optional[float]
            Interest income. (provider: fmp)
        total_interest_expense : Optional[float]
            Total interest expenses. (provider: fmp, intrinio);
            Interest Expense (provider: polygon)
        depreciation_and_amortization : Optional[float]
            Depreciation and amortization. (provider: fmp, polygon)
        ebitda : Optional[float]
            EBITDA. (provider: fmp);
            Earnings Before Interest, Taxes, Depreciation and Amortization. (provider: intrinio)
        ebitda_margin : Optional[float]
            EBITDA margin. (provider: fmp);
            Margin on Earnings Before Interest, Taxes, Depreciation and Amortization. (provider: intrinio)
        total_operating_income : Optional[float]
            Total operating income. (provider: fmp, intrinio)
        operating_income_margin : Optional[float]
            Operating income margin. (provider: fmp)
        total_other_income_expenses : Optional[float]
            Total other income and expenses. (provider: fmp)
        total_pre_tax_income : Optional[float]
            Total pre-tax income. (provider: fmp, intrinio);
            Income Before Tax (provider: polygon)
        pre_tax_income_margin : Optional[float]
            Pre-tax income margin. (provider: fmp, intrinio)
        income_tax_expense : Optional[float]
            Income tax expense. (provider: fmp, intrinio, polygon)
        consolidated_net_income : Optional[float]
            Consolidated net income. (provider: fmp, intrinio);
            Net Income/Loss (provider: polygon)
        net_income_margin : Optional[float]
            Net income margin. (provider: fmp)
        basic_earnings_per_share : Optional[float]
            Basic earnings per share. (provider: fmp, intrinio);
            Earnings Per Share (provider: polygon)
        diluted_earnings_per_share : Optional[float]
            Diluted earnings per share. (provider: fmp, intrinio, polygon)
        weighted_average_basic_shares_outstanding : Optional[float]
            Weighted average basic shares outstanding. (provider: fmp, intrinio);
            Basic Average Shares (provider: polygon)
        weighted_average_diluted_shares_outstanding : Optional[float]
            Weighted average diluted shares outstanding. (provider: fmp, intrinio);
            Diluted Average Shares (provider: polygon)
        link : Optional[str]
            Link to the filing. (provider: fmp)
        final_link : Optional[str]
            Link to the filing document. (provider: fmp)
        operating_revenue : Optional[float]
            Total operating revenue (provider: intrinio)
        operating_cost_of_revenue : Optional[float]
            Total operating cost of revenue (provider: intrinio)
        provision_for_credit_losses : Optional[float]
            Provision for credit losses (provider: intrinio)
        salaries_and_employee_benefits : Optional[float]
            Salaries and employee benefits (provider: intrinio)
        marketing_expense : Optional[float]
            Marketing expense (provider: intrinio)
        net_occupancy_and_equipment_expense : Optional[float]
            Net occupancy and equipment expense (provider: intrinio)
        other_operating_expenses : Optional[float]
            Other operating expenses (provider: intrinio, polygon)
        depreciation_expense : Optional[float]
            Depreciation expense (provider: intrinio)
        amortization_expense : Optional[float]
            Amortization expense (provider: intrinio)
        amortization_of_deferred_policy_acquisition_costs : Optional[float]
            Amortization of deferred policy acquisition costs (provider: intrinio)
        exploration_expense : Optional[float]
            Exploration expense (provider: intrinio)
        depletion_expense : Optional[float]
            Depletion expense (provider: intrinio)
        deposits_and_money_market_investments_interest_income : Optional[float]
            Deposits and money market investments interest income (provider: intrinio)
        federal_funds_sold_and_securities_borrowed_interest_income : Optional[float]
            Federal funds sold and securities borrowed interest income (provider: intrinio)
        investment_securities_interest_income : Optional[float]
            Investment securities interest income (provider: intrinio)
        loans_and_leases_interest_income : Optional[float]
            Loans and leases interest income (provider: intrinio)
        trading_account_interest_income : Optional[float]
            Trading account interest income (provider: intrinio)
        other_interest_income : Optional[float]
            Other interest income (provider: intrinio)
        total_non_interest_income : Optional[float]
            Total non-interest income (provider: intrinio)
        interest_and_investment_income : Optional[float]
            Interest and investment income (provider: intrinio)
        short_term_borrowings_interest_expense : Optional[float]
            Short-term borrowings interest expense (provider: intrinio)
        long_term_debt_interest_expense : Optional[float]
            Long-term debt interest expense (provider: intrinio)
        capitalized_lease_obligations_interest_expense : Optional[float]
            Capitalized lease obligations interest expense (provider: intrinio)
        deposits_interest_expense : Optional[float]
            Deposits interest expense (provider: intrinio)
        federal_funds_purchased_and_securities_sold_interest_expense : Optional[float]
            Federal funds purchased and securities sold interest expense (provider: intrinio)
        other_interest_expense : Optional[float]
            Other interest expense (provider: intrinio)
        net_interest_income : Optional[float]
            Net interest income (provider: intrinio);
            Interest Income Net (provider: polygon)
        other_non_interest_income : Optional[float]
            Other non-interest income (provider: intrinio)
        investment_banking_income : Optional[float]
            Investment banking income (provider: intrinio)
        trust_fees_by_commissions : Optional[float]
            Trust fees by commissions (provider: intrinio)
        premiums_earned : Optional[float]
            Premiums earned (provider: intrinio)
        insurance_policy_acquisition_costs : Optional[float]
            Insurance policy acquisition costs (provider: intrinio)
        current_and_future_benefits : Optional[float]
            Current and future benefits (provider: intrinio)
        property_and_liability_insurance_claims : Optional[float]
            Property and liability insurance claims (provider: intrinio)
        total_non_interest_expense : Optional[float]
            Total non-interest expense (provider: intrinio)
        net_realized_and_unrealized_capital_gains_on_investments : Optional[float]
            Net realized and unrealized capital gains on investments (provider: intrinio)
        other_gains : Optional[float]
            Other gains (provider: intrinio)
        non_operating_income : Optional[float]
            Non-operating income (provider: intrinio);
            Non Operating Income/Loss (provider: polygon)
        other_income : Optional[float]
            Other income (provider: intrinio)
        other_revenue : Optional[float]
            Other revenue (provider: intrinio)
        extraordinary_income : Optional[float]
            Extraordinary income (provider: intrinio)
        total_other_income : Optional[float]
            Total other income (provider: intrinio)
        ebit : Optional[float]
            Earnings Before Interest and Taxes. (provider: intrinio)
        impairment_charge : Optional[float]
            Impairment charge (provider: intrinio)
        restructuring_charge : Optional[float]
            Restructuring charge (provider: intrinio)
        service_charges_on_deposit_accounts : Optional[float]
            Service charges on deposit accounts (provider: intrinio)
        other_service_charges : Optional[float]
            Other service charges (provider: intrinio)
        other_special_charges : Optional[float]
            Other special charges (provider: intrinio)
        other_cost_of_revenue : Optional[float]
            Other cost of revenue (provider: intrinio)
        net_income_continuing_operations : Optional[float]
            Net income (continuing operations) (provider: intrinio)
        net_income_discontinued_operations : Optional[float]
            Net income (discontinued operations) (provider: intrinio)
        other_adjustments_to_consolidated_net_income : Optional[float]
            Other adjustments to consolidated net income (provider: intrinio)
        other_adjustment_to_net_income_attributable_to_common_shareholders : Optional[float]
            Other adjustment to net income attributable to common shareholders (provider: intrinio)
        net_income_attributable_to_noncontrolling_interest : Optional[float]
            Net income attributable to noncontrolling interest (provider: intrinio)
        net_income_attributable_to_common_shareholders : Optional[float]
            Net income attributable to common shareholders (provider: intrinio);
            Net Income/Loss Available To Common Stockholders Basic (provider: polygon)
        basic_and_diluted_earnings_per_share : Optional[float]
            Basic and diluted earnings per share (provider: intrinio)
        cash_dividends_to_common_per_share : Optional[float]
            Cash dividends to common per share (provider: intrinio)
        preferred_stock_dividends_declared : Optional[float]
            Preferred stock dividends declared (provider: intrinio)
        weighted_average_basic_and_diluted_shares_outstanding : Optional[float]
            Weighted average basic and diluted shares outstanding (provider: intrinio)
        cost_of_revenue_goods : Optional[float]
            Cost of Revenue - Goods (provider: polygon)
        cost_of_revenue_services : Optional[float]
            Cost of Revenue - Services (provider: polygon)
        provisions_for_loan_lease_and_other_losses : Optional[float]
            Provisions for loan lease and other losses (provider: polygon)
        income_tax_expense_benefit_current : Optional[float]
            Income tax expense benefit current (provider: polygon)
        deferred_tax_benefit : Optional[float]
            Deferred tax benefit (provider: polygon)
        benefits_costs_expenses : Optional[float]
            Benefits, costs and expenses (provider: polygon)
        selling_general_and_administrative_expense : Optional[float]
            Selling, general and administrative expense (provider: polygon)
        research_and_development : Optional[float]
            Research and development (provider: polygon)
        costs_and_expenses : Optional[float]
            Costs and expenses (provider: polygon)
        operating_expenses : Optional[float]
            Operating expenses (provider: polygon)
        operating_income : Optional[float]
            Operating Income/Loss (provider: polygon)
        interest_and_dividend_income : Optional[float]
            Interest and Dividend Income (provider: polygon)
        interest_and_debt_expense : Optional[float]
            Interest and Debt Expense (provider: polygon)
        interest_income_after_provision_for_losses : Optional[float]
            Interest Income After Provision for Losses (provider: polygon)
        non_interest_expense : Optional[float]
            Non-Interest Expense (provider: polygon)
        non_interest_income : Optional[float]
            Non-Interest Income (provider: polygon)
        income_from_discontinued_operations_net_of_tax_on_disposal : Optional[float]
            Income From Discontinued Operations Net of Tax on Disposal (provider: polygon)
        income_from_discontinued_operations_net_of_tax : Optional[float]
            Income From Discontinued Operations Net of Tax (provider: polygon)
        income_before_equity_method_investments : Optional[float]
            Income Before Equity Method Investments (provider: polygon)
        income_from_equity_method_investments : Optional[float]
            Income From Equity Method Investments (provider: polygon)
        income_after_tax : Optional[float]
            Income After Tax (provider: polygon)
        net_income_attributable_noncontrolling_interest : Optional[float]
            Net income (loss) attributable to noncontrolling interest (provider: polygon)
        net_income_attributable_to_parent : Optional[float]
            Net income (loss) attributable to parent (provider: polygon)
        participating_securities_earnings : Optional[float]
            Participating Securities Distributed And Undistributed Earnings Loss Basic (provider: polygon)
        undistributed_earnings_allocated_to_participating_securities : Optional[float]
            Undistributed Earnings Allocated To Participating Securities (provider: polygon)
        common_stock_dividends : Optional[float]
            Common Stock Dividends (provider: polygon)
        preferred_stock_dividends_and_other_adjustments : Optional[float]
            Preferred stock dividends and other adjustments (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.income(symbol="AAPL", period="annual", limit=5)
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/income",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/income",
                        ("fmp", "intrinio", "polygon", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "period": period,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def income_growth(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        period: Annotated[
            Literal["quarter", "annual"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the growth of a company's income statement items over time.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        limit : int
            The number of data entries to return.
        period : Literal['quarter', 'annual']
            Time period of the data to return.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[IncomeStatementGrowth]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        IncomeStatementGrowth
        ---------------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        period : str
            Period the statement is returned for.
        growth_revenue : float
            Growth rate of total revenue.
        growth_cost_of_revenue : float
            Growth rate of cost of goods sold.
        growth_gross_profit : float
            Growth rate of gross profit.
        growth_gross_profit_ratio : float
            Growth rate of gross profit as a percentage of revenue.
        growth_research_and_development_expenses : float
            Growth rate of expenses on research and development.
        growth_general_and_administrative_expenses : float
            Growth rate of general and administrative expenses.
        growth_selling_and_marketing_expenses : float
            Growth rate of expenses on selling and marketing activities.
        growth_other_expenses : float
            Growth rate of other operating expenses.
        growth_operating_expenses : float
            Growth rate of total operating expenses.
        growth_cost_and_expenses : float
            Growth rate of total costs and expenses.
        growth_interest_expense : float
            Growth rate of interest expenses.
        growth_depreciation_and_amortization : float
            Growth rate of depreciation and amortization expenses.
        growth_ebitda : float
            Growth rate of Earnings Before Interest, Taxes, Depreciation, and Amortization.
        growth_ebitda_ratio : float
            Growth rate of EBITDA as a percentage of revenue.
        growth_operating_income : float
            Growth rate of operating income.
        growth_operating_income_ratio : float
            Growth rate of operating income as a percentage of revenue.
        growth_total_other_income_expenses_net : float
            Growth rate of net total other income and expenses.
        growth_income_before_tax : float
            Growth rate of income before taxes.
        growth_income_before_tax_ratio : float
            Growth rate of income before taxes as a percentage of revenue.
        growth_income_tax_expense : float
            Growth rate of income tax expenses.
        growth_net_income : float
            Growth rate of net income.
        growth_net_income_ratio : float
            Growth rate of net income as a percentage of revenue.
        growth_eps : float
            Growth rate of Earnings Per Share (EPS).
        growth_eps_diluted : float
            Growth rate of diluted Earnings Per Share (EPS).
        growth_weighted_average_shs_out : float
            Growth rate of weighted average shares outstanding.
        growth_weighted_average_shs_out_dil : float
            Growth rate of diluted weighted average shares outstanding.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.income_growth(symbol="AAPL", limit=10, period="annual")
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/income_growth",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/income_growth",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "limit": limit,
                    "period": period,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def latest_attributes(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed for provider(s): intrinio."
            ),
        ],
        tag: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio."
            ),
        ],
        provider: Optional[Literal["intrinio"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the latest value of a data tag from Intrinio.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed for provider(s): intrinio.
        tag : Union[str, List[str]]
            Intrinio data tag ID or code. Multiple items allowed for provider(s): intrinio.
        provider : Optional[Literal['intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[LatestAttributes]
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        LatestAttributes
        ----------------
        symbol : str
            Symbol representing the entity requested in the data.
        tag : Optional[str]
            Tag name for the fetched data.
        value : Optional[Union[str, float]]
            The value of the data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.latest_attributes(tag='ceo')
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/latest_attributes",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/latest_attributes",
                        ("intrinio",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "tag": tag,
                },
                extra_params=kwargs,
                extra_info={
                    "symbol": {"multiple_items_allowed": ["intrinio"]},
                    "tag": {"multiple_items_allowed": ["intrinio"]},
                },
            )
        )

    @exception_handler
    @validate
    def management(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        provider: Optional[Literal["fmp", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """Get executive management team data for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[KeyExecutives]
                Serializable results.
            provider : Optional[Literal['fmp', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        KeyExecutives
        -------------
        title : str
            Designation of the key executive.
        name : str
            Name of the key executive.
        pay : Optional[int]
            Pay of the key executive.
        currency_pay : Optional[str]
            Currency of the pay.
        gender : Optional[str]
            Gender of the key executive.
        year_born : Optional[int]
            Birth year of the key executive.
        title_since : Optional[int]
            Date the tile was held since.
        exercised_value : Optional[int]
            Value of shares exercised. (provider: yfinance)
        unexercised_value : Optional[int]
            Value of shares not exercised. (provider: yfinance)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.management(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/management",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/management",
                        ("fmp", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def management_compensation(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed for provider(s): fmp."
            ),
        ],
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get executive management team compensation for a given company over time.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed for provider(s): fmp.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[ExecutiveCompensation]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ExecutiveCompensation
        ---------------------
        symbol : str
            Symbol representing the entity requested in the data.
        cik : Optional[str]
            Central Index Key (CIK) for the requested entity.
        filing_date : date
            Date of the filing.
        accepted_date : datetime
            Date the filing was accepted.
        name_and_position : str
            Name and position of the executive.
        year : int
            Year of the compensation.
        salary : float
            Salary of the executive.
        bonus : float
            Bonus of the executive.
        stock_award : float
            Stock award of the executive.
        incentive_plan_compensation : float
            Incentive plan compensation of the executive.
        all_other_compensation : float
            All other compensation of the executive.
        total : float
            Total compensation of the executive.
        url : str
            URL of the filing data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.management_compensation(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/management_compensation",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/management_compensation",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                extra_info={"symbol": {"multiple_items_allowed": ["fmp"]}},
            )
        )

    @exception_handler
    @validate
    def metrics(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed for provider(s): fmp, yfinance."
            ),
        ],
        period: Annotated[
            Optional[Literal["annual", "quarter"]],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Optional[Literal["fmp", "intrinio", "yfinance"]] = None,
        **kwargs
    ) -> OBBject:
        """Get fundamental metrics for a given company.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed for provider(s): fmp, yfinance.
        period : Optional[Literal['annual', 'quarter']]
            Time period of the data to return.
        limit : Optional[int]
            The number of data entries to return.
        provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        with_ttm : Optional[bool]
            Include trailing twelve months (TTM) data. (provider: fmp)

        Returns
        -------
        OBBject
            results : Union[List[KeyMetrics], KeyMetrics]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'yfinance']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        KeyMetrics
        ----------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        market_cap : Optional[float]
            Market capitalization
        pe_ratio : Optional[float]
            Price-to-earnings ratio (P/E ratio)
        date : Optional[date]
            The date of the data. (provider: fmp)
        period : Optional[str]
            Period of the data. (provider: fmp)
        calendar_year : Optional[int]
            Calendar year. (provider: fmp)
        revenue_per_share : Optional[float]
            Revenue per share (provider: fmp, yfinance)
        net_income_per_share : Optional[float]
            Net income per share (provider: fmp)
        operating_cash_flow_per_share : Optional[float]
            Operating cash flow per share (provider: fmp)
        free_cash_flow_per_share : Optional[float]
            Free cash flow per share (provider: fmp)
        cash_per_share : Optional[float]
            Cash per share (provider: fmp, yfinance)
        book_value_per_share : Optional[float]
            Book value per share (provider: fmp)
        tangible_book_value_per_share : Optional[float]
            Tangible book value per share (provider: fmp)
        shareholders_equity_per_share : Optional[float]
            Shareholders equity per share (provider: fmp)
        interest_debt_per_share : Optional[float]
            Interest debt per share (provider: fmp)
        enterprise_value : Optional[Union[float, int]]
            Enterprise value (provider: fmp, yfinance)
        price_to_sales_ratio : Optional[float]
            Price-to-sales ratio (provider: fmp)
        pocf_ratio : Optional[float]
            Price-to-operating cash flow ratio (provider: fmp)
        pfcf_ratio : Optional[float]
            Price-to-free cash flow ratio (provider: fmp)
        pb_ratio : Optional[float]
            Price-to-book ratio (provider: fmp)
        ptb_ratio : Optional[float]
            Price-to-tangible book ratio (provider: fmp)
        ev_to_sales : Optional[float]
            Enterprise value-to-sales ratio (provider: fmp)
        enterprise_value_over_ebitda : Optional[float]
            Enterprise value-to-EBITDA ratio (provider: fmp)
        ev_to_operating_cash_flow : Optional[float]
            Enterprise value-to-operating cash flow ratio (provider: fmp)
        ev_to_free_cash_flow : Optional[float]
            Enterprise value-to-free cash flow ratio (provider: fmp)
        earnings_yield : Optional[float]
            Earnings yield (provider: fmp)
        free_cash_flow_yield : Optional[float]
            Free cash flow yield (provider: fmp)
        debt_to_equity : Optional[float]
            Debt-to-equity ratio (provider: fmp, yfinance)
        debt_to_assets : Optional[float]
            Debt-to-assets ratio (provider: fmp)
        net_debt_to_ebitda : Optional[float]
            Net debt-to-EBITDA ratio (provider: fmp)
        current_ratio : Optional[float]
            Current ratio (provider: fmp, yfinance)
        interest_coverage : Optional[float]
            Interest coverage (provider: fmp)
        income_quality : Optional[float]
            Income quality (provider: fmp)
        dividend_yield : Optional[float]
            Dividend yield, as a normalized percent. (provider: fmp, intrinio, yfinance)
        payout_ratio : Optional[float]
            Payout ratio (provider: fmp, yfinance)
        sales_general_and_administrative_to_revenue : Optional[float]
            Sales general and administrative expenses-to-revenue ratio (provider: fmp)
        research_and_development_to_revenue : Optional[float]
            Research and development expenses-to-revenue ratio (provider: fmp)
        intangibles_to_total_assets : Optional[float]
            Intangibles-to-total assets ratio (provider: fmp)
        capex_to_operating_cash_flow : Optional[float]
            Capital expenditures-to-operating cash flow ratio (provider: fmp)
        capex_to_revenue : Optional[float]
            Capital expenditures-to-revenue ratio (provider: fmp)
        capex_to_depreciation : Optional[float]
            Capital expenditures-to-depreciation ratio (provider: fmp)
        stock_based_compensation_to_revenue : Optional[float]
            Stock-based compensation-to-revenue ratio (provider: fmp)
        graham_number : Optional[float]
            Graham number (provider: fmp)
        roic : Optional[float]
            Return on invested capital (provider: fmp)
        return_on_tangible_assets : Optional[float]
            Return on tangible assets (provider: fmp)
        graham_net_net : Optional[float]
            Graham net-net working capital (provider: fmp)
        working_capital : Optional[float]
            Working capital (provider: fmp)
        tangible_asset_value : Optional[float]
            Tangible asset value (provider: fmp)
        net_current_asset_value : Optional[float]
            Net current asset value (provider: fmp)
        invested_capital : Optional[float]
            Invested capital (provider: fmp)
        average_receivables : Optional[float]
            Average receivables (provider: fmp)
        average_payables : Optional[float]
            Average payables (provider: fmp)
        average_inventory : Optional[float]
            Average inventory (provider: fmp)
        days_sales_outstanding : Optional[float]
            Days sales outstanding (provider: fmp)
        days_payables_outstanding : Optional[float]
            Days payables outstanding (provider: fmp)
        days_of_inventory_on_hand : Optional[float]
            Days of inventory on hand (provider: fmp)
        receivables_turnover : Optional[float]
            Receivables turnover (provider: fmp)
        payables_turnover : Optional[float]
            Payables turnover (provider: fmp)
        inventory_turnover : Optional[float]
            Inventory turnover (provider: fmp)
        roe : Optional[float]
            Return on equity (provider: fmp)
        capex_per_share : Optional[float]
            Capital expenditures per share (provider: fmp)
        beta : Optional[float]
            Beta relative to the broad market calculated on a rolling three-year basis. (provider: intrinio);
            Beta relative to the broad market (5-year monthly). (provider: yfinance)
        volume : Optional[float]
            Volume (provider: intrinio)
        fifty_two_week_high : Optional[float]
            52 week high (provider: intrinio)
        fifty_two_week_low : Optional[float]
            52 week low (provider: intrinio)
        forward_pe : Optional[float]
            Forward price-to-earnings ratio. (provider: yfinance)
        peg_ratio : Optional[float]
            PEG ratio (5-year expected). (provider: yfinance)
        peg_ratio_ttm : Optional[float]
            PEG ratio (TTM). (provider: yfinance)
        eps_ttm : Optional[float]
            Earnings per share (TTM). (provider: yfinance)
        eps_forward : Optional[float]
            Forward earnings per share. (provider: yfinance)
        enterprise_to_ebitda : Optional[float]
            Enterprise value to EBITDA ratio. (provider: yfinance)
        earnings_growth : Optional[float]
            Earnings growth (Year Over Year), as a normalized percent. (provider: yfinance)
        earnings_growth_quarterly : Optional[float]
            Quarterly earnings growth (Year Over Year), as a normalized percent. (provider: yfinance)
        revenue_growth : Optional[float]
            Revenue growth (Year Over Year), as a normalized percent. (provider: yfinance)
        enterprise_to_revenue : Optional[float]
            Enterprise value to revenue ratio. (provider: yfinance)
        quick_ratio : Optional[float]
            Quick ratio. (provider: yfinance)
        gross_margin : Optional[float]
            Gross margin, as a normalized percent. (provider: yfinance)
        operating_margin : Optional[float]
            Operating margin, as a normalized percent. (provider: yfinance)
        ebitda_margin : Optional[float]
            EBITDA margin, as a normalized percent. (provider: yfinance)
        profit_margin : Optional[float]
            Profit margin, as a normalized percent. (provider: yfinance)
        return_on_assets : Optional[float]
            Return on assets, as a normalized percent. (provider: yfinance)
        return_on_equity : Optional[float]
            Return on equity, as a normalized percent. (provider: yfinance)
        dividend_yield_5y_avg : Optional[float]
            5-year average dividend yield, as a normalized percent. (provider: yfinance)
        book_value : Optional[float]
            Book value per share. (provider: yfinance)
        price_to_book : Optional[float]
            Price-to-book ratio. (provider: yfinance)
        overall_risk : Optional[float]
            Overall risk score. (provider: yfinance)
        audit_risk : Optional[float]
            Audit risk score. (provider: yfinance)
        board_risk : Optional[float]
            Board risk score. (provider: yfinance)
        compensation_risk : Optional[float]
            Compensation risk score. (provider: yfinance)
        shareholder_rights_risk : Optional[float]
            Shareholder rights risk score. (provider: yfinance)
        price_return_1y : Optional[float]
            One-year price return, as a normalized percent. (provider: yfinance)
        currency : Optional[str]
            Currency in which the data is presented. (provider: yfinance)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.metrics(symbol="AAPL", period="annual", limit=100)
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/metrics",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/metrics",
                        ("fmp", "intrinio", "yfinance"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "period": period,
                    "limit": limit,
                },
                extra_params=kwargs,
                extra_info={"symbol": {"multiple_items_allowed": ["fmp", "yfinance"]}},
            )
        )

    @exception_handler
    @validate
    def multiples(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="Symbol to get data for. Multiple items allowed for provider(s): fmp."
            ),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get equity valuation multiples for a given company.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple items allowed for provider(s): fmp.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EquityValuationMultiples]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EquityValuationMultiples
        ------------------------
        symbol : str
            Symbol representing the entity requested in the data.
        revenue_per_share_ttm : Optional[float]
            Revenue per share calculated as trailing twelve months.
        net_income_per_share_ttm : Optional[float]
            Net income per share calculated as trailing twelve months.
        operating_cash_flow_per_share_ttm : Optional[float]
            Operating cash flow per share calculated as trailing twelve months.
        free_cash_flow_per_share_ttm : Optional[float]
            Free cash flow per share calculated as trailing twelve months.
        cash_per_share_ttm : Optional[float]
            Cash per share calculated as trailing twelve months.
        book_value_per_share_ttm : Optional[float]
            Book value per share calculated as trailing twelve months.
        tangible_book_value_per_share_ttm : Optional[float]
            Tangible book value per share calculated as trailing twelve months.
        shareholders_equity_per_share_ttm : Optional[float]
            Shareholders equity per share calculated as trailing twelve months.
        interest_debt_per_share_ttm : Optional[float]
            Interest debt per share calculated as trailing twelve months.
        market_cap_ttm : Optional[float]
            Market capitalization calculated as trailing twelve months.
        enterprise_value_ttm : Optional[float]
            Enterprise value calculated as trailing twelve months.
        pe_ratio_ttm : Optional[float]
            Price-to-earnings ratio (P/E ratio) calculated as trailing twelve months.
        price_to_sales_ratio_ttm : Optional[float]
            Price-to-sales ratio calculated as trailing twelve months.
        pocf_ratio_ttm : Optional[float]
            Price-to-operating cash flow ratio calculated as trailing twelve months.
        pfcf_ratio_ttm : Optional[float]
            Price-to-free cash flow ratio calculated as trailing twelve months.
        pb_ratio_ttm : Optional[float]
            Price-to-book ratio calculated as trailing twelve months.
        ptb_ratio_ttm : Optional[float]
            Price-to-tangible book ratio calculated as trailing twelve months.
        ev_to_sales_ttm : Optional[float]
            Enterprise value-to-sales ratio calculated as trailing twelve months.
        enterprise_value_over_ebitda_ttm : Optional[float]
            Enterprise value-to-EBITDA ratio calculated as trailing twelve months.
        ev_to_operating_cash_flow_ttm : Optional[float]
            Enterprise value-to-operating cash flow ratio calculated as trailing twelve months.
        ev_to_free_cash_flow_ttm : Optional[float]
            Enterprise value-to-free cash flow ratio calculated as trailing twelve months.
        earnings_yield_ttm : Optional[float]
            Earnings yield calculated as trailing twelve months.
        free_cash_flow_yield_ttm : Optional[float]
            Free cash flow yield calculated as trailing twelve months.
        debt_to_equity_ttm : Optional[float]
            Debt-to-equity ratio calculated as trailing twelve months.
        debt_to_assets_ttm : Optional[float]
            Debt-to-assets ratio calculated as trailing twelve months.
        net_debt_to_ebitda_ttm : Optional[float]
            Net debt-to-EBITDA ratio calculated as trailing twelve months.
        current_ratio_ttm : Optional[float]
            Current ratio calculated as trailing twelve months.
        interest_coverage_ttm : Optional[float]
            Interest coverage calculated as trailing twelve months.
        income_quality_ttm : Optional[float]
            Income quality calculated as trailing twelve months.
        dividend_yield_ttm : Optional[float]
            Dividend yield calculated as trailing twelve months.
        dividend_yield_percentage_ttm : Optional[float]
            Dividend yield percentage calculated as trailing twelve months.
        dividend_to_market_cap_ttm : Optional[float]
            Dividend to market capitalization ratio calculated as trailing twelve months.
        dividend_per_share_ttm : Optional[float]
            Dividend per share calculated as trailing twelve months.
        payout_ratio_ttm : Optional[float]
            Payout ratio calculated as trailing twelve months.
        sales_general_and_administrative_to_revenue_ttm : Optional[float]
            Sales general and administrative expenses-to-revenue ratio calculated as trailing twelve months.
        research_and_development_to_revenue_ttm : Optional[float]
            Research and development expenses-to-revenue ratio calculated as trailing twelve months.
        intangibles_to_total_assets_ttm : Optional[float]
            Intangibles-to-total assets ratio calculated as trailing twelve months.
        capex_to_operating_cash_flow_ttm : Optional[float]
            Capital expenditures-to-operating cash flow ratio calculated as trailing twelve months.
        capex_to_revenue_ttm : Optional[float]
            Capital expenditures-to-revenue ratio calculated as trailing twelve months.
        capex_to_depreciation_ttm : Optional[float]
            Capital expenditures-to-depreciation ratio calculated as trailing twelve months.
        stock_based_compensation_to_revenue_ttm : Optional[float]
            Stock-based compensation-to-revenue ratio calculated as trailing twelve months.
        graham_number_ttm : Optional[float]
            Graham number calculated as trailing twelve months.
        roic_ttm : Optional[float]
            Return on invested capital calculated as trailing twelve months.
        return_on_tangible_assets_ttm : Optional[float]
            Return on tangible assets calculated as trailing twelve months.
        graham_net_net_ttm : Optional[float]
            Graham net-net working capital calculated as trailing twelve months.
        working_capital_ttm : Optional[float]
            Working capital calculated as trailing twelve months.
        tangible_asset_value_ttm : Optional[float]
            Tangible asset value calculated as trailing twelve months.
        net_current_asset_value_ttm : Optional[float]
            Net current asset value calculated as trailing twelve months.
        invested_capital_ttm : Optional[float]
            Invested capital calculated as trailing twelve months.
        average_receivables_ttm : Optional[float]
            Average receivables calculated as trailing twelve months.
        average_payables_ttm : Optional[float]
            Average payables calculated as trailing twelve months.
        average_inventory_ttm : Optional[float]
            Average inventory calculated as trailing twelve months.
        days_sales_outstanding_ttm : Optional[float]
            Days sales outstanding calculated as trailing twelve months.
        days_payables_outstanding_ttm : Optional[float]
            Days payables outstanding calculated as trailing twelve months.
        days_of_inventory_on_hand_ttm : Optional[float]
            Days of inventory on hand calculated as trailing twelve months.
        receivables_turnover_ttm : Optional[float]
            Receivables turnover calculated as trailing twelve months.
        payables_turnover_ttm : Optional[float]
            Payables turnover calculated as trailing twelve months.
        inventory_turnover_ttm : Optional[float]
            Inventory turnover calculated as trailing twelve months.
        roe_ttm : Optional[float]
            Return on equity calculated as trailing twelve months.
        capex_per_share_ttm : Optional[float]
            Capital expenditures per share calculated as trailing twelve months.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.multiples(symbol="AAPL")
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/multiples",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/multiples",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
                extra_info={"symbol": {"multiple_items_allowed": ["fmp"]}},
            )
        )

    @exception_handler
    @validate
    @deprecated(
        "This endpoint is deprecated; use `/equity/profile` instead. Deprecated in OpenBB Platform V4.1 to be removed in V4.3.",
        category=OpenBBDeprecationWarning,
    )
    def overview(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get company general business and stock data for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : CompanyOverview
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CompanyOverview
        ---------------
        symbol : str
            Symbol representing the entity requested in the data.
        price : Optional[float]
            Price of the company.
        beta : Optional[float]
            Beta of the company.
        vol_avg : Optional[int]
            Volume average of the company.
        mkt_cap : Optional[int]
            Market capitalization of the company.
        last_div : Optional[float]
            Last dividend of the company.
        range : Optional[str]
            Range of the company.
        changes : Optional[float]
            Changes of the company.
        company_name : Optional[str]
            Company name of the company.
        currency : Optional[str]
            Currency of the company.
        cik : Optional[str]
            Central Index Key (CIK) for the requested entity.
        isin : Optional[str]
            ISIN of the company.
        cusip : Optional[str]
            CUSIP of the company.
        exchange : Optional[str]
            Exchange of the company.
        exchange_short_name : Optional[str]
            Exchange short name of the company.
        industry : Optional[str]
            Industry of the company.
        website : Optional[str]
            Website of the company.
        description : Optional[str]
            Description of the company.
        ceo : Optional[str]
            CEO of the company.
        sector : Optional[str]
            Sector of the company.
        country : Optional[str]
            Country of the company.
        full_time_employees : Optional[str]
            Full time employees of the company.
        phone : Optional[str]
            Phone of the company.
        address : Optional[str]
            Address of the company.
        city : Optional[str]
            City of the company.
        state : Optional[str]
            State of the company.
        zip : Optional[str]
            Zip of the company.
        dcf_diff : Optional[float]
            Discounted cash flow difference of the company.
        dcf : Optional[float]
            Discounted cash flow of the company.
        image : Optional[str]
            Image of the company.
        ipo_date : Optional[date]
            IPO date of the company.
        default_image : bool
            If the image is the default image.
        is_etf : bool
            If the company is an ETF.
        is_actively_trading : bool
            If the company is actively trading.
        is_adr : bool
            If the company is an ADR.
        is_fund : bool
            If the company is a fund.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.overview(symbol="AAPL")
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn(
            "This endpoint is deprecated; use `/equity/profile` instead. Deprecated in OpenBB Platform V4.1 to be removed in V4.3.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self._run(
            "/equity/fundamental/overview",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/overview",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def ratios(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        period: Annotated[
            str, OpenBBCustomParameter(description="Time period of the data to return.")
        ] = "annual",
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 12,
        provider: Optional[Literal["fmp", "intrinio"]] = None,
        **kwargs
    ) -> OBBject:
        """Get an extensive set of financial and accounting ratios for a given company over time.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : str
            Time period of the data to return.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['fmp', 'intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        fiscal_year : Optional[int]
            The specific fiscal year.  Reports do not go beyond 2008. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[FinancialRatios]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        FinancialRatios
        ---------------
        period_ending : str
            The date of the data.
        fiscal_period : str
            Period of the financial ratios.
        fiscal_year : Optional[int]
            Fiscal year.
        current_ratio : Optional[float]
            Current ratio. (provider: fmp)
        quick_ratio : Optional[float]
            Quick ratio. (provider: fmp)
        cash_ratio : Optional[float]
            Cash ratio. (provider: fmp)
        days_of_sales_outstanding : Optional[float]
            Days of sales outstanding. (provider: fmp)
        days_of_inventory_outstanding : Optional[float]
            Days of inventory outstanding. (provider: fmp)
        operating_cycle : Optional[float]
            Operating cycle. (provider: fmp)
        days_of_payables_outstanding : Optional[float]
            Days of payables outstanding. (provider: fmp)
        cash_conversion_cycle : Optional[float]
            Cash conversion cycle. (provider: fmp)
        gross_profit_margin : Optional[float]
            Gross profit margin. (provider: fmp)
        operating_profit_margin : Optional[float]
            Operating profit margin. (provider: fmp)
        pretax_profit_margin : Optional[float]
            Pretax profit margin. (provider: fmp)
        net_profit_margin : Optional[float]
            Net profit margin. (provider: fmp)
        effective_tax_rate : Optional[float]
            Effective tax rate. (provider: fmp)
        return_on_assets : Optional[float]
            Return on assets. (provider: fmp)
        return_on_equity : Optional[float]
            Return on equity. (provider: fmp)
        return_on_capital_employed : Optional[float]
            Return on capital employed. (provider: fmp)
        net_income_per_ebt : Optional[float]
            Net income per EBT. (provider: fmp)
        ebt_per_ebit : Optional[float]
            EBT per EBIT. (provider: fmp)
        ebit_per_revenue : Optional[float]
            EBIT per revenue. (provider: fmp)
        debt_ratio : Optional[float]
            Debt ratio. (provider: fmp)
        debt_equity_ratio : Optional[float]
            Debt equity ratio. (provider: fmp)
        long_term_debt_to_capitalization : Optional[float]
            Long term debt to capitalization. (provider: fmp)
        total_debt_to_capitalization : Optional[float]
            Total debt to capitalization. (provider: fmp)
        interest_coverage : Optional[float]
            Interest coverage. (provider: fmp)
        cash_flow_to_debt_ratio : Optional[float]
            Cash flow to debt ratio. (provider: fmp)
        company_equity_multiplier : Optional[float]
            Company equity multiplier. (provider: fmp)
        receivables_turnover : Optional[float]
            Receivables turnover. (provider: fmp)
        payables_turnover : Optional[float]
            Payables turnover. (provider: fmp)
        inventory_turnover : Optional[float]
            Inventory turnover. (provider: fmp)
        fixed_asset_turnover : Optional[float]
            Fixed asset turnover. (provider: fmp)
        asset_turnover : Optional[float]
            Asset turnover. (provider: fmp)
        operating_cash_flow_per_share : Optional[float]
            Operating cash flow per share. (provider: fmp)
        free_cash_flow_per_share : Optional[float]
            Free cash flow per share. (provider: fmp)
        cash_per_share : Optional[float]
            Cash per share. (provider: fmp)
        payout_ratio : Optional[float]
            Payout ratio. (provider: fmp)
        operating_cash_flow_sales_ratio : Optional[float]
            Operating cash flow sales ratio. (provider: fmp)
        free_cash_flow_operating_cash_flow_ratio : Optional[float]
            Free cash flow operating cash flow ratio. (provider: fmp)
        cash_flow_coverage_ratios : Optional[float]
            Cash flow coverage ratios. (provider: fmp)
        short_term_coverage_ratios : Optional[float]
            Short term coverage ratios. (provider: fmp)
        capital_expenditure_coverage_ratio : Optional[float]
            Capital expenditure coverage ratio. (provider: fmp)
        dividend_paid_and_capex_coverage_ratio : Optional[float]
            Dividend paid and capex coverage ratio. (provider: fmp)
        dividend_payout_ratio : Optional[float]
            Dividend payout ratio. (provider: fmp)
        price_book_value_ratio : Optional[float]
            Price book value ratio. (provider: fmp)
        price_to_book_ratio : Optional[float]
            Price to book ratio. (provider: fmp)
        price_to_sales_ratio : Optional[float]
            Price to sales ratio. (provider: fmp)
        price_earnings_ratio : Optional[float]
            Price earnings ratio. (provider: fmp)
        price_to_free_cash_flows_ratio : Optional[float]
            Price to free cash flows ratio. (provider: fmp)
        price_to_operating_cash_flows_ratio : Optional[float]
            Price to operating cash flows ratio. (provider: fmp)
        price_cash_flow_ratio : Optional[float]
            Price cash flow ratio. (provider: fmp)
        price_earnings_to_growth_ratio : Optional[float]
            Price earnings to growth ratio. (provider: fmp)
        price_sales_ratio : Optional[float]
            Price sales ratio. (provider: fmp)
        dividend_yield : Optional[float]
            Dividend yield. (provider: fmp)
        dividend_yield_percentage : Optional[float]
            Dividend yield percentage. (provider: fmp)
        dividend_per_share : Optional[float]
            Dividend per share. (provider: fmp)
        enterprise_value_multiple : Optional[float]
            Enterprise value multiple. (provider: fmp)
        price_fair_value : Optional[float]
            Price fair value. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.ratios(symbol="AAPL", period="annual", limit=12)
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/ratios",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/ratios",
                        ("fmp", "intrinio"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "period": period,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def reported_financials(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        period: Annotated[
            str, OpenBBCustomParameter(description="Time period of the data to return.")
        ] = "annual",
        statement_type: Annotated[
            str,
            OpenBBCustomParameter(
                description="The type of financial statement - i.e, balance, income, cash."
            ),
        ] = "balance",
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(
                description="The number of data entries to return. Although the response object contains multiple results, because of the variance in the fields, year-to-year and quarter-to-quarter, it is recommended to view results in small chunks."
            ),
        ] = 100,
        provider: Optional[Literal["intrinio"]] = None,
        **kwargs
    ) -> OBBject:
        """Get financial statements as reported by the company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : str
            Time period of the data to return.
        statement_type : str
            The type of financial statement - i.e, balance, income, cash.
        limit : Optional[int]
            The number of data entries to return. Although the response object contains multiple results, because of the variance in the fields, year-to-year and quarter-to-quarter, it is recommended to view results in small chunks.
        provider : Optional[Literal['intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        fiscal_year : Optional[int]
            The specific fiscal year.  Reports do not go beyond 2008. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[ReportedFinancials]
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ReportedFinancials
        ------------------
        period_ending : date
            The ending date of the reporting period.
        fiscal_period : str
            The fiscal period of the report (e.g. FY, Q1, etc.).
        fiscal_year : Optional[int]
            The fiscal year of the fiscal period.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.reported_financials(symbol="AAPL", period="annual", statement_type="balance", limit=100)
        >>> # Get reported income statement
        >>> obb.equity.fundamental.reported_financials(symbol='AAPL', statement_type='income)
        >>> # Get reported cash flow statement
        >>> obb.equity.fundamental.reported_financials(symbol='AAPL', statement_type='cash')
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/reported_financials",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/reported_financials",
                        ("intrinio",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "period": period,
                    "statement_type": statement_type,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def revenue_per_geography(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        period: Annotated[
            Literal["quarter", "annual"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        structure: Annotated[
            Literal["hierarchical", "flat"],
            OpenBBCustomParameter(description="Structure of the returned data."),
        ] = "flat",
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the revenue geographic breakdown for a given company over time.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Literal['quarter', 'annual']
            Time period of the data to return.
        structure : Literal['hierarchical', 'flat']
            Structure of the returned data.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[RevenueGeographic]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        RevenueGeographic
        -----------------
        period_ending : date
            The end date of the reporting period.
        fiscal_period : Optional[str]
            The fiscal period of the reporting period.
        fiscal_year : Optional[int]
            The fiscal year of the reporting period.
        filing_date : Optional[date]
            The filing date of the report.
        geographic_segment : int
            Dictionary of the revenue by geographic segment.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.revenue_per_geography(symbol="AAPL", period="annual", structure="flat")
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/revenue_per_geography",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/revenue_per_geography",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "period": period,
                    "structure": structure,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def revenue_per_segment(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        period: Annotated[
            Literal["quarter", "annual"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        structure: Annotated[
            Literal["hierarchical", "flat"],
            OpenBBCustomParameter(description="Structure of the returned data."),
        ] = "flat",
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the revenue breakdown by business segment for a given company over time.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Literal['quarter', 'annual']
            Time period of the data to return.
        structure : Literal['hierarchical', 'flat']
            Structure of the returned data.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[RevenueBusinessLine]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        RevenueBusinessLine
        -------------------
        period_ending : date
            The end date of the reporting period.
        fiscal_period : Optional[str]
            The fiscal period of the reporting period.
        fiscal_year : Optional[int]
            The fiscal year of the reporting period.
        filing_date : Optional[date]
            The filing date of the report.
        business_line : int
            Dictionary containing the revenue of the business line.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.revenue_per_segment(symbol="AAPL", period="annual", structure="flat")
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/revenue_per_segment",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/revenue_per_segment",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "period": period,
                    "structure": structure,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def search_attributes(
        self,
        query: Annotated[
            str, OpenBBCustomParameter(description="Query to search for.")
        ],
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 1000,
        provider: Optional[Literal["intrinio"]] = None,
        **kwargs
    ) -> OBBject:
        """Search Intrinio data tags to search in latest or historical attributes.

        Parameters
        ----------
        query : str
            Query to search for.
        limit : Optional[int]
            The number of data entries to return.
        provider : Optional[Literal['intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[SearchAttributes]
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SearchAttributes
        ----------------
        id : str
            ID of the financial attribute.
        name : str
            Name of the financial attribute.
        tag : str
            Tag of the financial attribute.
        statement_code : str
            Code of the financial statement.
        statement_type : Optional[str]
            Type of the financial statement.
        parent_name : Optional[str]
            Parent's name of the financial attribute.
        sequence : Optional[int]
            Sequence of the financial statement.
        factor : Optional[str]
            Unit of the financial attribute.
        transaction : Optional[str]
            Transaction type (credit/debit) of the financial attribute.
        type : Optional[str]
            Type of the financial attribute.
        unit : Optional[str]
            Unit of the financial attribute.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.search_attributes(query='ebitda')
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/search_attributes",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/search_attributes",
                        ("intrinio",),
                    )
                },
                standard_params={
                    "query": query,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def trailing_dividend_yield(
        self,
        symbol: Annotated[
            Optional[str], OpenBBCustomParameter(description="Symbol to get data for.")
        ] = None,
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(
                description="The number of data entries to return. Default is 252, the number of trading days in a year."
            ),
        ] = 252,
        provider: Optional[Literal["tiingo"]] = None,
        **kwargs
    ) -> OBBject:
        """Get the 1 year trailing dividend yield for a given company over time.

        Parameters
        ----------
        symbol : Optional[str]
            Symbol to get data for.
        limit : Optional[int]
            The number of data entries to return. Default is 252, the number of trading days in a year.
        provider : Optional[Literal['tiingo']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'tiingo' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[TrailingDividendYield]
                Serializable results.
            provider : Optional[Literal['tiingo']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        TrailingDividendYield
        ---------------------
        date : date
            The date of the data.
        trailing_dividend_yield : float
            Trailing dividend yield.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.trailing_dividend_yield(limit=252)
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/trailing_dividend_yield",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/trailing_dividend_yield",
                        ("tiingo",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def transcript(
        self,
        symbol: Annotated[
            str, OpenBBCustomParameter(description="Symbol to get data for.")
        ],
        year: Annotated[
            int,
            OpenBBCustomParameter(description="Year of the earnings call transcript."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject:
        """Get earnings call transcripts for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        year : int
            Year of the earnings call transcript.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[EarningsCallTranscript]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EarningsCallTranscript
        ----------------------
        symbol : str
            Symbol representing the entity requested in the data.
        quarter : int
            Quarter of the earnings call transcript.
        year : int
            Year of the earnings call transcript.
        date : datetime
            The date of the data.
        content : str
            Content of the earnings call transcript.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.transcript(symbol='AAPL', year=2020)
        """  # noqa: E501

        return self._run(
            "/equity/fundamental/transcript",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/fundamental/transcript",
                        ("fmp",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "year": year,
                },
                extra_params=kwargs,
            )
        )
