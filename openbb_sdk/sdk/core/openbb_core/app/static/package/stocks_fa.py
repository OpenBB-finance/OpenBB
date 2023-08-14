### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Annotated, List, Literal, Optional, Union

import pydantic
import pydantic.main
from pydantic import BaseModel, validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_fa(Container):
    @filter_call
    @validate_arguments
    def analysis(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Analyse SEC filings with the help of machine learning."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/analysis",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def balance(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Literal["annually", "quarterly"],
            OpenBBCustomParameter(
                description="Period of the data to return (quarterly or annually)."
            ),
        ] = "annually",
        limit: Annotated[
            Optional[pydantic.types.NonNegativeInt],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 12,
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Balance Sheet.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp, polygon]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        period : Literal['annually', 'quarterly']
            Period of the data to return (quarterly or annually).
        limit : Optional[NonNegativeInt]
            The number of data entries to return.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        BalanceSheet
        ------------
        date : date
            Date of the fetched statement.
        symbol : Optional[str]
            Symbol of the company.
        cik : Optional[int]
            Central Index Key.
        currency : Optional[str]
            Reporting currency.
        filing_date : Optional[date]
            Filling date.
        accepted_date : Optional[datetime]
            Accepted date.
        period : Optional[str]
            Reporting period of the statement.
        cash_and_cash_equivalents : Optional[int]
            Cash and cash equivalents
        short_term_investments : Optional[int]
            Short-term investments
        inventory : Optional[int]
            Inventory
        net_receivables : Optional[int]
            Receivables, net
        other_current_assets : Optional[int]
            Other current assets
        current_assets : Optional[int]
            Total current assets
        long_term_investments : Optional[int]
            Long-term investments
        property_plant_equipment_net : Optional[int]
            Property, plant and equipment, net
        goodwill : Optional[int]
            Goodwill
        intangible_assets : Optional[int]
            Intangible assets
        other_non_current_assets : Optional[int]
            Other non-current assets
        tax_assets : Optional[int]
            Accrued income taxes
        other_assets : Optional[int]
            Other assets
        noncurrent_assets : Optional[int]
            None
        assets : Optional[int]
            None
        account_payables : Optional[int]
            None
        other_current_liabilities : Optional[int]
            None
        tax_payables : Optional[int]
            Accrued income taxes
        deferred_revenue : Optional[int]
            Accrued income taxes, other deferred revenue
        short_term_debt : Optional[int]
            Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year
        current_liabilities : Optional[int]
            None
        long_term_debt : Optional[int]
            Long-term debt, Operating lease obligations, Long-term finance lease obligations
        other_non_current_liabilities : Optional[int]
            Deferred income taxes and other
        other_liabilities : Optional[int]
            None
        noncurrent_liabilities : Optional[int]
            None
        liabilities : Optional[int]
            None
        common_stock : Optional[int]
            None
        other_stockholder_equity : Optional[int]
            Capital in excess of par value
        accumulated_other_comprehensive_income_loss : Optional[int]
            Accumulated other comprehensive income (loss)
        preferred_stock : Optional[int]
            Preferred stock
        retained_earnings : Optional[int]
            Retained earnings
        minority_interest : Optional[int]
            Minority interest
        total_stockholders_equity : Optional[int]
            None
        total_equity : Optional[int]
            None
        total_liabilities_and_stockholders_equity : Optional[int]
            None
        total_liabilities_and_total_equity : Optional[int]
            None

        fmp
        ===

        Parameters
        ----------
        cik : Optional[str]
            None


        BalanceSheet
        ------------
        calendarYear : Optional[int]
            None
        link : Optional[str]
            None
        finalLink : Optional[str]
            None
        cashAndShortTermInvestments : Optional[int]
            None
        goodwillAndIntangibleAssets : Optional[int]
            None
        deferredRevenueNonCurrent : Optional[int]
            None
        totalInvestments : Optional[int]
            None
        capitalLeaseObligations : Optional[int]
            None
        deferredTaxLiabilitiesNonCurrent : Optional[int]
            None
        totalNonCurrentLiabilities : Optional[int]
            None
        totalDebt : Optional[int]
            None
        netDebt : Optional[int]
            None

        polygon
        =======

        Parameters
        ----------
        company_name : Optional[str]
            The name of the company.
        company_name_search : Optional[str]
            The name of the company to search.
        sic : Optional[str]
            The Standard Industrial Classification (SIC) of the company.
        filing_date : Optional[date]
            The filing date of the financial statement.
        filing_date_lt : Optional[date]
            The filing date less than the given date.
        filing_date_lte : Optional[date]
            The filing date less than or equal to the given date.
        filing_date_gt : Optional[date]
            The filing date greater than the given date.
        filing_date_gte : Optional[date]
            The filing date greater than or equal to the given date.
        period_of_report_date : Optional[date]
            The period of report date of the financial statement.
        period_of_report_date_lt : Optional[date]
            The period of report date less than the given date.
        period_of_report_date_lte : Optional[date]
            The period of report date less than or equal to the given date.
        period_of_report_date_gt : Optional[date]
            The period of report date greater than the given date.
        period_of_report_date_gte : Optional[date]
            The period of report date greater than or equal to the given date.
        include_sources : Optional[bool]
            Whether to include the sources of the financial statement.
        order : Optional[Literal['asc', 'desc']]
            The order of the financial statement.
        sort : Optional[Literal['filing_date', 'period_of_report_date']]
            The sort of the financial statement.


        BalanceSheet
        ------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "period": period,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/balance",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def balance_growth(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Balance Sheet Statement Growth.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        limit : int
            The number of data entries to return.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        BalanceSheetGrowth
        ------------------
        symbol : str
            Symbol to get data for.
        date : date
            The date of the data.
        period : str
            The period the statement is returned for.
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

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        BalanceSheetGrowth
        ------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/balance_growth",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def cal(
        self,
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
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Show Dividend Calendar for a given start and end dates.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        start_date : Optional[date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[date]
            End date of the data, in YYYY-MM-DD format.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        DividendCalendar
        ----------------
        symbol : str
            Symbol to get data for.
        date : date
            The date of the data.
        label : str
            The date in human readable form in the calendar.
        adj_dividend : Optional[NonNegativeFloat]
            The adjusted dividend on a date in the calendar.
        dividend : Optional[NonNegativeFloat]
            The dividend amount in the calendar.
        record_date : Optional[date]
            The record date of the dividend in the calendar.
        payment_date : Optional[date]
            The payment date of the dividend in the calendar.
        declaration_date : Optional[date]
            The declaration date of the dividend in the calendar.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        DividendCalendar
        ----------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/cal",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def cash(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Literal["annually", "quarterly"],
            OpenBBCustomParameter(
                description="Period of the data to return (quarterly or annually)."
            ),
        ] = "annually",
        limit: Annotated[
            Optional[pydantic.types.NonNegativeInt],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 12,
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Cash Flow Statement.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp, polygon]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        period : Literal['annually', 'quarterly']
            Period of the data to return (quarterly or annually).
        limit : Optional[NonNegativeInt]
            The number of data entries to return.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        CashFlowStatement
        -----------------
        date : date
            Date of the fetched statement.
        symbol : Optional[str]
            Symbol of the company.
        cik : Optional[int]
            Central Index Key.
        currency : Optional[str]
            Reporting currency.
        filing_date : Optional[date]
            Filling date.
        accepted_date : Optional[datetime]
            Accepted date.
        period : Optional[str]
            Reporting period of the statement.
        cash_at_beginning_of_period : Optional[int]
            Cash at beginning of period.
        net_income : Optional[int]
            Net income.
        depreciation_and_amortization : Optional[int]
            Depreciation and amortization.
        stock_based_compensation : Optional[int]
            Stock based compensation.
        other_non_cash_items : Optional[int]
            Other non-cash items.
        deferred_income_tax : Optional[int]
            Deferred income tax.
        free_cash_flow : Optional[int]
            Net cash flow from operating, investing and financing activities
        inventory : Optional[int]
            Inventory.
        accounts_payables : Optional[int]
            Accounts payables.
        accounts_receivables : Optional[int]
            Accounts receivables.
        change_in_working_capital : Optional[int]
            Change in working capital.
        other_working_capital : Optional[int]
            Accrued expenses and other, Unearned revenue.
        capital_expenditure : Optional[int]
            Purchases of property and equipment.
        other_investing_activities : Optional[int]
            Proceeds from property and equipment sales and incentives.
        acquisitions_net : Optional[int]
            Acquisitions, net of cash acquired, and other
        sales_maturities_of_investments : Optional[int]
            Sales and maturities of investments.
        purchases_of_investments : Optional[int]
            Purchases of investments.
        net_cash_flow_from_operating_activities : Optional[int]
            Net cash flow from operating activities.
        net_cash_flow_from_investing_activities : Optional[int]
            Net cash flow from investing activities.
        net_cash_flow_from_financing_activities : Optional[int]
            Net cash flow from financing activities.
        investments_in_property_plant_and_equipment : Optional[int]
            Investments in property, plant, and equipment.
        net_cash_used_for_investing_activities : Optional[int]
            Net cash used for investing activities.
        effect_of_forex_changes_on_cash : Optional[int]
            Foreign currency effect on cash, cash equivalents, and restricted cash
        dividends_paid : Optional[int]
            Payments for dividends and dividend equivalents
        common_stock_issued : Optional[int]
            Proceeds from issuance of common stock
        common_stock_repurchased : Optional[int]
            Payments related to repurchase of common stock
        debt_repayment : Optional[int]
            Payments of long-term debt
        other_financing_activities : Optional[int]
            Other financing activities, net
        net_change_in_cash : Optional[int]
            Net increase (decrease) in cash, cash equivalents, and restricted cash
        cash_at_end_of_period : Optional[int]
            Cash, cash equivalents, and restricted cash at end of period
        operating_cash_flow : Optional[int]
            Net cash flow from operating activities

        fmp
        ===

        Parameters
        ----------
        cik : Optional[str]
            Central Index Key (CIK) of the company.


        CashFlowStatement
        -----------------
        calendar_year : Optional[int]
            Calendar Year
        link : Optional[str]
            None
        final_link : Optional[str]
            Final Link

        polygon
        =======

        Parameters
        ----------
        company_name : Optional[str]
            The name of the company.
        company_name_search : Optional[str]
            The name of the company to search.
        sic : Optional[str]
            The Standard Industrial Classification (SIC) of the company.
        filing_date : Optional[date]
            The filing date of the financial statement.
        filing_date_lt : Optional[date]
            The filing date less than the given date.
        filing_date_lte : Optional[date]
            The filing date less than or equal to the given date.
        filing_date_gt : Optional[date]
            The filing date greater than the given date.
        filing_date_gte : Optional[date]
            The filing date greater than or equal to the given date.
        period_of_report_date : Optional[date]
            The period of report date of the financial statement.
        period_of_report_date_lt : Optional[date]
            The period of report date less than the given date.
        period_of_report_date_lte : Optional[date]
            The period of report date less than or equal to the given date.
        period_of_report_date_gt : Optional[date]
            The period of report date greater than the given date.
        period_of_report_date_gte : Optional[date]
            The period of report date greater than or equal to the given date.
        include_sources : Optional[bool]
            Whether to include the sources of the financial statement.
        order : Optional[Literal['asc', 'desc']]
            The order of the financial statement.
        sort : Optional[Literal['filing_date', 'period_of_report_date']]
            The sort of the financial statement.


        CashFlowStatement
        -----------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "period": period,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/cash",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def cash_growth(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Cash Flow Statement Growth.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        limit : int
            The number of data entries to return.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        CashFlowStatementGrowth
        -----------------------
        symbol : str
            Symbol to get data for.
        date : date
            The date of the data.
        period : str
            The period the statement is returned for.
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

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        CashFlowStatementGrowth
        -----------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/cash_growth",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def comp(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Executive Compensation.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        ExecutiveCompensation
        ---------------------
        symbol : str
            Symbol to get data for.
        cik : Optional[str]
            The Central Index Key (CIK) of the company.
        filing_date : date
            The date of the filing.
        accepted_date : datetime
            The date the filing was accepted.
        name_and_position : str
            The name and position of the executive.
        year : int
            The year of the compensation.
        salary : PositiveFloat
            The salary of the executive.
        bonus : NonNegativeFloat
            The bonus of the executive.
        stock_award : NonNegativeFloat
            The stock award of the executive.
        incentive_plan_compensation : NonNegativeFloat
            The incentive plan compensation of the executive.
        all_other_compensation : NonNegativeFloat
            The all other compensation of the executive.
        total : PositiveFloat
            The total compensation of the executive.
        url : str
            The URL of the filing data.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        ExecutiveCompensation
        ---------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/comp",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def comsplit(
        self,
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
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Stock Split Calendar.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        start_date : Optional[date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[date]
            End date of the data, in YYYY-MM-DD format.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        StockSplitCalendar
        ------------------
        date : date
            The date of the stock splits.
        label : str
            The label of the stock splits.
        symbol : str
            The symbol of the company.
        numerator : float
            The numerator of the stock splits.
        denominator : float
            The denominator of the stock splits.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        StockSplitCalendar
        ------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/comsplit",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def customer(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """List of customers of the company."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/customer",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def dcfc(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Determine the (historical) discounted cash flow."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/dcfc",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def divs(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Historical Dividends.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        HistoricalDividends
        -------------------
        date : date
            The date of the historical dividends.
        label : str
            The label of the historical dividends.
        adj_dividend : float
            The adjusted dividend of the historical dividends.
        dividend : float
            The dividend of the historical dividends.
        record_date : Optional[date]
            The record date of the historical dividends.
        payment_date : Optional[date]
            The payment date of the historical dividends.
        declaration_date : Optional[date]
            The declaration date of the historical dividends.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        HistoricalDividends
        -------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/divs",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def dupont(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Detailed breakdown for Return on Equity (RoE)."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/dupont",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def earning(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 50,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Earnings Calendar.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        limit : Optional[int]
            The number of data entries to return.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        EarningsCalendar
        ----------------
        symbol : str
            Symbol to get data for.
        date : date
            The date of the data.
        eps : Optional[NonNegativeFloat]
            The EPS of the earnings calendar.
        eps_estimated : Optional[NonNegativeFloat]
            The estimated EPS of the earnings calendar.
        time : str
            The time of the earnings calendar.
        revenue : Optional[int]
            The revenue of the earnings calendar.
        revenue_estimated : Optional[int]
            The estimated revenue of the earnings calendar.
        updated_from_date : Optional[date]
            The updated from date of the earnings calendar.
        fiscal_date_ending : date
            The fiscal date ending of the earnings calendar.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        EarningsCalendar
        ----------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/earning",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def emp(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Number of Employees.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        HistoricalEmployees
        -------------------
        symbol : str
            Symbol to get data for.
        cik : int
            The CIK of the company to retrieve the historical employees of.
        acceptance_time : datetime
            The time of acceptance of the company employee.
        period_of_report : date
            The date of reporting of the company employee.
        company_name : str
            The registered name of the company to retrieve the historical employees of.
        form_type : str
            The form type of the company employee.
        filing_date : date
            The filing date of the company employee
        employee_count : int
            The count of employees of the company.
        source : str
            The source URL which retrieves this data for the company.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        HistoricalEmployees
        -------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/emp",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def enterprise(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Enterprise value."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/enterprise",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def epsfc(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Earnings Estimate by Analysts - EPS."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/epsfc",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def est(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Literal["annually", "quarterly"],
            OpenBBCustomParameter(
                description="Period of the data to return (quarterly or annually)."
            ),
        ] = "annually",
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 30,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Analyst Estimates.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        period : Literal['quarterly', 'annually']
            Period of the data to return (quarterly or annually).
        limit : int
            The number of data entries to return.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        AnalystEstimates
        ----------------
        symbol : str
            Symbol to get data for.
        date : date
            A specific date to get data for.
        estimated_revenue_low : int
            The estimated revenue low.
        estimated_revenue_high : int
            The estimated revenue high.
        estimated_revenue_avg : int
            The estimated revenue average.
        estimated_ebitda_low : int
            The estimated EBITDA low.
        estimated_ebitda_high : int
            The estimated EBITDA high.
        estimated_ebitda_avg : int
            The estimated EBITDA average.
        estimated_ebit_low : int
            The estimated EBIT low.
        estimated_ebit_high : int
            The estimated EBIT high.
        estimated_ebit_avg : int
            The estimated EBIT average.
        estimated_net_income_low : int
            The estimated net income low.
        estimated_net_income_high : int
            The estimated net income high.
        estimated_net_income_avg : int
            The estimated net income average.
        estimated_sga_expense_low : int
            The estimated SGA expense low.
        estimated_sga_expense_high : int
            The estimated SGA expense high.
        estimated_sga_expense_avg : int
            The estimated SGA expense average.
        estimated_eps_avg : float
            The estimated EPS average.
        estimated_eps_high : float
            The estimated EPS high.
        estimated_eps_low : float
            The estimated EPS low.
        number_analyst_estimated_revenue : int
            The number of analysts who estimated revenue.
        number_analysts_estimated_eps : int
            The number of analysts who estimated EPS.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        AnalystEstimates
        ----------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "period": period,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/est",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fama_coe(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Fama French 3 Factor Model - Coefficient of Earnings."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/fama_coe",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fama_raw(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Fama French 3 Factor Model - Raw Data."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/fama_raw",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fraud(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Key fraud ratios including M-score, Z-score and McKee."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/fraud",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def growth(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Growth of financial statement items and ratios."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/growth",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def historical_5(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/historical_5",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def income(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Literal["annually", "quarterly"],
            OpenBBCustomParameter(
                description="Period of the data to return (quarterly or annually)."
            ),
        ] = "annually",
        limit: Annotated[
            Optional[pydantic.types.NonNegativeInt],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 12,
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Income Statement.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp, polygon]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        period : Literal['annually', 'quarterly']
            Period of the data to return (quarterly or annually).
        limit : Optional[NonNegativeInt]
            The number of data entries to return.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        IncomeStatement
        ---------------
        date : date
            Date of the income statement.
        symbol : str
            Symbol of the company.
        cik : Optional[int]
            Central Index Key.
        currency : Optional[str]
            Reporting currency.
        filing_date : Optional[date]
            Filling date.
        accepted_date : Optional[datetime]
            Accepted date.
        calendar_year : Optional[int]
            Calendar year.
        period : Optional[str]
            Period of the income statement.
        revenue : Optional[int]
            Revenue.
        cost_of_revenue : Optional[int]
            Cost of revenue.
        gross_profit : Optional[int]
            Gross profit.
        cost_and_expenses : Optional[int]
            Cost and expenses.
        gross_profit_ratio : Optional[float]
            Gross profit ratio.
        research_and_development_expenses : Optional[int]
            Research and development expenses.
        general_and_administrative_expenses : Optional[int]
            General and administrative expenses.
        selling_and_marketing_expenses : Optional[float]
            Selling and marketing expenses.
        selling_general_and_administrative_expenses : Optional[int]
            Selling, general and administrative expenses.
        other_expenses : Optional[int]
            Other expenses.
        operating_expenses : Optional[int]
            Operating expenses.
        depreciation_and_amortization : Optional[int]
            Depreciation and amortization.
        ebitda : Optional[int]
            Earnings before interest, taxes, depreciation and amortization.
        ebitda_ratio : Optional[float]
            Earnings before interest, taxes, depreciation and amortization ratio.
        operating_income : Optional[int]
            Operating income.
        operating_income_ratio : Optional[float]
            Operating income ratio.
        interest_income : Optional[int]
            Interest income.
        interest_expense : Optional[int]
            Interest expense.
        total_other_income_expenses_net : Optional[int]
            Total other income expenses net.
        income_before_tax : Optional[int]
            Income before tax.
        income_before_tax_ratio : Optional[float]
            Income before tax ratio.
        income_tax_expense : Optional[int]
            Income tax expense.
        net_income : Optional[int]
            Net income.
        net_income_ratio : Optional[float]
            Net income ratio.
        eps : Optional[float]
            Earnings per share.
        eps_diluted : Optional[float]
            Earnings per share diluted.
        weighted_average_shares_outstanding : Optional[int]
            Weighted average shares outstanding.
        weighted_average_shares_outstanding_dil : Optional[int]
            Weighted average shares outstanding diluted.
        link : Optional[str]
            Link to the income statement.
        final_link : Optional[str]
            Final link to the income statement.

        fmp
        ===

        Parameters
        ----------
        cik : Optional[str]
            The CIK of the company if no symbol is provided.


        IncomeStatement
        ---------------
        All fields are standardized.

        polygon
        =======

        Parameters
        ----------
        company_name : Optional[str]
            The name of the company.
        company_name_search : Optional[str]
            The name of the company to search.
        sic : Optional[str]
            The Standard Industrial Classification (SIC) of the company.
        filing_date : Optional[date]
            The filing date of the financial statement.
        filing_date_lt : Optional[date]
            The filing date less than the given date.
        filing_date_lte : Optional[date]
            The filing date less than or equal to the given date.
        filing_date_gt : Optional[date]
            The filing date greater than the given date.
        filing_date_gte : Optional[date]
            The filing date greater than or equal to the given date.
        period_of_report_date : Optional[date]
            The period of report date of the financial statement.
        period_of_report_date_lt : Optional[date]
            The period of report date less than the given date.
        period_of_report_date_lte : Optional[date]
            The period of report date less than or equal to the given date.
        period_of_report_date_gt : Optional[date]
            The period of report date greater than the given date.
        period_of_report_date_gte : Optional[date]
            The period of report date greater than or equal to the given date.
        include_sources : Optional[bool]
            Whether to include the sources of the financial statement.
        order : Optional[Literal['asc', 'desc']]
            The order of the financial statement.
        sort : Optional[Literal['filing_date', 'period_of_report_date']]
            The sort of the financial statement.


        IncomeStatement
        ---------------
        income_loss_from_continuing_operations_after_tax : Optional[float]
            None
        benefits_costs_expenses : Optional[float]
            None
        net_income_loss_attributable_to_noncontrolling_interest : Optional[int]
            None
        net_income_loss_attributable_to_parent : Optional[float]
            None
        net_income_loss_available_to_common_stockholders_basic : Optional[float]
            None
        participating_securities_distributed_and_undistributed_earnings_loss_basic : Optional[float]
            None
        preferred_stock_dividends_and_other_adjustments : Optional[float]
            None"""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "period": period,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/income",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def income_growth(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        period: Annotated[
            Literal["annually", "quarterly"],
            OpenBBCustomParameter(
                description="Period of the data to return (quarterly or annually)."
            ),
        ] = "annually",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Income Statement Growth.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        limit : int
            The number of data entries to return.
        period : Literal['annually', 'quarterly']
            Period of the data to return (quarterly or annually).

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        IncomeStatementGrowth
        ---------------------
        symbol : str
            Symbol to get data for.
        date : date
            The date of the data.
        period : str
            The period the statement is returned for.
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

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        IncomeStatementGrowth
        ---------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "limit": limit,
                "period": period,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/income_growth",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ins(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        transactionType: Annotated[
            Optional[
                List[
                    Literal[
                        "A-Award",
                        "C-Conversion",
                        "D-Return",
                        "E-ExpireShort",
                        "F-InKind",
                        "G-Gift",
                        "H-ExpireLong",
                        "I-Discretionary",
                        "J-Other",
                        "L-Small",
                        "M-Exempt",
                        "O-OutOfTheMoney",
                        "P-Purchase",
                        "S-Sale",
                        "U-Tender",
                        "W-Will",
                        "X-InTheMoney",
                        "Z-Trust",
                    ]
                ]
            ],
            OpenBBCustomParameter(description="The type of the transaction."),
        ] = ["P-Purchase"],
        reportingCik: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The CIK of the reporting owner."),
        ] = None,
        companyCik: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The CIK of the company owner."),
        ] = None,
        page: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The page number of the data to fetch."),
        ] = 0,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Stock Insider Trading.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        transactionType : Optional[List[Literal['A-Award', 'C-Conversion', 'D-Return', 'E-ExpireShort', 'F-InKind', 'G-Gift', 'H-ExpireLong', 'I-Discretionary', 'J-Other', 'L-Small', 'M-Exempt', 'O-OutOfTheMoney', 'P-Purchase', 'S-Sale', 'U-Tender', 'W-Will', 'X-InTheMoney', 'Z-Trust']]]
            The type of the transaction.
        reportingCik : Optional[int]
            The CIK of the reporting owner.
        companyCik : Optional[int]
            The CIK of the company owner.
        page : Optional[int]
            The page number of the data to fetch.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        StockInsiderTrading
        -------------------
        symbol : str
            Symbol to get data for.
        filing_date : datetime
            The filing date of the stock insider trading.
        transaction_date : date
            The transaction date of the stock insider trading.
        reporting_cik : int
            The reporting CIK of the stock insider trading.
        transaction_type : str
            The transaction type of the stock insider trading.
        securities_owned : int
            The securities owned of the stock insider trading.
        company_cik : int
            The company CIK of the stock insider trading.
        reporting_name : str
            The reporting name of the stock insider trading.
        type_of_owner : str
            The type of owner of the stock insider trading.
        acquistion_or_disposition : str
            The acquistion or disposition of the stock insider trading.
        form_type : str
            The form type of the stock insider trading.
        securities_transacted : float
            The securities transacted of the stock insider trading.
        price : float
            The price of the stock insider trading.
        security_name : str
            The security name of the stock insider trading.
        link : str
            The link of the stock insider trading.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        StockInsiderTrading
        -------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "transactionType": transactionType,
                "reportingCik": reportingCik,
                "companyCik": companyCik,
                "page": page,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/ins",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ins_own(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        include_current_quarter: Annotated[
            bool, OpenBBCustomParameter(description="Include current quarter data.")
        ] = False,
        date: Annotated[
            Optional[datetime.date],
            OpenBBCustomParameter(description="A specific date to get data for."),
        ] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Institutional Ownership.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        include_current_quarter : bool
            Include current quarter data.
        date : Optional[date]
            A specific date to get data for.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        InstitutionalOwnership
        ----------------------
        symbol : str
            Symbol to get data for.
        cik : Optional[str]
            The CIK of the company.
        date : date
            The date of the data.
        investors_holding : int
            The number of investors holding the stock.
        last_investors_holding : int
            The number of investors holding the stock in the last quarter.
        investors_holding_change : int
            The change in the number of investors holding the stock.
        number_of_13f_shares : Optional[int]
            The number of 13F shares.
        last_number_of_13f_shares : Optional[int]
            The number of 13F shares in the last quarter.
        number_of_13f_shares_change : Optional[int]
            The change in the number of 13F shares.
        total_invested : float
            The total amount invested.
        last_total_invested : float
            The total amount invested in the last quarter.
        total_invested_change : float
            The change in the total amount invested.
        ownership_percent : float
            The ownership percent.
        last_ownership_percent : float
            The ownership percent in the last quarter.
        ownership_percent_change : float
            The change in the ownership percent.
        new_positions : int
            The number of new positions.
        last_new_positions : int
            The number of new positions in the last quarter.
        new_positions_change : int
            he change in the number of new positions.
        increased_positions : int
            The number of increased positions.
        last_increased_positions : int
            The number of increased positions in the last quarter.
        increased_positions_change : int
            The change in the number of increased positions.
        closed_positions : int
            The number of closed positions.
        last_closed_positions : int
            The number of closed positions in the last quarter.
        closed_positions_change : int
            The change in the number of closed positions.
        reduced_positions : int
            The number of reduced positions.
        last_reduced_positions : int
            The number of reduced positions in the last quarter.
        reduced_positions_change : int
            The change in the number of reduced positions.
        total_calls : int
            Total number of call options contracts traded for Apple Inc. on the specified date.
        last_total_calls : int
            Total number of call options contracts traded for Apple Inc. on the previous reporting date.
        total_calls_change : int
            Change in the total number of call options contracts traded between the current and previous reporting dates.
        total_puts : int
            Total number of put options contracts traded for Apple Inc. on the specified date.
        last_total_puts : int
            Total number of put options contracts traded for Apple Inc. on the previous reporting date.
        total_puts_change : int
            Change in the total number of put options contracts traded between the current and previous reporting dates.
        put_call_ratio : float
            The put-call ratio, which is the ratio of the total number of put options to call options traded on the specified date.
        last_put_call_ratio : float
            The put-call ratio on the previous reporting date.
        put_call_ratio_change : float
            Change in the put-call ratio between the current and previous reporting dates.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        InstitutionalOwnership
        ----------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "include_current_quarter": include_current_quarter,
                "date": date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/ins_own",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def key(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/key",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def metrics(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Literal["annually", "quarterly"],
            OpenBBCustomParameter(
                description="Period of the data to return (quarterly or annually)."
            ),
        ] = "annually",
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Key Metrics.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        period : Literal['annually', 'quarterly']
            Period of the data to return (quarterly or annually).
        limit : Optional[int]
            The number of data entries to return.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        KeyMetrics
        ----------
        symbol : str
            Symbol to get data for.
        date : date
            The date of the data.
        period : str
            The period of the data.
        revenue_per_share : Optional[float]
            Revenue per share
        net_income_per_share : Optional[float]
            Net income per share
        operating_cash_flow_per_share : Optional[float]
            Operating cash flow per share
        free_cash_flow_per_share : Optional[float]
            Free cash flow per share
        cash_per_share : Optional[float]
            Cash per share
        book_value_per_share : Optional[float]
            Book value per share
        tangible_book_value_per_share : Optional[float]
            Tangible book value per share
        shareholders_equity_per_share : Optional[float]
            Shareholders equity per share
        interest_debt_per_share : Optional[float]
            Interest debt per share
        market_cap : Optional[float]
            Market capitalization
        enterprise_value : Optional[float]
            Enterprise value
        pe_ratio : Optional[float]
            Price-to-earnings ratio (P/E ratio)
        price_to_sales_ratio : Optional[float]
            Price-to-sales ratio
        pocf_ratio : Optional[float]
            Price-to-operating cash flow ratio
        pfcf_ratio : Optional[float]
            Price-to-free cash flow ratio
        pb_ratio : Optional[float]
            Price-to-book ratio
        ptb_ratio : Optional[float]
            Price-to-tangible book ratio
        ev_to_sales : Optional[float]
            Enterprise value-to-sales ratio
        enterprise_value_over_ebitda : Optional[float]
            Enterprise value-to-EBITDA ratio
        ev_to_operating_cash_flow : Optional[float]
            Enterprise value-to-operating cash flow ratio
        ev_to_free_cash_flow : Optional[float]
            Enterprise value-to-free cash flow ratio
        earnings_yield : Optional[float]
            Earnings yield
        free_cash_flow_yield : Optional[float]
            Free cash flow yield
        debt_to_equity : Optional[float]
            Debt-to-equity ratio
        debt_to_assets : Optional[float]
            Debt-to-assets ratio
        net_debt_to_ebitda : Optional[float]
            Net debt-to-EBITDA ratio
        current_ratio : Optional[float]
            Current ratio
        interest_coverage : Optional[float]
            Interest coverage
        income_quality : Optional[float]
            Income quality
        dividend_yield : Optional[float]
            Dividend yield
        payout_ratio : Optional[float]
            Payout ratio
        sales_general_and_administrative_to_revenue : Optional[float]
            Sales general and administrative expenses-to-revenue ratio
        research_and_development_to_revenue : Optional[float]
            Research and development expenses-to-revenue ratio
        intangibles_to_total_assets : Optional[float]
            Intangibles-to-total assets ratio
        capex_to_operating_cash_flow : Optional[float]
            Capital expenditures-to-operating cash flow ratio
        capex_to_revenue : Optional[float]
            Capital expenditures-to-revenue ratio
        capex_to_depreciation : Optional[float]
            Capital expenditures-to-depreciation ratio
        stock_based_compensation_to_revenue : Optional[float]
            Stock-based compensation-to-revenue ratio
        graham_number : Optional[float]
            Graham number
        roic : Optional[float]
            Return on invested capital
        return_on_tangible_assets : Optional[float]
            Return on tangible assets
        graham_net_net : Optional[float]
            Graham net-net working capital
        working_capital : Optional[float]
            Working capital
        tangible_asset_value : Optional[float]
            Tangible asset value
        net_current_asset_value : Optional[float]
            Net current asset value
        invested_capital : Optional[float]
            Invested capital
        average_receivables : Optional[float]
            Average receivables
        average_payables : Optional[float]
            Average payables
        average_inventory : Optional[float]
            Average inventory
        days_sales_outstanding : Optional[float]
            Days sales outstanding
        days_payables_outstanding : Optional[float]
            Days payables outstanding
        days_of_inventory_on_hand : Optional[float]
            Days of inventory on hand
        receivables_turnover : Optional[float]
            Receivables turnover
        payables_turnover : Optional[float]
            Payables turnover
        inventory_turnover : Optional[float]
            Inventory turnover
        roe : Optional[float]
            Return on equity
        capex_per_share : Optional[float]
            Capital expenditures per share

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        KeyMetrics
        ----------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "period": period,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/metrics",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def mgmt(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Key Executives.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        KeyExecutives
        -------------
        title : str
            Designation of the key executive.
        name : str
            Name of the key executive.
        pay : Optional[int]
            Pay of the key executive.
        currency_pay : str
            The currency of the pay.
        gender : Optional[str]
            Gender of the key executive.
        year_born : Optional[str]
            Birth year of the key executive.
        title_since : Optional[int]
            Date the tile was held since.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        KeyExecutives
        -------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/mgmt",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def mktcap(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Obtain the market capitalization or enterprise value."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/mktcap",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def news(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/news",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def overview(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[BaseModel]:
        """Company Overview.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        CompanyOverview
        ---------------
        symbol : str
            Symbol to get data for.
        price : float
            The price of the company.
        beta : float
            The beta of the company.
        vol_avg : int
            The volume average of the company.
        mkt_cap : int
            The market capitalization of the company.
        last_div : float
            The last dividend of the company.
        range : str
            The range of the company.
        changes : float
            The changes of the company.
        company_name : str
            The company name of the company.
        currency : str
            The currency of the company.
        cik : Optional[str]
            The CIK of the company.
        isin : Optional[str]
            The ISIN of the company.
        cusip : Optional[str]
            The CUSIP of the company.
        exchange : str
            The exchange of the company.
        exchange_short_name : str
            The exchange short name of the company.
        industry : str
            The industry of the company.
        website : str
            The website of the company.
        description : str
            The description of the company.
        ceo : str
            The CEO of the company.
        sector : str
            The sector of the company.
        country : str
            The country of the company.
        full_time_employees : str
            The full time employees of the company.
        phone : str
            The phone of the company.
        address : str
            The address of the company.
        city : str
            The city of the company.
        state : str
            The state of the company.
        zip : str
            The zip of the company.
        dcf_diff : float
            The discounted cash flow difference of the company.
        dcf : float
            The discounted cash flow of the company.
        image : str
            The image of the company.
        ipo_date : date
            The IPO date of the company.
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

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        CompanyOverview
        ---------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/overview",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def own(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        date: Annotated[
            Optional[datetime.date],
            OpenBBCustomParameter(description="A specific date to get data for."),
        ] = None,
        page: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The page number of the data to fetch."),
        ] = 0,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Stock Ownership.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        date : Optional[date]
            A specific date to get data for.
        page : Optional[int]
            The page number of the data to fetch.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        StockOwnership
        --------------
        date : date
            The date of the data.
        cik : int
            The cik of the stock ownership.
        filing_date : date
            The filing date of the stock ownership.
        investor_name : str
            The investor name of the stock ownership.
        symbol : str
            The symbol of the stock ownership.
        security_name : str
            The security name of the stock ownership.
        type_of_security : str
            The type of security of the stock ownership.
        security_cusip : str
            The security cusip of the stock ownership.
        shares_type : str
            The shares type of the stock ownership.
        put_call_share : str
            The put call share of the stock ownership.
        investment_discretion : str
            The investment discretion of the stock ownership.
        industry_title : str
            The industry title of the stock ownership.
        weight : float
            The weight of the stock ownership.
        last_weight : float
            The last weight of the stock ownership.
        change_in_weight : float
            The change in weight of the stock ownership.
        change_in_weight_percentage : float
            The change in weight percentage of the stock ownership.
        market_value : int
            The market value of the stock ownership.
        last_market_value : int
            The last market value of the stock ownership.
        change_in_market_value : int
            The change in market value of the stock ownership.
        change_in_market_value_percentage : float
            The change in market value percentage of the stock ownership.
        shares_number : int
            The shares number of the stock ownership.
        last_shares_number : int
            The last shares number of the stock ownership.
        change_in_shares_number : float
            The change in shares number of the stock ownership.
        change_in_shares_number_percentage : float
            The change in shares number percentage of the stock ownership.
        quarter_end_price : float
            The quarter end price of the stock ownership.
        avg_price_paid : float
            The average price paid of the stock ownership.
        is_new : bool
            Is the stock ownership new.
        is_sold_out : bool
            Is the stock ownership sold out.
        ownership : float
            How much is the ownership.
        last_ownership : float
            The last ownership amount.
        change_in_ownership : float
            The change in ownership amount.
        change_in_ownership_percentage : float
            The change in ownership percentage.
        holding_period : int
            The holding period of the stock ownership.
        first_added : date
            The first added date of the stock ownership.
        performance : float
            The performance of the stock ownership.
        performance_percentage : float
            The performance percentage of the stock ownership.
        last_performance : float
            The last performance of the stock ownership.
        change_in_performance : float
            The change in performance of the stock ownership.
        is_counted_for_performance : bool
            Is the stock ownership counted for performance.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        StockOwnership
        --------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "date": date,
                "page": page,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/own",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def pt(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[BaseModel]:
        """Price Target Consensus.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        PriceTargetConsensus
        --------------------
        symbol : str
            Symbol to get data for.
        target_high : float
            The high target of the price target consensus.
        target_low : float
            The low target of the price target consensus.
        target_consensus : float
            The consensus target of the price target consensus.
        target_median : float
            The median target of the price target consensus.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        PriceTargetConsensus
        --------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/pt",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def pta(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Price Target.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        PriceTarget
        -----------
        symbol : str
            Symbol to get data for.
        published_date : datetime
            The published date of the price target.
        news_url : str
            The news URL of the price target.
        news_title : Optional[str]
            The news title of the price target.
        analyst_name : Optional[str]
            The analyst name of the price target.
        price_target : float
            The price target of the price target.
        adj_price_target : float
            The adjusted price target of the price target.
        price_when_posted : float
            The price when posted of the price target.
        news_publisher : str
            The news publisher of the price target.
        news_base_url : str
            The news base URL of the price target.
        analyst_company : str
            The analyst company of the price target.

        fmp
        ===

        Parameters
        ----------
        with_grade : bool
            Include upgrades and downgrades in the response.


        PriceTarget
        -----------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/pta",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def rating(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Analyst prices and ratings over time of the company."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/rating",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def ratios(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Literal["annually", "quarterly"],
            OpenBBCustomParameter(
                description="Period of the data to return (quarterly or annually)."
            ),
        ] = "annually",
        limit: Annotated[
            Optional[pydantic.types.NonNegativeInt],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 12,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Extensive set of ratios over time.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        period : Literal['annually', 'quarterly']
            Period of the data to return (quarterly or annually).
        limit : Optional[NonNegativeInt]
            The number of data entries to return.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        FinancialRatios
        ---------------
        symbol : str
            The symbol of the company.
        date : str
            The date of the financial ratios.
        period : str
            The period of the financial ratios.
        current_ratio : Optional[float]
            The current ratio.
        quick_ratio : Optional[float]
            The quick ratio.
        cash_ratio : Optional[float]
            The cash ratio.
        days_of_sales_outstanding : Optional[float]
            Days of sales outstanding.
        days_of_inventory_outstanding : Optional[float]
            Days of inventory outstanding.
        operating_cycle : Optional[float]
            Operating cycle.
        days_of_payables_outstanding : Optional[float]
            Days of payables outstanding.
        cash_conversion_cycle : Optional[float]
            Cash conversion cycle.
        gross_profit_margin : Optional[float]
            Gross profit margin.
        operating_profit_margin : Optional[float]
            Operating profit margin.
        pretax_profit_margin : Optional[float]
            Pretax profit margin.
        net_profit_margin : Optional[float]
            Net profit margin.
        effective_tax_rate : Optional[float]
            Effective tax rate.
        return_on_assets : Optional[float]
            Return on assets.
        return_on_equity : Optional[float]
            Return on equity.
        return_on_capital_employed : Optional[float]
            Return on capital employed.
        net_income_per_ebt : Optional[float]
            Net income per EBT.
        ebt_per_ebit : Optional[float]
            EBT per EBIT.
        ebit_per_revenue : Optional[float]
            EBIT per revenue.
        debt_ratio : Optional[float]
            Debt ratio.
        debt_equity_ratio : Optional[float]
            Debt equity ratio.
        long_term_debt_to_capitalization : Optional[float]
            Long term debt to capitalization.
        total_debt_to_capitalization : Optional[float]
            Total debt to capitalization.
        interest_coverage : Optional[float]
            Interest coverage.
        cash_flow_to_debt_ratio : Optional[float]
            Cash flow to debt ratio.
        company_equity_multiplier : Optional[float]
            Company equity multiplier.
        receivables_turnover : Optional[float]
            Receivables turnover.
        payables_turnover : Optional[float]
            Payables turnover.
        inventory_turnover : Optional[float]
            Inventory turnover.
        fixed_asset_turnover : Optional[float]
            Fixed asset turnover.
        asset_turnover : Optional[float]
            Asset turnover.
        operating_cash_flow_per_share : Optional[float]
            Operating cash flow per share.
        free_cash_flow_per_share : Optional[float]
            Free cash flow per share.
        cash_per_share : Optional[float]
            Cash per share.
        payout_ratio : Optional[float]
            Payout ratio.
        operating_cash_flow_sales_ratio : Optional[float]
            Operating cash flow sales ratio.
        free_cash_flow_operating_cash_flow_ratio : Optional[float]
            Free cash flow operating cash flow ratio.
        cash_flow_coverage_ratios : Optional[float]
            Cash flow coverage ratios.
        short_term_coverage_ratios : Optional[float]
            Short term coverage ratios.
        capital_expenditure_coverage_ratio : Optional[float]
            Capital expenditure coverage ratio.
        dividend_paid_and_capex_coverage_ratio : Optional[float]
            Dividend paid and capex coverage ratio.
        dividend_payout_ratio : Optional[float]
            Dividend payout ratio.
        price_book_value_ratio : Optional[float]
            Price book value ratio.
        price_to_book_ratio : Optional[float]
            Price to book ratio.
        price_to_sales_ratio : Optional[float]
            Price to sales ratio.
        price_earnings_ratio : Optional[float]
            Price earnings ratio.
        price_to_free_cash_flows_ratio : Optional[float]
            Price to free cash flows ratio.
        price_to_operating_cash_flows_ratio : Optional[float]
            Price to operating cash flows ratio.
        price_cash_flow_ratio : Optional[float]
            Price cash flow ratio.
        price_earnings_to_growth_ratio : Optional[float]
            Price earnings to growth ratio.
        price_sales_ratio : Optional[float]
            Price sales ratio.
        dividend_yield : Optional[float]
            Dividend yield.
        enterprise_value_multiple : Optional[float]
            Enterprise value multiple.
        price_fair_value : Optional[float]
            Price fair value.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        FinancialRatios
        ---------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "period": period,
                "limit": limit,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/ratios",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def revfc(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Earning Estimate by Analysts - Revenue."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/revfc",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def revgeo(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Literal["annually", "quarterly"],
            OpenBBCustomParameter(
                description="Period of the data to return (quarterly or annually)."
            ),
        ] = "annually",
        structure: Annotated[
            Literal["hierarchical", "flat"],
            OpenBBCustomParameter(description="The structure of the returned data."),
        ] = "flat",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Revenue Geographic.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        period : Literal['quarterly', 'annually']
            Period of the data to return (quarterly or annually).
        structure : Literal['hierarchical', 'flat']
            The structure of the returned data.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        RevenueGeographic
        -----------------
        date : date
            The date of the data.
        geographic_segment : Mapping[str, int]
            Day level data containing the revenue of the geographic segment.
        americas : Optional[int]
            The revenue from the the American segment.
        europe : Optional[int]
            The revenue from the the European segment.
        greater_china : Optional[int]
            The revenue from the the Greater China segment.
        japan : Optional[int]
            The revenue from the the Japan segment.
        rest_of_asia_pacific : Optional[int]
            The revenue from the the Rest of Asia Pacific segment.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        RevenueGeographic
        -----------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "period": period,
                "structure": structure,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/revgeo",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def revseg(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Literal["annually", "quarterly"],
            OpenBBCustomParameter(
                description="Period of the data to return (quarterly or annually)."
            ),
        ] = "annually",
        structure: Annotated[
            Literal["hierarchical", "flat"],
            OpenBBCustomParameter(description="The structure of the returned data."),
        ] = "flat",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Revenue Business Line.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        period : Literal['quarterly', 'annually']
            Period of the data to return (quarterly or annually).
        structure : Literal['hierarchical', 'flat']
            The structure of the returned data.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        RevenueBusinessLine
        -------------------
        date : date
            The date of the data.
        business_line : Mapping[str, int]
            Day level data containing the revenue of the business line.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        RevenueBusinessLine
        -------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "period": period,
                "structure": structure,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/revseg",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def rot(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Number of analyst ratings over time on a monthly basis."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/rot",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def score(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """Value investing scores for any time period."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/score",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def sec(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/sec",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def shares(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/shares",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def shrs(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Share Statistics.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        ShareStatistics
        ---------------
        symbol : str
            Symbol to get data for.
        date : date
            A specific date to get data for.
        free_float : float
            The percentage of unrestricted shares of a publicly-traded company.
        float_shares : float
            The number of shares available for trading by the general public.
        outstanding_shares : float
            The total number of shares of a publicly-traded company.
        source : str
            Source of the received data.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        ShareStatistics
        ---------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/shrs",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def split(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Historical Stock Splits.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        HistoricalStockSplits
        ---------------------
        date : date
            The date of the data.
        label : str
            The label of the historical stock splits.
        numerator : float
            The numerator of the historical stock splits.
        denominator : float
            The denominator of the historical stock splits.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        HistoricalStockSplits
        ---------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/split",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def supplier(
        self, chart: bool = False
    ) -> OBBject[openbb_core.app.model.results.empty.Empty]:
        """List of suppliers of the company."""  # noqa: E501
        inputs = filter_inputs(
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/supplier",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def transcript(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        year: Annotated[
            int,
            OpenBBCustomParameter(
                description="The year of the earnings call transcript."
            ),
        ],
        quarter: Annotated[
            Literal[1, 2, 3, 4],
            OpenBBCustomParameter(
                description="The quarter of the earnings call transcript."
            ),
        ] = 1,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Earnings Call Transcript.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            Symbol to get data for.
        year : int
            The year of the earnings call transcript.
        quarter : Literal[1, 2, 3, 4]
            The quarter of the earnings call transcript.

        Returns
        -------
        OBBject
            results: List[Data]
                Serializable results.
            provider: Optional[PROVIDERS]
                Provider name.
            warnings: Optional[List[Warning_]]
                List of warnings.
            error: Optional[Error]
                Caught exceptions.
            chart: Optional[Chart]
                Chart object.


        EarningsCallTranscript
        ----------------------
        symbol : str
            Symbol to get data for.
        quarter : int
            The quarter of the earnings call transcript.
        year : int
            The year of the earnings call transcript.
        date : datetime
            The date of the data.
        content : str
            The content of the earnings call transcript.

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        EarningsCallTranscript
        ----------------------
        All fields are standardized."""  # noqa: E501
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "year": year,
                "quarter": quarter,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/transcript",
            **inputs,
        ).output

        return filter_output(o)
