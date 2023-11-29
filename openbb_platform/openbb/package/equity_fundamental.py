### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from annotated_types import Ge
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from typing_extensions import Annotated


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
    revenue_per_geography
    revenue_per_segment
    search_attributes
    trailing_dividend_yield
    transcript
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def balance(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Optional[Literal["annual", "quarter"]],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: Annotated[
            Optional[Annotated[int, Ge(ge=0)]],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 5,
        provider: Optional[Literal["fmp", "intrinio", "polygon"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Balance Sheet. Balance sheet statement.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Optional[Literal['annual', 'quarter']]
            Time period of the data to return.
        limit : Optional[Annotated[int, Ge(ge=0)]]
            The number of data entries to return.
        provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        cik : Optional[str]
            Central Index Key (CIK) of the company. (provider: fmp)
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
            results : List[BalanceSheet]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        BalanceSheet
        ------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        cik : Optional[str]
            Central Index Key (CIK) for the requested entity.
        currency : Optional[str]
            Reporting currency.
        filling_date : Optional[date]
            Filling date.
        accepted_date : Optional[datetime]
            Accepted date.
        period : Optional[str]
            Reporting period of the statement.
        cash_and_cash_equivalents : Optional[Annotated[float, Strict(strict=True)]]
            Cash and cash equivalents
        short_term_investments : Optional[Annotated[float, Strict(strict=True)]]
            Short-term investments
        long_term_investments : Optional[Annotated[float, Strict(strict=True)]]
            Long-term investments
        inventory : Optional[Annotated[float, Strict(strict=True)]]
            Inventory
        net_receivables : Optional[Annotated[float, Strict(strict=True)]]
            Receivables, net
        marketable_securities : Optional[Annotated[float, Strict(strict=True)]]
            Marketable securities
        property_plant_equipment_net : Optional[Annotated[float, Strict(strict=True)]]
            Property, plant and equipment, net
        goodwill : Optional[Annotated[float, Strict(strict=True)]]
            Goodwill
        assets : Optional[Annotated[float, Strict(strict=True)]]
            Total assets
        current_assets : Optional[Annotated[float, Strict(strict=True)]]
            Total current assets
        other_current_assets : Optional[Annotated[float, Strict(strict=True)]]
            Other current assets
        intangible_assets : Optional[Annotated[float, Strict(strict=True)]]
            Intangible assets
        tax_assets : Optional[Annotated[float, Strict(strict=True)]]
            Accrued income taxes
        non_current_assets : Optional[Annotated[float, Strict(strict=True)]]
            Total non-current assets
        other_non_current_assets : Optional[Annotated[float, Strict(strict=True)]]
            Other non-current assets
        account_payables : Optional[Annotated[float, Strict(strict=True)]]
            Accounts payable
        tax_payables : Optional[Annotated[float, Strict(strict=True)]]
            Accrued income taxes
        deferred_revenue : Optional[Annotated[float, Strict(strict=True)]]
            Accrued income taxes, other deferred revenue
        other_assets : Optional[Annotated[float, Strict(strict=True)]]
            Other assets
        total_assets : Optional[Annotated[float, Strict(strict=True)]]
            Total assets
        long_term_debt : Optional[Annotated[float, Strict(strict=True)]]
            Long-term debt, Operating lease obligations, Long-term finance lease obligations
        short_term_debt : Optional[Annotated[float, Strict(strict=True)]]
            Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year
        liabilities : Optional[Annotated[float, Strict(strict=True)]]
            Total liabilities
        other_current_liabilities : Optional[Annotated[float, Strict(strict=True)]]
            Other current liabilities
        current_liabilities : Optional[Annotated[float, Strict(strict=True)]]
            Total current liabilities
        total_liabilities_and_total_equity : Optional[Annotated[float, Strict(strict=True)]]
            Total liabilities and total equity
        other_non_current_liabilities : Optional[Annotated[float, Strict(strict=True)]]
            Other non-current liabilities
        non_current_liabilities : Optional[Annotated[float, Strict(strict=True)]]
            Total non-current liabilities
        total_liabilities_and_stockholders_equity : Optional[Annotated[float, Strict(strict=True)]]
            Total liabilities and stockholders' equity
        other_stockholder_equity : Optional[Annotated[float, Strict(strict=True)]]
            Other stockholders equity
        total_stockholders_equity : Optional[Annotated[float, Strict(strict=True)]]
            Total stockholders' equity
        other_liabilities : Optional[Annotated[float, Strict(strict=True)]]
            Other liabilities
        total_liabilities : Optional[Annotated[float, Strict(strict=True)]]
            Total liabilities
        common_stock : Optional[Annotated[float, Strict(strict=True)]]
            Common stock
        preferred_stock : Optional[Annotated[float, Strict(strict=True)]]
            Preferred stock
        accumulated_other_comprehensive_income_loss : Optional[Annotated[float, Strict(strict=True)]]
            Accumulated other comprehensive income (loss)
        retained_earnings : Optional[Annotated[float, Strict(strict=True)]]
            Retained earnings
        minority_interest : Optional[Annotated[float, Strict(strict=True)]]
            Minority interest
        total_equity : Optional[Annotated[float, Strict(strict=True)]]
            Total equity
        calendar_year : Optional[int]
            Calendar Year (provider: fmp)
        cash_and_short_term_investments : Optional[int]
            Cash and Short Term Investments (provider: fmp)
        goodwill_and_intangible_assets : Optional[int]
            Goodwill and Intangible Assets (provider: fmp)
        deferred_revenue_non_current : Optional[int]
            Deferred Revenue Non Current (provider: fmp)
        total_investments : Optional[int]
            Total investments (provider: fmp)
        capital_lease_obligations : Optional[int]
            Capital lease obligations (provider: fmp)
        deferred_tax_liabilities_non_current : Optional[int]
            Deferred Tax Liabilities Non Current (provider: fmp)
        total_debt : Optional[int]
            Total Debt (provider: fmp)
        net_debt : Optional[int]
            Net Debt (provider: fmp)
        link : Optional[str]
            Link to the statement. (provider: fmp)
        final_link : Optional[str]
            Link to the final statement. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.balance(symbol="AAPL", period="annual", limit=5)
        """  # noqa: E501

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
        )

        return self._run(
            "/equity/fundamental/balance",
            **inputs,
        )

    @validate
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
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Balance Sheet Statement Growth. Information about the growth of the company balance sheet.

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
            extra: Dict[str, Any]
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

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/balance_growth",
            **inputs,
        )

    @validate
    def cash(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Optional[Literal["annual", "quarter"]],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: Annotated[
            Optional[Annotated[int, Ge(ge=0)]],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 5,
        provider: Optional[Literal["fmp", "intrinio", "polygon"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Cash Flow Statement. Information about the cash flow statement.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Optional[Literal['annual', 'quarter']]
            Time period of the data to return.
        limit : Optional[Annotated[int, Ge(ge=0)]]
            The number of data entries to return.
        provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        cik : Optional[str]
            Central Index Key (CIK) of the company. (provider: fmp)
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
            results : List[CashFlowStatement]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CashFlowStatement
        -----------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        period : Optional[str]
            Reporting period of the statement.
        cik : Optional[str]
            Central Index Key (CIK) for the requested entity.
        net_income : Optional[Annotated[float, Strict(strict=True)]]
            Net income.
        depreciation_and_amortization : Optional[Annotated[float, Strict(strict=True)]]
            Depreciation and amortization.
        stock_based_compensation : Optional[Annotated[float, Strict(strict=True)]]
            Stock based compensation.
        deferred_income_tax : Optional[Annotated[float, Strict(strict=True)]]
            Deferred income tax.
        other_non_cash_items : Optional[Annotated[float, Strict(strict=True)]]
            Other non-cash items.
        changes_in_operating_assets_and_liabilities : Optional[Annotated[float, Strict(strict=True)]]
            Changes in operating assets and liabilities.
        accounts_receivables : Optional[Annotated[float, Strict(strict=True)]]
            Accounts receivables.
        inventory : Optional[Annotated[float, Strict(strict=True)]]
            Inventory.
        vendor_non_trade_receivables : Optional[Annotated[float, Strict(strict=True)]]
            Vendor non-trade receivables.
        other_current_and_non_current_assets : Optional[Annotated[float, Strict(strict=True)]]
            Other current and non-current assets.
        accounts_payables : Optional[Annotated[float, Strict(strict=True)]]
            Accounts payables.
        deferred_revenue : Optional[Annotated[float, Strict(strict=True)]]
            Deferred revenue.
        other_current_and_non_current_liabilities : Optional[Annotated[float, Strict(strict=True)]]
            Other current and non-current liabilities.
        net_cash_flow_from_operating_activities : Optional[Annotated[float, Strict(strict=True)]]
            Net cash flow from operating activities.
        purchases_of_marketable_securities : Optional[Annotated[float, Strict(strict=True)]]
            Purchases of investments.
        sales_from_maturities_of_investments : Optional[Annotated[float, Strict(strict=True)]]
            Sales and maturities of investments.
        investments_in_property_plant_and_equipment : Optional[Annotated[float, Strict(strict=True)]]
            Investments in property, plant, and equipment.
        payments_from_acquisitions : Optional[Annotated[float, Strict(strict=True)]]
            Acquisitions, net of cash acquired, and other
        other_investing_activities : Optional[Annotated[float, Strict(strict=True)]]
            Other investing activities
        net_cash_flow_from_investing_activities : Optional[Annotated[float, Strict(strict=True)]]
            Net cash used for investing activities.
        taxes_paid_on_net_share_settlement : Optional[Annotated[float, Strict(strict=True)]]
            Taxes paid on net share settlement of equity awards.
        dividends_paid : Optional[Annotated[float, Strict(strict=True)]]
            Payments for dividends and dividend equivalents
        common_stock_repurchased : Optional[Annotated[float, Strict(strict=True)]]
            Payments related to repurchase of common stock
        debt_proceeds : Optional[Annotated[float, Strict(strict=True)]]
            Proceeds from issuance of term debt
        debt_repayment : Optional[Annotated[float, Strict(strict=True)]]
            Payments of long-term debt
        other_financing_activities : Optional[Annotated[float, Strict(strict=True)]]
            Other financing activities, net
        net_cash_flow_from_financing_activities : Optional[Annotated[float, Strict(strict=True)]]
            Net cash flow from financing activities.
        net_change_in_cash : Optional[Annotated[float, Strict(strict=True)]]
            Net increase (decrease) in cash, cash equivalents, and restricted cash
        reported_currency : Optional[str]
            Reported currency in the statement. (provider: fmp)
        filling_date : Optional[date]
            Filling date. (provider: fmp)
        accepted_date : Optional[datetime]
            Accepted date. (provider: fmp)
        calendar_year : Optional[int]
            Calendar year. (provider: fmp)
        change_in_working_capital : Optional[int]
            Change in working capital. (provider: fmp)
        other_working_capital : Optional[int]
            Other working capital. (provider: fmp)
        common_stock_issued : Optional[int]
            Common stock issued. (provider: fmp)
        effect_of_forex_changes_on_cash : Optional[int]
            Effect of forex changes on cash. (provider: fmp)
        cash_at_beginning_of_period : Optional[int]
            Cash at beginning of period. (provider: fmp)
        cash_at_end_of_period : Optional[int]
            Cash, cash equivalents, and restricted cash at end of period (provider: fmp)
        operating_cash_flow : Optional[int]
            Operating cash flow. (provider: fmp)
        capital_expenditure : Optional[int]
            Capital expenditure. (provider: fmp)
        free_cash_flow : Optional[int]
            Free cash flow. (provider: fmp)
        link : Optional[str]
            Link to the statement. (provider: fmp)
        final_link : Optional[str]
            Link to the final statement. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.cash(symbol="AAPL", period="annual", limit=5)
        """  # noqa: E501

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
        )

        return self._run(
            "/equity/fundamental/cash",
            **inputs,
        )

    @validate
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
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Cash Flow Statement Growth. Information about the growth of the company cash flow statement.

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
            extra: Dict[str, Any]
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

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/cash_growth",
            **inputs,
        )

    @validate
    def dividends(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Historical Dividends. Historical dividends data for a given company.

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
            results : List[HistoricalDividends]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        HistoricalDividends
        -------------------
        date : date
            The date of the data.
        label : str
            Label of the historical dividends.
        adj_dividend : float
            Adjusted dividend of the historical dividends.
        dividend : float
            Dividend of the historical dividends.
        record_date : Optional[date]
            Record date of the historical dividends.
        payment_date : Optional[date]
            Payment date of the historical dividends.
        declaration_date : Optional[date]
            Declaration date of the historical dividends.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.dividends(symbol="AAPL")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/dividends",
            **inputs,
        )

    @validate
    def employee_count(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Historical Employees. Historical number of employees.

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
            extra: Dict[str, Any]
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

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/employee_count",
            **inputs,
        )

    @validate
    def filings(
        self,
        symbol: Annotated[
            Union[str, None, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ] = None,
        form_type: Annotated[
            Optional[str],
            OpenBBCustomParameter(
                description="Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types."
            ),
        ] = None,
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Optional[Literal["fmp", "intrinio", "sec"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Company Filings. Company filings data.

        Parameters
        ----------
        symbol : Optional[str]
            Symbol to get data for.
        form_type : Optional[str]
            Filter by form type. Visit https://www.sec.gov/forms for a list of supported form types.
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
        cik : Optional[Union[str, int]]
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
            extra: Dict[str, Any]
                Extra info.

        CompanyFilings
        --------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        cik : Optional[str]
            Central Index Key (CIK) for the requested entity.
        filing_date : date
            Filing date of the SEC report.
        accepted_date : datetime
            Accepted date of the SEC report.
        report_type : str
            Type of the SEC report.
        filing_url : str
            URL to the filing page on the SEC site.
        report_url : str
            URL to the actual report on the SEC site.
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
        act : Optional[Union[str, int]]
            The SEC Act number. (provider: sec)
        items : Optional[Union[str, float]]
            The SEC Item numbers. (provider: sec)
        primary_doc_description : Optional[str]
            The description of the primary document. (provider: sec)
        primary_doc : Optional[str]
            The filename of the primary document. (provider: sec)
        accession_number : Optional[Union[str, int]]
            The accession number. (provider: sec)
        file_number : Optional[Union[str, int]]
            The file number. (provider: sec)
        film_number : Optional[Union[str, int]]
            The film number. (provider: sec)
        is_inline_xbrl : Optional[Union[str, int]]
            Whether the filing is an inline XBRL filing. (provider: sec)
        is_xbrl : Optional[Union[str, int]]
            Whether the filing is an XBRL filing. (provider: sec)
        size : Optional[Union[str, int]]
            The size of the filing. (provider: sec)
        complete_submission_url : Optional[str]
            The URL to the complete filing submission. (provider: sec)
        xml : Optional[str]
            The URL to the primary XML document. (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.filings(limit=100)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "form_type": form_type,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/filings",
            **inputs,
        )

    @validate
    def historical_attributes(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        tag: Annotated[
            str, OpenBBCustomParameter(description="Intrinio data tag ID or code.")
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
        type: Annotated[
            Optional[str],
            OpenBBCustomParameter(description="Filter by type, when applicable."),
        ] = None,
        sort: Annotated[
            Optional[Literal["asc", "desc"]],
            OpenBBCustomParameter(description="Sort order."),
        ] = "desc",
        provider: Optional[Literal["intrinio"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Fetch the historical values of a data tag from Intrinio.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        tag : str
            Intrinio data tag ID or code.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        frequency : Optional[Literal['daily', 'weekly', 'monthly', 'quarterly', 'year...
            The frequency of the data.
        limit : Optional[int]
            The number of data entries to return.
        type : Optional[str]
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
            extra: Dict[str, Any]
                Extra info.

        HistoricalAttributes
        --------------------
        date : date
            The date of the data.
        value : Optional[float]
            The value of the data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.historical_attributes(symbol="AAPL", tag="TEST_STRING", frequency="yearly", limit=1000, sort="desc")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "tag": tag,
                "start_date": start_date,
                "end_date": end_date,
                "frequency": frequency,
                "limit": limit,
                "type": type,
                "sort": sort,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/historical_attributes",
            **inputs,
        )

    @validate
    def historical_eps(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Historical earnings-per-share for a given company.

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
            extra: Dict[str, Any]
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
        actual_eps : Optional[float]
            The actual earnings per share announced. (provider: fmp)
        revenue_estimated : Optional[float]
            Estimated consensus revenue for the reporting period. (provider: fmp)
        actual_revenue : Optional[float]
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

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/historical_eps",
            **inputs,
        )

    @validate
    def historical_splits(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Historical Splits. Historical splits data.

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
            extra: Dict[str, Any]
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

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/historical_splits",
            **inputs,
        )

    @validate
    def income(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Optional[Literal["annual", "quarter"]],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: Annotated[
            Optional[Annotated[int, Ge(ge=0)]],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 5,
        provider: Optional[Literal["fmp", "intrinio", "polygon"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Income Statement. Report on a company's financial performance.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Optional[Literal['annual', 'quarter']]
            Time period of the data to return.
        limit : Optional[Annotated[int, Ge(ge=0)]]
            The number of data entries to return.
        provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        cik : Optional[str]
            The CIK of the company if no symbol is provided. (provider: fmp)
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
            provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        IncomeStatement
        ---------------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        date : date
            The date of the data. In this case, the date of the income statement.
        period : Optional[str]
            Period of the income statement.
        cik : Optional[str]
            Central Index Key (CIK) for the requested entity.
        revenue : Optional[Annotated[float, Strict(strict=True)]]
            Revenue.
        cost_of_revenue : Optional[Annotated[float, Strict(strict=True)]]
            Cost of revenue.
        gross_profit : Optional[Annotated[float, Strict(strict=True)]]
            Gross profit.
        cost_and_expenses : Optional[Annotated[float, Strict(strict=True)]]
            Cost and expenses.
        gross_profit_ratio : Optional[float]
            Gross profit ratio.
        research_and_development_expenses : Optional[Annotated[float, Strict(strict=True)]]
            Research and development expenses.
        general_and_administrative_expenses : Optional[Annotated[float, Strict(strict=True)]]
            General and administrative expenses.
        selling_and_marketing_expenses : Optional[float]
            Selling and marketing expenses.
        selling_general_and_administrative_expenses : Optional[Annotated[float, Strict(strict=True)]]
            Selling, general and administrative expenses.
        other_expenses : Optional[Annotated[float, Strict(strict=True)]]
            Other expenses.
        operating_expenses : Optional[Annotated[float, Strict(strict=True)]]
            Operating expenses.
        depreciation_and_amortization : Optional[Annotated[float, Strict(strict=True)]]
            Depreciation and amortization.
        ebit : Optional[Annotated[float, Strict(strict=True)]]
            Earnings before interest, and taxes.
        ebitda : Optional[Annotated[float, Strict(strict=True)]]
            Earnings before interest, taxes, depreciation and amortization.
        ebitda_ratio : Optional[float]
            Earnings before interest, taxes, depreciation and amortization ratio.
        operating_income : Optional[Annotated[float, Strict(strict=True)]]
            Operating income.
        operating_income_ratio : Optional[float]
            Operating income ratio.
        interest_income : Optional[Annotated[float, Strict(strict=True)]]
            Interest income.
        interest_expense : Optional[Annotated[float, Strict(strict=True)]]
            Interest expense.
        total_other_income_expenses_net : Optional[Annotated[float, Strict(strict=True)]]
            Total other income expenses net.
        income_before_tax : Optional[Annotated[float, Strict(strict=True)]]
            Income before tax.
        income_before_tax_ratio : Optional[float]
            Income before tax ratio.
        income_tax_expense : Optional[Annotated[float, Strict(strict=True)]]
            Income tax expense.
        net_income : Optional[Annotated[float, Strict(strict=True)]]
            Net income.
        net_income_ratio : Optional[float]
            Net income ratio.
        eps : Optional[float]
            Earnings per share.
        eps_diluted : Optional[float]
            Earnings per share diluted.
        weighted_average_shares_outstanding : Optional[Annotated[float, Strict(strict=True)]]
            Weighted average shares outstanding.
        weighted_average_shares_outstanding_dil : Optional[Annotated[float, Strict(strict=True)]]
            Weighted average shares outstanding diluted.
        link : Optional[str]
            Link to the income statement.
        final_link : Optional[str]
            Final link to the income statement.
        reported_currency : Optional[str]
            Reporting currency. (provider: fmp)
        filling_date : Optional[date]
            Filling date. (provider: fmp)
        accepted_date : Optional[datetime]
            Accepted date. (provider: fmp)
        calendar_year : Optional[int]
            Calendar year. (provider: fmp)
        income_loss_from_continuing_operations_before_tax : Optional[float]
            Income/Loss From Continuing Operations After Tax (provider: polygon)
        income_loss_from_continuing_operations_after_tax : Optional[float]
            Income (loss) from continuing operations after tax (provider: polygon)
        benefits_costs_expenses : Optional[float]
            Benefits, costs and expenses (provider: polygon)
        net_income_loss_attributable_to_noncontrolling_interest : Optional[int]
            Net income (loss) attributable to noncontrolling interest (provider: polygon)
        net_income_loss_attributable_to_parent : Optional[float]
            Net income (loss) attributable to parent (provider: polygon)
        net_income_loss_available_to_common_stockholders_basic : Optional[float]
            Net Income/Loss Available To Common Stockholders Basic (provider: polygon)
        participating_securities_distributed_and_undistributed_earnings_loss_basic : Optional[float]
            Participating Securities Distributed And Undistributed Earnings Loss Basic (provider: polygon)
        nonoperating_income_loss : Optional[float]
            Nonoperating Income Loss (provider: polygon)
        preferred_stock_dividends_and_other_adjustments : Optional[float]
            Preferred stock dividends and other adjustments (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.income(symbol="AAPL", period="annual", limit=5)
        """  # noqa: E501

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
        )

        return self._run(
            "/equity/fundamental/income",
            **inputs,
        )

    @validate
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
            Literal["quarter", "annual"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Income Statement Growth. Information about the growth of the company income statement.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        limit : int
            The number of data entries to return.
        period : Literal['annual', 'quarter']
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
            extra: Dict[str, Any]
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
        )

        return self._run(
            "/equity/fundamental/income_growth",
            **inputs,
        )

    @validate
    def latest_attributes(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        tag: Annotated[
            str, OpenBBCustomParameter(description="Intrinio data tag ID or code.")
        ],
        provider: Optional[Literal["intrinio"]] = None,
        **kwargs
    ) -> OBBject[Data]:
        """Fetch the latest value of a data tag from Intrinio.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        tag : str
            Intrinio data tag ID or code.
        provider : Optional[Literal['intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.

        Returns
        -------
        OBBject
            results : LatestAttributes
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        LatestAttributes
        ----------------
        value : Optional[Union[str, float]]
            The value of the data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.latest_attributes(symbol="AAPL", tag="TEST_STRING")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "tag": tag,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/latest_attributes",
            **inputs,
        )

    @validate
    def management(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Key Executives. Key executives for a given company.

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
            results : List[KeyExecutives]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        KeyExecutives
        -------------
        title : str
            Designation of the key executive.
        name : str
            Name of the key executive.
        pay : Optional[int]
            Pay of the key executive.
        currency_pay : str
            Currency of the pay.
        gender : Optional[str]
            Gender of the key executive.
        year_born : Optional[int]
            Birth year of the key executive.
        title_since : Optional[int]
            Date the tile was held since.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.management(symbol="AAPL")
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/management",
            **inputs,
        )

    @validate
    def management_compensation(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Get Executive Compensation. Information about the executive compensation for a given company.

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
            results : List[ExecutiveCompensation]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
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

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/management_compensation",
            **inputs,
        )

    @validate
    def metrics(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Optional[Literal["annual", "quarter"]],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Optional[Literal["fmp", "intrinio"]] = None,
        **kwargs
    ) -> OBBject[Union[List[Data], Data]]:
        """Key Metrics. Key metrics for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Optional[Literal['annual', 'quarter']]
            Time period of the data to return.
        limit : Optional[int]
            The number of data entries to return.
        provider : Optional[Literal['fmp', 'intrinio']]
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
            provider : Optional[Literal['fmp', 'intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
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
            Revenue per share (provider: fmp)
        net_income_per_share : Optional[float]
            Net income per share (provider: fmp)
        operating_cash_flow_per_share : Optional[float]
            Operating cash flow per share (provider: fmp)
        free_cash_flow_per_share : Optional[float]
            Free cash flow per share (provider: fmp)
        cash_per_share : Optional[float]
            Cash per share (provider: fmp)
        book_value_per_share : Optional[float]
            Book value per share (provider: fmp)
        tangible_book_value_per_share : Optional[float]
            Tangible book value per share (provider: fmp)
        shareholders_equity_per_share : Optional[float]
            Shareholders equity per share (provider: fmp)
        interest_debt_per_share : Optional[float]
            Interest debt per share (provider: fmp)
        enterprise_value : Optional[float]
            Enterprise value (provider: fmp)
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
            Debt-to-equity ratio (provider: fmp)
        debt_to_assets : Optional[float]
            Debt-to-assets ratio (provider: fmp)
        net_debt_to_ebitda : Optional[float]
            Net debt-to-EBITDA ratio (provider: fmp)
        current_ratio : Optional[float]
            Current ratio (provider: fmp)
        interest_coverage : Optional[float]
            Interest coverage (provider: fmp)
        income_quality : Optional[float]
            Income quality (provider: fmp)
        dividend_yield : Optional[float]
            Dividend yield (provider: fmp, intrinio)
        payout_ratio : Optional[float]
            Payout ratio (provider: fmp)
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
            Beta (provider: intrinio)
        volume : Optional[float]
            Volume (provider: intrinio)
        fifty_two_week_high : Optional[float]
            52 week high (provider: intrinio)
        fifty_two_week_low : Optional[float]
            52 week low (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.metrics(symbol="AAPL", period="annual", limit=100)
        """  # noqa: E501

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
        )

        return self._run(
            "/equity/fundamental/metrics",
            **inputs,
        )

    @validate
    def multiples(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Equity Valuation Multiples. Valuation multiples for a stock ticker.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        limit : Optional[int]
            The number of data entries to return.
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
            extra: Dict[str, Any]
                Extra info.

        EquityValuationMultiples
        ------------------------
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
        >>> obb.equity.fundamental.multiples(symbol="AAPL", limit=100)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/multiples",
            **inputs,
        )

    @validate
    def overview(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[Data]:
        """Company Overview. General information about a company.

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
            extra: Dict[str, Any]
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

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/overview",
            **inputs,
        )

    @validate
    def ratios(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: Annotated[
            Literal["quarter", "annual"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 12,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Extensive set of ratios over time. Financial ratios for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Literal['annual', 'quarter']
            Time period of the data to return.
        limit : int
            The number of data entries to return.
        provider : Optional[Literal['fmp']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        with_ttm : Optional[bool]
            Include trailing twelve months (TTM) data. (provider: fmp)

        Returns
        -------
        OBBject
            results : List[FinancialRatios]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        FinancialRatios
        ---------------
        symbol : str
            Symbol representing the entity requested in the data.
        date : str
            The date of the data.
        period : str
            Period of the financial ratios.
        current_ratio : Optional[float]
            Current ratio.
        quick_ratio : Optional[float]
            Quick ratio.
        cash_ratio : Optional[float]
            Cash ratio.
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
        dividend_yield_percentage : Optional[float]
            Dividend yield percentage.
        dividend_per_share : Optional[float]
            Dividend per share.
        enterprise_value_multiple : Optional[float]
            Enterprise value multiple.
        price_fair_value : Optional[float]
            Price fair value.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.ratios(symbol="AAPL", period="annual", limit=12)
        """  # noqa: E501

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
        )

        return self._run(
            "/equity/fundamental/ratios",
            **inputs,
        )

    @validate
    def revenue_per_geography(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
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
    ) -> OBBject[List[Data]]:
        """Revenue Geographic. Geographic revenue data.

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
            extra: Dict[str, Any]
                Extra info.

        RevenueGeographic
        -----------------
        date : date
            The date of the data.
        geographic_segment : int
            Day level data containing the revenue of the geographic segment.
        americas : Optional[int]
            Revenue from the the American segment.
        europe : Optional[int]
            Revenue from the the European segment.
        greater_china : Optional[int]
            Revenue from the the Greater China segment.
        japan : Optional[int]
            Revenue from the the Japan segment.
        rest_of_asia_pacific : Optional[int]
            Revenue from the the Rest of Asia Pacific segment.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.revenue_per_geography(symbol="AAPL", period="annual", structure="flat")
        """  # noqa: E501

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
        )

        return self._run(
            "/equity/fundamental/revenue_per_geography",
            **inputs,
        )

    @validate
    def revenue_per_segment(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
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
    ) -> OBBject[List[Data]]:
        """Revenue Business Line. Business line revenue data.

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
            extra: Dict[str, Any]
                Extra info.

        RevenueBusinessLine
        -------------------
        date : date
            The date of the data.
        business_line : int
            Day level data containing the revenue of the business line.

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.fundamental.revenue_per_segment(symbol="AAPL", period="annual", structure="flat")
        """  # noqa: E501

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
        )

        return self._run(
            "/equity/fundamental/revenue_per_segment",
            **inputs,
        )

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
    ) -> OBBject[List[Data]]:
        """Search Intrinio data tags.

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
            extra: Dict[str, Any]
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
        >>> obb.equity.fundamental.search_attributes(query="TEST_STRING", limit=1000)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "query": query,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/search_attributes",
            **inputs,
        )

    @validate
    def trailing_dividend_yield(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ] = None,
        provider: Optional[Literal["tiingo"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Trailing 1yr dividend yield.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
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
            extra: Dict[str, Any]
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
        >>> obb.equity.fundamental.trailing_dividend_yield()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/trailing_dividend_yield",
            **inputs,
        )

    @validate
    def transcript(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        year: Annotated[
            int,
            OpenBBCustomParameter(description="Year of the earnings call transcript."),
        ],
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Earnings Call Transcript. Earnings call transcript for a given company.

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
            extra: Dict[str, Any]
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
        >>> obb.equity.fundamental.transcript(symbol="AAPL", year=1)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "year": year,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/fundamental/transcript",
            **inputs,
        )
