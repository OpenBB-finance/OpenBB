### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

from typing import List, Literal, Optional, Union

from openbb_core.app.model.custom_parameter import OpenBBCustomParameter
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_inputs
from openbb_provider.abstract.data import Data
from pydantic import validate_call
from typing_extensions import Annotated


class ROUTER_etf(Container):
    """/etf
    countries
    historical_nav
    holdings
    info
    search
    sectors
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @validate_call
    def countries(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="The exchange ticker symbol for the ETF."
            ),
        ],
        provider: Optional[Literal["blackrock", "bmo", "fmp", "tmx"]] = None,
        **kwargs
    ) -> OBBject[Union[List[Data], Data]]:
        """ETF Country weighting.

        Parameters
        ----------
        symbol : str
            The exchange ticker symbol for the ETF.
        provider : Optional[Literal['blackrock', 'bmo', 'fmp', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'blackrock' if there is
            no default.
        country : Optional[Literal['america', 'canada']]
            The country the ETF is registered in.  Symbol suffix with `.TO` can be used as a proxy for Canada. (provider: blackrock)
        date : Optional[str]
            The as-of date for the data. (provider: blackrock)

        Returns
        -------
        OBBject
            results : Union[List[EtfCountries], EtfCountries]
                Serializable results.
            provider : Optional[Literal['blackrock', 'bmo', 'fmp', 'tmx']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfCountries
        ------------
        symbol : str
            The exchange ticker symbol for the ETF."""  # noqa: E501

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
            "/etf/countries",
            **inputs,
        )

    @validate_call
    def historical_nav(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="The exchange ticker symbol for the ETF."
            ),
        ],
        provider: Optional[Literal["bmo", "invesco"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """ETF Historical NAV.

        Parameters
        ----------
        symbol : str
            The exchange ticker symbol for the ETF.
        provider : Optional[Literal['bmo', 'invesco']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'bmo' if there is
            no default.
        country : Optional[Literal['america', 'canada']]
            The country the ETF is registered in. (provider: invesco)

        Returns
        -------
        OBBject
            results : List[EtfHistoricalNav]
                Serializable results.
            provider : Optional[Literal['bmo', 'invesco']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfHistoricalNav
        ----------------
        date : date
            The date of the NAV.
        nav : float
            The net asset value on the date.
        net_assets : Optional[float]
            The net assets of the fund. (provider: bmo)
        market_price : Optional[float]
            The closing market price of the fund. (provider: bmo)
        index_value : Optional[float]
            The value of the tracking index. (provider: bmo)
        fund_1_day_growth : Optional[float]
            The 1-day growth of the fund. (provider: bmo)
        index_1_day_growth : Optional[float]
            The 1-day growth of the tracking index. (provider: bmo)
        shares_outstanding : Optional[float]
            The number of shares outstanding. (provider: bmo)"""  # noqa: E501

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
            "/etf/historical_nav",
            **inputs,
        )

    @validate_call
    def holdings(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="The exchange ticker symbol for the ETF."
            ),
        ],
        provider: Optional[Literal["blackrock", "bmo", "fmp", "invesco", "tmx"]] = None,
        **kwargs
    ) -> OBBject[Union[List[Data], Data]]:
        """Get the holdings for an individual ETF.

        Parameters
        ----------
        symbol : str
            The exchange ticker symbol for the ETF.
        provider : Optional[Literal['blackrock', 'bmo', 'fmp', 'invesco', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'blackrock' if there is
            no default.
        date : Optional[Union[str, datetime.date]]
            The as-of date for historical daily holdings. (provider: blackrock, fmp)
        country : Optional[Literal['america', 'canada']]
            The country the ETF is registered in. (provider: blackrock, invesco)

        Returns
        -------
        OBBject
            results : Union[List[EtfHoldings], EtfHoldings]
                Serializable results.
            provider : Optional[Literal['blackrock', 'bmo', 'fmp', 'invesco', 'tmx']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfHoldings
        -----------
        holdings_data : Optional[Union[List[openbb_blackrock.models.etf_holdings.BlackrockEtfHoldingsData], List[openbb_fmp.models.etf_holdings.FMPEtfHoldingsData]]]
            None (provider: blackrock, fmp)
        extra_info : Optional[Dict[str, Any]]
            None (provider: blackrock, fmp)
        symbol : Optional[str]
            The ticker symbol of the asset. (provider: bmo, invesco, tmx)
        name : Optional[str]
            The name of the asset. (provider: bmo, invesco, tmx)
        label : Optional[str]
            The label of the asset. (provider: bmo)
        isin : Optional[str]
            The ISIN of the asset. (provider: bmo)
        asset_group : Optional[str]
            The type of asset. (provider: bmo)
        weight : Optional[float]
            The weight of the asset in the portfolio. (provider: bmo, invesco, tmx)
        shares : Optional[Union[float, int, str]]
            The number of shares or contracts of the asset held. (provider: bmo); The value of the assets under management. (provider: tmx)
        currency : Optional[str]
            The currency of the asset. (provider: bmo); The currency of the holding. (provider: tmx)
        market_value : Optional[Union[float, str]]
            The market value of the holding. (provider: bmo, invesco, tmx)
        value : Optional[float]
            The value of the holding. (provider: bmo)
        par_value : Optional[float]
            The par value of the holding. (provider: bmo)
        income_rate : Optional[float]
            The income rate of the holding. (provider: bmo)
        maturity_date : Optional[Union[date, str]]
            The maturity date of the holding. (provider: bmo, invesco)
        sector : Optional[str]
            The sector of the asset. (provider: bmo, invesco)
        holdings_date : Optional[date]
            The date of the holdings. (provider: bmo); The date the asset was added to the portfolio. (provider: invesco)
        security_identifier : Optional[Union[int, str]]
            The unique security identifier of the asset. (provider: invesco)
        identifier : Optional[str]
            The asset class identifier. (provider: invesco)
        shares_or_contracts : Optional[float]
            The number of shares or contracts of the asset held. (provider: invesco)
        rating : Optional[str]
            The rating of the bond. (provider: invesco)
        coupon_rate : Optional[float]
            The coupon rate of the bond. (provider: invesco)
        contract_expiry_date : Optional[Union[str, date]]
            The expiration date of the derivatives contract. (provider: invesco)
        effective_date : Optional[Union[str, date]]
            The effective date of the bond holding. (provider: invesco)
        next_call_date : Optional[Union[str, date]]
            The next call date of the bond. (provider: invesco)
        share_class : Optional[str]
            The share class of the asset. (provider: invesco)
        fund_ticker : Optional[str]
            The ticker symbol of the Fund. (provider: invesco)
        share_percentage : Optional[float]
            The share percentage of the holding. (provider: tmx)
        share_change : Optional[Union[float, str]]
            The change in shares of the holding. (provider: tmx)
        country : Optional[str]
            The country of the holding. (provider: tmx)
        exchange : Optional[str]
            The exchange code of the holding. (provider: tmx)
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

        return self._run(
            "/etf/holdings",
            **inputs,
        )

    @validate_call
    def info(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="The exchange ticker symbol for the ETF."
            ),
        ],
        provider: Optional[Literal["blackrock", "bmo", "fmp", "tmx"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """ETF Info.

        Parameters
        ----------
        symbol : str
            The exchange ticker symbol for the ETF.
        provider : Optional[Literal['blackrock', 'bmo', 'fmp', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'blackrock' if there is
            no default.
        country : Literal['america', 'canada']
            The country the ETF is registered in. '.TO' acts as a proxy to 'canada'. (provider: blackrock)

        Returns
        -------
        OBBject
            results : List[EtfInfo]
                Serializable results.
            provider : Optional[Literal['blackrock', 'bmo', 'fmp', 'tmx']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfInfo
        -------
        symbol : str
            The exchange ticker symbol for the ETF.
        inception_date : Optional[str]
            Inception date of the ETF.
        name : Optional[str]
            Name of the ETF.
        asset_class : Optional[str]
            The asset class of the ETF. (provider: blackrock, fmp)
        sub_asset_class : Optional[str]
            The sub-asset class of the ETF. (provider: blackrock)
        country : Optional[str]
            The country the ETF is registered in. (provider: blackrock); The country where the ETF is domiciled. (provider: fmp)
        region : Optional[str]
            The region of the ETF. (provider: blackrock)
        investment_style : Optional[str]
            The investment style of the ETF. (provider: blackrock, tmx)
        yield_ttm : Optional[float]
            The TTM yield of the ETF. (provider: blackrock)
        aum : Optional[Union[float, int]]
            The value of the assets under management. (provider: blackrock); The AUM of the ETF. (provider: fmp); The AUM of the ETF. (provider: tmx)
        issuer : Optional[str]
            The issuer of the ETF. (provider: fmp, tmx)
        currency : Optional[str]
            The currency of the ETF. (provider: fmp, tmx)
        cusip : Optional[str]
            The CUSIP number of the ETF. (provider: fmp)
        isin : Optional[str]
            The ISIN number of the ETF. (provider: fmp)
        holdings_count : Optional[int]
            The number of holdings of the ETF. (provider: fmp)
        nav : Optional[float]
            The NAV of the ETF. (provider: fmp)
        expense_ratio : Optional[float]
            The expense ratio of the ETF. (provider: fmp)
        avg_volume : Optional[Union[float, int]]
            The average daily volume of the ETF. (provider: fmp, tmx)
        sectors : Optional[List[Dict]]
            The sector weightings of the ETF holdings. (provider: fmp, tmx)
        website : Optional[str]
            The website of the ETF. (provider: fmp, tmx)
        description : Optional[str]
            The description of the ETF. (provider: fmp, tmx)
        esg : Optional[bool]
            Whether the ETF qualifies as an ESG fund. (provider: tmx)
        unit_price : Optional[float]
            The unit price of the ETF. (provider: tmx)
        close : Optional[float]
            The closing price of the ETF. (provider: tmx)
        prev_close : Optional[float]
            The previous closing price of the ETF. (provider: tmx)
        return_1m : Optional[float]
            The one-month return of the ETF. (provider: tmx)
        return_3m : Optional[float]
            The three-month return of the ETF. (provider: tmx)
        return_6m : Optional[float]
            The six-month return of the ETF. (provider: tmx)
        return_ytd : Optional[float]
            The year-to-date return of the ETF. (provider: tmx)
        return_1y : Optional[float]
            The one-year return of the ETF. (provider: tmx)
        avg_volume_30d : Optional[int]
            The 30-day average volume of the ETF. (provider: tmx)
        pe_ratio : Optional[float]
            The price-to-earnings ratio of the ETF. (provider: tmx)
        pb_ratio : Optional[float]
            The price-to-book ratio of the ETF. (provider: tmx)
        management_fee : Optional[float]
            The management fee of the ETF. (provider: tmx)
        mer : Optional[float]
            The management expense ratio of the ETF. (provider: tmx)
        distribution_yield : Optional[float]
            The distribution yield of the ETF. (provider: tmx)
        dividend_frequency : Optional[str]
            The dividend payment frequency of the ETF. (provider: tmx)
        regions : Optional[List[Dict]]
            The region weightings of the ETF holdings. (provider: tmx)
        holdings_top10 : Optional[List[Dict]]
            The top 10 holdings of the ETF. (provider: tmx)"""  # noqa: E501

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
            "/etf/info",
            **inputs,
        )

    @validate_call
    def search(
        self,
        query: Annotated[
            Optional[str], OpenBBCustomParameter(description="Search query.")
        ] = "",
        provider: Optional[Literal["blackrock", "bmo", "fmp", "invesco", "tmx"]] = None,
        **kwargs
    ) -> OBBject[List[Data]]:
        """Fuzzy search for ETFs. An empty query returns the full list of ETFs from the provider.

        Parameters
        ----------
        query : Optional[str]
            Search query.
        provider : Optional[Literal['blackrock', 'bmo', 'fmp', 'invesco', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'blackrock' if there is
            no default.
        country : Literal['america', 'canada']
            The country the ETF is registered in. (provider: blackrock, invesco)
        exchange : Optional[Literal['AMEX', 'NYSE', 'NASDAQ', 'ETF', 'TSX', 'EURONEXT']]
            The exchange code the ETF trades on. (provider: fmp)
        is_active : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)
        div_freq : Optional[Literal['monthly', 'annually', 'quarterly']]
            The dividend payment frequency. (provider: invesco, tmx)
        options : Optional[Literal['True', 'False']]
            Does the fund trade options? (provider: invesco)
        short : Optional[Literal['True', 'False']]
            Is the fund shortable? (provider: invesco)
        sort_by : Optional[Literal['nav', 'return_1m', 'return_3m', 'return_6m', 'return_1y', 'return_3y', 'return_ytd', 'beta_1y', 'volume_avg_daily', 'management_fee', 'distribution_yield', 'pb_ratio', 'pe_ratio']]
            The column to sort by. (provider: tmx)

        Returns
        -------
        OBBject
            results : List[EtfSearch]
                Serializable results.
            provider : Optional[Literal['blackrock', 'bmo', 'fmp', 'invesco', 'tmx']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfSearch
        ---------
        symbol : str
            The exchange ticker symbol for the ETF.
        name : Optional[str]
            Name of the ETF.
        asset_class : Optional[str]
            The asset class of the ETF. (provider: blackrock, bmo)
        sub_asset_class : Optional[str]
            The sub-asset class of the ETF. (provider: blackrock)
        region : Optional[str]
            The region of the ETF. (provider: blackrock); The target region of the fund. (provider: bmo)
        country : Optional[str]
            The country the ETF is registered in. (provider: blackrock, fmp)
        market_type : Optional[str]
            The market type of the ETF. (provider: blackrock)
        investment_style : Optional[str]
            The investment style of the ETF. (provider: blackrock, tmx)
        investment_strategy : Optional[str]
            The investment strategy of the ETF. (provider: blackrock)
        nav : Optional[Union[float, int]]
            The value of the assets under management. (provider: blackrock, tmx)
        currency : Optional[str]
            The currency of the fund. (provider: bmo)
        trading_currency : Optional[str]
            The currency the fund trades in. (provider: bmo)
        fees : Optional[float]
            The management fee of the fund. (provider: bmo)
        mer : Optional[float]
            The management expense ratio of the fund. (provider: bmo)
        inception_date : Optional[date]
            The inception date of the fund. (provider: bmo, invesco)
        market_cap : Optional[float]
            The market cap of the ETF. (provider: fmp)
        sector : Optional[str]
            The sector of the ETF. (provider: fmp)
        industry : Optional[str]
            The industry of the ETF. (provider: fmp)
        beta : Optional[float]
            The beta of the ETF. (provider: fmp)
        price : Optional[float]
            The current price of the ETF. (provider: fmp)
        last_annual_dividend : Optional[float]
            The last annual dividend paid. (provider: fmp)
        volume : Optional[float]
            The current trading volume of the ETF. (provider: fmp)
        exchange : Optional[str]
            The exchange code the ETF trades on. (provider: fmp); The primary exchange where the fund is listed. (provider: invesco)
        exchange_name : Optional[str]
            The full name of the exchange the ETF trades on. (provider: fmp)
        actively_trading : Optional[Literal[True, False]]
            Whether the ETF is actively trading. (provider: fmp)
        index_ticker : Optional[str]
            The ticker symbol of the tracking index. (provider: invesco)
        iiv_ticker : Optional[str]
            The intraday indicative value ticker. (provider: invesco)
        cusip : Optional[str]
            The CUSIP of the fund. (provider: invesco)
        isin : Optional[str]
            The ISIN of the fund. (provider: invesco)
        distribution_yield : Optional[float]
            The distribution yield of the fund. (provider: invesco); The distribution yield. (provider: tmx)
        sec_yield : Optional[float]
            The SEC yield of the fund. (provider: invesco)
        ttm_yield : Optional[float]
            The TTM yield of the fund. (provider: invesco)
        distribution_frequency : Optional[str]
            The distribution frequency of the fund. (provider: invesco)
        marginable : Optional[str]
            Is the fund marginable? (provider: invesco)
        short : Optional[str]
            Is the fund shortable? (provider: invesco)
        options : Optional[str]
            Is the fund optionable? (provider: invesco)
        return_1m : Optional[float]
            The one-month return. (provider: tmx)
        return_3m : Optional[float]
            The three-month return. (provider: tmx)
        return_ytd : Optional[float]
            The year-to-date return. (provider: tmx)
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

        return self._run(
            "/etf/search",
            **inputs,
        )

    @validate_call
    def sectors(
        self,
        symbol: Annotated[
            Union[str, List[str]],
            OpenBBCustomParameter(
                description="The exchange ticker symbol for the ETF."
            ),
        ],
        provider: Optional[Literal["blackrock", "bmo", "fmp", "tmx"]] = None,
        **kwargs
    ) -> OBBject[Union[List[Data], Data]]:
        """ETF Sector weighting.

        Parameters
        ----------
        symbol : str
            The exchange ticker symbol for the ETF.
        provider : Optional[Literal['blackrock', 'bmo', 'fmp', 'tmx']]
            The provider to use for the query, by default None.
            If None, the provider specified in defaults is selected or 'blackrock' if there is
            no default.
        country : Optional[Literal['america', 'canada']]
            The country the ETF is registered in.  Symbol suffix with `.TO` can be used as a proxy for Canada. (provider: blackrock)
        date : Optional[str]
            The as-of date for the data. (provider: blackrock)

        Returns
        -------
        OBBject
            results : Union[List[EtfSectors], EtfSectors]
                Serializable results.
            provider : Optional[Literal['blackrock', 'bmo', 'fmp', 'tmx']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra: Dict[str, Any]
                Extra info.

        EtfSectors
        ----------
        symbol : str
            The exchange ticker symbol for the ETF.
        energy : Optional[float]
            Energy Sector Weight
        materials : Optional[float]
            Materials Sector Weight.
        industrials : Optional[float]
            Industrials Sector Weight.
        consumer_cyclical : Optional[float]
            Consumer Cyclical Sector Weight.
        consumer_defensive : Optional[float]
            Consumer Defensive Sector Weight.
        financial_services : Optional[float]
            Financial Services Sector Weight.
        technology : Optional[float]
            Technology Sector Weight.
        health_care : Optional[float]
            Health Care Sector Weight.
        communication_services : Optional[float]
            Communication Services Sector Weight.
        utilities : Optional[float]
            Utilities Sector Weight.
        real_estate : Optional[float]
            Real Estate Sector Weight.
        cash_or_derivatives : Optional[float]
            Cash and/or derivatives. (provider: blackrock)
        other : Optional[float]
            Other Sector Weight. (provider: fmp, tmx)"""  # noqa: E501

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
            "/etf/sectors",
            **inputs,
        )
