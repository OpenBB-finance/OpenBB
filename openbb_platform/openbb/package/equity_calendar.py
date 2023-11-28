### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data
from typing_extensions import Annotated


class ROUTER_equity_calendar(Container):
    """/equity/calendar
    dividend
    earnings
    ipo
    split
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate
    def dividend(
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
        provider: Optional[Literal["fmp", "intrinio"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Upcoming and Historical Dividend Calendar.

        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'intrinio']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        symbol : Optional[str]
            Symbol to get data for. (provider: intrinio)
        limit : Optional[int]
            The number of data entries to return. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[CalendarDividend]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        CalendarDividend
        ----------------
        date : date
            The date of the data. (Ex-Dividend)
        symbol : str
            Symbol representing the entity requested in the data.
        amount : Optional[float]
            Dividend amount, per-share.
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
        factor : Optional[float]
            factor by which to multiply stock prices before this date, in order to calculate historically-adjusted stock prices. (provider: intrinio)
        dividend_currency : Optional[str]
            The currency of the dividend. (provider: intrinio)
        split_ratio : Optional[float]
            The ratio of the stock split, if a stock split occurred. (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.calendar.dividend()
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
            "/equity/calendar/dividend",
            **inputs,
        )

    @validate
    def earnings(
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
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Upcoming and Historical earnings calendar.

        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
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
            extra: Dict[str, Any]
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
        actual_eps : Optional[float]
            The actual earnings per share announced. (provider: fmp)
        actual_revenue : Optional[float]
            The actual reported revenue. (provider: fmp)
        revenue_consensus : Optional[float]
            The revenue forecast consensus. (provider: fmp)
        period_ending : Optional[date]
            The fiscal period end date. (provider: fmp)
        reporting_time : Optional[str]
            The reporting time - e.g. after market close. (provider: fmp)
        updated_date : Optional[date]
            The date the data was updated last. (provider: fmp)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.calendar.earnings()
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
            "/equity/calendar/earnings",
            **inputs,
        )

    @validate
    def ipo(
        self,
        symbol: Annotated[
            Union[str, None, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ] = None,
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
        limit: Annotated[
            Optional[int],
            OpenBBCustomParameter(description="The number of data entries to return."),
        ] = 100,
        provider: Optional[Literal["intrinio"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Upcoming and Historical IPO Calendar.

        Parameters
        ----------
        symbol : Optional[str]
            Symbol to get data for.
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
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
            extra: Dict[str, Any]
                Extra info.

        CalendarIpo
        -----------
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        ipo_date : Optional[date]
            The date of the IPO, when the stock first trades on a major exchange.
        status : Optional[Literal['upcoming', 'priced', 'withdrawn']]

                    The status of the IPO. Upcoming IPOs have not taken place yet but are expected to.
                    Priced IPOs have taken place.
                    Withdrawn IPOs were expected to take place, but were subsequently withdrawn and did not take place
                 (provider: intrinio)
        exchange : Optional[str]

                    The acronym of the stock exchange that the company is going to trade publicly on.
                    Typically NYSE or NASDAQ.
                 (provider: intrinio)
        offer_amount : Optional[float]
            The total dollar amount of shares offered in the IPO. Typically this is share price * share count (provider: intrinio)
        share_price : Optional[float]
            The price per share at which the IPO was offered. (provider: intrinio)
        share_price_lowest : Optional[float]

                    The expected lowest price per share at which the IPO will be offered.
                    Before an IPO is priced, companies typically provide a range of prices per share at which
                    they expect to offer the IPO (typically available for upcoming IPOs).
                 (provider: intrinio)
        share_price_highest : Optional[float]

                    The expected highest price per share at which the IPO will be offered.
                    Before an IPO is priced, companies typically provide a range of prices per share at which
                    they expect to offer the IPO (typically available for upcoming IPOs).
                 (provider: intrinio)
        share_count : Optional[int]
            The number of shares offered in the IPO. (provider: intrinio)
        share_count_lowest : Optional[int]

                    The expected lowest number of shares that will be offered in the IPO. Before an IPO is priced,
                    companies typically provide a range of shares that they expect to offer in the IPO
                    (typically available for upcoming IPOs).
                 (provider: intrinio)
        share_count_highest : Optional[int]

                    The expected highest number of shares that will be offered in the IPO. Before an IPO is priced,
                    companies typically provide a range of shares that they expect to offer in the IPO
                    (typically available for upcoming IPOs).
                 (provider: intrinio)
        announcement_url : Optional[str]
            The URL to the company's announcement of the IPO (provider: intrinio)
        sec_report_url : Optional[str]

                    The URL to the company's S-1, S-1/A, F-1, or F-1/A SEC filing,
                    which is required to be filed before an IPO takes place.
                 (provider: intrinio)
        open_price : Optional[float]
            The opening price at the beginning of the first trading day (only available for priced IPOs). (provider: intrinio)
        close_price : Optional[float]
            The closing price at the end of the first trading day (only available for priced IPOs). (provider: intrinio)
        volume : Optional[int]
            The volume at the end of the first trading day (only available for priced IPOs). (provider: intrinio)
        day_change : Optional[float]

                    The percentage change between the open price and the close price on the first trading day
                    (only available for priced IPOs).
                 (provider: intrinio)
        week_change : Optional[float]

                    The percentage change between the open price on the first trading day and the close price approximately
                    a week after the first trading day (only available for priced IPOs).
                 (provider: intrinio)
        month_change : Optional[float]

                    The percentage change between the open price on the first trading day and the close price approximately
                    a month after the first trading day (only available for priced IPOs).
                 (provider: intrinio)
        id : Optional[str]
            The Intrinio ID of the IPO. (provider: intrinio)
        company : Optional[openbb_intrinio.utils.references.IntrinioCompany]
            The company that is going public via the IPO. (provider: intrinio)
        security : Optional[openbb_intrinio.utils.references.IntrinioSecurity]
            The primary Security for the Company that is going public via the IPO (provider: intrinio)

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.calendar.ipo(limit=100)
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
                "start_date": start_date,
                "end_date": end_date,
                "limit": limit,
            },
            extra_params=kwargs,
        )

        return self._run(
            "/equity/calendar/ipo",
            **inputs,
        )

    @validate
    def split(
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
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Calendar Splits. Show Stock Split Calendar.

        Parameters
        ----------
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Optional[datetime.date]
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
            extra: Dict[str, Any]
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

        Example
        -------
        >>> from openbb import obb
        >>> obb.equity.calendar.split()
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
            "/equity/calendar/split",
            **inputs,
        )
