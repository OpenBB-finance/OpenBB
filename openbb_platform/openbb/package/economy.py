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


class ROUTER_economy(Container):
    """/economy
    available_indicators
    balance_of_payments
    calendar
    central_bank_holdings
    composite_leading_indicator
    country_profile
    cpi
    export_destinations
    fred_regional
    fred_release_table
    fred_search
    fred_series
    /gdp
    house_price_index
    immediate_interest_rate
    indicators
    interest_rates
    long_term_interest_rate
    money_measures
    pce
    primary_dealer_positioning
    retail_prices
    risk_premium
    share_price_index
    short_term_interest_rate
    /survey
    unemployment
    """

    def __repr__(self) -> str:
        return self.__doc__ or ""

    @exception_handler
    @validate
    def available_indicators(
        self,
        provider: Annotated[Optional[Literal["econdb"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb.")] = None,
        **kwargs
    ) -> OBBject:
        """Get the available economic indicators for a provider.

        Parameters
        ----------
        provider : Optional[Literal['econdb']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb.
        use_cache : bool
            Whether to use cache or not, by default is True The cache of indicator symbols will persist for one week. (provider: econdb)

        Returns
        -------
        OBBject
            results : List[AvailableIndicators]
                Serializable results.
            provider : Optional[Literal['econdb']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        AvailableIndicators
        -------------------
        symbol_root : Optional[str]
            The root symbol representing the indicator. 
        symbol : Optional[str]
            Symbol representing the entity requested in the data. The root symbol with additional codes. 
        country : Optional[str]
            The name of the country, region, or entity represented by the symbol. 
        iso : Optional[str]
            The ISO code of the country, region, or entity represented by the symbol. 
        description : Optional[str]
            The description of the indicator. 
        frequency : Optional[str]
            The frequency of the indicator data. 
        currency : Optional[str]
            The currency, or unit, the data is based in. (provider: econdb)
        scale : Optional[str]
            The scale of the data. (provider: econdb)
        multiplier : Optional[int]
            The multiplier of the data to arrive at whole units. (provider: econdb)
        transformation : Optional[str]
            Transformation type. (provider: econdb)
        source : Optional[str]
            The original source of the data. (provider: econdb)
        first_date : Optional[date]
            The first date of the data. (provider: econdb)
        last_date : Optional[date]
            The last date of the data. (provider: econdb)
        last_insert_timestamp : Optional[datetime]
            The time of the last update. Data is typically reported with a lag. (provider: econdb)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.available_indicators(provider='econdb')
        """  # noqa: E501

        return self._run(
            "/economy/available_indicators",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.available_indicators",
                        ("econdb",),
                    )
                },
                standard_params={
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def balance_of_payments(
        self,
        provider: Annotated[Optional[Literal["fred"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.")] = None,
        **kwargs
    ) -> OBBject:
        """Balance of Payments Reports.

        Parameters
        ----------
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        country : Literal['argentina', 'australia', 'austria', 'belgium', 'brazil', 'canada', 'chile', 'china', 'colombia', 'costa_rica', 'czechia', 'denmark', 'estonia', 'finland', 'france', 'germany', 'greece', 'hungary', 'iceland', 'india', 'indonesia', 'ireland', 'israel', 'italy', 'japan', 'korea', 'latvia', 'lithuania', 'luxembourg', 'mexico', 'netherlands', 'new_zealand', 'norway', 'poland', 'portugal', 'russia', 'saudi_arabia', 'slovak_republic', 'slovenia', 'south_africa', 'spain', 'sweden', 'switzerland', 'turkey', 'united_kingdom', 'united_states', 'g7', 'g20']
            The country to get data. Enter as a 3-letter ISO country code, default is USA. (provider: fred)
        start_date : Optional[datetime.date]
            Start date of the data, in YYYY-MM-DD format. (provider: fred)
        end_date : Optional[datetime.date]
            End date of the data, in YYYY-MM-DD format. (provider: fred)

        Returns
        -------
        OBBject
            results : List[BalanceOfPayments]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        BalanceOfPayments
        -----------------
        period : Optional[date]
            The date representing the beginning of the reporting period. 
        balance_percent_of_gdp : Optional[float]
            Current Account Balance as Percent of GDP 
        balance_total : Optional[float]
            Current Account Total Balance (USD) 
        balance_total_services : Optional[float]
            Current Account Total Services Balance (USD) 
        balance_total_secondary_income : Optional[float]
            Current Account Total Secondary Income Balance (USD) 
        balance_total_goods : Optional[float]
            Current Account Total Goods Balance (USD) 
        balance_total_primary_income : Optional[float]
            Current Account Total Primary Income Balance (USD) 
        credits_services_percent_of_goods_and_services : Optional[float]
            Current Account Credits Services as Percent of Goods and Services 
        credits_services_percent_of_current_account : Optional[float]
            Current Account Credits Services as Percent of Current Account 
        credits_total_services : Optional[float]
            Current Account Credits Total Services (USD) 
        credits_total_goods : Optional[float]
            Current Account Credits Total Goods (USD) 
        credits_total_primary_income : Optional[float]
            Current Account Credits Total Primary Income (USD) 
        credits_total_secondary_income : Optional[float]
            Current Account Credits Total Secondary Income (USD) 
        credits_total : Optional[float]
            Current Account Credits Total (USD) 
        debits_services_percent_of_goods_and_services : Optional[float]
            Current Account Debits Services as Percent of Goods and Services 
        debits_services_percent_of_current_account : Optional[float]
            Current Account Debits Services as Percent of Current Account 
        debits_total_services : Optional[float]
            Current Account Debits Total Services (USD) 
        debits_total_goods : Optional[float]
            Current Account Debits Total Goods (USD) 
        debits_total_primary_income : Optional[float]
            Current Account Debits Total Primary Income (USD) 
        debits_total : Optional[float]
            Current Account Debits Total (USD) 
        debits_total_secondary_income : Optional[float]
            Current Account Debits Total Secondary Income (USD) 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.balance_of_payments(provider='fred')
        >>> obb.economy.balance_of_payments(provider='fred', country='brazil')
        """  # noqa: E501

        return self._run(
            "/economy/balance_of_payments",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.balance_of_payments",
                        ("fred",),
                    )
                },
                standard_params={
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def calendar(
        self,
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["fmp", "tradingeconomics"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, tradingeconomics.")] = None,
        **kwargs
    ) -> OBBject:
        """Get the upcoming, or historical, economic calendar of global events.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fmp', 'tradingeconomics']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp, tradingeconomics.
        country : Optional[str]
            Country of the event. Multiple comma separated items allowed. (provider: tradingeconomics)
        importance : Optional[Literal['low', 'medium', 'high']]
            Importance of the event. (provider: tradingeconomics)
        group : Optional[Literal['interest_rate', 'inflation', 'bonds', 'consumer', 'gdp', 'government', 'housing', 'labour', 'markets', 'money', 'prices', 'trade', 'business']]
            Grouping of events. (provider: tradingeconomics)
        calendar_id : Optional[Union[int, str]]
            Get events by TradingEconomics Calendar ID. Multiple comma separated items allowed. (provider: tradingeconomics)

        Returns
        -------
        OBBject
            results : List[EconomicCalendar]
                Serializable results.
            provider : Optional[Literal['fmp', 'tradingeconomics']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EconomicCalendar
        ----------------
        date : Optional[datetime]
            The date of the data. 
        country : Optional[str]
            Country of event. 
        category : Optional[str]
            Category of event. 
        event : Optional[str]
            Event name. 
        importance : Optional[str]
            The importance level for the event. 
        source : Optional[str]
            Source of the data. 
        currency : Optional[str]
            Currency of the data. 
        unit : Optional[str]
            Unit of the data. 
        consensus : Optional[Union[str, float]]
            Average forecast among a representative group of economists. 
        previous : Optional[Union[str, float]]
            Value for the previous period after the revision (if revision is applicable). 
        revised : Optional[Union[str, float]]
            Revised previous value, if applicable. 
        actual : Optional[Union[str, float]]
            Latest released value. 
        change : Optional[float]
            Value change since previous. (provider: fmp)
        change_percent : Optional[float]
            Percentage change since previous. (provider: fmp)
        last_updated : Optional[datetime]
            Last updated timestamp. (provider: fmp);
            Last update of the data. (provider: tradingeconomics)
        created_at : Optional[datetime]
            Created at timestamp. (provider: fmp)
        forecast : Optional[Union[str, float]]
            TradingEconomics projections. (provider: tradingeconomics)
        reference : Optional[str]
            Abbreviated period for which released data refers to. (provider: tradingeconomics)
        reference_date : Optional[date]
            Date for the reference period. (provider: tradingeconomics)
        calendar_id : Optional[int]
            TradingEconomics Calendar ID. (provider: tradingeconomics)
        date_span : Optional[int]
            Date span of the event. (provider: tradingeconomics)
        symbol : Optional[str]
            TradingEconomics Symbol. (provider: tradingeconomics)
        ticker : Optional[str]
            TradingEconomics Ticker symbol. (provider: tradingeconomics)
        te_url : Optional[str]
            TradingEconomics URL path. (provider: tradingeconomics)
        source_url : Optional[str]
            Source URL. (provider: tradingeconomics)

        Examples
        --------
        >>> from openbb import obb
        >>> # By default, the calendar will be forward-looking.
        >>> obb.economy.calendar(provider='fmp')
        >>> obb.economy.calendar(provider='fmp', start_date='2020-03-01', end_date='2020-03-31')
        """  # noqa: E501

        return self._run(
            "/economy/calendar",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.calendar",
                        ("fmp", "tradingeconomics"),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"country": {"tradingeconomics": {"multiple_items_allowed": True, "choices": ["afghanistan", "albania", "algeria", "andorra", "angola", "antigua_and_barbuda", "argentina", "armenia", "aruba", "australia", "austria", "azerbaijan", "bahamas", "bahrain", "bangladesh", "barbados", "belarus", "belgium", "belize", "benin", "bermuda", "bhutan", "bolivia", "bosnia_and_herzegovina", "botswana", "brazil", "brunei", "bulgaria", "burkina_faso", "burundi", "cambodia", "cameroon", "canada", "cape_verde", "cayman_islands", "central_african_republic", "chad", "chile", "china", "colombia", "comoros", "congo", "costa_rica", "croatia", "cuba", "cyprus", "czech_republic", "denmark", "djibouti", "dominica", "dominican_republic", "east_timor", "ecuador", "egypt", "el_salvador", "equatorial_guinea", "eritrea", "estonia", "ethiopia", "euro_area", "faroe_islands", "fiji", "finland", "france", "gabon", "gambia", "georgia", "germany", "ghana", "greece", "grenada", "guatemala", "guinea", "guinea_bissau", "guyana", "haiti", "honduras", "hong_kong", "hungary", "iceland", "india", "indonesia", "iran", "iraq", "ireland", "isle_of_man", "israel", "italy", "ivory_coast", "jamaica", "japan", "jordan", "kazakhstan", "kenya", "kiribati", "kosovo", "kuwait", "kyrgyzstan", "laos", "latvia", "lebanon", "lesotho", "liberia", "libya", "liechtenstein", "lithuania", "luxembourg", "macao", "madagascar", "malawi", "malaysia", "maldives", "mali", "malta", "mauritania", "mauritius", "mexico", "moldova", "monaco", "mongolia", "montenegro", "morocco", "mozambique", "myanmar", "namibia", "nepal", "netherlands", "new_caledonia", "new_zealand", "nicaragua", "niger", "nigeria", "north_korea", "north_macedonia", "norway", "oman", "pakistan", "palestine", "panama", "papua_new_guinea", "paraguay", "peru", "philippines", "poland", "portugal", "puerto_rico", "qatar", "republic_of_the_congo", "romania", "russia", "rwanda", "samoa", "sao_tome_and_principe", "saudi_arabia", "senegal", "serbia", "seychelles", "sierra_leone", "singapore", "slovakia", "slovenia", "solomon_islands", "somalia", "south_africa", "south_korea", "south_sudan", "spain", "sri_lanka", "sudan", "suriname", "swaziland", "sweden", "switzerland", "syria", "taiwan", "tajikistan", "tanzania", "thailand", "togo", "tonga", "trinidad_and_tobago", "tunisia", "turkey", "turkmenistan", "uganda", "ukraine", "united_arab_emirates", "united_kingdom", "united_states", "uruguay", "uzbekistan", "vanuatu", "venezuela", "vietnam", "yemen", "zambia", "zimbabwe"]}}, "calendar_id": {"tradingeconomics": {"multiple_items_allowed": True, "choices": ["low", "medium", "high"]}}},
            )
        )

    @exception_handler
    @validate
    def central_bank_holdings(
        self,
        date: Annotated[Union[datetime.date, None, str], OpenBBField(description="A specific date to get data for.")] = None,
        provider: Annotated[Optional[Literal["federal_reserve"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve.")] = None,
        **kwargs
    ) -> OBBject:
        """Get the balance sheet holdings of a central bank.

        Parameters
        ----------
        date : Union[date, None, str]
            A specific date to get data for.
        provider : Optional[Literal['federal_reserve']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve.
        holding_type : Literal['all_agency', 'agency_debts', 'mbs', 'cmbs', 'all_treasury', 'bills', 'notesbonds', 'frn', 'tips']
            Type of holdings to return. (provider: federal_reserve)
        summary : bool
            If True, returns historical weekly summary by holding type. This parameter takes priority over other parameters. (provider: federal_reserve)
        cusip : Optional[str]
             Multiple comma separated items allowed.
        wam : bool
            If True, returns weighted average maturity aggregated by agency or treasury securities. This parameter takes priority over `holding_type`, `cusip`, and `monthly`. (provider: federal_reserve)
        monthly : bool
            If True, returns historical data for all Treasury securities at a monthly interval. This parameter takes priority over other parameters, except `wam`. Only valid when `holding_type` is set to: 'all_treasury', 'bills', 'notesbonds', 'frn', 'tips'. (provider: federal_reserve)

        Returns
        -------
        OBBject
            results : List[CentralBankHoldings]
                Serializable results.
            provider : Optional[Literal['federal_reserve']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CentralBankHoldings
        -------------------
        date : date
            The date of the data. 
        security_type : Optional[str]
            Type of security - i.e. TIPs, FRNs, etc. (provider: federal_reserve)
        description : Optional[str]
            Description of the security. Only returned for Agency securities. (provider: federal_reserve)
        is_aggreated : Optional[Literal['Y']]
            Whether the security is aggregated. Only returned for Agency securities. (provider: federal_reserve)
        cusip : Optional[str]
            
        issuer : Optional[str]
            Issuer of the security. (provider: federal_reserve)
        maturity_date : Optional[date]
            Maturity date of the security. (provider: federal_reserve)
        term : Optional[str]
            Term of the security. Only returned for Agency securities. (provider: federal_reserve)
        face_value : Optional[float]
            Current face value of the security (Thousands of $USD). Current face value of the securities, which is the remaining principal balance of the securities. (provider: federal_reserve)
        par_value : Optional[float]
            Par value of the security (Thousands of $USD). Changes in par may reflect primary and secondary market transactions and/or custodial account activity. (provider: federal_reserve)
        coupon : Optional[float]
            Coupon rate of the security. (provider: federal_reserve)
        spread : Optional[float]
            Spread to the current reference rate, as determined at each security's initial auction. (provider: federal_reserve)
        percent_outstanding : Optional[float]
            Total percent of the outstanding CUSIP issuance. (provider: federal_reserve)
        bills : Optional[float]
            Treasury bills amount (Thousands of $USD). Only returned when 'summary' is True. (provider: federal_reserve)
        frn : Optional[float]
            Floating rate Treasury notes amount (Thousands of $USD). Only returned when 'summary' is True. (provider: federal_reserve)
        notes_and_bonds : Optional[float]
            Treasuy Notes and bonds amount (Thousands of $USD). Only returned when 'summary' is True. (provider: federal_reserve)
        tips : Optional[float]
            Treasury inflation-protected securities amount (Thousands of $USD). Only returned when 'summary' is True. (provider: federal_reserve)
        mbs : Optional[float]
            Mortgage-backed securities amount (Thousands of $USD). Only returned when 'summary' is True. (provider: federal_reserve)
        cmbs : Optional[float]
            Commercial mortgage-backed securities amount (Thousands of $USD). Only returned when 'summary' is True. (provider: federal_reserve)
        agencies : Optional[float]
            Agency securities amount (Thousands of $USD). Only returned when 'summary' is True. (provider: federal_reserve)
        total : Optional[float]
            Total SOMA holdings amount (Thousands of $USD). Only returned when 'summary' is True. (provider: federal_reserve)
        tips_inflation_compensation : Optional[float]
            Treasury inflation-protected securities inflation compensation amount (Thousands of $USD). Only returned when 'summary' is True. (provider: federal_reserve)
        change_prior_week : Optional[float]
            Change in SOMA holdings from the prior week (Thousands of $USD). (provider: federal_reserve)
        change_prior_year : Optional[float]
            Change in SOMA holdings from the prior year (Thousands of $USD). (provider: federal_reserve)

        Examples
        --------
        >>> from openbb import obb
        >>> # The default is the latest Treasury securities held by the Federal Reserve.
        >>> obb.economy.central_bank_holdings(provider='federal_reserve')
        >>> # Get historical summaries of the Fed's holdings.
        >>> obb.economy.central_bank_holdings(provider='federal_reserve', summary=True)
        >>> # Get the balance sheet holdings as-of a historical date.
        >>> obb.economy.central_bank_holdings(provider='federal_reserve', date='2019-05-21')
        >>> # Use the `holding_type` parameter to select Agency securities, or specific categories or Treasury securities.
        >>> obb.economy.central_bank_holdings(provider='federal_reserve', holding_type='agency_debts')
        """  # noqa: E501

        return self._run(
            "/economy/central_bank_holdings",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.central_bank_holdings",
                        ("federal_reserve",),
                    )
                },
                standard_params={
                    "date": date,
                },
                extra_params=kwargs,
                info={"cusip": {"federal_reserve": {"multiple_items_allowed": True, "choices": None}}},
            )
        )

    @exception_handler
    @validate
    def composite_leading_indicator(
        self,
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["oecd"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.")] = None,
        **kwargs
    ) -> OBBject:
        """Get the composite leading indicator (CLI).

        It is designed to provide early signals of turning points
        in business cycles showing fluctuation of the economic activity around its long term potential level.

        CLIs show short-term economic movements in qualitative rather than quantitative terms.
        

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.
        country : Union[Literal['g20', 'g7', 'asia5', 'north_america', 'europe4', 'australia', 'brazil', 'canada', 'china', 'france', 'germany', 'india', 'indonesia', 'italy', 'japan', 'mexico', 'south_africa', 'south_korea', 'spain', 'turkey', 'united_kingdom', 'united_states', 'all'], str]
            Country to get the CLI for, default is G20. Multiple comma separated items allowed. (provider: oecd)
        adjustment : Literal['amplitude', 'normalized']
            Adjustment of the data, either 'amplitude' or 'normalized'. Default is amplitude. (provider: oecd)
        growth_rate : bool
            Return the 1-year growth rate (%) of the CLI, default is False. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[CompositeLeadingIndicator]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CompositeLeadingIndicator
        -------------------------
        date : date
            The date of the data. 
        value : Optional[float]
            CLI value 
        country : str
            Country for the CLI value. 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.composite_leading_indicator(provider='oecd')
        >>> obb.economy.composite_leading_indicator(country='all', provider='oecd', growth_rate=True)
        """  # noqa: E501

        return self._run(
            "/economy/composite_leading_indicator",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.composite_leading_indicator",
                        ("oecd",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"country": {"oecd": {"multiple_items_allowed": True, "choices": ["g20", "g7", "asia5", "north_america", "europe4", "australia", "brazil", "canada", "china", "france", "germany", "india", "indonesia", "italy", "japan", "mexico", "spain", "south_africa", "south_korea", "turkey", "united_states", "united_kingdom", "all"]}}},
            )
        )

    @exception_handler
    @validate
    def country_profile(
        self,
        country: Annotated[Union[str, List[str]], OpenBBField(description="The country to get data. Multiple comma separated items allowed for provider(s): econdb.")],
        provider: Annotated[Optional[Literal["econdb"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb.")] = None,
        **kwargs
    ) -> OBBject:
        """Get a profile of country statistics and economic indicators.

        Parameters
        ----------
        country : Union[str, List[str]]
            The country to get data. Multiple comma separated items allowed for provider(s): econdb.
        provider : Optional[Literal['econdb']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb.
        latest : bool
            If True, return only the latest data. If False, return all available data for each indicator. (provider: econdb)
        use_cache : bool
            If True, the request will be cached for one day.Using cache is recommended to avoid needlessly requesting the same data. (provider: econdb)

        Returns
        -------
        OBBject
            results : List[CountryProfile]
                Serializable results.
            provider : Optional[Literal['econdb']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CountryProfile
        --------------
        country : str
            
        population : Optional[int]
            Population. 
        gdp_usd : Optional[float]
            Gross Domestic Product, in billions of USD. 
        gdp_qoq : Optional[float]
            GDP growth quarter-over-quarter change, as a normalized percent. 
        gdp_yoy : Optional[float]
            GDP growth year-over-year change, as a normalized percent. 
        cpi_yoy : Optional[float]
            Consumer Price Index year-over-year change, as a normalized percent. 
        core_yoy : Optional[float]
            Core Consumer Price Index year-over-year change, as a normalized percent. 
        retail_sales_yoy : Optional[float]
            Retail Sales year-over-year change, as a normalized percent. 
        industrial_production_yoy : Optional[float]
            Industrial Production year-over-year change, as a normalized percent. 
        policy_rate : Optional[float]
            Short term policy rate, as a normalized percent. 
        yield_10y : Optional[float]
            10-year government bond yield, as a normalized percent. 
        govt_debt_gdp : Optional[float]
            Government debt as a percent (normalized) of GDP. 
        current_account_gdp : Optional[float]
            Current account balance as a percent (normalized) of GDP. 
        jobless_rate : Optional[float]
            Unemployment rate, as a normalized percent. 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.country_profile(provider='econdb', country='united_kingdom')
        >>> # Enter the country as the full name, or iso code. If `latest` is False, the complete history for each series is returned.
        >>> obb.economy.country_profile(country='united_states,jp', latest=False, provider='econdb')
        """  # noqa: E501

        return self._run(
            "/economy/country_profile",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.country_profile",
                        ("econdb",),
                    )
                },
                standard_params={
                    "country": country,
                },
                extra_params=kwargs,
                info={"country": {"econdb": {"multiple_items_allowed": True, "choices": None}}},
            )
        )

    @exception_handler
    @validate
    def cpi(
        self,
        country: Annotated[Union[str, List[str]], OpenBBField(description="The country to get data. Multiple comma separated items allowed for provider(s): fred, oecd.")] = "united_states",
        transform: Annotated[Literal["index", "yoy", "period"], OpenBBField(description="Transformation of the CPI data. Period represents the change since previous. Defaults to change from one year ago (yoy).")] = "yoy",
        frequency: Annotated[Literal["annual", "quarter", "monthly"], OpenBBField(description="The frequency of the data.")] = "monthly",
        harmonized: Annotated[bool, OpenBBField(description="If true, returns harmonized data.")] = False,
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["fred", "oecd"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred, oecd.")] = None,
        **kwargs
    ) -> OBBject:
        """Get Consumer Price Index (CPI).

        Returns either the rescaled index value, or a rate of change (inflation).
        

        Parameters
        ----------
        country : Union[str, List[str]]
            The country to get data. Multiple comma separated items allowed for provider(s): fred, oecd.
        transform : Literal['index', 'yoy', 'period']
            Transformation of the CPI data. Period represents the change since previous. Defaults to change from one year ago (yoy).
        frequency : Literal['annual', 'quarter', 'monthly']
            The frequency of the data.
        harmonized : bool
            If true, returns harmonized data.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred', 'oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred, oecd.
        expenditure : Literal['total', 'all', 'actual_rentals', 'alcoholic_beverages_tobacco_narcotics', 'all_non_food_non_energy', 'clothing_footwear', 'communication', 'education', 'electricity_gas_other_fuels', 'energy', 'overall_excl_energy_food_alcohol_tobacco', 'food_non_alcoholic_beverages', 'fuels_lubricants_personal', 'furniture_household_equipment', 'goods', 'housing', 'housing_excluding_rentals', 'housing_water_electricity_gas', 'health', 'imputed_rentals', 'maintenance_repair_dwelling', 'miscellaneous_goods_services', 'recreation_culture', 'residuals', 'restaurants_hotels', 'services_less_housing', 'services_less_house_excl_rentals', 'services', 'transport', 'water_supply_other_services']
            Expenditure component of CPI. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[ConsumerPriceIndex]
                Serializable results.
            provider : Optional[Literal['fred', 'oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ConsumerPriceIndex
        ------------------
        date : date
            The date of the data. 
        country : str
            None
        value : float
            CPI index value or period change. 
        expenditure : Optional[str]
            Expenditure component of CPI. (provider: oecd)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.cpi(country='japan,china,turkey', provider='fred')
        >>> # Use the `transform` parameter to define the reference period for the change in values. Default is YoY.
        >>> obb.economy.cpi(country='united_states,united_kingdom', transform='period', provider='oecd')
        """  # noqa: E501

        return self._run(
            "/economy/cpi",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.cpi",
                        ("fred", "oecd"),
                    )
                },
                standard_params={
                    "country": country,
                    "transform": transform,
                    "frequency": frequency,
                    "harmonized": harmonized,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"country": {"fred": {"multiple_items_allowed": True, "choices": ["australia", "austria", "belgium", "brazil", "bulgaria", "canada", "chile", "china", "croatia", "cyprus", "czech_republic", "denmark", "estonia", "euro_area", "finland", "france", "germany", "greece", "hungary", "iceland", "india", "indonesia", "ireland", "israel", "italy", "japan", "korea", "latvia", "lithuania", "luxembourg", "malta", "mexico", "netherlands", "new_zealand", "norway", "poland", "portugal", "romania", "russian_federation", "slovak_republic", "slovakia", "slovenia", "south_africa", "spain", "sweden", "switzerland", "turkey", "united_kingdom", "united_states"]}, "oecd": {"multiple_items_allowed": True, "choices": ["G20", "G7", "argentina", "australia", "austria", "belgium", "brazil", "canada", "chile", "china", "colombia", "costa_rica", "czech_republic", "denmark", "estonia", "euro_area_20", "europe", "european_union_27", "finland", "france", "germany", "greece", "hungary", "iceland", "india", "indonesia", "ireland", "israel", "italy", "japan", "korea", "latvia", "lithuania", "luxembourg", "mexico", "netherlands", "new_zealand", "norway", "oecd_total", "poland", "portugal", "russia", "saudi_arabia", "slovak_republic", "slovenia", "south_africa", "spain", "sweden", "switzerland", "turkey", "united_kingdom", "united_states", "all"]}}},
            )
        )

    @exception_handler
    @validate
    def export_destinations(
        self,
        country: Annotated[Union[str, List[str]], OpenBBField(description="The country to get data. Multiple comma separated items allowed for provider(s): econdb.")],
        provider: Annotated[Optional[Literal["econdb"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb.")] = None,
        **kwargs
    ) -> OBBject:
        """Get top export destinations by country from the UN Comtrade International Trade Statistics Database.

        Parameters
        ----------
        country : Union[str, List[str]]
            The country to get data. Multiple comma separated items allowed for provider(s): econdb.
        provider : Optional[Literal['econdb']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb.

        Returns
        -------
        OBBject
            results : List[ExportDestinations]
                Serializable results.
            provider : Optional[Literal['econdb']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ExportDestinations
        ------------------
        origin_country : str
            The country of origin. 
        destination_country : str
            The destination country. 
        value : Union[float, int]
            The value of the export. 
        units : Optional[str]
            The units of measurement for the value. (provider: econdb)
        title : Optional[str]
            The title of the data. (provider: econdb)
        footnote : Optional[str]
            The footnote for the data. (provider: econdb)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.export_destinations(provider='econdb', country='us')
        """  # noqa: E501

        return self._run(
            "/economy/export_destinations",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.export_destinations",
                        ("econdb",),
                    )
                },
                standard_params={
                    "country": country,
                },
                extra_params=kwargs,
                info={"country": {"econdb": {"multiple_items_allowed": True, "choices": None}}},
            )
        )

    @exception_handler
    @validate
    def export_destinations(
        self,
        country: Annotated[
            Union[str, List[str]],
            OpenBBField(
                description="The country to get data. Multiple comma separated items allowed for provider(s): econdb."
            ),
        ],
        provider: Annotated[
            Optional[Literal["econdb"]],
            OpenBBField(
                description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb."
            ),
        ] = None,
        **kwargs
    ) -> OBBject:
        """Get top export destinations by country from the UN Comtrade International Trade Statistics Database.

        Parameters
        ----------
        country : Union[str, List[str]]
            The country to get data. Multiple comma separated items allowed for provider(s): econdb.
        provider : Optional[Literal['econdb']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb.

        Returns
        -------
        OBBject
            results : List[ExportDestinations]
                Serializable results.
            provider : Optional[Literal['econdb']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ExportDestinations
        ------------------
        origin_country : str
            The country of origin.
        destination_country : str
            The destination country.
        value : Union[float, int]
            The value of the export.
        units : Optional[str]
            The units of measurement for the value. (provider: econdb)
        title : Optional[str]
            The title of the data. (provider: econdb)
        footnote : Optional[str]
            The footnote for the data. (provider: econdb)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.export_destinations(provider='econdb', country='us')
        """  # noqa: E501

        return self._run(
            "/economy/export_destinations",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.export_destinations",
                        ("econdb",),
                    )
                },
                standard_params={
                    "country": country,
                },
                extra_params=kwargs,
                info={
                    "country": {
                        "econdb": {"multiple_items_allowed": True, "choices": None}
                    }
                },
            )
        )

    @exception_handler
    @validate
    def fred_regional(
        self,
        symbol: Annotated[str, OpenBBField(description="Symbol to get data for.")],
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        limit: Annotated[Optional[int], OpenBBField(description="The number of data entries to return.")] = 100000,
        provider: Annotated[Optional[Literal["fred"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.")] = None,
        **kwargs
    ) -> OBBject:
        """Query the Geo Fred API for regional economic data by series group.

        The series group ID is found by using `fred_search` and the `series_id` parameter.
        

        Parameters
        ----------
        symbol : str
            Symbol to get data for.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        limit : Optional[int]
            The number of data entries to return.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        is_series_group : bool
            When True, the symbol provided is for a series_group, else it is for a series ID. (provider: fred)
        region_type : Optional[Literal['bea', 'msa', 'frb', 'necta', 'state', 'country', 'county', 'censusregion']]
            The type of regional data. Parameter is only valid when `is_series_group` is True. (provider: fred)
        season : Literal['sa', 'nsa', 'ssa']
            The seasonal adjustments to the data. Parameter is only valid when `is_series_group` is True. (provider: fred)
        units : Optional[str]
            The units of the data. This should match the units returned from searching by series ID. An incorrect field will not necessarily return an error. Parameter is only valid when `is_series_group` is True. (provider: fred)
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'd', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]
            Frequency aggregation to convert high frequency data to lower frequency.
                
            None = No change
                
            a = Annual
                
            q = Quarterly
                
            m = Monthly
                
            w = Weekly
                
            d = Daily
                
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
                This parameter has no affect if the frequency parameter is not set.
                
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
            results : List[FredRegional]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        FredRegional
        ------------
        date : date
            The date of the data. 
        region : Optional[str]
            The name of the region. (provider: fred)
        code : Optional[Union[int, str]]
            The code of the region. (provider: fred)
        value : Optional[Union[int, float]]
            The obersvation value. The units are defined in the search results by series ID. (provider: fred)
        series_id : Optional[str]
            The individual series ID for the region. (provider: fred)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.fred_regional(symbol='NYICLAIMS', provider='fred')
        >>> # With a date, time series data is returned.
        >>> obb.economy.fred_regional(symbol='NYICLAIMS', start_date='2021-01-01', end_date='2021-12-31', limit=10, provider='fred')
        """  # noqa: E501

        return self._run(
            "/economy/fred_regional",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.fred_regional",
                        ("fred",),
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
    def fred_release_table(
        self,
        release_id: Annotated[str, OpenBBField(description="The ID of the release. Use `fred_search` to find releases.")],
        element_id: Annotated[Optional[str], OpenBBField(description="The element ID of a specific table in the release.")] = None,
        date: Annotated[Union[str, datetime.date, None, List[Union[str, datetime.date, None]]], OpenBBField(description="A specific date to get data for. Multiple comma separated items allowed for provider(s): fred.")] = None,
        provider: Annotated[Optional[Literal["fred"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.")] = None,
        **kwargs
    ) -> OBBject:
        """Get economic release data by ID and/or element from FRED.

        Parameters
        ----------
        release_id : str
            The ID of the release. Use `fred_search` to find releases.
        element_id : Optional[str]
            The element ID of a specific table in the release.
        date : Union[str, date, None, List[Union[str, date, None]]]
            A specific date to get data for. Multiple comma separated items allowed for provider(s): fred.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.

        Returns
        -------
        OBBject
            results : List[FredReleaseTable]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        FredReleaseTable
        ----------------
        date : Optional[date]
            The date of the data. 
        level : Optional[int]
            The indentation level of the element. 
        element_type : Optional[str]
            The type of the element. 
        line : Optional[int]
            The line number of the element. 
        element_id : Optional[str]
            The element id in the parent/child relationship. 
        parent_id : Optional[str]
            The parent id in the parent/child relationship. 
        children : Optional[str]
            The element_id of each child, as a comma-separated string. 
        symbol : Optional[str]
            Symbol representing the entity requested in the data. 
        name : Optional[str]
            The name of the series. 
        value : Optional[float]
            The reported value of the series. 

        Examples
        --------
        >>> from openbb import obb
        >>> # Get the top-level elements of a release by not supplying an element ID.
        >>> obb.economy.fred_release_table(release_id='50', provider='fred')
        >>> # Drill down on a specific section of the release.
        >>> obb.economy.fred_release_table(release_id='50', element_id='4880', provider='fred')
        >>> # Drill down on a specific table of the release.
        >>> obb.economy.fred_release_table(release_id='50', element_id='4881', provider='fred')
        """  # noqa: E501

        return self._run(
            "/economy/fred_release_table",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.fred_release_table",
                        ("fred",),
                    )
                },
                standard_params={
                    "release_id": release_id,
                    "element_id": element_id,
                    "date": date,
                },
                extra_params=kwargs,
                info={"date": {"fred": {"multiple_items_allowed": True, "choices": None}}},
            )
        )

    @exception_handler
    @validate
    def fred_search(
        self,
        query: Annotated[Optional[str], OpenBBField(description="The search word(s).")] = None,
        provider: Annotated[Optional[Literal["fred"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.")] = None,
        **kwargs
    ) -> OBBject:
        """Search for FRED series or economic releases by ID or string.

        This does not return the observation values, only the metadata.
        Use this function to find series IDs for `fred_series()`.
        

        Parameters
        ----------
        query : Optional[str]
            The search word(s).
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        is_release : Optional[bool]
            Is release?  If True, other search filter variables are ignored. If no query text or release_id is supplied, this defaults to True. (provider: fred)
        release_id : Optional[Union[int, str]]
            A specific release ID to target. (provider: fred)
        limit : Optional[int]
            The number of data entries to return. (1-1000) (provider: fred)
        offset : Optional[Annotated[int, Ge(ge=0)]]
            Offset the results in conjunction with limit. (provider: fred)
        filter_variable : Optional[Literal['frequency', 'units', 'seasonal_adjustment']]
            Filter by an attribute. (provider: fred)
        filter_value : Optional[str]
            String value to filter the variable by.  Used in conjunction with filter_variable. (provider: fred)
        tag_names : Optional[str]
            A semicolon delimited list of tag names that series match all of.  Example: 'japan;imports' Multiple comma separated items allowed. (provider: fred)
        exclude_tag_names : Optional[str]
            A semicolon delimited list of tag names that series match none of.  Example: 'imports;services'. Requires that variable tag_names also be set to limit the number of matching series. Multiple comma separated items allowed. (provider: fred)
        series_id : Optional[str]
            A FRED Series ID to return series group information for. This returns the required information to query for regional data. Not all series that are in FRED have geographical data. Entering a value for series_id will override all other parameters. Multiple series_ids can be separated by commas. (provider: fred)

        Returns
        -------
        OBBject
            results : List[FredSearch]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        FredSearch
        ----------
        release_id : Optional[Union[int, str]]
            The release ID for queries. 
        series_id : Optional[str]
            The series ID for the item in the release. 
        name : Optional[str]
            The name of the release. 
        title : Optional[str]
            The title of the series. 
        observation_start : Optional[date]
            The date of the first observation in the series. 
        observation_end : Optional[date]
            The date of the last observation in the series. 
        frequency : Optional[str]
            The frequency of the data. 
        frequency_short : Optional[str]
            Short form of the data frequency. 
        units : Optional[str]
            The units of the data. 
        units_short : Optional[str]
            Short form of the data units. 
        seasonal_adjustment : Optional[str]
            The seasonal adjustment of the data. 
        seasonal_adjustment_short : Optional[str]
            Short form of the data seasonal adjustment. 
        last_updated : Optional[datetime]
            The datetime of the last update to the data. 
        notes : Optional[str]
            Description of the release. 
        press_release : Optional[bool]
            If the release is a press release. 
        url : Optional[str]
            URL to the release. 
        popularity : Optional[int]
            Popularity of the series (provider: fred)
        group_popularity : Optional[int]
            Group popularity of the release (provider: fred)
        region_type : Optional[str]
            The region type of the series. (provider: fred)
        series_group : Optional[Union[int, str]]
            The series group ID of the series. This value is used to query for regional data. (provider: fred)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.fred_search(provider='fred')
        """  # noqa: E501

        return self._run(
            "/economy/fred_search",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.fred_search",
                        ("fred",),
                    )
                },
                standard_params={
                    "query": query,
                },
                extra_params=kwargs,
                info={"tag_names": {"fred": {"multiple_items_allowed": True, "choices": None}}, "exclude_tag_names": {"fred": {"multiple_items_allowed": True, "choices": None}}},
            )
        )

    @exception_handler
    @validate
    def fred_series(
        self,
        symbol: Annotated[Union[str, List[str]], OpenBBField(description="Symbol to get data for. Multiple comma separated items allowed for provider(s): fred.")],
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        limit: Annotated[Optional[int], OpenBBField(description="The number of data entries to return.")] = 100000,
        provider: Annotated[Optional[Literal["fred", "intrinio"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred, intrinio.")] = None,
        **kwargs
    ) -> OBBject:
        """Get data by series ID from FRED.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. Multiple comma separated items allowed for provider(s): fred.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        limit : Optional[int]
            The number of data entries to return.
        provider : Optional[Literal['fred', 'intrinio']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred, intrinio.
        frequency : Optional[Literal['a', 'q', 'm', 'w', 'd', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'wesa', 'bwew', 'bwem']]
            Frequency aggregation to convert high frequency data to lower frequency.
                
            None = No change
                
            a = Annual
                
            q = Quarterly
                
            m = Monthly
                
            w = Weekly
                
            d = Daily
                
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
                This parameter has no affect if the frequency parameter is not set.
                
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
        all_pages : Optional[bool]
            Returns all pages of data from the API call at once. (provider: intrinio)
        sleep : Optional[float]
            Time to sleep between requests to avoid rate limiting. (provider: intrinio)

        Returns
        -------
        OBBject
            results : List[FredSeries]
                Serializable results.
            provider : Optional[Literal['fred', 'intrinio']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        FredSeries
        ----------
        date : date
            The date of the data. 
        value : Optional[float]
            Value of the index. (provider: intrinio)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.fred_series(symbol='NFCI', provider='fred')
        >>> # Multiple series can be passed in as a list.
        >>> obb.economy.fred_series(symbol='NFCI,STLFSI4', provider='fred')
        >>> # Use the `transform` parameter to transform the data as change, log, or percent change.
        >>> obb.economy.fred_series(symbol='CBBTCUSD', transform='pc1', provider='fred')
        """  # noqa: E501

        return self._run(
            "/economy/fred_series",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.fred_series",
                        ("fred", "intrinio"),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                    "limit": limit,
                },
                extra_params=kwargs,
                info={"symbol": {"fred": {"multiple_items_allowed": True, "choices": None}}},
            )
        )

    @property
    def gdp(self):
        # pylint: disable=import-outside-toplevel
        from . import economy_gdp

        return economy_gdp.ROUTER_economy_gdp(command_runner=self._command_runner)

    @exception_handler
    @validate
    def house_price_index(
        self,
        country: Annotated[Union[str, List[str]], OpenBBField(description="The country to get data. Multiple comma separated items allowed for provider(s): oecd.")] = "united_states",
        frequency: Annotated[Literal["monthly", "quarter", "annual"], OpenBBField(description="The frequency of the data.")] = "quarter",
        transform: Annotated[Literal["index", "yoy", "period"], OpenBBField(description="Transformation of the CPI data. Period represents the change since previous. Defaults to change from one year ago (yoy).")] = "index",
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["oecd"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.")] = None,
        **kwargs
    ) -> OBBject:
        """Get the House Price Index by country from the OECD Short-Term Economics Statistics.

        Parameters
        ----------
        country : Union[str, List[str]]
            The country to get data. Multiple comma separated items allowed for provider(s): oecd.
        frequency : Literal['monthly', 'quarter', 'annual']
            The frequency of the data.
        transform : Literal['index', 'yoy', 'period']
            Transformation of the CPI data. Period represents the change since previous. Defaults to change from one year ago (yoy).
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.

        Returns
        -------
        OBBject
            results : List[HousePriceIndex]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        HousePriceIndex
        ---------------
        date : Optional[date]
            The date of the data. 
        country : Optional[str]
            
        value : Optional[float]
            Share price index value. 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.house_price_index(provider='oecd')
        >>> # Multiple countries can be passed in as a list.
        >>> obb.economy.house_price_index(country='united_kingdom,germany', frequency='quarter', provider='oecd')
        """  # noqa: E501

        return self._run(
            "/economy/house_price_index",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.house_price_index",
                        ("oecd",),
                    )
                },
                standard_params={
                    "country": country,
                    "frequency": frequency,
                    "transform": transform,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"country": {"oecd": {"multiple_items_allowed": True, "choices": ["G20", "G7", "argentina", "australia", "austria", "belgium", "brazil", "bulgaria", "canada", "chile", "china", "colombia", "costa_rica", "croatia", "czech_republic", "denmark", "estonia", "euro_area_20", "euro_area_19", "europe", "european_union_27", "finland", "france", "germany", "greece", "hungary", "iceland", "india", "indonesia", "ireland", "israel", "italy", "japan", "korea", "latvia", "lithuania", "luxembourg", "mexico", "netherlands", "new_zealand", "norway", "oecd_total", "poland", "portugal", "romania", "russia", "saudi_arabia", "slovak_republic", "slovenia", "south_africa", "spain", "sweden", "switzerland", "turkey", "united_kingdom", "united_states", "all"]}}},
            )
        )

    @exception_handler
    @validate
    @deprecated(
        "This endpoint will be removed in a future version. Use, `/economy/interest_rates`, instead. Deprecated in OpenBB Platform V4.3 to be removed in V4.5.",
        category=OpenBBDeprecationWarning,
    )
    def immediate_interest_rate(
        self,
        country: Annotated[Union[str, List[str]], OpenBBField(description="The country to get data. Multiple comma separated items allowed for provider(s): oecd.")] = "united_states",
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["oecd"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.")] = None,
        **kwargs
    ) -> OBBject:
        """Get immediate interest rates by country.

        Parameters
        ----------
        country : Union[str, List[str]]
            The country to get data. Multiple comma separated items allowed for provider(s): oecd.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.
        frequency : Literal['monthly', 'quarter', 'annual']
            The frequency of the data. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[ImmediateInterestRate]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        ImmediateInterestRate
        ---------------------
        date : Optional[date]
            The date of the data. 
        country : Optional[str]
            Country for which interest rate is given 
        value : Optional[float]
            Immediate interest rates, call money, interbank rate. 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.immediate_interest_rate(provider='oecd')
        >>> # Multiple countries can be passed in as a list.
        >>> obb.economy.immediate_interest_rate(country='united_kingdom,germany', frequency='monthly', provider='oecd')
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn("This endpoint will be removed in a future version. Use, `/economy/interest_rates`, instead. Deprecated in OpenBB Platform V4.3 to be removed in V4.5.", category=DeprecationWarning, stacklevel=2)

        return self._run(
            "/economy/immediate_interest_rate",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.immediate_interest_rate",
                        ("oecd",),
                    )
                },
                standard_params={
                    "country": country,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"country": {"oecd": {"multiple_items_allowed": True, "choices": ["belgium", "bulgaria", "brazil", "ireland", "mexico", "indonesia", "new_zealand", "japan", "united_kingdom", "france", "chile", "canada", "netherlands", "united_states", "south_korea", "norway", "austria", "south_africa", "denmark", "switzerland", "hungary", "luxembourg", "australia", "germany", "sweden", "iceland", "turkey", "greece", "israel", "czech_republic", "latvia", "slovenia", "poland", "estonia", "lithuania", "portugal", "costa_rica", "slovakia", "finland", "spain", "romania", "russia", "euro_area19", "colombia", "italy", "india", "china", "croatia", "all"]}}},
            )
        )

    @exception_handler
    @validate
    def indicators(
        self,
        symbol: Annotated[Union[str, List[str]], OpenBBField(description="Symbol to get data for. The base symbol for the indicator (e.g. GDP, CPI, etc.). Multiple comma separated items allowed for provider(s): econdb.")],
        country: Annotated[Union[str, None, List[Optional[str]]], OpenBBField(description="The country to get data. The country represented by the indicator, if available. Multiple comma separated items allowed for provider(s): econdb.")] = None,
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["econdb"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb.")] = None,
        **kwargs
    ) -> OBBject:
        """Get economic indicators by country and indicator.

        Parameters
        ----------
        symbol : Union[str, List[str]]
            Symbol to get data for. The base symbol for the indicator (e.g. GDP, CPI, etc.). Multiple comma separated items allowed for provider(s): econdb.
        country : Union[str, None, List[Optional[str]]]
            The country to get data. The country represented by the indicator, if available. Multiple comma separated items allowed for provider(s): econdb.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['econdb']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: econdb.
        transform : Optional[Literal['toya', 'tpop', 'tusd', 'tpgp']]
            The transformation to apply to the data, default is None.
        
            tpop: Change from previous period
            toya: Change from one year ago
            tusd: Values as US dollars
            tpgp: Values as a percent of GDP
        
            Only 'tpop' and 'toya' are applicable to all indicators. Applying transformations across multiple indicators/countries may produce unexpected results.
            This is because not all indicators are compatible with all transformations, and the original units and scale differ between entities.
            `tusd` should only be used where values are currencies. (provider: econdb)
        frequency : Literal['annual', 'quarter', 'month']
            The frequency of the data, default is 'quarter'. Only valid when 'symbol' is 'main'. (provider: econdb)
        use_cache : bool
            If True, the request will be cached for one day. Using cache is recommended to avoid needlessly requesting the same data. (provider: econdb)

        Returns
        -------
        OBBject
            results : List[EconomicIndicators]
                Serializable results.
            provider : Optional[Literal['econdb']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        EconomicIndicators
        ------------------
        date : date
            The date of the data. 
        symbol_root : Optional[str]
            The root symbol for the indicator (e.g. GDP). 
        symbol : Optional[str]
            Symbol representing the entity requested in the data. 
        country : Optional[str]
            The country represented by the data. 
        value : Optional[Union[int, float]]
            

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.indicators(provider='econdb', symbol='PCOCO')
        >>> # Enter the country as the full name, or iso code. Use `available_indicators()` to get a list of supported indicators from EconDB.
        >>> obb.economy.indicators(symbol='CPI', country='united_states,jp', provider='econdb')
        >>> # Use the `main` symbol to get the group of main indicators for a country.
        >>> obb.economy.indicators(provider='econdb', symbol='main', country='eu')
        """  # noqa: E501

        return self._run(
            "/economy/indicators",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.indicators",
                        ("econdb",),
                    )
                },
                standard_params={
                    "symbol": symbol,
                    "country": country,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"symbol": {"econdb": {"multiple_items_allowed": True, "choices": None}}, "country": {"econdb": {"multiple_items_allowed": True, "choices": None}}},
            )
        )

    @exception_handler
    @validate
    def interest_rates(
        self,
        country: Annotated[Union[str, List[str]], OpenBBField(description="The country to get data. Multiple comma separated items allowed for provider(s): oecd.")] = "united_states",
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["oecd"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.")] = None,
        **kwargs
    ) -> OBBject:
        """Get interest rates by country(s) and duration.
        Most OECD countries publish short-term, a long-term, and immediate rates monthly.
        

        Parameters
        ----------
        country : Union[str, List[str]]
            The country to get data. Multiple comma separated items allowed for provider(s): oecd.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.
        duration : Literal['immediate', 'short', 'long']
            Duration of the interest rate. 'immediate' is the overnight rate, 'short' is the 3-month rate, and 'long' is the 10-year rate. (provider: oecd)
        frequency : Literal['monthly', 'quarter', 'annual']
            Frequency to get interest rate for for. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[CountryInterestRates]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        CountryInterestRates
        --------------------
        date : Optional[date]
            The date of the data. 
        value : Optional[float]
            The interest rate value. 
        country : Optional[str]
            Country for which the interest rate is given. 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.interest_rates(provider='oecd')
        >>> # For OECD, duration can be 'immediate', 'short', or 'long'. Default is 'short', which is the 3-month rate. Overnight interbank rate is 'immediate', and 10-year rate is 'long'.
        >>> obb.economy.interest_rates(provider='oecd', country='all', duration='immediate', frequency='quarter')
        >>> # Multiple countries can be passed in as a list.
        >>> obb.economy.interest_rates(duration='long', country='united_kingdom,germany', frequency='monthly', provider='oecd')
        """  # noqa: E501

        return self._run(
            "/economy/interest_rates",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.interest_rates",
                        ("oecd",),
                    )
                },
                standard_params={
                    "country": country,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"country": {"oecd": {"multiple_items_allowed": True, "choices": ["belgium", "bulgaria", "brazil", "ireland", "mexico", "indonesia", "new_zealand", "japan", "united_kingdom", "france", "chile", "canada", "netherlands", "united_states", "south_korea", "norway", "austria", "south_africa", "denmark", "switzerland", "hungary", "luxembourg", "australia", "germany", "sweden", "iceland", "turkey", "greece", "israel", "czech_republic", "latvia", "slovenia", "poland", "estonia", "lithuania", "portugal", "costa_rica", "slovakia", "finland", "spain", "romania", "russia", "euro_area19", "colombia", "italy", "india", "china", "croatia", "all"]}}, "duration": {"oecd": {"multiple_items_allowed": False, "choices": ["immediate", "short", "long"]}}, "frequency": {"oecd": {"multiple_items_allowed": False, "choices": ["monthly", "quarter", "annual"]}}},
            )
        )

    @exception_handler
    @validate
    @deprecated(
        "This endpoint will be removed in a future version. Use, `/economy/interest_rates`, instead. Deprecated in OpenBB Platform V4.3 to be removed in V4.5.",
        category=OpenBBDeprecationWarning,
    )
    def long_term_interest_rate(
        self,
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["oecd"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.")] = None,
        **kwargs
    ) -> OBBject:
        """Get Long-term interest rates that refer to government bonds maturing in ten years.

        Rates are mainly determined by the price charged by the lender, the risk from the borrower and the
        fall in the capital value. Long-term interest rates are generally averages of daily rates,
        measured as a percentage. These interest rates are implied by the prices at which the government bonds are
        traded on financial markets, not the interest rates at which the loans were issued.
        In all cases, they refer to bonds whose capital repayment is guaranteed by governments.
        Long-term interest rates are one of the determinants of business investment.
        Low long-term interest rates encourage investment in new equipment and high interest rates discourage it.
        Investment is, in turn, a major source of economic growth.
        

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.
        country : Literal['belgium', 'bulgaria', 'brazil', 'ireland', 'mexico', 'indonesia', 'new_zealand', 'japan', 'united_kingdom', 'france', 'chile', 'canada', 'netherlands', 'united_states', 'south_korea', 'norway', 'austria', 'south_africa', 'denmark', 'switzerland', 'hungary', 'luxembourg', 'australia', 'germany', 'sweden', 'iceland', 'turkey', 'greece', 'israel', 'czech_republic', 'latvia', 'slovenia', 'poland', 'estonia', 'lithuania', 'portugal', 'costa_rica', 'slovakia', 'finland', 'spain', 'romania', 'russia', 'euro_area19', 'colombia', 'italy', 'india', 'china', 'croatia', 'all']
            Country to get interest rate for. (provider: oecd)
        frequency : Literal['monthly', 'quarterly', 'annual']
            Frequency to get interest rate for for. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[LTIR]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        LTIR
        ----
        date : Optional[date]
            The date of the data. 
        value : Optional[float]
            Interest rate (given as a whole number, i.e 10=10%) 
        country : Optional[str]
            Country for which interest rate is given 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.long_term_interest_rate(provider='oecd')
        >>> obb.economy.long_term_interest_rate(country='all', frequency='quarterly', provider='oecd')
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn("This endpoint will be removed in a future version. Use, `/economy/interest_rates`, instead. Deprecated in OpenBB Platform V4.3 to be removed in V4.5.", category=DeprecationWarning, stacklevel=2)

        return self._run(
            "/economy/long_term_interest_rate",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.long_term_interest_rate",
                        ("oecd",),
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
    def money_measures(
        self,
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        adjusted: Annotated[Optional[bool], OpenBBField(description="Whether to return seasonally adjusted data.")] = True,
        provider: Annotated[Optional[Literal["federal_reserve"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve.")] = None,
        **kwargs
    ) -> OBBject:
        """Get Money Measures (M1/M2 and components).

        The Federal Reserve publishes as part of the H.6 Release.
        

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        adjusted : Optional[bool]
            Whether to return seasonally adjusted data.
        provider : Optional[Literal['federal_reserve']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve.

        Returns
        -------
        OBBject
            results : List[MoneyMeasures]
                Serializable results.
            provider : Optional[Literal['federal_reserve']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        MoneyMeasures
        -------------
        month : date
            The date of the data. 
        M1 : float
            Value of the M1 money supply in billions. 
        M2 : float
            Value of the M2 money supply in billions. 
        currency : Optional[float]
            Value of currency in circulation in billions. 
        demand_deposits : Optional[float]
            Value of demand deposits in billions. 
        retail_money_market_funds : Optional[float]
            Value of retail money market funds in billions. 
        other_liquid_deposits : Optional[float]
            Value of other liquid deposits in billions. 
        small_denomination_time_deposits : Optional[float]
            Value of small denomination time deposits in billions. 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.money_measures(provider='federal_reserve')
        >>> obb.economy.money_measures(adjusted=False, provider='federal_reserve')
        """  # noqa: E501

        return self._run(
            "/economy/money_measures",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.money_measures",
                        ("federal_reserve",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                    "adjusted": adjusted,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def pce(
        self,
        date: Annotated[Union[str, datetime.date, None, List[Union[str, datetime.date, None]]], OpenBBField(description="A specific date to get data for. Default is the latest report. Multiple comma separated items allowed for provider(s): fred.")] = None,
        provider: Annotated[Optional[Literal["fred"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.")] = None,
        **kwargs
    ) -> OBBject:
        """Get Personal Consumption Expenditures (PCE) reports.

        Parameters
        ----------
        date : Union[str, date, None, List[Union[str, date, None]]]
            A specific date to get data for. Default is the latest report. Multiple comma separated items allowed for provider(s): fred.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        category : Literal['personal_income', 'wages_by_industry', 'real_pce_percent_change', 'real_pce_quantity_index', 'pce_price_index', 'pce_dollars', 'real_pce_chained_dollars', 'pce_price_percent_change']
            The category to query. (provider: fred)

        Returns
        -------
        OBBject
            results : List[PersonalConsumptionExpenditures]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        PersonalConsumptionExpenditures
        -------------------------------
        date : date
            The date of the data. 
        symbol : str
            Symbol representing the entity requested in the data. 
        value : float
            
        name : Optional[str]
            The name of the series. (provider: fred)
        element_id : Optional[str]
            The element id in the parent/child relationship. (provider: fred)
        parent_id : Optional[str]
            The parent id in the parent/child relationship. (provider: fred)
        children : Optional[str]
            The element_id of each child, as a comma-separated string. (provider: fred)
        level : Optional[int]
            The indentation level of the element. (provider: fred)
        line : Optional[int]
            The line number of the series in the table. (provider: fred)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.pce(provider='fred')
        >>> # Get reports for multiple dates, entered as a comma-separated string.
        >>> obb.economy.pce(provider='fred', date='2024-05-01,2024-04-01,2023-05-01', category='pce_price_index')
        """  # noqa: E501

        return self._run(
            "/economy/pce",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.pce",
                        ("fred",),
                    )
                },
                standard_params={
                    "date": date,
                },
                extra_params=kwargs,
                info={"date": {"fred": {"multiple_items_allowed": True, "choices": None}}},
            )
        )

    @exception_handler
    @validate
    def primary_dealer_positioning(
        self,
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["federal_reserve"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve.")] = None,
        **kwargs
    ) -> OBBject:
        """Get Primary dealer positioning statistics.

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['federal_reserve']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: federal_reserve.
        category : Literal['treasuries', 'bills', 'coupons', 'notes', 'tips', 'mbs', 'cmbs', 'municipal', 'corporate', 'commercial_paper', 'corporate_ig', 'corporate_junk', 'abs']
            The category of asset to return, defaults to 'treasuries'. (provider: federal_reserve)

        Returns
        -------
        OBBject
            results : List[PrimaryDealerPositioning]
                Serializable results.
            provider : Optional[Literal['federal_reserve']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        PrimaryDealerPositioning
        ------------------------
        date : date
            The date of the data. 
        symbol : str
            Symbol representing the entity requested in the data. 
        value : Optional[int]
            The reported value of the net position (long - short), in millions of $USD. (provider: federal_reserve)
        name : Optional[str]
            Short name for the series. (provider: federal_reserve)
        title : Optional[str]
            Title of the series. (provider: federal_reserve)

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.primary_dealer_positioning(provider='federal_reserve')
        >>> obb.economy.primary_dealer_positioning(category='abs', provider='federal_reserve')
        """  # noqa: E501

        return self._run(
            "/economy/primary_dealer_positioning",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.primary_dealer_positioning",
                        ("federal_reserve",),
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
    def retail_prices(
        self,
        item: Annotated[Optional[str], OpenBBField(description="The item or basket of items to query.")] = None,
        country: Annotated[str, OpenBBField(description="The country to get data.")] = "united_states",
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["fred"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.")] = None,
        **kwargs
    ) -> OBBject:
        """Get retail prices for common items.

        Parameters
        ----------
        item : Optional[str]
            The item or basket of items to query.
        country : str
            The country to get data.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['fred']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fred.
        region : Literal['all_city', 'northeast', 'midwest', 'south', 'west']
            The region to get average price levels for. (provider: fred)
        frequency : Literal['annual', 'quarter', 'monthly']
            The frequency of the data. (provider: fred)
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
            results : List[RetailPrices]
                Serializable results.
            provider : Optional[Literal['fred']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        RetailPrices
        ------------
        date : Optional[date]
            The date of the data. 
        symbol : Optional[str]
            Symbol representing the entity requested in the data. 
        country : Optional[str]
            
        description : Optional[str]
            Description of the item. 
        value : Optional[float]
            Price, or change in price, per unit. 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.retail_prices(provider='fred')
        >>> # The price of eggs in the northeast census region.
        >>> obb.economy.retail_prices(item='eggs', region='northeast', provider='fred')
        >>> # The percentage change in price, from one-year ago, of various meats, US City Average.
        >>> obb.economy.retail_prices(item='meats', transform='pc1', provider='fred')
        """  # noqa: E501

        return self._run(
            "/economy/retail_prices",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.retail_prices",
                        ("fred",),
                    )
                },
                standard_params={
                    "item": item,
                    "country": country,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def risk_premium(
        self,
        provider: Annotated[Optional[Literal["fmp"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp.")] = None,
        **kwargs
    ) -> OBBject:
        """Get Market Risk Premium by country.

        Parameters
        ----------
        provider : Optional[Literal['fmp']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: fmp.

        Returns
        -------
        OBBject
            results : List[RiskPremium]
                Serializable results.
            provider : Optional[Literal['fmp']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        RiskPremium
        -----------
        country : str
            Market country. 
        continent : Optional[str]
            Continent of the country. 
        total_equity_risk_premium : Optional[Annotated[float, Gt(gt=0)]]
            Total equity risk premium for the country. 
        country_risk_premium : Optional[Annotated[float, Ge(ge=0)]]
            Country-specific risk premium. 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.risk_premium(provider='fmp')
        """  # noqa: E501

        return self._run(
            "/economy/risk_premium",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.risk_premium",
                        ("fmp",),
                    )
                },
                standard_params={
                },
                extra_params=kwargs,
            )
        )

    @exception_handler
    @validate
    def share_price_index(
        self,
        country: Annotated[Union[str, List[str]], OpenBBField(description="The country to get data. Multiple comma separated items allowed for provider(s): oecd.")] = "united_states",
        frequency: Annotated[Literal["monthly", "quarter", "annual"], OpenBBField(description="The frequency of the data.")] = "monthly",
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["oecd"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.")] = None,
        **kwargs
    ) -> OBBject:
        """Get the Share Price Index by country from the OECD Short-Term Economics Statistics.

        Parameters
        ----------
        country : Union[str, List[str]]
            The country to get data. Multiple comma separated items allowed for provider(s): oecd.
        frequency : Literal['monthly', 'quarter', 'annual']
            The frequency of the data.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.

        Returns
        -------
        OBBject
            results : List[SharePriceIndex]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        SharePriceIndex
        ---------------
        date : Optional[date]
            The date of the data. 
        country : Optional[str]
            
        value : Optional[float]
            Share price index value. 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.share_price_index(provider='oecd')
        >>> # Multiple countries can be passed in as a list.
        >>> obb.economy.share_price_index(country='united_kingdom,germany', frequency='quarter', provider='oecd')
        """  # noqa: E501

        return self._run(
            "/economy/share_price_index",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.share_price_index",
                        ("oecd",),
                    )
                },
                standard_params={
                    "country": country,
                    "frequency": frequency,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"country": {"oecd": {"multiple_items_allowed": True, "choices": ["G20", "G7", "all", "argentina", "australia", "austria", "belgium", "brazil", "bulgaria", "canada", "chile", "china", "colombia", "costa_rica", "croatia", "czech_republic", "denmark", "estonia", "euro_area_19", "euro_area_20", "europe", "european_union_27", "finland", "france", "germany", "greece", "hungary", "iceland", "india", "indonesia", "ireland", "israel", "italy", "japan", "korea", "latvia", "lithuania", "luxembourg", "mexico", "netherlands", "new_zealand", "norway", "oecd_total", "poland", "portugal", "romania", "russia", "saudi_arabia", "slovak_republic", "slovenia", "south_africa", "spain", "sweden", "switzerland", "turkey", "united_kingdom", "united_states"]}}},
            )
        )

    @exception_handler
    @validate
    @deprecated(
        "This endpoint will be removed in a future version. Use, `/economy/interest_rates`, instead. Deprecated in OpenBB Platform V4.3 to be removed in V4.5.",
        category=OpenBBDeprecationWarning,
    )
    def short_term_interest_rate(
        self,
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["oecd"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.")] = None,
        **kwargs
    ) -> OBBject:
        """Get Short-term interest rates.

        They are the rates at which short-term borrowings are effected between
        financial institutions or the rate at which short-term government paper is issued or traded in the market.

        Short-term interest rates are generally averages of daily rates, measured as a percentage.
        Short-term interest rates are based on three-month money market rates where available.
        Typical standardised names are "money market rate" and "treasury bill rate".
        

        Parameters
        ----------
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.
        country : Literal['belgium', 'bulgaria', 'brazil', 'ireland', 'mexico', 'indonesia', 'new_zealand', 'japan', 'united_kingdom', 'france', 'chile', 'canada', 'netherlands', 'united_states', 'south_korea', 'norway', 'austria', 'south_africa', 'denmark', 'switzerland', 'hungary', 'luxembourg', 'australia', 'germany', 'sweden', 'iceland', 'turkey', 'greece', 'israel', 'czech_republic', 'latvia', 'slovenia', 'poland', 'estonia', 'lithuania', 'portugal', 'costa_rica', 'slovakia', 'finland', 'spain', 'romania', 'russia', 'euro_area19', 'colombia', 'italy', 'india', 'china', 'croatia', 'all']
            Country to get interest rate for. (provider: oecd)
        frequency : Literal['monthly', 'quarterly', 'annual']
            Frequency to get interest rate for for. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[STIR]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        STIR
        ----
        date : Optional[date]
            The date of the data. 
        value : Optional[float]
            Interest rate (given as a whole number, i.e 10=10%) 
        country : Optional[str]
            Country for which interest rate is given 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.short_term_interest_rate(provider='oecd')
        >>> obb.economy.short_term_interest_rate(country='all', frequency='quarterly', provider='oecd')
        """  # noqa: E501

        simplefilter("always", DeprecationWarning)
        warn("This endpoint will be removed in a future version. Use, `/economy/interest_rates`, instead. Deprecated in OpenBB Platform V4.3 to be removed in V4.5.", category=DeprecationWarning, stacklevel=2)

        return self._run(
            "/economy/short_term_interest_rate",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.short_term_interest_rate",
                        ("oecd",),
                    )
                },
                standard_params={
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
            )
        )

    @property
    def survey(self):
        # pylint: disable=import-outside-toplevel
        from . import economy_survey

        return economy_survey.ROUTER_economy_survey(command_runner=self._command_runner)

    @exception_handler
    @validate
    def unemployment(
        self,
        country: Annotated[Union[str, List[str]], OpenBBField(description="The country to get data. Multiple comma separated items allowed for provider(s): oecd.")] = "united_states",
        frequency: Annotated[Literal["monthly", "quarter", "annual"], OpenBBField(description="The frequency of the data.")] = "monthly",
        start_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="Start date of the data, in YYYY-MM-DD format.")] = None,
        end_date: Annotated[Union[datetime.date, None, str], OpenBBField(description="End date of the data, in YYYY-MM-DD format.")] = None,
        provider: Annotated[Optional[Literal["oecd"]], OpenBBField(description="The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.")] = None,
        **kwargs
    ) -> OBBject:
        """Get global unemployment data.

        Parameters
        ----------
        country : Union[str, List[str]]
            The country to get data. Multiple comma separated items allowed for provider(s): oecd.
        frequency : Literal['monthly', 'quarter', 'annual']
            The frequency of the data.
        start_date : Union[date, None, str]
            Start date of the data, in YYYY-MM-DD format.
        end_date : Union[date, None, str]
            End date of the data, in YYYY-MM-DD format.
        provider : Optional[Literal['oecd']]
            The provider to use, by default None. If None, the priority list configured in the settings is used. Default priority: oecd.
        sex : Literal['total', 'male', 'female']
            Sex to get unemployment for. (provider: oecd)
        age : Literal['total', '15-24', '25+']
            Age group to get unemployment for. Total indicates 15 years or over (provider: oecd)
        seasonal_adjustment : bool
            Whether to get seasonally adjusted unemployment. Defaults to False. (provider: oecd)

        Returns
        -------
        OBBject
            results : List[Unemployment]
                Serializable results.
            provider : Optional[Literal['oecd']]
                Provider name.
            warnings : Optional[List[Warning_]]
                List of warnings.
            chart : Optional[Chart]
                Chart object.
            extra : Dict[str, Any]
                Extra info.

        Unemployment
        ------------
        date : Optional[date]
            The date of the data. 
        country : Optional[str]
            Country for which unemployment rate is given 
        value : Optional[float]
            Unemployment rate, as a normalized percent. 

        Examples
        --------
        >>> from openbb import obb
        >>> obb.economy.unemployment(provider='oecd')
        >>> obb.economy.unemployment(country='all', frequency='quarter', provider='oecd')
        >>> # Demographics for the statistics are selected with the `age` parameter.
        >>> obb.economy.unemployment(country='all', frequency='quarter', age='total', provider='oecd')
        """  # noqa: E501

        return self._run(
            "/economy/unemployment",
            **filter_inputs(
                provider_choices={
                    "provider": self._get_provider(
                        provider,
                        "economy.unemployment",
                        ("oecd",),
                    )
                },
                standard_params={
                    "country": country,
                    "frequency": frequency,
                    "start_date": start_date,
                    "end_date": end_date,
                },
                extra_params=kwargs,
                info={"country": {"oecd": {"multiple_items_allowed": True, "choices": ["all", "australia", "austria", "belgium", "canada", "chile", "colombia", "costa_rica", "czech_republic", "denmark", "estonia", "euro_area20", "european_union27_2020", "finland", "france", "g7", "germany", "greece", "hungary", "iceland", "ireland", "israel", "italy", "japan", "korea", "latvia", "lithuania", "luxembourg", "mexico", "netherlands", "new_zealand", "norway", "oecd", "poland", "portugal", "russia", "slovakia", "slovenia", "south_africa", "spain", "sweden", "switzerland", "turkey", "united_kingdom", "united_states"]}}},
            )
        )
