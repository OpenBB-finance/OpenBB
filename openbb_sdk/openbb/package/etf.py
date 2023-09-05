### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from pydantic import validate_arguments
from typing_extensions import Annotated


class CLASS_etf(Container):
    """/etf
    holdings
    search
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_arguments
    def holdings(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(description="Symbol to get data for."),
        ],
        provider: Optional[Literal["blackrock", "tmx"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Get holdings for an ETF.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for.
        provider : Optional[Literal['blackrock', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'blackrock' if there is
            no default.
        date : Union[str, datetime.date, NoneType]
            The as-of date for historical daily holdings. (provider: blackrock)
        country : Optional[Literal['canada']]
            The country the ETF is registered in. (provider: blackrock)

        Returns
        -------
        OBBject
            results : List[EtfHoldings]
                Serializable results.
            provider : Optional[Literal['blackrock', 'tmx']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        EtfHoldings
        -----------
        symbol : Optional[str]
            The asset's ticker symbol. (provider: blackrock)
        name : Optional[str]
            The name of the asset. (provider: blackrock)
        weight : Optional[float]
            The weight of the holding. (provider: blackrock)
        price : Optional[float]
            The price-per-share of the asset. (provider: blackrock)
        shares : Optional[int]
            The number of shares held. (provider: blackrock)
        market_value : Optional[float]
            The market value of the holding. (provider: blackrock)
        notional_value : Optional[float]
            The notional value of the holding. (provider: blackrock)
        sector : Optional[str]
            The sector the asset belongs to. (provider: blackrock)
        sedol : Optional[str]
            The SEDOL of the asset. (provider: blackrock)
        cusip : Optional[str]
            The CUSIP of the asset. (provider: blackrock)
        exchange : Optional[str]
            The exchange the asset is traded on. (provider: blackrock)
        country : Optional[str]
            The location of the risk exposure is. (provider: blackrock)
        currency : Optional[str]
            The currency of the asset. (provider: blackrock)
        market_currency : Optional[str]
            The currency for the market the asset trades in. (provider: blackrock)
        fx_rate : Optional[float]
            The exchange rate of the asset against the fund's base currency. (provider: blackrock)
        share_percentage : Optional[float]
            The share percentage of the holding. (provider: tmx)
        share_change : Optional[float]
            The change in shares of the holding. (provider: tmx)
        type_id : Optional[str]
            The holding type ID of the asset. (provider: tmx)
        fund_id : Optional[str]
            The fund ID of the asset. (provider: tmx)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": ",".join(symbol) if isinstance(symbol, list) else symbol,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/etf/holdings",
            **inputs,
        )

    @validate_arguments
    def search(
        self,
        query: Annotated[
            Optional[str], OpenBBCustomParameter(description="Search query.")
        ] = "",
        provider: Optional[Literal["blackrock", "tmx"]] = None,
        **kwargs
    ) -> OBBject[List]:
        """Search for ETFs. An empty query returns the full list of ETFs from the provider.

        Parameters
        ----------
        query : Optional[str]
            Search query.
        provider : Optional[Literal['blackrock', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'blackrock' if there is
            no default.
        div_freq : Optional[Literal['monthly', 'annually', 'quarterly']]
            The dividend payment frequency. (provider: tmx)
        sort_by : Optional[Literal['aum', 'return_1m', 'return_3m', 'return_ytd', 'volume_avg_daily', 'management_fee', 'distribution_yield']]
            The column to sort by. (provider: tmx)

        Returns
        -------
        OBBject
            results : List[EtfSearch]
                Serializable results.
            provider : Optional[Literal['blackrock', 'tmx']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            metadata: Optional[Metadata]
                Metadata info about the command execution.

        EtfSearch
        ---------
        symbol : Optional[str]
            The exchange ticker symbol for the ETF.
        name : Optional[str]
            Name of the ETF.
        currency : Optional[str]
            Currency of the ETF.
        aum : Union[float, NoneType, int]
            The value of the assets under management. (provider: blackrock)
        asset_class : Optional[str]
            The asset class of the ETF. (provider: blackrock)
        sub_asset_class : Optional[str]
            The sub-asset class of the ETF. (provider: blackrock)
        region : Optional[str]
            The region of the ETF. (provider: blackrock)
        market_type : Optional[str]
            The market type of the ETF. (provider: blackrock)
        investment_style : Optional[str]
            The investment style of the ETF. (provider: blackrock)
        investment_strategy : Optional[str]
            The investment strategy of the ETF. (provider: blackrock)
        premium_discount : Optional[float]
            The premium/discount to NAV. (provider: blackrock)
        distribution_yield : Optional[float]
            The annualized distribution yield. (provider: blackrock)
        ttm_yield : Optional[float]
            The trailing twelve months (TTM) annualized yield. (provider: blackrock)
        weighted_avg_ytm : Optional[float]
            The weighted average yield-to-maturity. (provider: blackrock)
        return_1y : Optional[float]
            The one-year annualized return on net assets. (provider: blackrock)
        return_3y : Optional[float]
            The three-year annualized return on net assets. (provider: blackrock)
        return_5y : Optional[float]
            The five-year annualized return on net assets. (provider: blackrock)
        return_ytd : Optional[float]
            The year-to-date annualized return on net assets. (provider: blackrock)
        return_inception : Optional[float]
            The annualized return on net assets since inception. (provider: blackrock)
        mer : Optional[float]
            The management expense ratio. (provider: blackrock)
        ineception_date : Optional[str]
            The inception date. (provider: blackrock)
        return_1m : Optional[float]
            The one-month return. (provider: tmx)
        return_3m : Optional[float]
            The three-month return. (provider: tmx)
        close : Optional[float]
            The closing price. (provider: tmx)
        prev_close : Optional[float]
            The previous closing price. (provider: tmx)
        volume_avg_daily : Optional[int]
            The average daily volume. (provider: tmx)
        management_fee : Optional[float]
            The management fee. (provider: tmx)
        dividend_frequency : Optional[str]
            The dividend payment frequency. (provider: tmx)"""  # noqa: E501

        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "query": query,
            },
            extra_params=kwargs,
        )

        return self._command_runner.run(
            "/etf/search",
            **inputs,
        )
