### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Union

import typing_extensions
from annotated_types import Ge
from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data


class ROUTER_stocks_fa(Container):
    """/stocks/fa
    balance
    balance_growth
    cash
    cash_growth
    comp
    comsplit
    divs
    earning
    emp
    est
    filings
    income
    income_growth
    ins
    ins_own
    metrics
    mgmt
    overview
    own
    pt
    pta
    ratios
    revgeo
    revseg
    shrs
    split
    transcript
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def balance(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: typing_extensions.Annotated[
            Union[Literal["annual", "quarter"], None],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: typing_extensions.Annotated[
            Union[typing_extensions.Annotated[int, Ge(ge=0)], None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 5,
        provider: Union[Literal["fmp", "intrinio", "polygon", "yfinance"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Balance Sheet. Balance sheet statement.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Union[Literal['annual', 'quarter'], None]
            Time period of the data to return.
        limit : Union[typing_extensions.Annotated[int, Ge(ge=0)], None]
            The number of data entries to return.
        provider : Union[Literal['fmp', 'intrinio', 'polygon', 'yfinance'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        cik : Optional[Union[str]]
            Central Index Key (CIK) of the company. (provider: fmp)
        filing_date : Optional[Union[datetime.date]]
            Filing date of the financial statement. (provider: polygon)
        filing_date_lt : Optional[Union[datetime.date]]
            Filing date less than the given date. (provider: polygon)
        filing_date_lte : Optional[Union[datetime.date]]
            Filing date less than or equal to the given date. (provider: polygon)
        filing_date_gt : Optional[Union[datetime.date]]
            Filing date greater than the given date. (provider: polygon)
        filing_date_gte : Optional[Union[datetime.date]]
            Filing date greater than or equal to the given date. (provider: polygon)
        period_of_report_date : Optional[Union[datetime.date]]
            Period of report date of the financial statement. (provider: polygon)
        period_of_report_date_lt : Optional[Union[datetime.date]]
            Period of report date less than the given date. (provider: polygon)
        period_of_report_date_lte : Optional[Union[datetime.date]]
            Period of report date less than or equal to the given date. (provider: polygon)
        period_of_report_date_gt : Optional[Union[datetime.date]]
            Period of report date greater than the given date. (provider: polygon)
        period_of_report_date_gte : Optional[Union[datetime.date]]
            Period of report date greater than or equal to the given date. (provider: polygon)
        include_sources : Optional[Union[bool]]
            Whether to include the sources of the financial statement. (provider: polygon)
        order : Optional[Union[Literal['asc', 'desc']]]
            Order of the financial statement. (provider: polygon)
        sort : Optional[Union[Literal['filing_date', 'period_of_report_date']]]
            Sort of the financial statement. (provider: polygon)

        Returns
        -------
        OBBject
            results : Union[List[BalanceSheet]]
                Serializable results.
            provider : Union[Literal['fmp', 'intrinio', 'polygon', 'yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        BalanceSheet
        ------------
        symbol : Optional[Union[str]]
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        cik : Optional[Union[str]]
            Central Index Key (CIK) of the company.
        currency : Optional[Union[str]]
            Reporting currency.
        filling_date : Optional[Union[date]]
            Filling date.
        accepted_date : Optional[Union[datetime]]
            Accepted date.
        period : Optional[Union[str]]
            Reporting period of the statement.
        cash_and_cash_equivalents : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Cash and cash equivalents
        short_term_investments : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Short-term investments
        long_term_investments : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Long-term investments
        inventory : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Inventory
        net_receivables : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Receivables, net
        marketable_securities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Marketable securities
        property_plant_equipment_net : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Property, plant and equipment, net
        goodwill : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Goodwill
        assets : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total assets
        current_assets : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total current assets
        other_current_assets : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other current assets
        intangible_assets : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Intangible assets
        tax_assets : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Accrued income taxes
        non_current_assets : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total non-current assets
        other_non_current_assets : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other non-current assets
        account_payables : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Accounts payable
        tax_payables : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Accrued income taxes
        deferred_revenue : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Accrued income taxes, other deferred revenue
        other_assets : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other assets
        total_assets : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total assets
        long_term_debt : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Long-term debt, Operating lease obligations, Long-term finance lease obligations
        short_term_debt : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Short-term borrowings, Long-term debt due within one year, Operating lease obligations due within one year, Finance lease obligations due within one year
        liabilities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total liabilities
        other_current_liabilities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other current liabilities
        current_liabilities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total current liabilities
        total_liabilities_and_total_equity : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total liabilities and total equity
        other_non_current_liabilities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other non-current liabilities
        non_current_liabilities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total non-current liabilities
        total_liabilities_and_stockholders_equity : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total liabilities and stockholders' equity
        other_stockholder_equity : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other stockholders equity
        total_stockholders_equity : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total stockholders' equity
        other_liabilities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other liabilities
        total_liabilities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total liabilities
        common_stock : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Common stock
        preferred_stock : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Preferred stock
        accumulated_other_comprehensive_income_loss : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Accumulated other comprehensive income (loss)
        retained_earnings : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Retained earnings
        minority_interest : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Minority interest
        total_equity : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
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
        link : Optional[Union[str]]
            Link to the statement. (provider: fmp)
        final_link : Optional[Union[str]]
            Link to the final statement. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.balance(symbol="AAPL", period="annual", limit=5)
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
            "/stocks/fa/balance",
            **inputs,
        )

    @validate
    def balance_growth(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        limit: typing_extensions.Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Balance Sheet Statement Growth. Information about the growth of the company balance sheet.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        limit : int
            The number of data entries to return.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[BalanceSheetGrowth]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        BalanceSheetGrowth
        ------------------
        symbol : Optional[Union[str]]
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
        >>> obb.stocks.fa.balance_growth(symbol="AAPL", limit=10)
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
            "/stocks/fa/balance_growth",
            **inputs,
        )

    @validate
    def cash(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: typing_extensions.Annotated[
            Union[Literal["annual", "quarter"], None],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: typing_extensions.Annotated[
            Union[typing_extensions.Annotated[int, Ge(ge=0)], None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 5,
        provider: Union[Literal["fmp", "intrinio", "polygon", "yfinance"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Cash Flow Statement. Information about the cash flow statement.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Union[Literal['annual', 'quarter'], None]
            Time period of the data to return.
        limit : Union[typing_extensions.Annotated[int, Ge(ge=0)], None]
            The number of data entries to return.
        provider : Union[Literal['fmp', 'intrinio', 'polygon', 'yfinance'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        cik : Optional[Union[str]]
            Central Index Key (CIK) of the company. (provider: fmp)
        filing_date : Optional[Union[datetime.date]]
            Filing date of the financial statement. (provider: polygon)
        filing_date_lt : Optional[Union[datetime.date]]
            Filing date less than the given date. (provider: polygon)
        filing_date_lte : Optional[Union[datetime.date]]
            Filing date less than or equal to the given date. (provider: polygon)
        filing_date_gt : Optional[Union[datetime.date]]
            Filing date greater than the given date. (provider: polygon)
        filing_date_gte : Optional[Union[datetime.date]]
            Filing date greater than or equal to the given date. (provider: polygon)
        period_of_report_date : Optional[Union[datetime.date]]
            Period of report date of the financial statement. (provider: polygon)
        period_of_report_date_lt : Optional[Union[datetime.date]]
            Period of report date less than the given date. (provider: polygon)
        period_of_report_date_lte : Optional[Union[datetime.date]]
            Period of report date less than or equal to the given date. (provider: polygon)
        period_of_report_date_gt : Optional[Union[datetime.date]]
            Period of report date greater than the given date. (provider: polygon)
        period_of_report_date_gte : Optional[Union[datetime.date]]
            Period of report date greater than or equal to the given date. (provider: polygon)
        include_sources : Optional[Union[bool]]
            Whether to include the sources of the financial statement. (provider: polygon)
        order : Optional[Union[Literal['asc', 'desc']]]
            Order of the financial statement. (provider: polygon)
        sort : Optional[Union[Literal['filing_date', 'period_of_report_date']]]
            Sort of the financial statement. (provider: polygon)

        Returns
        -------
        OBBject
            results : Union[List[CashFlowStatement]]
                Serializable results.
            provider : Union[Literal['fmp', 'intrinio', 'polygon', 'yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CashFlowStatement
        -----------------
        symbol : Optional[Union[str]]
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        period : Optional[Union[str]]
            Reporting period of the statement.
        cik : Optional[Union[str]]
            Central Index Key (CIK) of the company.
        net_income : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Net income.
        depreciation_and_amortization : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Depreciation and amortization.
        stock_based_compensation : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Stock based compensation.
        deferred_income_tax : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Deferred income tax.
        other_non_cash_items : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other non-cash items.
        changes_in_operating_assets_and_liabilities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Changes in operating assets and liabilities.
        accounts_receivables : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Accounts receivables.
        inventory : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Inventory.
        vendor_non_trade_receivables : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Vendor non-trade receivables.
        other_current_and_non_current_assets : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other current and non-current assets.
        accounts_payables : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Accounts payables.
        deferred_revenue : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Deferred revenue.
        other_current_and_non_current_liabilities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other current and non-current liabilities.
        net_cash_flow_from_operating_activities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Net cash flow from operating activities.
        purchases_of_marketable_securities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Purchases of investments.
        sales_from_maturities_of_investments : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Sales and maturities of investments.
        investments_in_property_plant_and_equipment : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Investments in property, plant, and equipment.
        payments_from_acquisitions : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Acquisitions, net of cash acquired, and other
        other_investing_activities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other investing activities
        net_cash_flow_from_investing_activities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Net cash used for investing activities.
        taxes_paid_on_net_share_settlement : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Taxes paid on net share settlement of equity awards.
        dividends_paid : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Payments for dividends and dividend equivalents
        common_stock_repurchased : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Payments related to repurchase of common stock
        debt_proceeds : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Proceeds from issuance of term debt
        debt_repayment : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Payments of long-term debt
        other_financing_activities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other financing activities, net
        net_cash_flow_from_financing_activities : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Net cash flow from financing activities.
        net_change_in_cash : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Net increase (decrease) in cash, cash equivalents, and restricted cash
        reported_currency : Optional[Union[str]]
            Reported currency in the statement. (provider: fmp)
        filling_date : Optional[Union[date]]
            Filling date. (provider: fmp)
        accepted_date : Optional[Union[datetime]]
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
        link : Optional[Union[str]]
            Link to the statement. (provider: fmp)
        final_link : Optional[Union[str]]
            Link to the final statement. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.cash(symbol="AAPL", period="annual", limit=5)
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
            "/stocks/fa/cash",
            **inputs,
        )

    @validate
    def cash_growth(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        limit: typing_extensions.Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Cash Flow Statement Growth. Information about the growth of the company cash flow statement.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        limit : int
            The number of data entries to return.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[CashFlowStatementGrowth]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CashFlowStatementGrowth
        -----------------------
        symbol : Optional[Union[str]]
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
        >>> obb.stocks.fa.cash_growth(symbol="AAPL", limit=10)
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
            "/stocks/fa/cash_growth",
            **inputs,
        )

    @validate
    def comp(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Executive Compensation. Information about the executive compensation for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[ExecutiveCompensation]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        cik : Optional[Union[str]]
            Central Index Key (CIK) of the company.
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
        >>> obb.stocks.fa.comp(symbol="AAPL")
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
            "/stocks/fa/comp",
            **inputs,
        )

    @validate
    def comsplit(
        self,
        start_date: typing_extensions.Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="Start date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        end_date: typing_extensions.Annotated[
            Union[datetime.date, None, str],
            OpenBBCustomParameter(
                description="End date of the data, in YYYY-MM-DD format."
            ),
        ] = None,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Stock Split Calendar. Show Stock Split Calendar.

        Parameters
        ----------
        start_date : Union[datetime.date, None]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None]
            End date of the data, in YYYY-MM-DD format.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[StockSplitCalendar]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        StockSplitCalendar
        ------------------
        date : date
            The date of the data.
        label : str
            Label of the stock splits.
        symbol : str
            Symbol representing the entity requested in the data.
        numerator : float
            Numerator of the stock splits.
        denominator : float
            Denominator of the stock splits.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.comsplit()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/fa/comsplit",
            **inputs,
        )

    @validate
    def divs(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Historical Dividends. Historical dividends data for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[HistoricalDividends]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        record_date : Optional[Union[date]]
            Record date of the historical dividends.
        payment_date : Optional[Union[date]]
            Payment date of the historical dividends.
        declaration_date : Optional[Union[date]]
            Declaration date of the historical dividends.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.divs(symbol="AAPL")
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
            "/stocks/fa/divs",
            **inputs,
        )

    @validate
    def earning(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        limit: typing_extensions.Annotated[
            Union[int, None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 50,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Earnings Calendar. Earnings calendar for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        limit : Union[int, None]
            The number of data entries to return.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[EarningsCalendar]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EarningsCalendar
        ----------------
        symbol : str
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        eps : Optional[Union[float]]
            EPS of the earnings calendar.
        eps_estimated : Optional[Union[float]]
            Estimated EPS of the earnings calendar.
        time : str
            Time of the earnings calendar.
        revenue : Optional[Union[float]]
            Revenue of the earnings calendar.
        revenue_estimated : Optional[Union[float]]
            Estimated revenue of the earnings calendar.
        updated_from_date : Optional[date]
            Updated from date of the earnings calendar.
        fiscal_date_ending : date
            Fiscal date ending of the earnings calendar.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.earning(symbol="AAPL", limit=50)
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
            "/stocks/fa/earning",
            **inputs,
        )

    @validate
    def emp(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Historical Employees. Historical number of employees.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[HistoricalEmployees]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
            CIK of the company to retrieve the historical employees of.
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
        >>> obb.stocks.fa.emp(symbol="AAPL")
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
            "/stocks/fa/emp",
            **inputs,
        )

    @validate
    def est(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: typing_extensions.Annotated[
            Literal["quarter", "annual"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: typing_extensions.Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 30,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Analyst Estimates. Analyst stock recommendations.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Literal['quarter', 'annual']
            Time period of the data to return.
        limit : int
            The number of data entries to return.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[AnalystEstimates]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        AnalystEstimates
        ----------------
        symbol : str
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        estimated_revenue_low : int
            Estimated revenue low.
        estimated_revenue_high : int
            Estimated revenue high.
        estimated_revenue_avg : int
            Estimated revenue average.
        estimated_ebitda_low : int
            Estimated EBITDA low.
        estimated_ebitda_high : int
            Estimated EBITDA high.
        estimated_ebitda_avg : int
            Estimated EBITDA average.
        estimated_ebit_low : int
            Estimated EBIT low.
        estimated_ebit_high : int
            Estimated EBIT high.
        estimated_ebit_avg : int
            Estimated EBIT average.
        estimated_net_income_low : int
            Estimated net income low.
        estimated_net_income_high : int
            Estimated net income high.
        estimated_net_income_avg : int
            Estimated net income average.
        estimated_sga_expense_low : int
            Estimated SGA expense low.
        estimated_sga_expense_high : int
            Estimated SGA expense high.
        estimated_sga_expense_avg : int
            Estimated SGA expense average.
        estimated_eps_avg : float
            Estimated EPS average.
        estimated_eps_high : float
            Estimated EPS high.
        estimated_eps_low : float
            Estimated EPS low.
        number_analyst_estimated_revenue : int
            Number of analysts who estimated revenue.
        number_analysts_estimated_eps : int
            Number of analysts who estimated EPS.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.est(symbol="AAPL", period="annual", limit=30)
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
            "/stocks/fa/est",
            **inputs,
        )

    @validate
    def filings(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, None, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ] = None,
        limit: typing_extensions.Annotated[
            Union[int, None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 300,
        provider: Union[Literal["fmp", "sec"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Company Filings. Company filings data.

        Parameters
        ----------
        symbol : Union[str, None]
            Symbol to get data for.
        limit : Union[int, None]
            The number of data entries to return.
        provider : Union[Literal['fmp', 'sec'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        type : Optional[Union[Literal['1', '1-A', '1-E', '1-K', '1-N', '1-SA', '1-U', '1-Z', '10', '10-D', '10-K', '10-M', '10-Q', '11-K', '12b-25', '13F', '13H', '144', '15', '15F', '17-H', '18', '18-K', '19b-4', '19b-4(e)', '19b-7', '2-E', '20-F', '24F-2', '25', '3', '4', '40-F', '5', '6-K', '7-M', '8-A', '8-K', '8-M', '9-M', 'ABS-15G', 'ABS-EE', 'ABS DD-15E', 'ADV', 'ADV-E', 'ADV-H', 'ADV-NR', 'ADV-W', 'ATS', 'ATS-N', 'ATS-R', 'BD', 'BD-N', 'BDW', 'C', 'CA-1', 'CB', 'CFPORTAL', 'CRS', 'CUSTODY', 'D', 'F-1', 'F-10', 'F-3', 'F-4', 'F-6', 'F-7', 'F-8', 'F-80', 'F-N', 'F-X', 'ID', 'MA', 'MA-I', 'MA-NR', 'MA-W', 'MSD', 'MSDW', 'N-14', 'N-17D-1', 'N-17f-1', 'N-17f-2', 'N-18f-1', 'N-1A', 'N-2', 'N-23c-3', 'N-27D-1', 'N-3', 'N-4', 'N-5', 'N-54A', 'N-54C', 'N-6', 'N-6EI-1', 'N-6F', 'N-8A', 'N-8B-2', 'N-8B-4', 'N-8F', 'N-CEN'], Literal['1', '1-A', '1-A POS', '1-A-W', '1-E', '1-E AD', '1-K', '1-SA', '1-U', '1-Z', '1-Z-W', '10-12B', '10-12G', '10-D', '10-K', '10-KT', '10-Q', '10-QT', '11-K', '11-KT', '13F-HR', '13F-NT', '13FCONP', '144', '15-12B', '15-12G', '15-15D', '15F-12B', '15F-12G', '15F-15D', '18-12B', '18-K', '19B-4E', '2-A', '2-AF', '2-E', '20-F', '20FR12B', '20FR12G', '24F-2NT', '25', '25-NSE', '253G1', '253G2', '253G3', '253G4', '3', '305B2', '34-12H', '4', '40-17F1', '40-17F2', '40-17G', '40-17GCS', '40-202A', '40-203A', '40-206A', '40-24B2', '40-33', '40-6B', '40-8B25', '40-8F-2', '40-APP', '40-F', '40-OIP', '40FR12B', '40FR12G', '424A', '424B1', '424B2', '424B3', '424B4', '424B5', '424B7', '424B8', '424H', '425', '485APOS', '485BPOS', '485BXT', '486APOS', '486BPOS', '486BXT', '487', '497', '497AD', '497H2', '497J', '497K', '497VPI', '497VPU', '5', '6-K', '6B NTC', '6B ORDR', '8-A12B', '8-A12G', '8-K', '8-K12B', '8-K12G3', '8-K15D5', '8-M', '8F-2 NTC', '8F-2 ORDR', '9-M', 'ABS-15G', 'ABS-EE', 'ADN-MTL', 'ADV-E', 'ADV-H-C', 'ADV-H-T', 'ADV-NR', 'ANNLRPT', 'APP NTC', 'APP ORDR', 'APP WD', 'APP WDG', 'ARS', 'ATS-N', 'ATS-N-C', 'ATS-N/UA', 'AW', 'AW WD', 'C', 'C-AR', 'C-AR-W', 'C-TR', 'C-TR-W', 'C-U', 'C-U-W', 'C-W', 'CB', 'CERT', 'CERTARCA', 'CERTBATS', 'CERTCBO', 'CERTNAS', 'CERTNYS', 'CERTPAC', 'CFPORTAL', 'CFPORTAL-W', 'CORRESP', 'CT ORDER', 'D', 'DEF 14A', 'DEF 14C', 'DEFA14A', 'DEFA14C', 'DEFC14A', 'DEFC14C', 'DEFM14A', 'DEFM14C', 'DEFN14A', 'DEFR14A', 'DEFR14C', 'DEL AM', 'DFAN14A', 'DFRN14A', 'DOS', 'DOSLTR', 'DRS', 'DRSLTR', 'DSTRBRPT', 'EFFECT', 'F-1', 'F-10', 'F-10EF', 'F-10POS', 'F-1MEF', 'F-3', 'F-3ASR', 'F-3D', 'F-3DPOS', 'F-3MEF', 'F-4', 'F-4 POS', 'F-4MEF', 'F-6', 'F-6 POS', 'F-6EF', 'F-7', 'F-7 POS', 'F-8', 'F-8 POS', 'F-80', 'F-80POS', 'F-9', 'F-9 POS', 'F-N', 'F-X', 'FOCUSN', 'FWP', 'G-405', 'G-405N', 'G-FIN', 'G-FINW', 'IRANNOTICE', 'MA', 'MA-A', 'MA-I', 'MA-W', 'MSD', 'MSDCO', 'MSDW', 'N-1', 'N-14', 'N-14 8C', 'N-14MEF', 'N-18F1', 'N-1A', 'N-2', 'N-2 POSASR', 'N-23C-2', 'N-23C3A', 'N-23C3B', 'N-23C3C', 'N-2ASR', 'N-2MEF', 'N-30B-2', 'N-30D', 'N-4', 'N-5', 'N-54A', 'N-54C', 'N-6', 'N-6F', 'N-8A', 'N-8B-2', 'N-8F', 'N-8F NTC', 'N-8F ORDR', 'N-CEN', 'N-CR', 'N-CSR', 'N-CSRS', 'N-MFP', 'N-MFP1', 'N-MFP2', 'N-PX', 'N-Q', 'N-VP', 'N-VPFS', 'NO ACT', 'NPORT-EX', 'NPORT-NP', 'NPORT-P', 'NRSRO-CE', 'NRSRO-UPD', 'NSAR-A', 'NSAR-AT', 'NSAR-B', 'NSAR-BT', 'NSAR-U', 'NT 10-D', 'NT 10-K', 'NT 10-Q', 'NT 11-K', 'NT 20-F', 'NT N-CEN', 'NT N-MFP', 'NT N-MFP1', 'NT N-MFP2', 'NT NPORT-EX', 'NT NPORT-P', 'NT-NCEN', 'NT-NCSR', 'NT-NSAR', 'NTFNCEN', 'NTFNCSR', 'NTFNSAR', 'NTN 10D', 'NTN 10K', 'NTN 10Q', 'NTN 20F', 'OIP NTC', 'OIP ORDR', 'POS 8C', 'POS AM', 'POS AMI', 'POS EX', 'POS462B', 'POS462C', 'POSASR', 'PRE 14A', 'PRE 14C', 'PREC14A', 'PREC14C', 'PREM14A', 'PREM14C', 'PREN14A', 'PRER14A', 'PRER14C', 'PRRN14A', 'PX14A6G', 'PX14A6N', 'QRTLYRPT', 'QUALIF', 'REG-NR', 'REVOKED', 'RW', 'RW WD', 'S-1', 'S-11', 'S-11MEF', 'S-1MEF', 'S-20', 'S-3', 'S-3ASR', 'S-3D', 'S-3DPOS', 'S-3MEF', 'S-4', 'S-4 POS', 'S-4EF', 'S-4MEF', 'S-6', 'S-8', 'S-8 POS', 'S-B', 'S-BMEF', 'SBSE', 'SBSE-A', 'SBSE-BD', 'SBSE-C', 'SBSE-W', 'SC 13D', 'SC 13E1', 'SC 13E3', 'SC 13G', 'SC 14D9', 'SC 14F1', 'SC 14N', 'SC TO-C', 'SC TO-I', 'SC TO-T', 'SC13E4F', 'SC14D1F', 'SC14D9C', 'SC14D9F', 'SD', 'SDR', 'SE', 'SEC ACTION', 'SEC STAFF ACTION', 'SEC STAFF LETTER', 'SF-1', 'SF-3', 'SL', 'SP 15D2', 'STOP ORDER', 'SUPPL', 'T-3', 'TA-1', 'TA-2', 'TA-W', 'TACO', 'TH', 'TTW', 'UNDER', 'UPLOAD', 'WDL-REQ', 'X-17A-5']]]
            Type of the SEC filing form. (provider: fmp, sec)
        page : Optional[Union[int]]
            Page number of the results. (provider: fmp)
        cik : Optional[Union[str, int]]
            Lookup filings by Central Index Key (CIK) instead of by symbol. (provider: sec)
        use_cache : bool
            Whether or not to use cache.  If True, cache will store for one day. (provider: sec)

        Returns
        -------
        OBBject
            results : Union[List[CompanyFilings]]
                Serializable results.
            provider : Union[Literal['fmp', 'sec'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CompanyFilings
        --------------
        date : date
            The date of the data. In this case, it is the date of the filing.
        type : str
            Type of document.
        link : str
            URL to the document.
        symbol : Optional[Union[str]]
            The ticker symbol of the company. (provider: fmp)
        cik : Optional[Union[str]]
            CIK of the SEC filing. (provider: fmp)
        accepted_date : Optional[Union[datetime]]
            Accepted date of the SEC filing. (provider: fmp, sec)
        final_link : Optional[Union[str]]
            Final link of the SEC filing. (provider: fmp)
        report_date : Optional[Union[date]]
            The date of the filing. (provider: sec)
        act : Optional[Union[str, int]]
            The SEC Act number. (provider: sec)
        items : Optional[Union[str, float]]
            The SEC Item numbers. (provider: sec)
        primary_doc_description : Optional[Union[str]]
            The description of the primary document. (provider: sec)
        primary_doc : Optional[Union[str]]
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
        complete_submission_url : Optional[Union[str]]
            The URL to the complete filing submission. (provider: sec)
        filing_detail_url : Optional[Union[str]]
            The URL to the filing details. (provider: sec)
        xml : Optional[Union[str]]
            The URL to the primary XML document. (provider: sec)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.filings(limit=300)
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
            "/stocks/fa/filings",
            **inputs,
        )

    @validate
    def income(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: typing_extensions.Annotated[
            Union[Literal["annual", "quarter"], None],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: typing_extensions.Annotated[
            Union[typing_extensions.Annotated[int, Ge(ge=0)], None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 5,
        provider: Union[Literal["fmp", "intrinio", "polygon", "yfinance"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Income Statement. Report on a company's finanacial performance.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Union[Literal['annual', 'quarter'], None]
            Time period of the data to return.
        limit : Union[typing_extensions.Annotated[int, Ge(ge=0)], None]
            The number of data entries to return.
        provider : Union[Literal['fmp', 'intrinio', 'polygon', 'yfinance'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        cik : Optional[Union[str]]
            The CIK of the company if no symbol is provided. (provider: fmp)
        filing_date : Optional[Union[datetime.date]]
            Filing date of the financial statement. (provider: polygon)
        filing_date_lt : Optional[Union[datetime.date]]
            Filing date less than the given date. (provider: polygon)
        filing_date_lte : Optional[Union[datetime.date]]
            Filing date less than or equal to the given date. (provider: polygon)
        filing_date_gt : Optional[Union[datetime.date]]
            Filing date greater than the given date. (provider: polygon)
        filing_date_gte : Optional[Union[datetime.date]]
            Filing date greater than or equal to the given date. (provider: polygon)
        period_of_report_date : Optional[Union[datetime.date]]
            Period of report date of the financial statement. (provider: polygon)
        period_of_report_date_lt : Optional[Union[datetime.date]]
            Period of report date less than the given date. (provider: polygon)
        period_of_report_date_lte : Optional[Union[datetime.date]]
            Period of report date less than or equal to the given date. (provider: polygon)
        period_of_report_date_gt : Optional[Union[datetime.date]]
            Period of report date greater than the given date. (provider: polygon)
        period_of_report_date_gte : Optional[Union[datetime.date]]
            Period of report date greater than or equal to the given date. (provider: polygon)
        include_sources : Optional[Union[bool]]
            Whether to include the sources of the financial statement. (provider: polygon)
        order : Optional[Union[Literal['asc', 'desc']]]
            Order of the financial statement. (provider: polygon)
        sort : Optional[Union[Literal['filing_date', 'period_of_report_date']]]
            Sort of the financial statement. (provider: polygon)

        Returns
        -------
        OBBject
            results : Union[List[IncomeStatement]]
                Serializable results.
            provider : Union[Literal['fmp', 'intrinio', 'polygon', 'yfinance'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        IncomeStatement
        ---------------
        symbol : Optional[Union[str]]
            Symbol representing the entity requested in the data.
        date : date
            The date of the data. In this case, the date of the income statement.
        period : Optional[Union[str]]
            Period of the income statement.
        cik : Optional[Union[str]]
            Central Index Key.
        revenue : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Revenue.
        cost_of_revenue : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Cost of revenue.
        gross_profit : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Gross profit.
        cost_and_expenses : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Cost and expenses.
        gross_profit_ratio : Optional[Union[float]]
            Gross profit ratio.
        research_and_development_expenses : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Research and development expenses.
        general_and_administrative_expenses : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            General and administrative expenses.
        selling_and_marketing_expenses : Optional[Union[float]]
            Selling and marketing expenses.
        selling_general_and_administrative_expenses : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Selling, general and administrative expenses.
        other_expenses : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Other expenses.
        operating_expenses : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Operating expenses.
        depreciation_and_amortization : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Depreciation and amortization.
        ebitda : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Earnings before interest, taxes, depreciation and amortization.
        ebitda_ratio : Optional[Union[float]]
            Earnings before interest, taxes, depreciation and amortization ratio.
        operating_income : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Operating income.
        operating_income_ratio : Optional[Union[float]]
            Operating income ratio.
        interest_income : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Interest income.
        interest_expense : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Interest expense.
        total_other_income_expenses_net : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Total other income expenses net.
        income_before_tax : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Income before tax.
        income_before_tax_ratio : Optional[Union[float]]
            Income before tax ratio.
        income_tax_expense : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Income tax expense.
        net_income : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Net income.
        net_income_ratio : Optional[Union[float]]
            Net income ratio.
        eps : Optional[Union[float]]
            Earnings per share.
        eps_diluted : Optional[Union[float]]
            Earnings per share diluted.
        weighted_average_shares_outstanding : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Weighted average shares outstanding.
        weighted_average_shares_outstanding_dil : Optional[Union[typing_extensions.Annotated[float, Strict(strict=True)]]]
            Weighted average shares outstanding diluted.
        link : Optional[Union[str]]
            Link to the income statement.
        final_link : Optional[Union[str]]
            Final link to the income statement.
        reported_currency : Optional[Union[str]]
            Reporting currency. (provider: fmp)
        filling_date : Optional[Union[date]]
            Filling date. (provider: fmp)
        accepted_date : Optional[Union[datetime]]
            Accepted date. (provider: fmp)
        calendar_year : Optional[Union[int]]
            Calendar year. (provider: fmp)
        income_loss_from_continuing_operations_before_tax : Optional[Union[float]]
            Income/Loss From Continuing Operations After Tax (provider: polygon)
        income_loss_from_continuing_operations_after_tax : Optional[Union[float]]
            Income (loss) from continuing operations after tax (provider: polygon)
        benefits_costs_expenses : Optional[Union[float]]
            Benefits, costs and expenses (provider: polygon)
        net_income_loss_attributable_to_noncontrolling_interest : Optional[int]
            Net income (loss) attributable to noncontrolling interest (provider: polygon)
        net_income_loss_attributable_to_parent : Optional[Union[float]]
            Net income (loss) attributable to parent (provider: polygon)
        net_income_loss_available_to_common_stockholders_basic : Optional[Union[float]]
            Net Income/Loss Available To Common Stockholders Basic (provider: polygon)
        participating_securities_distributed_and_undistributed_earnings_loss_basic : Optional[Union[float]]
            Participating Securities Distributed And Undistributed Earnings Loss Basic (provider: polygon)
        nonoperating_income_loss : Optional[Union[float]]
            Nonoperating Income Loss (provider: polygon)
        preferred_stock_dividends_and_other_adjustments : Optional[Union[float]]
            Preferred stock dividends and other adjustments (provider: polygon)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.income(symbol="AAPL", period="annual", limit=5)
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
            "/stocks/fa/income",
            **inputs,
        )

    @validate
    def income_growth(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        limit: typing_extensions.Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 10,
        period: typing_extensions.Annotated[
            Literal["annual", "quarter"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        provider: Union[Literal["fmp"], None] = None,
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
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[IncomeStatementGrowth]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        IncomeStatementGrowth
        ---------------------
        symbol : Optional[Union[str]]
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
        >>> obb.stocks.fa.income_growth(symbol="AAPL", limit=10, period="annual")
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
            "/stocks/fa/income_growth",
            **inputs,
        )

    @validate
    def ins(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        transaction_type: typing_extensions.Annotated[
            Union[
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
                ],
                str,
                None,
            ],
            OpenBBCustomParameter(description="Type of the transaction."),
        ] = ["P-Purchase"],
        limit: typing_extensions.Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Stock Insider Trading. Information about insider trading.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        transaction_type : Union[List[Literal['A-Award', 'C-Conversion', 'D-Return', ...
            Type of the transaction.
        limit : int
            The number of data entries to return.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[StockInsiderTrading]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        StockInsiderTrading
        -------------------
        symbol : str
            Symbol representing the entity requested in the data.
        filing_date : datetime
            Filing date of the stock insider trading.
        transaction_date : date
            Transaction date of the stock insider trading.
        reporting_cik : int
            Reporting CIK of the stock insider trading.
        transaction_type : str
            Transaction type of the stock insider trading.
        securities_owned : int
            Securities owned of the stock insider trading.
        company_cik : int
            Company CIK of the stock insider trading.
        reporting_name : str
            Reporting name of the stock insider trading.
        type_of_owner : str
            Type of owner of the stock insider trading.
        acquisition_or_disposition : Optional[Union[str]]
            Acquisition or disposition of the stock insider trading.
        form_type : str
            Form type of the stock insider trading.
        securities_transacted : float
            Securities transacted of the stock insider trading.
        price : Optional[Union[float]]
            Price of the stock insider trading.
        security_name : str
            Security name of the stock insider trading.
        link : str
            Link of the stock insider trading.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.ins(symbol="AAPL", transaction_type=['P-Purchase'], limit=100)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "transaction_type": transaction_type,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/stocks/fa/ins",
            **inputs,
        )

    @validate
    def ins_own(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        include_current_quarter: typing_extensions.Annotated[
            Union[bool, None],
            OpenBBCustomParameter(description="Include current quarter data."),
        ] = False,
        date: typing_extensions.Annotated[
            Union[datetime.date, None],
            OpenBBCustomParameter(description="A specific date to get data for."),
        ] = None,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Institutional Ownership. Institutional ownership data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        include_current_quarter : Union[bool, None]
            Include current quarter data.
        date : Union[datetime.date, None]
            A specific date to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[InstitutionalOwnership]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        InstitutionalOwnership
        ----------------------
        symbol : str
            Symbol representing the entity requested in the data.
        cik : Optional[Union[str]]
            CIK of the company.
        date : date
            The date of the data.
        investors_holding : int
            Number of investors holding the stock.
        last_investors_holding : int
            Number of investors holding the stock in the last quarter.
        investors_holding_change : int
            Change in the number of investors holding the stock.
        number_of_13f_shares : Optional[int]
            Number of 13F shares.
        last_number_of_13f_shares : Optional[int]
            Number of 13F shares in the last quarter.
        number_of_13f_shares_change : Optional[int]
            Change in the number of 13F shares.
        total_invested : float
            Total amount invested.
        last_total_invested : float
            Total amount invested in the last quarter.
        total_invested_change : float
            Change in the total amount invested.
        ownership_percent : float
            Ownership percent.
        last_ownership_percent : float
            Ownership percent in the last quarter.
        ownership_percent_change : float
            Change in the ownership percent.
        new_positions : int
            Number of new positions.
        last_new_positions : int
            Number of new positions in the last quarter.
        new_positions_change : int
            Change in the number of new positions.
        increased_positions : int
            Number of increased positions.
        last_increased_positions : int
            Number of increased positions in the last quarter.
        increased_positions_change : int
            Change in the number of increased positions.
        closed_positions : int
            Number of closed positions.
        last_closed_positions : int
            Number of closed positions in the last quarter.
        closed_positions_change : int
            Change in the number of closed positions.
        reduced_positions : int
            Number of reduced positions.
        last_reduced_positions : int
            Number of reduced positions in the last quarter.
        reduced_positions_change : int
            Change in the number of reduced positions.
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
            Put-call ratio, which is the ratio of the total number of put options to call options traded on the specified date.
        last_put_call_ratio : float
            Put-call ratio on the previous reporting date.
        put_call_ratio_change : float
            Change in the put-call ratio between the current and previous reporting dates.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.ins_own(symbol="AAPL")
        """  # noqa: E501

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
        )

        return self._run(
            "/stocks/fa/ins_own",
            **inputs,
        )

    @validate
    def metrics(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: typing_extensions.Annotated[
            Union[Literal["annual", "quarter"], None],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: typing_extensions.Annotated[
            Union[int, None],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Key Metrics. Key metrics for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        period : Union[Literal['annual', 'quarter'], None]
            Time period of the data to return.
        limit : Union[int, None]
            The number of data entries to return.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        with_ttm : Optional[Union[bool]]
            Include trailing twelve months (TTM) data. (provider: fmp)

        Returns
        -------
        OBBject
            results : Union[List[KeyMetrics]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        KeyMetrics
        ----------
        symbol : Optional[Union[str]]
            Symbol representing the entity requested in the data.
        date : date
            The date of the data.
        period : str
            Period of the data.
        revenue_per_share : Optional[Union[float]]
            Revenue per share
        net_income_per_share : Optional[Union[float]]
            Net income per share
        operating_cash_flow_per_share : Optional[Union[float]]
            Operating cash flow per share
        free_cash_flow_per_share : Optional[Union[float]]
            Free cash flow per share
        cash_per_share : Optional[Union[float]]
            Cash per share
        book_value_per_share : Optional[Union[float]]
            Book value per share
        tangible_book_value_per_share : Optional[Union[float]]
            Tangible book value per share
        shareholders_equity_per_share : Optional[Union[float]]
            Shareholders equity per share
        interest_debt_per_share : Optional[Union[float]]
            Interest debt per share
        market_cap : Optional[Union[float]]
            Market capitalization
        enterprise_value : Optional[Union[float]]
            Enterprise value
        pe_ratio : Optional[Union[float]]
            Price-to-earnings ratio (P/E ratio)
        price_to_sales_ratio : Optional[Union[float]]
            Price-to-sales ratio
        pocf_ratio : Optional[Union[float]]
            Price-to-operating cash flow ratio
        pfcf_ratio : Optional[Union[float]]
            Price-to-free cash flow ratio
        pb_ratio : Optional[Union[float]]
            Price-to-book ratio
        ptb_ratio : Optional[Union[float]]
            Price-to-tangible book ratio
        ev_to_sales : Optional[Union[float]]
            Enterprise value-to-sales ratio
        enterprise_value_over_ebitda : Optional[Union[float]]
            Enterprise value-to-EBITDA ratio
        ev_to_operating_cash_flow : Optional[Union[float]]
            Enterprise value-to-operating cash flow ratio
        ev_to_free_cash_flow : Optional[Union[float]]
            Enterprise value-to-free cash flow ratio
        earnings_yield : Optional[Union[float]]
            Earnings yield
        free_cash_flow_yield : Optional[Union[float]]
            Free cash flow yield
        debt_to_equity : Optional[Union[float]]
            Debt-to-equity ratio
        debt_to_assets : Optional[Union[float]]
            Debt-to-assets ratio
        net_debt_to_ebitda : Optional[Union[float]]
            Net debt-to-EBITDA ratio
        current_ratio : Optional[Union[float]]
            Current ratio
        interest_coverage : Optional[Union[float]]
            Interest coverage
        income_quality : Optional[Union[float]]
            Income quality
        dividend_yield : Optional[Union[float]]
            Dividend yield
        payout_ratio : Optional[Union[float]]
            Payout ratio
        sales_general_and_administrative_to_revenue : Optional[Union[float]]
            Sales general and administrative expenses-to-revenue ratio
        research_and_development_to_revenue : Optional[Union[float]]
            Research and development expenses-to-revenue ratio
        intangibles_to_total_assets : Optional[Union[float]]
            Intangibles-to-total assets ratio
        capex_to_operating_cash_flow : Optional[Union[float]]
            Capital expenditures-to-operating cash flow ratio
        capex_to_revenue : Optional[Union[float]]
            Capital expenditures-to-revenue ratio
        capex_to_depreciation : Optional[Union[float]]
            Capital expenditures-to-depreciation ratio
        stock_based_compensation_to_revenue : Optional[Union[float]]
            Stock-based compensation-to-revenue ratio
        graham_number : Optional[Union[float]]
            Graham number
        roic : Optional[Union[float]]
            Return on invested capital
        return_on_tangible_assets : Optional[Union[float]]
            Return on tangible assets
        graham_net_net : Optional[Union[float]]
            Graham net-net working capital
        working_capital : Optional[Union[float]]
            Working capital
        tangible_asset_value : Optional[Union[float]]
            Tangible asset value
        net_current_asset_value : Optional[Union[float]]
            Net current asset value
        invested_capital : Optional[Union[float]]
            Invested capital
        average_receivables : Optional[Union[float]]
            Average receivables
        average_payables : Optional[Union[float]]
            Average payables
        average_inventory : Optional[Union[float]]
            Average inventory
        days_sales_outstanding : Optional[Union[float]]
            Days sales outstanding
        days_payables_outstanding : Optional[Union[float]]
            Days payables outstanding
        days_of_inventory_on_hand : Optional[Union[float]]
            Days of inventory on hand
        receivables_turnover : Optional[Union[float]]
            Receivables turnover
        payables_turnover : Optional[Union[float]]
            Payables turnover
        inventory_turnover : Optional[Union[float]]
            Inventory turnover
        roe : Optional[Union[float]]
            Return on equity
        capex_per_share : Optional[Union[float]]
            Capital expenditures per share
        calendar_year : Optional[int]
            Calendar year. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.metrics(symbol="AAPL", period="annual", limit=100)
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
            "/stocks/fa/metrics",
            **inputs,
        )

    @validate
    def mgmt(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Key Executives. Key executives for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[KeyExecutives]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        gender : Optional[Union[str]]
            Gender of the key executive.
        year_born : Optional[int]
            Birth year of the key executive.
        title_since : Optional[int]
            Date the tile was held since.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.mgmt(symbol="AAPL")
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
            "/stocks/fa/mgmt",
            **inputs,
        )

    @validate
    def overview(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[Data]:
        """Company Overview. General information about a company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[CompanyOverview]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        price : Optional[Union[float]]
            Price of the company.
        beta : Optional[Union[float]]
            Beta of the company.
        vol_avg : Optional[int]
            Volume average of the company.
        mkt_cap : Optional[int]
            Market capitalization of the company.
        last_div : Optional[Union[float]]
            Last dividend of the company.
        range : Optional[Union[str]]
            Range of the company.
        changes : Optional[Union[float]]
            Changes of the company.
        company_name : Optional[Union[str]]
            Company name of the company.
        currency : Optional[Union[str]]
            Currency of the company.
        cik : Optional[Union[str]]
            CIK of the company.
        isin : Optional[Union[str]]
            ISIN of the company.
        cusip : Optional[Union[str]]
            CUSIP of the company.
        exchange : Optional[Union[str]]
            Exchange of the company.
        exchange_short_name : Optional[Union[str]]
            Exchange short name of the company.
        industry : Optional[Union[str]]
            Industry of the company.
        website : Optional[Union[str]]
            Website of the company.
        description : Optional[Union[str]]
            Description of the company.
        ceo : Optional[Union[str]]
            CEO of the company.
        sector : Optional[Union[str]]
            Sector of the company.
        country : Optional[Union[str]]
            Country of the company.
        full_time_employees : Optional[Union[str]]
            Full time employees of the company.
        phone : Optional[Union[str]]
            Phone of the company.
        address : Optional[Union[str]]
            Address of the company.
        city : Optional[Union[str]]
            City of the company.
        state : Optional[Union[str]]
            State of the company.
        zip : Optional[Union[str]]
            Zip of the company.
        dcf_diff : Optional[Union[float]]
            Discounted cash flow difference of the company.
        dcf : Optional[Union[float]]
            Discounted cash flow of the company.
        image : Optional[Union[str]]
            Image of the company.
        ipo_date : Optional[Union[date]]
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
        >>> obb.stocks.fa.overview(symbol="AAPL")
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
            "/stocks/fa/overview",
            **inputs,
        )

    @validate
    def own(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        date: typing_extensions.Annotated[
            Union[datetime.date, None],
            OpenBBCustomParameter(description="A specific date to get data for."),
        ] = None,
        page: typing_extensions.Annotated[
            Union[int, None],
            OpenBBCustomParameter(description="Page number of the data to fetch."),
        ] = 0,
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Stock Ownership. Information about the company ownership.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        date : Union[datetime.date, None]
            A specific date to get data for.
        page : Union[int, None]
            Page number of the data to fetch.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[StockOwnership]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        StockOwnership
        --------------
        date : date
            The date of the data.
        cik : int
            Cik of the stock ownership.
        filing_date : date
            Filing date of the stock ownership.
        investor_name : str
            Investor name of the stock ownership.
        symbol : str
            Symbol representing the entity requested in the data.
        security_name : str
            Security name of the stock ownership.
        type_of_security : str
            Type of security of the stock ownership.
        security_cusip : str
            Security cusip of the stock ownership.
        shares_type : str
            Shares type of the stock ownership.
        put_call_share : str
            Put call share of the stock ownership.
        investment_discretion : str
            Investment discretion of the stock ownership.
        industry_title : str
            Industry title of the stock ownership.
        weight : float
            Weight of the stock ownership.
        last_weight : float
            Last weight of the stock ownership.
        change_in_weight : float
            Change in weight of the stock ownership.
        change_in_weight_percentage : float
            Change in weight percentage of the stock ownership.
        market_value : int
            Market value of the stock ownership.
        last_market_value : int
            Last market value of the stock ownership.
        change_in_market_value : int
            Change in market value of the stock ownership.
        change_in_market_value_percentage : float
            Change in market value percentage of the stock ownership.
        shares_number : int
            Shares number of the stock ownership.
        last_shares_number : int
            Last shares number of the stock ownership.
        change_in_shares_number : float
            Change in shares number of the stock ownership.
        change_in_shares_number_percentage : float
            Change in shares number percentage of the stock ownership.
        quarter_end_price : float
            Quarter end price of the stock ownership.
        avg_price_paid : float
            Average price paid of the stock ownership.
        is_new : bool
            Is the stock ownership new.
        is_sold_out : bool
            Is the stock ownership sold out.
        ownership : float
            How much is the ownership.
        last_ownership : float
            Last ownership amount.
        change_in_ownership : float
            Change in ownership amount.
        change_in_ownership_percentage : float
            Change in ownership percentage.
        holding_period : int
            Holding period of the stock ownership.
        first_added : date
            First added date of the stock ownership.
        performance : float
            Performance of the stock ownership.
        performance_percentage : float
            Performance percentage of the stock ownership.
        last_performance : float
            Last performance of the stock ownership.
        change_in_performance : float
            Change in performance of the stock ownership.
        is_counted_for_performance : bool
            Is the stock ownership counted for performance.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.own(symbol="AAPL")
        """  # noqa: E501

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
        )

        return self._run(
            "/stocks/fa/own",
            **inputs,
        )

    @validate
    def pt(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[Data]:
        """Price Target Consensus. Price target consensus data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[PriceTargetConsensus]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        PriceTargetConsensus
        --------------------
        symbol : str
            Symbol representing the entity requested in the data.
        target_high : Optional[Union[float]]
            High target of the price target consensus.
        target_low : Optional[Union[float]]
            Low target of the price target consensus.
        target_consensus : Optional[Union[float]]
            Consensus target of the price target consensus.
        target_median : Optional[Union[float]]
            Median target of the price target consensus.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.pt(symbol="AAPL")
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
            "/stocks/fa/pt",
            **inputs,
        )

    @validate
    def pta(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Price Target. Price target data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        with_grade : bool
            Include upgrades and downgrades in the response. (provider: fmp)

        Returns
        -------
        OBBject
            results : Union[List[PriceTarget]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        PriceTarget
        -----------
        symbol : str
            Symbol representing the entity requested in the data.
        published_date : datetime
            Published date of the price target.
        news_url : Optional[Union[str]]
            News URL of the price target.
        news_title : Optional[Union[str]]
            News title of the price target.
        analyst_name : Optional[Union[str]]
            Analyst name.
        analyst_company : Optional[Union[str]]
            Analyst company.
        price_target : Optional[Union[float]]
            Price target.
        adj_price_target : Optional[Union[float]]
            Adjusted price target.
        price_when_posted : Optional[Union[float]]
            Price when posted.
        news_publisher : Optional[Union[str]]
            News publisher of the price target.
        news_base_url : Optional[Union[str]]
            News base URL of the price target.
        new_grade : Optional[Union[str]]
            New grade (provider: fmp)
        previous_grade : Optional[Union[str]]
            Previous grade (provider: fmp)
        grading_company : Optional[Union[str]]
            Grading company (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.pta(symbol="AAPL")
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
            "/stocks/fa/pta",
            **inputs,
        )

    @validate
    def ratios(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: typing_extensions.Annotated[
            Literal["annual", "quarter"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        limit: typing_extensions.Annotated[
            int,
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 12,
        provider: Union[Literal["fmp"], None] = None,
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
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        with_ttm : Optional[Union[bool]]
            Include trailing twelve months (TTM) data. (provider: fmp)

        Returns
        -------
        OBBject
            results : Union[List[FinancialRatios]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        current_ratio : Optional[Union[float]]
            Current ratio.
        quick_ratio : Optional[Union[float]]
            Quick ratio.
        cash_ratio : Optional[Union[float]]
            Cash ratio.
        days_of_sales_outstanding : Optional[Union[float]]
            Days of sales outstanding.
        days_of_inventory_outstanding : Optional[Union[float]]
            Days of inventory outstanding.
        operating_cycle : Optional[Union[float]]
            Operating cycle.
        days_of_payables_outstanding : Optional[Union[float]]
            Days of payables outstanding.
        cash_conversion_cycle : Optional[Union[float]]
            Cash conversion cycle.
        gross_profit_margin : Optional[Union[float]]
            Gross profit margin.
        operating_profit_margin : Optional[Union[float]]
            Operating profit margin.
        pretax_profit_margin : Optional[Union[float]]
            Pretax profit margin.
        net_profit_margin : Optional[Union[float]]
            Net profit margin.
        effective_tax_rate : Optional[Union[float]]
            Effective tax rate.
        return_on_assets : Optional[Union[float]]
            Return on assets.
        return_on_equity : Optional[Union[float]]
            Return on equity.
        return_on_capital_employed : Optional[Union[float]]
            Return on capital employed.
        net_income_per_ebt : Optional[Union[float]]
            Net income per EBT.
        ebt_per_ebit : Optional[Union[float]]
            EBT per EBIT.
        ebit_per_revenue : Optional[Union[float]]
            EBIT per revenue.
        debt_ratio : Optional[Union[float]]
            Debt ratio.
        debt_equity_ratio : Optional[Union[float]]
            Debt equity ratio.
        long_term_debt_to_capitalization : Optional[Union[float]]
            Long term debt to capitalization.
        total_debt_to_capitalization : Optional[Union[float]]
            Total debt to capitalization.
        interest_coverage : Optional[Union[float]]
            Interest coverage.
        cash_flow_to_debt_ratio : Optional[Union[float]]
            Cash flow to debt ratio.
        company_equity_multiplier : Optional[Union[float]]
            Company equity multiplier.
        receivables_turnover : Optional[Union[float]]
            Receivables turnover.
        payables_turnover : Optional[Union[float]]
            Payables turnover.
        inventory_turnover : Optional[Union[float]]
            Inventory turnover.
        fixed_asset_turnover : Optional[Union[float]]
            Fixed asset turnover.
        asset_turnover : Optional[Union[float]]
            Asset turnover.
        operating_cash_flow_per_share : Optional[Union[float]]
            Operating cash flow per share.
        free_cash_flow_per_share : Optional[Union[float]]
            Free cash flow per share.
        cash_per_share : Optional[Union[float]]
            Cash per share.
        payout_ratio : Optional[Union[float]]
            Payout ratio.
        operating_cash_flow_sales_ratio : Optional[Union[float]]
            Operating cash flow sales ratio.
        free_cash_flow_operating_cash_flow_ratio : Optional[Union[float]]
            Free cash flow operating cash flow ratio.
        cash_flow_coverage_ratios : Optional[Union[float]]
            Cash flow coverage ratios.
        short_term_coverage_ratios : Optional[Union[float]]
            Short term coverage ratios.
        capital_expenditure_coverage_ratio : Optional[Union[float]]
            Capital expenditure coverage ratio.
        dividend_paid_and_capex_coverage_ratio : Optional[Union[float]]
            Dividend paid and capex coverage ratio.
        dividend_payout_ratio : Optional[Union[float]]
            Dividend payout ratio.
        price_book_value_ratio : Optional[Union[float]]
            Price book value ratio.
        price_to_book_ratio : Optional[Union[float]]
            Price to book ratio.
        price_to_sales_ratio : Optional[Union[float]]
            Price to sales ratio.
        price_earnings_ratio : Optional[Union[float]]
            Price earnings ratio.
        price_to_free_cash_flows_ratio : Optional[Union[float]]
            Price to free cash flows ratio.
        price_to_operating_cash_flows_ratio : Optional[Union[float]]
            Price to operating cash flows ratio.
        price_cash_flow_ratio : Optional[Union[float]]
            Price cash flow ratio.
        price_earnings_to_growth_ratio : Optional[Union[float]]
            Price earnings to growth ratio.
        price_sales_ratio : Optional[Union[float]]
            Price sales ratio.
        dividend_yield : Optional[Union[float]]
            Dividend yield.
        enterprise_value_multiple : Optional[Union[float]]
            Enterprise value multiple.
        price_fair_value : Optional[Union[float]]
            Price fair value.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.ratios(symbol="AAPL", period="annual", limit=12)
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
            "/stocks/fa/ratios",
            **inputs,
        )

    @validate
    def revgeo(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: typing_extensions.Annotated[
            Literal["quarter", "annual"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        structure: typing_extensions.Annotated[
            Literal["hierarchical", "flat"],
            OpenBBCustomParameter(description="Structure of the returned data."),
        ] = "flat",
        provider: Union[Literal["fmp"], None] = None,
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
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[RevenueGeographic]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        geographic_segment : Dict[str, int]
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
        >>> obb.stocks.fa.revgeo(symbol="AAPL", period="annual", structure="flat")
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
            "/stocks/fa/revgeo",
            **inputs,
        )

    @validate
    def revseg(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        period: typing_extensions.Annotated[
            Literal["quarter", "annual"],
            OpenBBCustomParameter(description="Time period of the data to return."),
        ] = "annual",
        structure: typing_extensions.Annotated[
            Literal["hierarchical", "flat"],
            OpenBBCustomParameter(description="Structure of the returned data."),
        ] = "flat",
        provider: Union[Literal["fmp"], None] = None,
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
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[RevenueBusinessLine]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        business_line : Dict[str, int]
            Day level data containing the revenue of the business line.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.revseg(symbol="AAPL", period="annual", structure="flat")
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
            "/stocks/fa/revseg",
            **inputs,
        )

    @validate
    def shrs(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Share Statistics. Share statistics for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[ShareStatistics]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        ShareStatistics
        ---------------
        symbol : str
            Symbol representing the entity requested in the data.
        date : Optional[Union[date]]
            The date of the data.
        free_float : Optional[Union[float]]
            Percentage of unrestricted shares of a publicly-traded company.
        float_shares : Optional[Union[float]]
            Number of shares available for trading by the general public.
        outstanding_shares : Optional[Union[float]]
            Total number of shares of a publicly-traded company.
        source : Optional[Union[str]]
            Source of the received data.

        Example
        -------
        >>> from openbb import obb
        >>> obb.stocks.fa.shrs(symbol="AAPL")
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
            "/stocks/fa/shrs",
            **inputs,
        )

    @validate
    def split(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Historical Stock Splits. Historical stock splits data.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[HistoricalStockSplits]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        HistoricalStockSplits
        ---------------------
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
        >>> obb.stocks.fa.split(symbol="AAPL")
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
            "/stocks/fa/split",
            **inputs,
        )

    @validate
    def transcript(
        self,
        symbol: typing_extensions.Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        year: typing_extensions.Annotated[
            int,
            OpenBBCustomParameter(description="Year of the earnings call transcript."),
        ],
        provider: Union[Literal["fmp"], None] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Earnings Call Transcript. Earnings call transcript for a given company.

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        year : int
            Year of the earnings call transcript.
        provider : Union[Literal['fmp'], None]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : Union[List[EarningsCallTranscript]]
                Serializable results.
            provider : Union[Literal['fmp'], None]
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
        >>> obb.stocks.fa.transcript(symbol="AAPL", year=1)
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
            "/stocks/fa/transcript",
            **inputs,
        )
