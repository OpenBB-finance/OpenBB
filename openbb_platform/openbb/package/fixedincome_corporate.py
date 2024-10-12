### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
from typing import List, Literal, Optional, Union
from warnings import simplefilter, warn

from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.field import OpenBBField
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.static.container import Container
from openbb_core.app.static.utils.decorators import exception_handler, validate
from openbb_core.app.static.utils.filters import filter_inputs
from typing_extensions import Annotated, deprecated


class ROUTER_fixedincome_corporate(Container):
    """/fixedincome/corporate
    bond_prices
    commercial_paper
    hqm
    ice_bofa
    moody
    spot_rates
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def bond_prices(
        self,
        country: Annotated[
            Optional[str],
            OpenBBField(description="The country to get data. Matches partial name."),
        ] = None,
        issuer_name: Annotated[
            Optional[str],
            OpenBBField(
                description="Name of the issuer.  Returns partial matches and is case insensitive."
            ),
        ] = None,
        isin: Annotated[
            Union[List, str, None],
            OpenBBField(
                description="International Securities Identification Number(s) of the bond(s)."
            ),
        ] = None,
        lei: Annotated[
            Optional[str],
            OpenBBField(description="Legal Entity Identifier of the issuing entity."),
        ] = None,
        currency: Annotated[
            Union[List, str, None],
            OpenBBField(
                description="Currency of the bond. Formatted as the 3-letter ISO 4217 code (e.g. GBP, EUR, USD)."
            ),
        ] = None,
        coupon_min: Annotated[
            Optional[float], OpenBBField(description="Minimum coupon rate of the bond.")
        ] = None,
        coupon_max: Annotated[
            Optional[float], OpenBBField(description="Maximum coupon rate of the bond.")
        ] = None,
        issued_amount_min: Annotated[
            Optional[int], OpenBBField(description="Minimum issued amount of the bond.")
        ] = None,
        issued_amount_max: Annotated[
            Optional[str], OpenBBField(description="Maximum issued amount of the bond.")
        ] = None,
        maturity_date_min: Annotated[
            Optional[datetime.date],
            OpenBBField(description="Minimum maturity date of the bond."),
        ] = None,
        maturity_date_max: Annotated[
            Optional[datetime.date],
            OpenBBField(description="Maximum maturity date of the bond."),
        ] = None,
        provider: Annotated[
            Optional[Literal["tmx"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: tmx."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Corporate Bond Prices.

        Parameters
        ----------
        country : Optional[str]
            The country to get data. Matches partial name.
        issuer_name : Optional[str]
            Name of the issuer.  Returns partial matches and is case insensitive.
        isin : Union[List, str, None]
            International Securities Identification Number(s) of the bond(s).
        lei : Optional[str]
            Legal Entity Identifier of the issuing entity.
        currency : Union[List, str, None]
            Currency of the bond. Formatted as the 3-letter ISO 4217 code (e.g. GBP, EUR, USD).
        coupon_min : Optional[float]
            Minimum coupon rate of the bond.
        coupon_max : Optional[float]
            Maximum coupon rate of the bond.
        issued_amount_min : Optional[int]
            Minimum issued amount of the bond.
        issued_amount_max : Optional[str]
            Maximum issued amount of the bond.
        maturity_date_min : Optional[date]
            Minimum maturity date of the bond.
        maturity_date_max : Optional[date]
            Maximum maturity date of the bond.
        provider : Optional[Literal['tmx']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: tmx.
        issue_date_min : Optional[datetime.date]
            Filter by the minimum original issue date. (provider: tmx)
        issue_date_max : Optional[datetime.date]
            Filter by the maximum original issue date. (provider: tmx)
        last_traded_min : Optional[datetime.date]
            Filter by the minimum last trade date. (provider: tmx)
        use_cache : bool
            All bond data is sourced from a single JSON file that is updated daily. The file is cached for one day to eliminate downloading more than once. Caching will significantly speed up subsequent queries. To bypass, set to False. (provider: tmx)

        Returns
        -------
        OBBject
            results : List[BondPrices]
                Serializable results.
            provider : Optional[Literal['tmx']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        BondPrices
        ----------
        isin : Optional[str]
            International Securities Identification Number of the bond.
        lei : Optional[str]
            Legal Entity Identifier of the issuing entity.
        figi : Optional[str]
            FIGI of the bond.
        cusip : Optional[str]
            CUSIP of the bond.
        coupon_rate : Optional[float]
            Coupon rate of the bond.
        ytm : Optional[float]
            Yield to maturity (YTM) is the rate of return anticipated on a bond if it is held until the maturity date. It takes into account the current market price, par value, coupon rate and time to maturity. It is assumed that all coupons are reinvested at the same rate. Values are returned as a normalized percent. (provider: tmx)
        price : Optional[float]
            The last price for the bond. (provider: tmx)
        highest_price : Optional[float]
            The highest price for the bond on the last traded date. (provider: tmx)
        lowest_price : Optional[float]
            The lowest price for the bond on the last traded date. (provider: tmx)
        total_trades : Optional[int]
            Total number of trades on the last traded date. (provider: tmx)
        last_traded_date : Optional[date]
            Last traded date of the bond. (provider: tmx)
        maturity_date : Optional[date]
            Maturity date of the bond. (provider: tmx)
        issue_date : Optional[date]
            Issue date of the bond. This is the date when the bond first accrues interest. (provider: tmx)
        issuer_name : Optional[str]
            Name of the issuing entity. (provider: tmx)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.bond_prices(provider='tmx')
        """  # noqa: E501

        return self._run(
            "/fixedincome/corporate/bond_prices",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.corporate.bond_prices",
                        ("tmx",),
                    )
                },
                standard_params={
                    "country": country,
                    "issuer_name": issuer_name,
                    "isin": isin,
                    "lei": lei,
                    "currency": currency,
                    "coupon_min": coupon_min,
                    "coupon_max": coupon_max,
                    "issued_amount_min": issued_amount_min,
                    "issued_amount_max": issued_amount_max,
                    "maturity_date_min": maturity_date_min,
                    "maturity_date_max": maturity_date_max,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def commercial_paper(
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
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Commercial Paper.

        Commercial paper (CP) consists of short-term, promissory notes issued primarily by corporations.
        Maturities range up to 270 days but average about 30 days.
        Many companies use CP to raise cash needed for current transactions,
        and many find it to be a lower-cost alternative to bank loans.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        maturity : Union[str, Literal['all', 'overnight', '7d', '15d', '30d', '60d', '90d']]
            A target maturity. Multiple comma separated items allowed. (provider: fred)
        category : Union[str, Literal['all', 'asset_backed', 'financial', 'nonfinancial', 'a2p2']]
            The category of asset. Multiple comma separated items allowed. (provider: fred)
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]

                Frequency aggregation to convert daily data to lower frequency.
                    a = Annual
                    q = Quarterly
                    m = Monthly
                    w = Weekly
                    wef = Weekly, Ending Friday
                    weth = Weekly, Ending Thursday
                    wew = Weekly, Ending Wednesday
                    wetu = Weekly, Ending Tuesday
                    wem = Weekly, Ending Monday
                    wesu = Weekly, Ending Sunday
                    wesa = Weekly, Ending Saturday
                    bwew = Biweekly, Ending Wednesday
                    bwem = Biweekly, Ending Monday
                 (provider: fred)
        aggregation_method : Optional[Literal['avg', 'sum', 'eop']]

                A key that indicates the aggregation method used for frequency aggregation.
                    avg = Average
                    sum = Sum
                    eop = End of Period
                 (provider: fred)
        transform : Optional[Literal['chg', 'ch1', 'pch', 'pc1', 'pca', 'cch', 'cca', 'log']]

                Transformation type
                    None = No transformation
                    chg = Change
                    ch1 = Change from Year Ago
                    pch = Percent Change
                    pc1 = Percent Change from Year Ago
                    pca = Compounded Annual Rate of Change
                    cch = Continuously Compounded Rate of Change
                    cca = Continuously Compounded Annual Rate of Change
                    log = Natural Log
                 (provider: fred)

        Returns
        -------
        OBBject
            results : List[CommercialPaper]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CommercialPaper
        ---------------
        date : date
            The date of the data.
        symbol : Optional[str]
            Symbol representing the entity requested in the data.
        maturity : str
            Maturity length of the item.
        rate : float
            Interest rate.
        title : Optional[str]
            Title of the series.
        asset_type : Optional[Literal['asset_backed', 'financial', 'nonfinancial', 'a2p2']]
            The category of asset. (provider: fred)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.commercial_paper(provider='fred')
        >>> obb.fixedincome.corporate.commercial_paper(category='all', maturity='15d', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/corporate/commercial_paper",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.corporate.commercial_paper",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={
                    "maturity": {
                        "fred": {
                            "multiple_items_allowed": True,
                            "choices": [
                                "all",
                                "overnight",
                                "7d",
                                "15d",
                                "30d",
                                "60d",
                                "90d",
                            ],
                        }
                    },
                    "category": {
                        "fred": {
                            "multiple_items_allowed": True,
                            "choices": [
                                "all",
                                "asset_backed",
                                "financial",
                                "nonfinancial",
                                "a2p2",
                            ],
                        }
                    },
                },
            )
        )

    @exception_handler
    @validate
    def hqm(
        self,
        date: Annotated[
            Union[datetime.date, str, None, List[Union[datetime.date, str, None]]],
            OpenBBField(
                description="A specific date to get data for. Multiple comma separated items allowed for provider(s): fred."
            ),
        ] = None,
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """High Quality Market Corporate Bond.

        The HQM yield curve represents the high quality corporate bond market, i.e.,
        corporate bonds rated AAA, AA, or A.  The HQM curve contains two regression terms.
        These terms are adjustment factors that blend AAA, AA, and A bonds into a single HQM yield curve
        that is the market-weighted average (MWA) quality of high quality bonds.


        Parameters
        ----------
        date : Union[date, str, None, List[Union[date, str, None]]]
            A specific date to get data for. Multiple comma separated items allowed for provider(s): fred.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        yield_curve : Literal['spot', 'par']
            The yield curve type. (provider: fred)

        Returns
        -------
        OBBject
            results : List[HighQualityMarketCorporateBond]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        HighQualityMarketCorporateBond
        ------------------------------
        date : date
            The date of the data.
        rate : float
            Interest rate.
        maturity : str
            Maturity.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.hqm(provider='fred')
        >>> obb.fixedincome.corporate.hqm(yield_curve='par', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/corporate/hqm",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.corporate.hqm",
                        ("fred",),
                    )
                },
                standard_params={
                    "date": date,
                },
                extra_params=kwargs,
                info={
                    "date": {"fred": {"multiple_items_allowed": True, "choices": None}}
                },
            )
        )

    @exception_handler
    @validate
    @deprecated(
        "This endpoint is deprecated; use `/fixedincome/bond_indices` instead. Deprecated in OpenBB Platform V4.2 to be removed in V4.5.",
        category=OpenBBDeprecationWarning,
    )
    def ice_bofa(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        index_type: Annotated[
            Literal["yield", "yield_to_worst", "total_return", "spread"],
            OpenBBField(description="The type of series."),
        ] = "yield",
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """ICE BofA US Corporate Bond Indices.

        The ICE BofA US Corporate Index tracks the performance of US dollar denominated investment grade corporate debt
        publicly issued in the US domestic market. Qualifying securities must have an investment grade rating (based on an
        average of Moody’s, S&P and Fitch), at least 18 months to final maturity at the time of issuance, at least one year
        remaining term to final maturity as of the rebalance date, a fixed coupon schedule and a minimum amount
        outstanding of $250 million. The ICE BofA US Corporate Index is a component of the US Corporate Master Index.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        index_type : Literal['yield', 'yield_to_worst', 'total_return', 'spread']
            The type of series.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        category : Literal['all', 'duration', 'eur', 'usd']
            The type of category. (provider: fred)
        area : Literal['asia', 'emea', 'eu', 'ex_g10', 'latin_america', 'us']
            The type of area. (provider: fred)
        grade : Literal['a', 'aa', 'aaa', 'b', 'bb', 'bbb', 'ccc', 'crossover', 'high_grade', 'high_yield', 'non_financial', 'non_sovereign', 'private_sector', 'public_sector']
            The type of grade. (provider: fred)
        options : bool
            Whether to include options in the results. (provider: fred)

        Returns
        -------
        OBBject
            results : List[ICEBofA]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ICEBofA
        -------
        date : date
            The date of the data.
        rate : Optional[float]
            ICE BofA US Corporate Bond Indices Rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.ice_bofa(provider='fred')
        >>> obb.fixedincome.corporate.ice_bofa(index_type='yield_to_worst', provider='fred')
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn(
            "This endpoint is deprecated; use `/fixedincome/bond_indices` instead. Deprecated in OpenBB Platform V4.2 to be removed in V4.5.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self._run(
            "/fixedincome/corporate/ice_bofa",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.corporate.ice_bofa",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "index_type": index_type,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    @deprecated(
        "This endpoint is deprecated; use `/fixedincome/bond_indices` instead. Set `category` to `us` and `index` to `seasoned_corporate`. Deprecated in OpenBB Platform V4.2 to be removed in V4.5.",
        category=OpenBBDeprecationWarning,
    )
    def moody(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        index_type: Annotated[
            Literal["aaa", "baa"], OpenBBField(description="The type of series.")
        ] = "aaa",
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Moody Corporate Bond Index.

        Moody's Aaa and Baa are investment bonds that acts as an index of
        the performance of all bonds given an Aaa or Baa rating by Moody's Investors Service respectively.
        These corporate bonds often are used in macroeconomics as an alternative to the federal ten-year
        Treasury Bill as an indicator of the interest rate.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        index_type : Literal['aaa', 'baa']
            The type of series.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        spread : Optional[Literal['treasury', 'fed_funds']]
            The type of spread. (provider: fred)

        Returns
        -------
        OBBject
            results : List[MoodyCorporateBondIndex]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        MoodyCorporateBondIndex
        -----------------------
        date : date
            The date of the data.
        rate : Optional[float]
            Moody Corporate Bond Index Rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.moody(provider='fred')
        >>> obb.fixedincome.corporate.moody(index_type='baa', provider='fred')
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn(
            "This endpoint is deprecated; use `/fixedincome/bond_indices` instead. Set `category` to `us` and `index` to `seasoned_corporate`. Deprecated in OpenBB Platform V4.2 to be removed in V4.5.",
            category=DeprecationWarning,
            stacklevel=2,
        )

        return self._run(
            "/fixedincome/corporate/moody",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.corporate.moody",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "index_type": index_type,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def spot_rates(
        self,
        start_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="Start date of the data, in YYYY-MM-DD format."),
        ] = None,
        end_date: Annotated[
            Union[datetime.date, None, str],
            OpenBBField(description="End date of the data, in YYYY-MM-DD format."),
        ] = None,
        maturity: Annotated[
            Union[float, str, List[Union[float, str]]],
            OpenBBField(
                description="Maturities in years. Multiple comma separated items allowed for provider(s): fred."
            ),
        ] = 10.0,
        category: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="Rate category. Options: spot_rate, par_yield. Multiple comma separated items allowed for provider(s): fred."
            ),
        ] = "spot_rate",
        provider: Annotated[
            Optional[Literal["fred"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Spot Rates.

        The spot rates for any maturity is the yield on a bond that provides a single payment at that maturity.
        This is a zero coupon bond.
        Because each spot rate pertains to a single cashflow, it is the relevant interest rate
        concept for discounting a pension liability at the same maturity.


        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        maturity : Union[float, str, List[Union[float, str]]]
            Maturities in years. Multiple comma separated items allowed for provider(s): fred.
        category : Union[str, List[str]]
            Rate category. Options: spot_rate, par_yield. Multiple comma separated items allowed for provider(s): fred.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.

        Returns
        -------
        OBBject
            results : List[SpotRate]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SpotRate
        --------
        date : date
            The date of the data.
        rate : Optional[float]
            Spot Rate.

        Examples
        --------
        >>> from openbb import obb
        >>> obb.fixedincome.corporate.spot_rates(provider='fred')
        >>> obb.fixedincome.corporate.spot_rates(maturity='10,20,30,50', provider='fred')
        """  # noqa: E501

        return self._run(
            "/fixedincome/corporate/spot_rates",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "fixedincome.corporate.spot_rates",
                        ("fred",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "maturity": maturity,
                    "category": category,
                },
                extra_params=kwargs,
                info={
                    "maturity": {
                        "fred": {"multiple_items_allowed": True, "choices": None}
                    },
                    "category": {
                        "fred": {
                            "multiple_items_allowed": True,
                            "choices": ["par_yield", "spot_rate"],
                        }
                    },
                },
            )
        )
