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
    reference_rates
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
    def reference_rates(
        self,
        provider: Annotated[
            Optional[Literal["ecb"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: ecb."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get current, official, currency reference rates.

        Foreign exchange reference rates are the exchange rates set by a major financial institution or regulatory body,
        serving as a benchmark for the value of currencies around the world.
        These rates are used as a standard to facilitate international trade and financial transactions,
        ensuring consistency and reliability in currency conversion.
        They are typically updated on a daily basis and reflect the market conditions at a specific time.
        Central banks and financial institutions often use these rates to guide their own exchange rates,
        impacting global trade, loans, and investments.


        Parameters
        ----------
        provider : Optional[Literal['ecb']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: ecb.

        Returns
        -------
        OBBject
            results : CurrencyReferenceRates
                Serializable results.
            provider : Optional[Literal['ecb']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CurrencyReferenceRates
        ----------------------
        date : date
            The date of the data.
        EUR : Optional[float]
            Euro.
        USD : Optional[float]
            US Dollar.
        JPY : Optional[float]
            Japanese Yen.
        BGN : Optional[float]
            Bulgarian Lev.
        CZK : Optional[float]
            Czech Koruna.
        DKK : Optional[float]
            Danish Krone.
        GBP : Optional[float]
            Pound Sterling.
        HUF : Optional[float]
            Hungarian Forint.
        PLN : Optional[float]
            Polish Zloty.
        RON : Optional[float]
            Romanian Leu.
        SEK : Optional[float]
            Swedish Krona.
        CHF : Optional[float]
            Swiss Franc.
        ISK : Optional[float]
            Icelandic Krona.
        NOK : Optional[float]
            Norwegian Krone.
        TRY : Optional[float]
            Turkish Lira.
        AUD : Optional[float]
            Australian Dollar.
        BRL : Optional[float]
            Brazilian Real.
        CAD : Optional[float]
            Canadian Dollar.
        CNY : Optional[float]
            Chinese Yuan.
        HKD : Optional[float]
            Hong Kong Dollar.
        IDR : Optional[float]
            Indonesian Rupiah.
        ILS : Optional[float]
            Israeli Shekel.
        INR : Optional[float]
            Indian Rupee.
        KRW : Optional[float]
            South Korean Won.
        MXN : Optional[float]
            Mexican Peso.
        MYR : Optional[float]
            Malaysian Ringgit.
        NZD : Optional[float]
            New Zealand Dollar.
        PHP : Optional[float]
            Philippine Peso.
        SGD : Optional[float]
            Singapore Dollar.
        THB : Optional[float]
            Thai Baht.
        ZAR : Optional[float]
            South African Rand.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.currency.reference_rates(provider='ecb')
        """  # noqa: E501

        return self._run(
            "/currency/reference_rates",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "currency.reference_rates",
                        ("ecb",),
                    )
                },
                standard_params={},
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def search(
        self,
        query: Annotated[
            Optional[str],
            OpenBBField(description="Query to search for currency pairs."),
        ] = None,
        provider: Annotated[
            Optional[Literal["fmp", "intrinio", "polygon"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio, polygon."
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
        query : Optional[str]
            Query to search for currency pairs.
        provider : Optional[Literal['fmp', 'intrinio', 'polygon']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, intrinio, polygon.

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
        symbol : str
            Symbol representing the entity requested in the data.
        name : Optional[str]
            Name of the currency pair.
        currency : Optional[str]
            Base currency of the currency pair. (provider: fmp)
        stock_exchange : Optional[str]
            Stock exchange of the currency pair. (provider: fmp)
        exchange_short_name : Optional[str]
            Short name of the stock exchange of the currency pair. (provider: fmp)
        base_currency : Optional[str]
            ISO 4217 currency code of the base currency. (provider: intrinio)
        quote_currency : Optional[str]
            ISO 4217 currency code of the quote currency. (provider: intrinio)
        currency_symbol : Optional[str]
            The symbol of the quote currency. (provider: polygon)
        base_currency_symbol : Optional[str]
            The symbol of the base currency. (provider: polygon)
        base_currency_name : Optional[str]
            Name of the base currency. (provider: polygon)
        market : Optional[str]
            Name of the trading market. Always 'fx'. (provider: polygon)
        locale : Optional[str]
            Locale of the currency pair. (provider: polygon)
        last_updated : Optional[date]
            The date the reference data was last updated. (provider: polygon)
        delisted : Optional[date]
            The date the item was delisted. (provider: polygon)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.currency.search(provider='fmp')
        >>> # Search for 'EUR' currency pair using 'intrinio' as provider.
        >>> obb.currency.search(provider='intrinio', query='EUR')
        >>> # Search for terms  using 'polygon' as provider.
        >>> obb.currency.search(provider='polygon', query='EUR')
        """  # noqa: E501

        return self._run(
            "/currency/search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "currency.search",
                        ("fmp", "intrinio", "polygon"),
                    )
                },
                standard_params={
                    "query": query,
                },
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
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, polygon."
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
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, polygon.

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
                        "currency.snapshots",
                        ("fmp", "polygon"),
                    )
                },
                standard_params={
                    "base": base,
                    "quote_type": quote_type,
                    "counter_currencies": counter_currencies,
                },
                extra_params=kwargs,
                info={
                    "base": {
                        "fmp": {"multiple_items_allowed": True, "choices": None},
                        "polygon": {"multiple_items_allowed": True, "choices": None},
                    }
                },
            )
        )
