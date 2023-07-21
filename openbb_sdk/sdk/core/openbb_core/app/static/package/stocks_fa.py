### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
import typing
from typing import List, Literal, Optional, Union

import openbb_provider
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
        symbol: str,
        period: Literal["annually", "quarterly"] = "annually",
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Balance Sheet.

        Available providers: fmp, polygon

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.
        period : Literal["annually", "quarterly"]
            The period of the balance sheet.


        Returns
        -------
        date : date
            The date of the balance sheet.
        cik : Optional[int]
            The CIK of the company.
        cash_and_cash_equivalents : Optional[int]
            The cash and cash equivalents of the balance sheet.
        short_term_investments : Optional[int]
            The short term investments of the balance sheet.
        cash_and_short_term_investments : Optional[int]
            The cash and short term investments of the balance sheet.
        net_receivables : Optional[int]
            The net receivables of the balance sheet.
        inventory : Optional[int]
            The inventory of the balance sheet.
        other_current_assets : Optional[int]
            The other current assets of the balance sheet.
        current_assets : Optional[int]
            The current assets of the balance sheet.
        long_term_investments : Optional[int]
            The long term investments of the balance sheet.
        property_plant_equipment_net : Optional[int]
            The property plant equipment net of the balance sheet.
        other_non_current_assets : Optional[int]
            The other non current assets of the balance sheet.
        noncurrent_assets : Optional[int]
            The non current assets of the balance sheet.
        assets : Optional[int]
            The assets of the balance sheet.
        accounts_payable : Optional[int]
            The accounts payable of the balance sheet.
        other_current_liabilities : Optional[int]
            The other current liabilities of the balance sheet.
        deferred_revenue : Optional[int]
            The deferred revenue of the balance sheet.
        current_liabilities : Optional[int]
            The current liabilities of the balance sheet.
        long_term_debt : Optional[int]
            The long term debt of the balance sheet.
        other_non_current_liabilities : Optional[int]
            The other non current liabilities of the balance sheet.
        noncurrent_liabilities : Optional[int]
            The non current liabilities of the balance sheet.
        liabilities : Optional[int]
            The liabilities of the balance sheet.
        common_stock : Optional[int]
            The common stock of the balance sheet.
        retained_earnings : Optional[int]
            The retained earnings of the balance sheet.
        accumulated_other_comprehensive_income_loss : Optional[int]
            The accumulated other comprehensive income loss of the balance sheet.
        total_equity : Optional[int]
            The total equity of the balance sheet.
        total_liabilities_and_stockholders_equity : Optional[int]
            The total liabilities and stockholders equity of the balance sheet.

        fmp
        ===

        Source: https://financialmodelingprep.com/developer/docs/#Balance-Sheet

        Parameter
        ---------
        cik : Optional[str]
            The CIK of the company if symbol is not provided.
        limit : Optional[NonNegativeInt]
            The limit of the balance sheet.


        Returns
        -------
        Documentation not available.


        polygon
        =======

        Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials

        Parameter
        ---------
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
        timeframe : Optional[Literal["annual", "quarterly", "ttm"]]
            The timeframe of the financial statement.
        include_sources : Optional[bool]
            Whether to include the sources of the financial statement.
        order : Optional[Literal["asc", "desc"]]
            The order of the financial statement.
        limit : Optional[PositiveInt]
            The limit of the financial statement.
        sort : Optional[Literal["filing_date", "period_of_report_date"]]
            The sort of the financial statement.


        Returns
        -------
        Documentation not available.
        """
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
    def cal(
        self,
        start_date: Union[datetime.date, None, str] = datetime.date(2023, 6, 20),
        end_date: Union[datetime.date, None, str] = datetime.date(2023, 7, 20),
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Show Dividend Calendar for a given start and end dates.

        Available providers: fmp,

        Standard
        ========

        The maximum time interval between the start and end date can be 3 months.
        Default value for time interval is 1 month.

        Parameter
        ---------
        start_date : date
            The starting date to fetch the dividend calendar from. Default value is the
            previous day from the last month.
        end_date : date
            The ending date to fetch the dividend calendar till. Default value is the
            previous day from the current month.


        Returns
        -------
        date : dateType
            The date of the dividend in the calendar.
        label : str
            The date in human readable form in the calendar.
        adjDividend : Optional[NonNegativeFloat]
            The adjusted dividend on a date in the calendar.
        symbol : str
            The symbol of the company for which the dividend is returned in the calendar.
        dividend : Optional[NonNegativeFloat]
            The dividend amount in the calendar.
        recordDate : Optional[dateType]
            The record date of the dividend in the calendar.
        paymentDate : Optional[dateType]
            The payment date of the dividend in the calendar.
        declarationDate : Optional[dateType]
            The declaration date of the dividend in the calendar.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/dividend-calendar-api/

        The maximum time interval between the start and end date can be 3 months.
        Default value for time interval is 1 month.

        Parameter
        ---------
        All fields are standardized.
        """
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
        symbol: str,
        period: Literal["annually", "quarterly"] = "annually",
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Cash Flow Statement.

        Available providers: fmp, polygon

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.
        period : Literal["annually", "quarterly"]
            The period of the income statement.


        Returns
        -------
        date : date
            The date of the cash flow statement.
        symbol : str
            The symbol of the company.
        currency : Optional[str]
            The currency of the cash flow statement.
        cik : Optional[int]
            The Central Index Key (CIK) of the company.
        period : Optional[str]
            The period of the cash flow statement.
        cash_at_beginning_of_period : Optional[int]
            The cash at the beginning of the period.
        net_income : Optional[int]
            The net income.
        depreciation_and_amortization : Optional[int]
            The depreciation and amortization.
        stock_based_compensation : Optional[int]
            The stock based compensation.
        accounts_receivables : Optional[int]
            The accounts receivables.
        inventory : Optional[int]
            The inventory.
        accounts_payables : Optional[int]
            The accounts payables.
        net_cash_flow_from_operating_activities : Optional[int]
            The net cash flow from operating activities.
        purchases_of_investments : Optional[int]
            The purchases of investments.
        sales_maturities_of_investments : Optional[int]
            The sales maturities of investments.
        investments_in_property_plant_and_equipment : Optional[int]
            The investments in property plant and equipment.
        net_cash_flow_from_investing_activities : Optional[int]
            The net cash flow from investing activities.
        dividends_paid : Optional[int]
            The dividends paid.
        common_stock_repurchased : Optional[int]
            The common stock repurchased.
        debt_repayment : Optional[int]
            The debt repayment.
        other_financing_activities : Optional[int]
            The other financing activities.
        net_cash_flow_from_financing_activities : Optional[int]
            The net cash flow from financing activities.
        net_cash_flow : Optional[int]
            The net cash flow.
        cash_at_end_of_period : Optional[int]
            The cash at the end of the period.

        fmp
        ===

        Source: https://financialmodelingprep.com/developer/docs/#Cash-Flow-Statement

        Parameter
        ---------
        cik : Optional[str]
            The CIK of the company if symbol is not provided.
        limit : Optional[NonNegativeInt]
            The limit of the cash flow statement.


        Returns
        -------
        Documentation not available.


        polygon
        =======

        Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials

        Parameter
        ---------
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
        timeframe : Optional[Literal["annual", "quarterly", "ttm"]]
            The timeframe of the financial statement.
        include_sources : Optional[bool]
            Whether to include the sources of the financial statement.
        order : Optional[Literal["asc", "desc"]]
            The order of the financial statement.
        limit : Optional[PositiveInt]
            The limit of the financial statement.
        sort : Optional[Literal["filing_date", "period_of_report_date"]]
            The sort of the financial statement.


        Returns
        -------
        Documentation not available.
        """
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
    def comp(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Executive Compensation.

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.


        Returns
        -------
        cik : Optional[str]
            The Central Index Key (CIK) of the company.
        symbol : str
            The symbol of the company.
        filing_date : dateType
            The date of the filing.
        accepted_date : dateType
            The date the filing was accepted.
        name_and_position : str
            The name and position of the executive.
        year : int
            The year of the compensation.
        salary : float
            The salary of the executive.
        bonus : float
            The bonus of the executive.
        stock_award : float
            The stock award of the executive.
        incentive_plan_compensation : float
            The incentive plan compensation of the executive.
        all_other_compensation : float
            The all other compensation of the executive.
        total : float
            The total compensation of the executive.
        url : str
            The URL of the filing.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/executive-compensation-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        start_date : date
            The start date of the stock splits from which to retrieve the data.
        end_date : date
            The end date of the stock splits up to which to retrieve the data.


        Returns
        -------
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

        Source: https://site.financialmodelingprep.com/developer/docs/stock-split-calendar-api/

        Parameter
        ---------
        All fields are standardized.
        """
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

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.


        Returns
        -------
        date : date
            The date of the historical dividends.
        label : str
            The label of the historical dividends.
        adj_dividend : float
            The adjusted dividend of the historical dividends.
        dividend : float
            The dividend of the historical dividends.
        record_date : date
            The record date of the historical dividends.
        payment_date : date
            The payment date of the historical dividends.
        declaration_date : date
            The declaration date of the historical dividends.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/#Historical-Dividends

        Parameter
        ---------
        All fields are standardized.
        """
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
        limit: Optional[int] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Earnings Calendar.

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.
        limit : int


        Returns
        -------
        symbol : str
            The symbol of the asset.
        date : date
            The date of the earnings calendar.
        eps : float
            The EPS of the earnings calendar.
        eps_estimated : float
            The estimated EPS of the earnings calendar.
        time : str
            The time of the earnings calendar.
        revenue : int
            The revenue of the earnings calendar.
        revenue_estimated : int
            The estimated revenue of the earnings calendar.
        updated_from_date : date
            The updated from date of the earnings calendar.
        fiscal_date_ending : date
            The fiscal date ending of the earnings calendar.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/earnings-calendar-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.


        Returns
        -------
        symbol : str
            The symbol of the company to retrieve the historical employees of.
        cik : int
            The CIK of the company to retrieve the historical employees of.
        acceptance_time : datetime
            The time of acceptance of the company employee.
        period_of_report : date
            The date of reporting of the company employee.
        company_name : str
            The registered name of the company to retrieve the historical employees of.
        form_type : float
            The form type of the company employee.
        filing_date : date
            The filing date of the company employee
        employee_count : int
            The count of employees of the company.
        source : str
            The source URL which retrieves this data for the company.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/historical-numer-of-employees-api/

        Parameter
        ---------
        All fields are standardized.
        """
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
        period: Literal["quarter", "annual"] = "annual",
        limit: int = 30,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Analyst Estimates.

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.
        period : Literal["quarter", "annual"]
            The period of the analyst estimates.
        limit : int
            The limit of the analyst estimates.


        Returns
        -------
        symbol : str
            The symbol of the asset.
        date : date
            The date of the analyst estimates.
        estimated_revenue_low : int
            The estimated revenue low of the analyst estimates.
        estimated_revenue_high : int
            The estimated revenue high of the analyst estimates.
        estimated_revenue_avg : int
            The estimated revenue average of the analyst estimates.
        estimated_ebitda_low : int
            The estimated EBITDA low of the analyst estimates.
        estimated_ebitda_high : int
            The estimated EBITDA high of the analyst estimates.
        estimated_ebitda_avg : int
            The estimated EBITDA average of the analyst estimates.
        estimated_ebit_low : int
            The estimated EBIT low of the analyst estimates.
        estimated_ebit_high : int
            The estimated EBIT high of the analyst estimates.
        estimated_ebit_avg : int
            The estimated EBIT average of the analyst estimates.
        estimated_net_income_low : int
            The estimated net income low of the analyst estimates.
        estimated_net_income_high : int
            The estimated net income high of the analyst estimates.
        estimated_net_income_avg : int
            The estimated net income average of the analyst estimates.
        estimated_sga_expense_low : int
            The estimated SGA expense low of the analyst estimates.
        estimated_sga_expense_high : int
            The estimated SGA expense high of the analyst estimates.
        estimated_sga_expense_avg : int
            The estimated SGA expense average of the analyst estimates.
        estimated_eps_avg : float
            The estimated EPS average of the analyst estimates.
        estimated_eps_high : float
            The estimated EPS high of the analyst estimates.
        estimated_eps_low : float
            The estimated EPS low of the analyst estimates.
        number_analyst_estimated_revenue : int
            The number of analysts who estimated revenue of the analyst estimates.
        number_analysts_estimated_eps : int
            The number of analysts who estimated EPS of the analyst estimates.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/analyst-estimates-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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

        Available providers: fmp, polygon

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.
        period : Literal["annually", "quarterly"]
            The period of the income statement.


        Returns
        -------
        date : date
            The date of the income statement.
        symbol : str
            The symbol of the company.
        currency : Optional[str]
            The currency of the income statement.
        cik : Optional[int]
            The Central Index Key (CIK) of the company.
        filing_date : date
            The filing date of the income statement.
        accepted_date : Optional[date]
            The accepted date of the income statement.
        period : Optional[str]
            The period of the income statement.
        revenue : Optional[int]
            The revenue of the income statement.
        cost_of_revenue : Optional[int]
            The cost of revenue of the income statement.
        gross_profit : Optional[int]
            The gross profit of the income statement.
        research_and_development_expenses : Optional[int]
            The research and development expenses of the income statement.
        general_and_administrative_expenses : Optional[int]
            The general and administrative expenses of the income statement.
        selling_and_marketing_expenses : Optional[float]
            The selling and marketing expenses of the income statement.
        selling_general_and_administrative_expenses : Optional[int]
            The selling, general and administrative expenses of the income statement.
        other_expenses : Optional[int]
            The other expenses of the income statement.
        operating_expenses : Optional[int]
            The operating expenses of the income statement.
        depreciation_and_amortization : Optional[int]
            The depreciation and amortization of the income statement.
        ebitda : Optional[int]
            The earnings before interest, taxes, depreciation and amortization of the income statement.
        operating_income : Optional[int]
            The operating income of the income statement.
        interest_income : Optional[int]
            The interest income of the income statement.
        interest_expense : Optional[int]
            The interest expense of the income statement.
        total_other_income_expenses_net : Optional[int]
            The total other income expenses net of the income statement.
        income_before_tax : Optional[int]
            The income before tax of the income statement.
        income_tax_expense : Optional[int]
            The income tax expense of the income statement.
        net_income : Optional[int]
            The net income of the income statement.
        eps : Optional[float]
            The earnings per share of the income statement.
        eps_diluted : Optional[float]
            The diluted earnings per share of the income statement.
        weighted_average_shares_outstanding : Optional[int]
            The weighted average shares outstanding of the income statement.
        weighted_average_shares_outstanding_dil : Optional[int]
            The weighted average shares outstanding diluted of the income statement.

        fmp
        ===

        Source: https://financialmodelingprep.com/developer/docs/#Income-Statement

        Parameter
        ---------
        cik : Optional[str]
            The CIK of the company if no symbol is provided.
        limit : Optional[NonNegativeInt]
            The limit of the income statement.


        Returns
        -------
        Documentation not available.


        polygon
        =======

        Source: https://polygon.io/docs/stocks#!/get_vx_reference_financials

        Parameter
        ---------
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
        timeframe : Optional[Literal["annual", "quarterly", "ttm"]]
            The timeframe of the financial statement.
        include_sources : Optional[bool]
            Whether to include the sources of the financial statement.
        order : Optional[Literal["asc", "desc"]]
            The order of the financial statement.
        limit : Optional[PositiveInt]
            The limit of the financial statement.
        sort : Optional[Literal["filing_date", "period_of_report_date"]]
            The sort of the financial statement.


        Returns
        -------
        Documentation not available.
        """
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
    def ins(
        self,
        transactionType: List[
            openbb_provider.models.stock_insider_trading.TransactionTypes
        ] = [],
        symbol: Optional[str] = None,
        reportingCik: Optional[int] = None,
        companyCik: Optional[int] = None,
        page: int = 0,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Stock Insider Trading.

        Available providers: fmp,

        Standard
        ========


        Parameter
        ---------
        transactionType : List[TransactionTypes]
            The type of the transaction. Possible values are:
            A-Award, C-Conversion, D-Return, E-ExpireShort, F-InKind, G-Gift, H-ExpireLong
            I-Discretionary, J-Other, L-Small, M-Exempt, O-OutOfTheMoneym P-Purchase
            S-Sale, U-Tender, W-Will, X-InTheMoney, Z-Trust
        symbol : Optional[str]
            The symbol of the company.
        reportingCik : Optional[int]
            The CIK of the reporting owner.
        companyCik : Optional[int]
            The CIK of the company owner.
        page: int
            The page number to get


        Returns
        -------
        symbol : str
            The symbol of the asset.
        filingDate : datetime
            The filing date of the stock insider trading.
        transactionDate : date
            The transaction date of the stock insider trading.
        reportingCik : int
            The reporting CIK of the stock insider trading.
        transactionType : str
            The transaction type of the stock insider trading.
        securitiesOwned : int
            The securities owned of the stock insider trading.
        companyCik : int
            The company CIK of the stock insider trading.
        reportingName : str
            The reporting name of the stock insider trading.
        typeOfOwner : str
            The type of owner of the stock insider trading.
        acquistionOrDisposition : str
            The acquistion or disposition of the stock insider trading.
        formType : str
            The form type of the stock insider trading.
        securitiesTransacted : float
            The securities transacted of the stock insider trading.
        price : float
            The price of the stock insider trading.
        securityName : str
            The security name of the stock insider trading.
        link : str
            The link of the stock insider trading.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/#Stock-Insider-Trading

        Parameter
        ---------
            The type of the transaction. Possible values are:
            A-Award, C-Conversion, D-Return, E-ExpireShort, F-InKind, G-Gift, H-ExpireLong
            I-Discretionary, J-Other, L-Small, M-Exempt, O-OutOfTheMoneym P-Purchase
            S-Sale, U-Tender, W-Will, X-InTheMoney, Z-Trust
        companyCik: Optional[str]
            The CIK of the company owner.
        page: int
            The page number to get
        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "transactionType": transactionType,
                "symbol": symbol,
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
        period: Literal["annually", "quarterly"] = "annually",
        limit: Optional[int] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Key Metrics.

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.


        Returns
        -------
        symbol : str
            The symbol of the stock.
        date : DateType
            The date of the key metrics.
        period : str
            The period of the key metrics.
        revenue_per_share : float
            The revenue per share of the stock.
        net_income_per_share : float
            The net income per share of the stock.
        operating_cash_flow_per_share : float
            The operating cash flow per share of the stock.
        free_cash_flow_per_share : float
            The free cash flow per share of the stock.
        cash_per_share : float
            The cash per share of the stock.
        book_value_per_share : float
            The book value per share of the stock.
        tangible_book_value_per_share : float
            The tangible book value per share of the stock.
        shareholders_equity_per_share : float
            The shareholders equity per share of the stock.
        interest_debt_per_share : float
            The interest debt per share of the stock.
        market_cap : float
            The market cap of the stock.
        enterprise_value : float
            The enterprise value of the stock.
        pe_ratio : float
            The PE ratio of the stock.
        price_to_sales_ratio : float
            The price to sales ratio of the stock.
        pocf_ratio : float
            The POCF ratio of the stock.
        pfcf_ratio : float
            The PFCF ratio of the stock.
        pb_ratio : float
            The PB ratio of the stock.
        ptb_ratio : float
            The PTB ratio of the stock.
        ev_to_sales : float
            The EV to sales of the stock.
        enterprise_value_over_ebitda : float
            The enterprise value over EBITDA of the stock.
        ev_to_operating_cash_flow : float
            The EV to operating cash flow of the stock.
        ev_to_free_cash_flow : float
            The EV to free cash flow of the stock.
        earnings_yield : float
            The earnings yield of the stock.
        free_cash_flow_yield : float
            The free cash flow yield of the stock.
        debt_to_equity : float
            The debt to equity of the stock.
        debt_to_assets : float
            The debt to assets of the stock.
        net_debt_to_ebitda : float
            The net debt to EBITDA of the stock.
        current_ratio : float
            The current ratio of the stock.
        interest_coverage : float
            The interest coverage of the stock.
        income_quality : float
            The income quality of the stock.
        dividend_yield : float
            The dividend yield of the stock.
        payout_ratio : float
            The payout ratio of the stock.
        sales_general_and_administrative_to_revenue : float
            The sales general and administrative to revenue of the stock.
        research_and_developement_to_revenue : float
            The research and development to revenue of the stock.
        intangibles_to_total_assets : float
            The intangibles to total assets of the stock.
        capex_to_operating_cash_flow : float
            The capex to operating cash flow of the stock.
        capex_to_revenue : float
            The capex to revenue of the stock.
        capex_to_depreciation : float
            The capex to depreciation of the stock.
        stock_based_compensation_to_revenue : float
            The stock based compensation to revenue of the stock.
        graham_number : float
            The graham number of the stock.
        roic : float
            The ROIC of the stock.
        return_on_tangible_assets : float
            The return on tangible assets of the stock.
        graham_net_net : float
            The graham net net of the stock.
        working_capital : float
            The working capital of the stock.
        tangible_asset_value : float
            The tangible asset value of the stock.
        net_current_asset_value : float
            The net current asset value of the stock.
        invested_capital : float
            The invested capital of the stock.
        average_receivables : float
            The average receivables of the stock.
        average_payables : float
            The average payables of the stock.
        average_inventory : float
            The average inventory of the stock.
        days_sales_outstanding : float
            The days sales outstanding of the stock.
        days_payables_outstanding : float
            The days payables outstanding of the stock.
        days_of_inventory_on_hand : float
            The days of inventory on hand of the stock.
        receivables_turnover : float
            The receivables turnover of the stock.
        payables_turnover : float
            The payables turnover of the stock.
        inventory_turnover : float
            The inventory turnover of the stock.
        roe : float
            The ROE of the stock.
        capex_per_share : float
            The capex per share of the stock.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/company-key-metrics-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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
        key_executive_name: Optional[str] = None,
        key_executive_title: Optional[str] = None,
        key_executive_title_since: Optional[datetime.datetime] = None,
        key_executive_year_born: Optional[datetime.datetime] = None,
        key_executive_gender: Optional[str] = None,
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Key Executives.

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.
        key_executive_name : Optional[str]
            The name of the key executive to be retrieved.
        key_executive_title : Optional[str]
            The title of the key executive to be retrieved.
        key_executive_title_since : Optional[datetime]
            The period since the position of the key executive to be retrieved.
        key_executive_year_born : Optional[datetime]
            The year born of the key executive to be retrieved.
        key_executive_gender: Optional[str]
            The gender of the key executive to be retrieved.


        Returns
        -------
        name : Optional[str]
            The name of the key executive.
        title : Optional[str]
            The title of the key executive.
        title_since : Optional[datetime]
            The title since of the key executive.
        year_born : Optional[datetime]
            The year born of the key executive.
        gender : Optional[str]
            The gender of the key executive.

        fmp
        ===

        Source: https://financialmodelingprep.com/developer/docs/#Key-Executives

        Parameter
        ---------
        key_executive_gender: Optional[str]
            The gender of the key executive.


        Returns
        -------
        Documentation not available.
        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "key_executive_name": key_executive_name,
                "key_executive_title": key_executive_title,
                "key_executive_title_since": key_executive_title_since,
                "key_executive_year_born": key_executive_year_born,
                "key_executive_gender": key_executive_gender,
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

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.


        Returns
        -------
        symbol : str
            The symbol of the company.
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

        Source: https://site.financialmodelingprep.com/developer/docs/companies-key-stats-free-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.
        include_current_quarter : bool
            Whether to include the current quarter. Default is False.
        date : Optional[dateType]
            A specific date to get data for.


        Returns
        -------
        symbol : str
            The symbol of the company.
        cik : str
            The CIK of the company.
        date : dateType
            The date of the institutional ownership.
        investors_holding : int
            The number of investors holding the stock.
        last_investors_holding : int
            The number of investors holding the stock in the last quarter.
        investors_holding_change : int
            The change in the number of investors holding the stock.
        number_of_13f_shares : int
            The number of 13F shares.
        last_number_of_13f_shares : int
            The number of 13F shares in the last quarter.
        number_of_13f_shares_change : int
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
            The change in the number of new positions.
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

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/institutional-stock-ownership-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.


        Returns
        -------
        symbol : str
            The symbol of the asset.
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

        Source: https://site.financialmodelingprep.com/developer/docs/price-target-consensus-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.


        Returns
        -------
        symbol : str
            The symbol of the asset.
        published_date : datetime
            The published date of the price target.
        news_url : str
            The news URL of the price target.
        news_title : str
            The news title of the price target.
        analyst_name : str
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

        Source: https://site.financialmodelingprep.com/developer/docs/#Price-Target

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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
        period: Literal["quarterly", "annually"] = "quarterly",
        structure: Literal["hierarchical", "flat"] = "flat",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Revenue Geographic.

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.
        period : Literal["quarterly", "annually"]
            The period of the income statement.
        structure : Literal["hierarchical", "flat"]
            The structure of the revenue geographic. Should always be flat.


        Returns
        -------
        date : date
            The date of the revenue.
        americas : Optional[int]
            The revenue of the America segment.
        europe : Optional[int]
            The revenue of the Europe segment.
        greater_china : Optional[int]
            The revenue of the Greater China segment.
        japan : Optional[int]
            The revenue of the Japan segment.
        rest_of_asia_pacific : Optional[int]
            The revenue of the Rest of Asia Pacific segment.

        fmp
        ===

        Source: https://financialmodelingprep.com/developer/docs/#Revenue-Geographic-Segmentation

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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
        period: Literal["quarterly", "annually"] = "quarterly",
        structure: Literal["hierarchical", "flat"] = "flat",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Revenue Business Line.

        Available providers: fmp,

        Standard
        ========


        Parameter
        ---------
        symbol : str
            The symbol of the company.
        period : Literal["quarterly", "annually"]
            The period of the income statement.
        structure : Literal["hierarchical", "flat"]
            The structure of the revenue business line. Should always be flat.


        Returns
        -------
        date : date
            The date of the revenue.
        data_and_service : Dict[str, int]
            The data and service of the revenue.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/sales-revenue-by-segments-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.


        Returns
        -------
        symbol : str
            The symbol of the company.
        date : dateType
            The date of the share statistics.
        free_float : float
            The free float of the company.
        float_shares : float
            The float shares of the company.
        outstanding_shares : float
            The outstanding shares of the company.
        source : str
            The source of the data.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/shares-float-api/

        Parameter
        ---------
        All fields are standardized.


        Returns
        -------
        Documentation not available.
        """
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

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.


        Returns
        -------
        date : date
            The date of the historical stock splits.
        label : str
            The label of the historical stock splits.
        numerator : float
            The numerator of the historical stock splits.
        denominator : float
            The denominator of the historical stock splits.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/historical-stock-splits-api/

        Parameter
        ---------
        All fields are standardized.
        """
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
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Earnings Call Transcript.

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the company.
        year : int
            The year of the earnings call transcript.


        Returns
        -------
        symbol : str
            The symbol of the asset.
        quarter : int
            The quarter of the earnings call transcript.
        year : int
            The year of the earnings call transcript.
        date : datetime
            The date of the earnings call transcript.
        content : str
            The content of the earnings call transcript.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/earnings-calendar-api/

        Parameter
        ---------
        All fields are standardized.
        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
                "year": year,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/stocks/fa/transcript",
            **inputs,
        ).output

        return filter_output(o)
