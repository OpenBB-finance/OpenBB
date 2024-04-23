### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated


class ROUTER_currency(Container):
    """/currency
    /price
    search
    snapshots
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def price(self):
        # pylint: disable=import-outside-toplevel
        from . import currency_price

        return currency_price.ROUTER_currency_price(command_runner=self._command_runner)

    @exception_handler
    @validate
    def search(
        self,
        provider: Annotated[
            Optional[Literal["fmp", "intrinio", "polygon"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Currency Search.

        Search available currency pairs.
        Currency pairs are the national currencies from two countries coupled for trading on
        the foreign exchange (FX) marketplace.
        Both currencies will have exchange rates on which the trade will have its position basis.
        All trading within the forex market, whether selling, buying, or trading, will take place through currency pairs.
        (ref: Investopedia)
        Major currency pairs include pairs such as EUR/USD, USD/JPY, GBP/USD, etc.


        Parameters
        ----------
        provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.
        symbol : Optional[str]
            Symbol of the pair to search. (provider: polygon)
        date : Optional[datetime.date]
            A specific date to get data for. (provider: polygon)
        search : Optional[str]
            Search for terms within the ticker and/or company name. (provider: polygon)
        active : Optional[bool]
            Specify if the tickers returned should be actively traded on the queried date. (provider: polygon)
        order : Optional[Literal['asc', 'desc']]
            Order data by ascending or descending. (provider: polygon)
        sort : Optional[Literal['ticker', 'name', 'market', 'locale', 'currency_symbol', 'currency_name', 'base_currency_symbol', 'base_currency_name', 'last_updated_utc', 'delisted_utc']]
            Sort field used for ordering. (provider: polygon)
        limit : Optional[Annotated[int, Gt(gt=0)]]
            The number of data entries to return. (provider: polygon)

        Returns
        -------
        OBBject
            results : List[CurrencyPairs]
                Serializable results.
            provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CurrencyPairs
        -------------
        name : str
            Name of the currency pair.
        symbol : Optional[str]
            Symbol of the currency pair. (provider: fmp)
        currency : Optional[str]
            Base currency of the currency pair. (provider: fmp)
        stock_exchange : Optional[str]
            Stock exchange of the currency pair. (provider: fmp)
        exchange_short_name : Optional[str]
            Short name of the stock exchange of the currency pair. (provider: fmp)
        code : Optional[str]
            Code of the currency pair. (provider: intrinio)
        base_currency : Optional[str]
            ISO 4217 currency code of the base currency. (provider: intrinio)
        quote_currency : Optional[str]
            ISO 4217 currency code of the quote currency. (provider: intrinio)
        market : Optional[str]
            Name of the trading market. Always 'fx'. (provider: polygon)
        locale : Optional[str]
            Locale of the currency pair. (provider: polygon)
        currency_symbol : Optional[str]
            The symbol of the quote currency. (provider: polygon)
        currency_name : Optional[str]
            Name of the quote currency. (provider: polygon)
        base_currency_symbol : Optional[str]
            The symbol of the base currency. (provider: polygon)
        base_currency_name : Optional[str]
            Name of the base currency. (provider: polygon)
        last_updated_utc : Optional[datetime]
            The last updated timestamp in UTC. (provider: polygon)
        delisted_utc : Optional[datetime]
            The delisted timestamp in UTC. (provider: polygon)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.currency.search(provider='intrinio')
        >>> # Search for 'EURUSD' currency pair using 'intrinio' as provider.
        >>> obb.currency.search(provider='intrinio', symbol='EURUSD')
        >>> # Search for actively traded currency pairs on the queried date using 'polygon' as provider.
        >>> obb.currency.search(provider='polygon', date='2024-01-02', active=True)
        >>> # Search for terms  using 'polygon' as provider.
        >>> obb.currency.search(provider='polygon', search='Euro zone')
        """  # noqa: E501

        return self._run(
            "/currency/search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/currency/search",
                        ("fmp", "intrinio", "polygon"),
                    )
                },
                standard_params={},
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def snapshots(
        self,
        base: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="The base currency symbol. Multiple comma separated items allowed for provider(s): fmp, polygon."
            ),
        ] = "usd",
        quote_type: Annotated[
            Literal["direct", "indirect"],
            OpenBBField(
                description="Whether the quote is direct or indirect. Selecting 'direct' will return the exchange rate as the amount of domestic currency required to buy one unit of the foreign currency. Selecting 'indirect' (default) will return the exchange rate as the amount of foreign currency required to buy one unit of the domestic currency."
            ),
        ] = "indirect",
        counter_currencies: Annotated[
            Union[List[str], str, None],
            OpenBBField(
                description="An optional list of counter currency symbols to filter for. None returns all."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["fmp", "polygon"]],
            OpenBBField(
                description="The provider to use for the query, by default None.\n    If None, the provider specified in defaults is selected or 'fmp' if there is\n    no default."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Snapshots of currency exchange rates from an indirect or direct perspective of a base currency.

        Parameters
        ----------
        base : Union[str, List[str]]
            The base currency symbol. Multiple comma separated items allowed for provider(s): fmp, polygon.
        quote_type : Literal['direct', 'indirect']
            Whether the quote is direct or indirect. Selecting 'direct' will return the exchange rate as the amount of domestic currency required to buy one unit of the foreign currency. Selecting 'indirect' (default) will return the exchange rate as the amount of foreign currency required to buy one unit of the domestic currency.
        counter_currencies : Union[List[str], str, None]
            An optional list of counter currency symbols to filter for. None returns all.
        provider : Optional[Literal['fmp', 'polygon']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'fmp' if there is
            no default.

        Returns
        -------
        OBBject
            results : List[CurrencySnapshots]
                Serializable results.
            provider : Optional[Literal['fmp', 'polygon']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CurrencySnapshots
        -----------------
        base_currency : str
            The base, or domestic, currency.
        counter_currency : str
            The counter, or foreign, currency.
        last_rate : float
            The exchange rate, relative to the base currency. Rates are expressed as the amount of foreign currency received from selling one unit of the base currency, or the quantity of foreign currency required to purchase one unit of the domestic currency. To inverse the perspective, set the 'quote_type' parameter as 'direct'.
        open : Optional[float]
            The open price.
        high : Optional[float]
            The high price.
        low : Optional[float]
            The low price.
        close : Optional[float]
            The close price.
        volume : Optional[int]
            The trading volume.
        prev_close : Optional[float]
            The previous close price.
        change : Optional[float]
            The change in the price from the previous close. (provider: fmp, polygon)
        change_percent : Optional[float]
            The change in the price from the previous close, as a normalized percent. (provider: fmp);
            The percentage change in price from the previous day. (provider: polygon)
        ma50 : Optional[float]
            The 50-day moving average. (provider: fmp)
        ma200 : Optional[float]
            The 200-day moving average. (provider: fmp)
        year_high : Optional[float]
            The 52-week high. (provider: fmp)
        year_low : Optional[float]
            The 52-week low. (provider: fmp)
        last_rate_timestamp : Optional[datetime]
            The timestamp of the last rate. (provider: fmp)
        vwap : Optional[float]
            The volume-weighted average price. (provider: polygon)
        prev_open : Optional[float]
            The previous day's opening price. (provider: polygon)
        prev_high : Optional[float]
            The previous day's high price. (provider: polygon)
        prev_low : Optional[float]
            The previous day's low price. (provider: polygon)
        prev_volume : Optional[float]
            The previous day's volume. (provider: polygon)
        prev_vwap : Optional[float]
            The previous day's VWAP. (provider: polygon)
        bid : Optional[float]
            The current bid price. (provider: polygon)
        ask : Optional[float]
            The current ask price. (provider: polygon)
        minute_open : Optional[float]
            The open price from the most recent minute bar. (provider: polygon)
        minute_high : Optional[float]
            The high price from the most recent minute bar. (provider: polygon)
        minute_low : Optional[float]
            The low price from the most recent minute bar. (provider: polygon)
        minute_close : Optional[float]
            The close price from the most recent minute bar. (provider: polygon)
        minute_volume : Optional[float]
            The volume from the most recent minute bar. (provider: polygon)
        minute_vwap : Optional[float]
            The VWAP from the most recent minute bar. (provider: polygon)
        minute_transactions : Optional[float]
            The number of transactions in the most recent minute bar. (provider: polygon)
        quote_timestamp : Optional[datetime]
            The timestamp of the last quote. (provider: polygon)
        minute_timestamp : Optional[datetime]
            The timestamp for the start of the most recent minute bar. (provider: polygon)
        last_updated : Optional[datetime]
            The last time the data was updated. (provider: polygon)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.currency.snapshots(provider='fmp')
        >>> # Get exchange rates from USD and XAU to EUR, JPY, and GBP using 'fmp' as provider.
        >>> obb.currency.snapshots(provider='fmp', base='USD,XAU', counter_currencies='EUR,JPY,GBP', quote_type='indirect')
        """  # noqa: E501

        return self._run(
            "/currency/snapshots",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "/currency/snapshots",
                        ("fmp", "polygon"),
                    )
                },
                standard_params={
                    "base": base,
                    "quote_type": quote_type,
                    "counter_currencies": counter_currencies,
                },
                extra_params=kwargs,
                info={"base": {"multiple_items_allowed": ["fmp", "polygon"]}},
            )
        )
