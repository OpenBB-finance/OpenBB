### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_equity_calendar(Container):
    """/equity/calendar
    dividend
    earnings
    ipo
    splits
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def dividend(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get historical and upcoming dividend payments. Includes dividend amount, ex-dividend and payment dates.

        Parameters
        ----------
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
            results : List[CalendarDividend]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CalendarDividend
        ----------------
        ex_dividend_date : date
            The ex-dividend date - the date on which the stock begins trading without rights to the dividend.
        symbol : str
            Symbol representing the entity requested in the data.
        amount : Optional[float]
            The dividend amount per share.
        name : Optional[str]
            Name of the entity.
        record_date : Optional[date]
            The record date of ownership for eligibility.
        payment_date : Optional[date]
            The payment date of the dividend.
        declaration_date : Optional[date]
            Declaration date of the dividend.
        adjusted_amount : Optional[float]
            The adjusted-dividend amount. (provider: fmp)
        label : Optional[str]
            Ex-dividend date formatted for display. (provider: fmp)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.calendar.dividend(provider='fmp')
        """  # noqa: E501

        return self._run(
            "/equity/calendar/dividend",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/calendar/dividend",
                        ("fmp",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def earnings(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get historical and upcoming company earnings releases. Includes earnings per share (EPS) and revenue data.

        Parameters
        ----------
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
            results : List[CalendarEarnings]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CalendarEarnings
        ----------------
        report_date : date
            The date of the earnings report.
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the entity.
        eps_previous : Optional[float]
            The earnings-per-share from the same previously reported period.
        eps_consensus : Optional[float]
            The analyst conesus earnings-per-share estimate.
        eps_actual : Optional[float]
            The actual earnings per share announced. (provider: fmp)
        revenue_actual : Optional[float]
            The actual reported revenue. (provider: fmp)
        revenue_consensus : Optional[float]
            The revenue forecast consensus. (provider: fmp)
        period_ending : Optional[date]
            The fiscal period end date. (provider: fmp)
        reporting_time : Optional[str]
            The reporting time - e.g. after market close. (provider: fmp)
        updated_date : Optional[date]
            The date the data was updated last. (provider: fmp)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.calendar.earnings(provider='fmp')
        >>> # Get earnings calendar for specific dates.
        >>> obb.equity.calendar.earnings(start_date='2024-02-01', end_date='2024-02-07', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/equity/calendar/earnings",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/calendar/earnings",
                        ("fmp",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def ipo(
        self,
        symbol: Annotated[
            Optional[str], OpenBBField(description="Symbol to get data for.")
        ] = None,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        limit: Annotated[
            Optional[int],
            OpenBBField(description="The number of data entries to return."),
        ] = 100,
        provider: Annotated[
            Optional[Literal["intrinio"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'intrinio' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get historical and upcoming initial public offerings (IPOs).

        Parameters
        ----------
        symbol : Optional[str]
            Symbol to get data for.
        start_date : Union[datetime.date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[datetime.date, None, str]
            End date of the data, in YYYY-MM-DD format.
        limit : Optional[int]
            The number of data entries to return.
        provider : Optional[Literal['intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'intrinio' if there is
            no default.
        status : Optional[Literal['upcoming', 'priced', 'withdrawn']]
            Status of the IPO. [upcoming, priced, or withdrawn] (provider: intrinio)
        min_value : Optional[int]
            Return IPOs with an offer dollar amount greater than the given amount. (provider: intrinio)
        max_value : Optional[int]
            Return IPOs with an offer dollar amount less than the given amount. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[CalendarIpo]
                Serializable results.
            provider : Optional[Literal['intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CalendarIpo
        -----------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        ipo_date : Optional[date]
            The date of the IPO, when the stock first trades on a major exchange.
        status : Optional[Literal['upcoming', 'priced', 'withdrawn']]
            The status of the IPO. Upcoming IPOs have not taken place yet but are expected to. Priced IPOs have taken place. Withdrawn IPOs were expected to take place, but were subsequently withdrawn. (provider: intrinio)
        exchange : Optional[str]
            The acronym of the stock exchange that the company is going to trade publicly on. Typically NYSE or NASDAQ. (provider: intrinio)
        offer_amount : Optional[float]
            The total dollar amount of shares offered in the IPO. Typically this is share price * share count (provider: intrinio)
        share_price : Optional[float]
            The price per share at which the IPO was offered. (provider: intrinio)
        share_price_lowest : Optional[float]
            The expected lowest price per share at which the IPO will be offered. Before an IPO is priced, companies typically provide a range of prices per share at which they expect to offer the IPO (typically available for upcoming IPOs). (provider: intrinio)
        share_price_highest : Optional[float]
            The expected highest price per share at which the IPO will be offered. Before an IPO is priced, companies typically provide a range of prices per share at which they expect to offer the IPO (typically available for upcoming IPOs). (provider: intrinio)
        share_count : Optional[int]
            The number of shares offered in the IPO. (provider: intrinio)
        share_count_lowest : Optional[int]
            The expected lowest number of shares that will be offered in the IPO. Before an IPO is priced, companies typically provide a range of shares that they expect to offer in the IPO (typically available for upcoming IPOs). (provider: intrinio)
        share_count_highest : Optional[int]
            The expected highest number of shares that will be offered in the IPO. Before an IPO is priced, companies typically provide a range of shares that they expect to offer in the IPO (typically available for upcoming IPOs). (provider: intrinio)
        announcement_url : Optional[str]
            The URL to the company's announcement of the IPO (provider: intrinio)
        sec_report_url : Optional[str]
            The URL to the company's S-1, S-1/A, F-1, or F-1/A SEC filing, which is required to be filed before an IPO takes place. (provider: intrinio)
        open_price : Optional[float]
            The opening price at the beginning of the first trading day (only available for priced IPOs). (provider: intrinio)
        close_price : Optional[float]
            The closing price at the end of the first trading day (only available for priced IPOs). (provider: intrinio)
        volume : Optional[int]
            The volume at the end of the first trading day (only available for priced IPOs). (provider: intrinio)
        day_change : Optional[float]
            The percentage change between the open price and the close price on the first trading day (only available for priced IPOs). (provider: intrinio)
        week_change : Optional[float]
            The percentage change between the open price on the first trading day and the close price approximately a week after the first trading day (only available for priced IPOs). (provider: intrinio)
        month_change : Optional[float]
            The percentage change between the open price on the first trading day and the close price approximately a month after the first trading day (only available for priced IPOs). (provider: intrinio)
        id : Optional[str]
            The Intrinio ID of the IPO. (provider: intrinio)
        company : Optional[IntrinioCompany]
            The company that is going public via the IPO. (provider: intrinio)
        security : Optional[IntrinioSecurity]
            The primary Security for the Company that is going public via the IPO (provider: intrinio)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.calendar.ipo(provider='intrinio')
        >>> # Get all IPOs available.
        >>> obb.equity.calendar.ipo(provider='intrinio')
        """  # noqa: E501

        return self._run(
            "/equity/calendar/ipo",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/calendar/ipo",
                        ("intrinio",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": limit,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def splits(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fmp"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get historical and upcoming stock split operations.

        Parameters
        ----------
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
            results : List[CalendarSplits]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CalendarSplits
        --------------
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

        Examples
        --------
        >>> from openbb import obb
        >>> obb.equity.calendar.splits(provider='fmp')
        >>> # Get stock splits calendar for specific dates.
        >>> obb.equity.calendar.splits(start_date='2024-02-01', end_date='2024-02-07', provider='fmp')
        """  # noqa: E501

        return self._run(
            "/equity/calendar/splits",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/equity/calendar/splits",
                        ("fmp",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )
