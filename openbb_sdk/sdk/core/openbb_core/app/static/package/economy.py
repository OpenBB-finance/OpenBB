### THIS FILE IS AUTO-GENERATED. DO NOT EDIT. ###

import datetime
import typing
from typing import List, Literal, Optional, Union

from pydantic import validate_arguments

import openbb_core.app.model.command_context
import openbb_core.app.model.results.empty
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.static.container import Container
from openbb_core.app.static.filters import filter_call, filter_inputs, filter_output


class CLASS_economy(Container):
    @filter_call
    @validate_arguments
    def corecpi(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """CORECPI."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/corecpi",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def const(
        self,
        index: Literal["nasdaq", "sp500", "dowjones"] = "dowjones",
        chart: bool = False,
        provider: Optional[Literal["fmp"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """

        Available providers: fmp,

        Standard
        ========

        Parameter
        ---------
        index : Literal['nasdaq', 'sp500', 'dowjones']
            The index for which we want to fetch the constituents. Default is 'dowjones'.


        Returns
        -------
        symbol : str
            The symbol of the constituent company in the index.
        name : str
            The name of the constituent company in the index.
        sector : str
            The sector the constituent company in the index belongs to.
        subSector : str
            The sub-sector the constituent company in the index belongs to.
        headQuarter : str
            The location of the headquarter of the constituent company in the index.
        dateFirstAdded : date
            The date the constituent company was added to the index.
        cik : int
            The Central Index Key of the constituent company in the index.
        founded : date
            The founding year of the constituent company in the index.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/list-of-dow-companies-api/
                https://site.financialmodelingprep.com/developer/docs/list-of-sp-500-companies-api/
                https://site.financialmodelingprep.com/developer/docs/list-of-nasdaq-companies-api/

        Parameter
        ---------
        All fields are standardized.
        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "index": index,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/const",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def cpi(
        self,
        countries: List[
            Literal[
                "australia",
                "austria",
                "belgium",
                "brazil",
                "bulgaria",
                "canada",
                "chile",
                "china",
                "croatia",
                "cyprus",
                "czech_republic",
                "denmark",
                "estonia",
                "euro_area",
                "finland",
                "france",
                "germany",
                "greece",
                "hungary",
                "iceland",
                "india",
                "indonesia",
                "ireland",
                "israel",
                "italy",
                "japan",
                "korea",
                "latvia",
                "lithuania",
                "luxembourg",
                "malta",
                "mexico",
                "netherlands",
                "new_zealand",
                "norway",
                "poland",
                "portugal",
                "romania",
                "russian_federation",
                "slovak_republic",
                "slovakia",
                "slovenia",
                "south_africa",
                "spain",
                "sweden",
                "switzerland",
                "turkey",
                "united_kingdom",
                "united_states",
            ]
        ],
        units: Literal["growth_previous", "growth_same", "index_2015"] = "growth_same",
        frequency: Literal["monthly", "quarterly", "annual"] = "monthly",
        harmonized: bool = False,
        start_date: Union[datetime.date, None, str] = None,
        end_date: Union[datetime.date, None, str] = None,
        chart: bool = False,
        provider: Optional[Literal["fred"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """CPI.

        Available providers: fred,

        Standard
        ========
        When other provders are added, this will probably need less strict types

        Parameter
        ---------
        countries: List[CPI_COUNTRIES]
            The country or countries you want to see.
        units: List[CPI_UNITS]
            The units you want to see, can be "growth_previous", "growth_same" or "index_2015".
        frequency: List[CPI_FREQUENCY]
            The frequency you want to see, either "annual", monthly" or "quarterly".
        harmonized: bool
            Whether you wish to obtain harmonized data.
        start_date: Optional[date]
            Start date, formatted YYYY-MM-DD
        end_date: Optional[date]
            End date, formatted YYYY-MM-DD


        Returns
        -------
        Documentation not available.


        fred
        ====
        When other provders are added, this will probably need less strict types

        Parameter
        ---------
        countries: List[CPI_COUNTRIES]
            The country or countries you want to see.
        units: List[CPI_UNITS]
            The units you want to see, can be "growth_previous", "growth_same" or "index_2015".
        frequency: List[CPI_FREQUENCY]
            The frequency you want to see, either "annual", monthly" or "quarterly".
        harmonized: bool
            Whether you wish to obtain harmonized data.
        start_date: Optional[date]
            Start date, formatted YYYY-MM-DD
        end_date: Optional[date]
            End date, formatted YYYY-MM-DD
        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "countries": countries,
                "units": units,
                "frequency": frequency,
                "harmonized": harmonized,
                "start_date": start_date,
                "end_date": end_date,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/cpi",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def cpi_options(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Get the options for v3 cpi(options=True)"""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/cpi_options",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def index(
        self,
        symbol: str,
        chart: bool = False,
        provider: Optional[Literal["fmp", "polygon"]] = None,
        **kwargs
    ) -> CommandOutput[typing.List]:
        """Get OHLCV data for an index.

        Available providers: fmp, polygon

        Standard
        ========

        Parameter
        ---------
        symbol : str
            The symbol of the index.


        Returns
        -------
        open : PositiveFloat
            The open price of the stock.
        high : PositiveFloat
            The high price of the stock.
        low : PositiveFloat
            The low price of the stock.
        close : PositiveFloat
            The close price of the stock.
        date : datetime
            The date of the stock.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/#Historical-stock-index-prices

        Parameter
        ---------
        interval : Literal['1min', '5min', '15min', '30min', '1hour', '4hour']
            The interval of the index data to fetch. Default is '1hour`.


        polygon
        =======

        Source: https://polygon.io/docs/indices/getting-started

        Parameters
        ----------
        start_date : Union[date, datetime]
            The start date of the query.
        end_date : Union[date, datetime]
            The end date of the query.
        timespan : Timespan, optional
            The timespan of the query, by default Timespan.day
        sort : Literal["asc", "desc"], optional
            The sort order of the query, by default "desc"
        limit : PositiveInt, optional
            The limit of the query, by default 49999
        adjusted : bool, optional
            Whether the query is adjusted, by default True
        multiplier : PositiveInt, optional
            The multiplier of the query, by default 1
        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={
                "symbol": symbol,
            },
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/index",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def available_indices(
        self, chart: bool = False, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> CommandOutput[typing.List]:
        """AVAILABLE_INDICES.

        Available providers: fmp,

        Standard
        ========


        Returns the major indices from Dow Jones, Nasdaq and, S&P 500.

        Returns
        -------
        symbol : str
            The symbol of the index.
        name : Optional[str]
            The name of the index.
        currency : Optional[str]
            The currency the index is traded in.
        stock_exchange : str
            The stock exchange where the index is listed.
        exchange_short_name : str
            The short name of the stock exchange where the index is listed.

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/#Historical-stock-index-prices

        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/available_indices",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def risk(
        self, chart: bool = False, provider: Optional[Literal["fmp"]] = None, **kwargs
    ) -> CommandOutput[typing.List]:
        """Market Risk Premium.

        Available providers: fmp,

        Standard
        ========


        Returns
        -------
        country : str
        continent : str
        totalEquityRiskPremium : PositiveFloat
        countryRiskPremium : PositiveFloat

        fmp
        ===

        Source: https://site.financialmodelingprep.com/developer/docs/market-risk-premium-api/

        """
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            standard_params={},
            extra_params=kwargs,
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/risk",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def macro(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """Query EconDB for macro data."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/macro",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def macro_countries(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """MACRO_COUNTRIES."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/macro_countries",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def macro_parameters(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """MACRO_PARAMETERS."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/macro_parameters",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def balance(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """BALANCE."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/balance",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def bigmac(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """BIGMAC."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/bigmac",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def country_codes(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """COUNTRY_CODES."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/country_codes",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def currencies(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """CURRENCIES."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/currencies",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def debt(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """DEBT."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/debt",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def events(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """EVENTS."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/events",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fgdp(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """FGDP."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/fgdp",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fred(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """FRED."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/fred",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def fred_search(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """FRED Search (was fred_notes)."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/fred_search",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def futures(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """FUTURES. 2 sources"""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/futures",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def gdp(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """GDP."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/gdp",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def glbonds(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """GLBONDS."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/glbonds",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def indices(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """INDICES."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/indices",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def overview(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """OVERVIEW."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/overview",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def perfmap(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """PERFMAP."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/perfmap",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def performance(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """PERFORMANCE."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/performance",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def revenue(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """REVENUE."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/revenue",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def rgdp(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """RGDP."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/rgdp",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def rtps(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """RTPS."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/rtps",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def search_index(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """SEARCH_INDEX."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/search_index",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def spending(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """SPENDING."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/spending",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def trust(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """TRUST."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/trust",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def usbonds(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """USBONDS."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/usbonds",
            **inputs,
        ).output

        return filter_output(o)

    @filter_call
    @validate_arguments
    def valuation(
        self,
        chart: bool = False,
        provider: Optional[Literal["benzinga", "fmp", "polygon", "fred"]] = None,
    ) -> CommandOutput[openbb_core.app.model.results.empty.Empty]:
        """VALUATION."""
        inputs = filter_inputs(
            provider_choices={
                "provider": provider,
            },
            chart=chart,
        )

        o = self._command_runner_session.run(
            "/economy/valuation",
            **inputs,
        ).output

        return filter_output(o)
