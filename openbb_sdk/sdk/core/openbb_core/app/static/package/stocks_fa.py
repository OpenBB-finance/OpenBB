### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
import typing
from typing import List, Literal, Optional, Union

from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_stocks_fa(Container):
    @filter_call
    @validate_arguments
    def analysis(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Analyse SEC filings with the help of machine learning."""
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
        symbol: Optional[str] = None,
        period: Literal["annual", "quarter"] = "annual",
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Balance Sheet.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp, polygon]
            The provider to use for the query.
        symbol : Optional[str]
            None
        period : Literal['annual', 'quarter']
            None

        Returns
        -------
        CommandOutput
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
            None
        cik : Optional[int]
            None
        inventory : Optional[int]
            None

        fmp
        ===

        Parameters
        ----------
        cik : Optional[str]
            None
        limit : Optional[NonNegativeInt]
            None


        BalanceSheet
        ------------
        symbol : str
            None
        reportedCurrency : Optional[str]
            None
        fillingDate : Optional[date]
            None
        acceptedDate : Optional[datetime]
            None
        calendarYear : Optional[int]
            None
        period : Optional[str]
            None
        cashAndCashEquivalents : Optional[int]
            None
        shortTermInvestments : Optional[int]
            None
        cashAndShortTermInvestments : Optional[int]
            None
        netReceivables : Optional[int]
            None
        otherCurrentAssets : Optional[int]
            None
        totalCurrentAssets : Optional[int]
            None
        longTermInvestments : Optional[int]
            None
        propertyPlantEquipmentNet : Optional[int]
            None
        goodwill : Optional[int]
            None
        intangibleAssets : Optional[int]
            None
        goodwillAndIntangibleAssets : Optional[int]
            None
        taxAssets : Optional[int]
            None
        otherNonCurrentAssets : Optional[int]
            None
        totalNonCurrentAssets : Optional[int]
            None
        totalAssets : Optional[int]
            None
        accountPayables : Optional[int]
            None
        otherCurrentLiabilities : Optional[int]
            None
        deferredRevenue : Optional[int]
            None
        shortTermDebt : Optional[int]
            None
        taxPayables : Optional[int]
            None
        totalCurrentLiabilities : Optional[int]
            None
        longTermDebt : Optional[int]
            None
        deferredRevenueNonCurrent : Optional[int]
            None
        deferredTaxLiabilitiesNonCurrent : Optional[int]
            None
        otherNonCurrentLiabilities : Optional[int]
            None
        totalNonCurrentLiabilities : Optional[int]
            None
        totalLiabilities : Optional[int]
            None
        commonStock : Optional[int]
            None
        retainedEarnings : Optional[int]
            None
        accumulatedOtherComprehensiveIncomeLoss : Optional[int]
            None
        othertotalStockholdersEquity : Optional[int]
            None
        totalEquity : Optional[int]
            None
        totalLiabilitiesAndStockholdersEquity : Optional[int]
            None
        totalStockholdersEquity : Optional[int]
            None
        minorityInterest : Optional[int]
            None
        totalLiabilitiesAndTotalEquity : Optional[int]
            None
        totalInvestments : Optional[int]
            None
        netDebt : Optional[int]
            None
        finalLink : Optional[str]
            None

        polygon
        =======

        Parameters
        ----------
        ticker : Optional[str]
            The symbol of the company if no CIK is provided.
        cik : Optional[str]
            The CIK of the company if no symbol is provided.
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
        timeframe : Optional[Literal['annual', 'quarterly', 'ttm']]
            The timeframe of the financial statement.
        include_sources : Optional[bool]
            Whether to include the sources of the financial statement.
        order : Optional[Literal['asc', 'desc']]
            The order of the financial statement.
        limit : Optional[PositiveInt]
            The limit of the financial statement.
        sort : Optional[Literal['filing_date', 'period_of_report_date']]
            The sort of the financial statement.


        BalanceSheet
        ------------
        start_date : date
            None
        equity : Optional[int]
            None
        equity_attributable_to_noncontrolling_interest : Optional[int]
            None
        equity_attributable_to_parent : Optional[int]
            None
        liabilities_and_equity : Optional[int]
            None"""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "period": period,
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
        symbol: str,
        limit: int = 10,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Balance Sheet Statement Growth.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        limit : int
            The number of data entries to return.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
        start_date: Union[datetime.date, None, str] = None,
        end_date: Union[datetime.date, None, str] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
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
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
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
        symbol: Optional[str] = None,
        period: Literal["annual", "quarter"] = "annual",
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Cash Flow Statement.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp, polygon]
            The provider to use for the query.
        symbol : Optional[str]
            None
        period : Literal['annual', 'quarter']
            None

        Returns
        -------
        CommandOutput
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
            None
        symbol : str
            None
        cik : Optional[int]
            None
        period : Optional[str]
            None
        inventory : Optional[int]
            None

        fmp
        ===

        Parameters
        ----------
        cik : Optional[str]
            None
        limit : Optional[NonNegativeInt]
            None


        CashFlowStatement
        -----------------
        reportedCurrency : str
            None
        fillingDate : Optional[date]
            None
        acceptedDate : Optional[datetime]
            None
        calendarYear : Optional[int]
            None
        netIncome : Optional[int]
            None
        depreciationAndAmortization : Optional[int]
            None
        deferredIncomeTax : Optional[int]
            None
        stockBasedCompensation : Optional[int]
            None
        changeInWorkingCapital : Optional[int]
            None
        accountsReceivables : Optional[int]
            None
        accountsPayables : Optional[int]
            None
        otherWorkingCapital : Optional[int]
            None
        otherNonCashItems : Optional[int]
            None
        netCashProvidedByOperatingActivities : Optional[int]
            None
        investmentsInPropertyPlantAndEquipment : Optional[int]
            None
        acquisitionsNet : Optional[int]
            None
        purchasesOfInvestments : Optional[int]
            None
        salesMaturitiesOfInvestments : Optional[int]
            None
        otherInvestingActivites : Optional[int]
            None
        netCashUsedForInvestingActivites : Optional[int]
            None
        debtRepayment : Optional[int]
            None
        commonStockIssued : Optional[int]
            None
        commonStockRepurchased : Optional[int]
            None
        dividendsPaid : Optional[int]
            None
        otherFinancingActivites : Optional[int]
            None
        netCashUsedProvidedByFinancingActivities : Optional[int]
            None
        effectOfForexChangesOnCash : Optional[int]
            None
        netChangeInCash : Optional[int]
            None
        cashAtEndOfPeriod : Optional[int]
            None
        cashAtBeginningOfPeriod : Optional[int]
            None
        operatingCashFlow : Optional[int]
            None
        capitalExpenditure : Optional[int]
            None
        freeCashFlow : Optional[int]
            None
        link : Optional[str]
            None
        finalLink : Optional[str]
            None

        polygon
        =======

        Parameters
        ----------
        ticker : Optional[str]
            The symbol of the company if no CIK is provided.
        cik : Optional[str]
            The CIK of the company if no symbol is provided.
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
        timeframe : Optional[Literal['annual', 'quarterly', 'ttm']]
            The timeframe of the financial statement.
        include_sources : Optional[bool]
            Whether to include the sources of the financial statement.
        order : Optional[Literal['asc', 'desc']]
            The order of the financial statement.
        limit : Optional[PositiveInt]
            The limit of the financial statement.
        sort : Optional[Literal['filing_date', 'period_of_report_date']]
            The sort of the financial statement.


        CashFlowStatement
        -----------------
        start_date : date
            None
        tickers : Optional[List[str]]
            None
        filing_date : Optional[date]
            None
        acceptance_datetime : Optional[datetime]
            None
        fiscal_period : Optional[str]
            None
        net_cash_flow_continuing : int
            None
        net_cash_flow_from_financing_activities_continuing : int
            None
        net_cash_flow_from_investing_activities_continuing : int
            None
        net_cash_flow_from_operating_activities_continuing : int
            None"""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "period": period,
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
        symbol: str,
        limit: int = 10,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Cash Flow Statement Growth.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        limit : int
            The number of data entries to return.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Executive Compensation.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
        start_date: Union[datetime.date, None, str] = None,
        end_date: Union[datetime.date, None, str] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
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
        CommandOutput
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
        All fields are standardized."""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """List of customers of the company."""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Determine the (historical) discounted cash flow."""
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
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Historical Dividends.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        CommandOutput
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Detailed breakdown for Return on Equity (RoE)."""
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
        symbol: str,
        limit: Optional[int] = 50,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Earnings Calendar.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        limit : Optional[int]
            The number of data entries to return.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Number of Employees.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Enterprise value."""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Earnings Estimate by Analysts - EPS."""
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
        symbol: str,
        period: Literal["quarterly", "annually"] = "annually",
        limit: int = 30,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Analyst Estimates.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        period : Literal['quarterly', 'annually']
            Period of the data to return (quarterly or annually).
        limit : int
            The number of data entries to return.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Fama French 3 Factor Model - Coefficient of Earnings."""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Fama French 3 Factor Model - Raw Data."""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Key fraud ratios including M-score, Z-score and McKee."""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Growth of financial statement items and ratios."""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
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
        symbol: str,
        period: Literal["annually", "quarterly"] = "annually",
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Income Statement.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp, polygon]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        period : Literal['annually', 'quarterly']
            Period of the data to return (quarterly or annually).

        Returns
        -------
        CommandOutput
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
        currency : Optional[str]
            Reporting currency.
        filing_date : Optional[date]
            Filling date.
        accepted_date : Optional[date]
            Accepted date.
        period : Optional[str]
            Period of the income statement.
        revenue : Optional[int]
            Revenue.
        cost_of_revenue : Optional[int]
            Cost of revenue.
        gross_profit : Optional[int]
            Gross profit.
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
        operating_income : Optional[int]
            Operating income.
        interest_income : Optional[int]
            Interest income.
        interest_expense : Optional[int]
            Interest expense.
        total_other_income_expenses_net : Optional[int]
            Total other income expenses net.
        income_before_tax : Optional[int]
            Income before tax.
        income_tax_expense : Optional[int]
            Income tax expense.
        net_income : Optional[int]
            Net income.
        eps : Optional[float]
            Earnings per share.
        eps_diluted : Optional[float]
            Earnings per share diluted.
        weighted_average_shares_outstanding : Optional[int]
            Weighted average shares outstanding.
        weighted_average_shares_outstanding_dil : Optional[int]
            Weighted average shares outstanding diluted.

        fmp
        ===

        Parameters
        ----------
        cik : Optional[str]
            The CIK of the company if no symbol is provided.
        limit : Optional[NonNegativeInt]
            The limit of the income statement.


        IncomeStatement
        ---------------
        symbol : str
            None
        cik : Optional[int]
            None
        calendarYear : Optional[int]
            None
        grossProfitRatio : Optional[float]
            None
        costAndExpenses : Optional[int]
            None
        ebitdaratio : Optional[float]
            None
        operatingIncomeRatio : Optional[float]
            None
        incomeBeforeTaxRatio : Optional[float]
            None
        netIncomeRatio : Optional[float]
            None
        link : Optional[str]
            None
        finalLink : Optional[str]
            None

        polygon
        =======

        Parameters
        ----------
        ticker : Optional[str]
            The symbol of the company if no CIK is provided.
        cik : Optional[str]
            The CIK of the company if no symbol is provided.
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
        timeframe : Optional[Literal['annual', 'quarterly', 'ttm']]
            The timeframe of the financial statement.
        include_sources : Optional[bool]
            Whether to include the sources of the financial statement.
        order : Optional[Literal['asc', 'desc']]
            The order of the financial statement.
        limit : Optional[PositiveInt]
            The limit of the financial statement.
        sort : Optional[Literal['filing_date', 'period_of_report_date']]
            The sort of the financial statement.


        IncomeStatement
        ---------------
        start_date : date
            None
        tickers : Optional[List[str]]
            None
        cik : Optional[str]
            None
        acceptance_datetime : Optional[datetime]
            None
        fiscal_period : Optional[str]
            None
        revenues : Optional[float]
            None
        income_loss_from_continuing_operations_before_tax : Optional[float]
            None
        income_loss_from_continuing_operations_after_tax : Optional[float]
            None
        income_tax_expense_benefit : Optional[float]
            None
        net_income_loss : Optional[float]
            None
        basic_earnings_per_share : Optional[float]
            None
        diluted_earnings_per_share : Optional[float]
            None
        benefits_costs_expenses : Optional[float]
            None
        interest_expense_operating : Optional[float]
            None
        net_income_loss_attributable_to_noncontrolling_interest : Optional[int]
            None
        net_income_loss_attributable_to_parent : Optional[float]
            None
        net_income_loss_available_to_common_stockholders_basic : Optional[float]
            None
        operating_income_loss : Optional[float]
            None
        participating_securities_distributed_and_undistributed_earnings_loss_basic : Optional[float]
            None
        preferred_stock_dividends_and_other_adjustments : Optional[float]
            None"""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "period": period,
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
        symbol: str,
        limit: int = 10,
        period: Literal["annually", "quarterly"] = "annually",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Income Statement Growth.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        limit : int
            The number of data entries to return.
        period : Literal['annually', 'quarterly']
            Period of the data to return (quarterly or annually).

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
        symbol: str,
        transactionType: Optional[
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
        ] = ["P-Purchase"],
        reportingCik: Optional[int] = None,
        companyCik: Optional[int] = None,
        page: Optional[int] = 0,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Stock Insider Trading.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
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
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
    def key(
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
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
        symbol: str,
        period: Literal["quarter", "annual"] = "annual",
        limit: Optional[int] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Key Metrics.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : str
            None
        period : Literal['quarter', 'annual']
            None
        limit : Optional[int]
            None

        Returns
        -------
        CommandOutput
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
            None
        date : date
            None
        period : str
            None
        roic : Optional[float]
            None
        roe : Optional[float]
            None

        fmp
        ===

        Parameters
        ----------
        All fields are standardized.


        KeyMetrics
        ----------
        revenuePerShare : float
            None
        netIncomePerShare : float
            None
        operatingCashFlowPerShare : Optional[float]
            None
        freeCashFlowPerShare : Optional[float]
            None
        cashPerShare : Optional[float]
            None
        bookValuePerShare : Optional[float]
            None
        tangibleBookValuePerShare : Optional[float]
            None
        shareholdersEquityPerShare : Optional[float]
            None
        interestDebtPerShare : Optional[float]
            None
        marketCap : Optional[float]
            None
        enterpriseValue : Optional[float]
            None
        peRatio : Optional[float]
            None
        priceToSalesRatio : Optional[float]
            None
        pocfratio : Optional[float]
            None
        pfcfRatio : Optional[float]
            None
        pbRatio : Optional[float]
            None
        ptbRatio : Optional[float]
            None
        evToSales : Optional[float]
            None
        enterpriseValueOverEBITDA : Optional[float]
            None
        evToOperatingCashFlow : Optional[float]
            None
        evToFreeCashFlow : Optional[float]
            None
        earningsYield : Optional[float]
            None
        freeCashFlowYield : Optional[float]
            None
        debtToEquity : Optional[float]
            None
        debtToAssets : Optional[float]
            None
        netDebtToEBITDA : Optional[float]
            None
        currentRatio : Optional[float]
            None
        interestCoverage : Optional[float]
            None
        incomeQuality : Optional[float]
            None
        dividendYield : Optional[float]
            None
        payoutRatio : Optional[float]
            None
        salesGeneralAndAdministrativeToRevenue : Optional[float]
            None
        researchAndDdevelopementToRevenue : Optional[float]
            None
        intangiblesToTotalAssets : Optional[float]
            None
        capexToOperatingCashFlow : Optional[float]
            None
        capexToRevenue : Optional[float]
            None
        capexToDepreciation : Optional[float]
            None
        stockBasedCompensationToRevenue : Optional[float]
            None
        grahamNumber : Optional[float]
            None
        returnOnTangibleAssets : Optional[float]
            None
        grahamNetNet : Optional[float]
            None
        workingCapital : Optional[float]
            None
        tangibleAssetValue : Optional[float]
            None
        netCurrentAssetValue : Optional[float]
            None
        investedCapital : Optional[float]
            None
        averageReceivables : Optional[float]
            None
        averagePayables : Optional[float]
            None
        averageInventory : Optional[float]
            None
        daysSalesOutstanding : Optional[float]
            None
        daysPayablesOutstanding : Optional[float]
            None
        daysOfInventoryOnHand : Optional[float]
            None
        receivablesTurnover : Optional[float]
            None
        payablesTurnover : Optional[float]
            None
        inventoryTurnover : Optional[float]
            None
        capexPerShare : Optional[float]
            None"""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Key Executives.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        CommandOutput
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Obtain the market capitalization or enterprise value."""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
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
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Company Overview.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
        symbol: str,
        include_current_quarter: bool = False,
        date: Optional[datetime.date] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Institutional Ownership.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        include_current_quarter : bool
            Include current quarter data.
        date : Optional[date]
            A specific date to get data for.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "include_current_quarter": include_current_quarter,
                "date": date,
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
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Price Target Consensus.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Price Target.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized.


        PriceTarget
        -----------
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Analyst prices and ratings over time of the company."""
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
        self, chart: bool = False
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Extensive set of ratios over time."""
        inputs = filter_inputs(
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Earning Estimate by Analysts - Revenue."""
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
        symbol: str,
        period: Literal["quarterly", "annually"] = "annually",
        structure: Literal["hierarchical", "flat"] = "flat",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Revenue Geographic.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        period : Literal['quarterly', 'annually']
            Period of the data to return (quarterly or annually).
        structure : Literal['hierarchical', 'flat']
            The structure of the returned data.

        Returns
        -------
        CommandOutput
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
        symbol: str,
        period: Literal["quarterly", "annually"] = "annually",
        structure: Literal["hierarchical", "flat"] = "flat",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Revenue Business Line.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        period : Literal['quarterly', 'annually']
            Period of the data to return (quarterly or annually).
        structure : Literal['hierarchical', 'flat']
            The structure of the returned data.

        Returns
        -------
        CommandOutput
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Number of analyst ratings over time on a monthly basis."""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Value investing scores for any time period."""
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
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
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Share Statistics.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Historical Stock Splits.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.

        Returns
        -------
        CommandOutput
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """List of suppliers of the company."""
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
        symbol: str,
        year: int,
        quarter: Literal[1, 2, 3, 4] = 1,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Earnings Call Transcript.


        openbb
        ======

        Parameters
        ----------
        provider: Literal[fmp]
            The provider to use for the query.
        symbol : ConstrainedStrValue
            Symbol to get data for.
        year : int
            The year of the earnings call transcript.
        quarter : Literal[1, 2, 3, 4]
            The quarter of the earnings call transcript.

        Returns
        -------
        CommandOutput
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
        symbol : ConstrainedStrValue
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
        All fields are standardized."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
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
