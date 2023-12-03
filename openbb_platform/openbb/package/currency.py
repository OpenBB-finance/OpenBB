### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional

from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.decorators import validate
from openbb_core.app.static.filters import filter_inputs
from openbb_core.provider.abstract.data import Data


class ROUTER_currency(Container):
    """/currency
    /price
    search
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @property
    def price(self):  # route = "/currency/price"
        from . import currency_price

        return currency_price.ROUTER_currency_price(command_runner=self._command_runner)

    @validate
    def search(
        self, provider: Optional[Literal["fmp", "intrinio", "polygon"]] = None, **kwargs
    ) -> OBBject[List[Data]]:
        """Currency Search. Search available currency pairs.

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
            extra: Dict[str, Any]
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

        Example
        -------
        >>> from openbb import obb
        >>> obb.currency.search()
        """  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
        )

        return self._run(
            "/currency/search",
            **inputs,
        )
