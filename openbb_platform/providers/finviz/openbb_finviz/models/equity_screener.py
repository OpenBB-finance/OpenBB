"""Finviz Equity Screener Model."""

# pylint: disable=unused-argument,too-many-statements,too-many-branches,too-many-locals

from typing import Any, Dict, List, Literal, Optional, Union
from warnings import warn

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_screener import (
    EquityScreenerData,
    EquityScreenerQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_finviz.utils.screener_helper import (
    EXCHANGE_MAP,
    INDEX_MAP,
    INDUSTRY_MAP,
    MARKET_CAP_MAP,
    RECOMMENDATION_MAP,
    SECTOR_MAP,
    SIGNALS,
    SIGNALS_DESC_STR,
    MarketCap,
    Recommendation,
    Sectors,
)
from pydantic import Field, field_validator


class FinvizEquityScreenerQueryParams(EquityScreenerQueryParams):
    """Finviz Equity Screener Query Params."""

    __json_schema_extra__ = {
        "metric": {
            "choices": [
                "overview",
                "valuation",
                "financial",
                "ownership",
                "performance",
                "technical",
            ],
        },
        "signal": {"choices": SIGNALS},
        "exchange": {"choices": list(EXCHANGE_MAP)},
        "index": {"choices": list(INDEX_MAP)},
        "sector": {"choices": list(SECTOR_MAP)},
        "industry": {"choices": list(INDUSTRY_MAP)},
        "market_cap": {"choices": list(MARKET_CAP_MAP)},
        "recommendation": {"choices": list(RECOMMENDATION_MAP)},
    }

    metric: Literal[
        "overview",
        "valuation",
        "financial",
        "ownership",
        "performance",
        "technical",
    ] = Field(
        default="overview",
        description="The data group to return, default is 'overview'.",
    )
    exchange: Literal["all", "amex", "nasdaq", "nyse"] = Field(
        default="all", description="Filter by exchange."
    )
    index: Literal["all", "dow", "nasdaq", "sp500", "russell"] = Field(
        default="all",
        description="Filter by index.",
    )
    sector: Sectors = Field(
        default="all",
        description="Filter by sector.",
    )
    industry: Optional[str] = Field(
        default="all",
        description="Filter by industry.",
    )
    mktcap: MarketCap = Field(
        default="all",
        description="Filter by market cap."
        + "\n    Mega - > 200B"
        + "\n    Large - 10B - 200B"
        + "\n    Mid - 2B - 10B"
        + "\n    Small - 300M - 2B"
        + "\n    Micro - 50M - 300M"
        + "\n    Nano - < 50M",
    )
    recommendation: Recommendation = Field(
        default="all", description="Filter by analyst recommendation."
    )
    signal: Optional[str] = Field(
        default=None,
        description="The Finviz screener signal to use."
        + " When no parameters are provided, the screener defaults to 'top_gainers'."
        + f" Available signals are:{SIGNALS_DESC_STR}",
    )
    preset: Optional[str] = Field(
        default=None,
        description="A configured preset file to use for the query."
        + " This overrides all other query parameters except 'metric', and 'limit'."
        + " Presets (.ini text files) can be created and modified in the '~/OpenBBUserData/finviz/presets' directory."
        + " If the path does not exist, it will be created and populated with the default presets on the first run."
        + " Refer to the file, 'screener_template.ini', for the format and options."
        + "\n\nNote: Syntax of parameters in preset files must follow the template file exactly "
        + " - i.e, Analyst Recom. = Strong Buy (1)",
    )
    filters_dict: Optional[Union[Dict, str]] = Field(
        default=None,
        kw_only=True,
        description="A formatted dictionary, or serialized JSON string, of additional filters to apply to the query."
        + " This parameter can be used as an alternative to preset files, and is ignored when a preset is supplied."
        + " Invalid entries will raise an error. Syntax should follow the 'screener_template.ini' file.",
    )
    limit: Optional[int] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("limit", ""),
    )

    @field_validator("signal", mode="before", check_fields=False)
    @classmethod
    def validate_signal(cls, v):
        """Validate the signal."""
        if v is not None and v not in SIGNALS:
            raise OpenBBError(
                f"Invalid signal '{v}'. Available signals are:\n{SIGNALS_DESC_STR}"
            )
        return v if v else None

    @field_validator("industry", mode="before", check_fields=False)
    @classmethod
    def validate_industry(cls, v):
        """Validate the industry."""
        if v is not None and v not in INDUSTRY_MAP:
            raise OpenBBError(
                f"Invalid industry '{v}'. Available industries are:\n{', '.join(INDUSTRY_MAP)}"
            )
        return v if v else None

    @field_validator("preset", mode="before", check_fields=False)
    @classmethod
    def validate_preset(cls, v):
        """Check to reject running template file."""
        if v is not None and v == "screener_template":
            raise OpenBBError(
                f"Invalid preset '{v}'. Please rename the file to use as a preset."
            )
        return v if v else None

    @field_validator("filters_dict", mode="before", check_fields=False)
    @classmethod
    def validate_filters_dict(cls, v):
        """Validate the filters_dict."""
        if isinstance(v, str):
            # pylint: disable=import-outside-toplevel
            import json

            try:
                v = json.loads(v)
            except json.JSONDecodeError as e:
                raise OpenBBError(f"Invalid JSON format for 'filters_dict': {e}") from e
        if v is not None and not isinstance(v, dict):
            raise OpenBBError(
                "Invalid 'filters_dict' format. Must be a dictionary or serialized JSON string."
            )

        return v


class FinvizEquityScreenerData(EquityScreenerData):
    """Finviz Equity Screener Data. Actual returned data varies by the 'metric' parameter."""

    __alias_dict__ = {
        "symbol": "Ticker",
        "name": "Company",
        "earnings_date": "Earnings",
        "sector": "Sector",
        "industry": "Industry",
        "country": "Country",
        "shares_outstanding": "Outstanding",
        "shares_float": "Float",
        "short_interest": "Float Short",
        "short_ratio": "Short Ratio",
        "insider_ownership": "Insider Own",
        "insider_ownership_change": "Insider Trans",
        "institutional_ownership": "Inst Own",
        "institutional_ownership_change": "Inst Trans",
        "analyst_recommendation": "Recom",
        "beta": "Beta",
        "market_cap": "Market Cap",
        "price": "Price",
        "change_percent": "Change",
        "change_from_open": "from Open",
        "gap": "Gap",
        "year_high_percent": "52W High",
        "year_low_percent": "52W Low",
        "sma20_percent": "SMA20",
        "sma50_percent": "SMA50",
        "sma200_percent": "SMA200",
        "rsi": "RSI",
        "volume": "Volume",
        "volume_avg": "Avg Volume",
        "volume_relative": "Rel Volume",
        "average_true_range": "ATR",
        "price_change_1w": "Perf Week",
        "price_change_1m": "Perf Month",
        "price_change_3m": "Perf Quart",
        "price_change_6m": "Perf Half",
        "price_change_1y": "Perf Year",
        "price_change_ytd": "Perf YTD",
        "volatility_1w": "Volatility W",
        "volatility_1m": "Volatility M",
        "price_to_earnings": "P/E",
        "forward_pe": "Fwd P/E",
        "peg_ratio": "PEG",
        "price_to_sales": "P/S",
        "price_to_book": "P/B",
        "price_to_cash": "P/C",
        "price_to_free_cash_flow": "P/FCF",
        "eps_growth_past_1y": "EPS this Y",
        "eps_growth_next_1y": "EPS next Y",
        "eps_growth_past_5y": "EPS past 5Y",
        "eps_growth_next_5y": "EPS next 5Y",
        "sales_growth_past_5y": "Sales past 5Y",
        "dividend_yield": "Dividend",
        "return_on_assets": "ROA",
        "return_on_equity": "ROE",
        "return_on_investment": "ROI",
        "current_ratio": "Curr R",
        "quick_ratio": "Quick R",
        "long_term_debt_to_equity": "LTDebt/Eq",
        "debt_to_equity": "Debt/Eq",
        "gross_margin": "Gross M",
        "operating_margin": "Oper M",
        "profit_margin": "Profit M",
    }

    earnings_date: Optional[str] = Field(
        default=None,
        description="Earnings date, where 'a' and 'b' mean after and before market close, respectively.",
    )
    country: Optional[str] = Field(
        default=None,
        description="Country of the company.",
    )
    sector: Optional[str] = Field(
        default=None,
        description="Sector of the company.",
    )
    industry: Optional[str] = Field(
        default=None,
        description="Industry of the company.",
    )
    beta: Optional[float] = Field(
        default=None,
        description="Beta of the stock.",
    )
    analyst_recommendation: Optional[float] = Field(
        default=None,
        description="Analyst's mean recommendation. (1=Buy 5=Sell).",
    )
    market_cap: Optional[float] = Field(
        default=None,
        description="Market capitalization of the company.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    price: Optional[float] = Field(
        default=None,
        description="Price of a share.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="Price change percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    change_from_open: Optional[float] = Field(
        default=None,
        description="Price change percentage, from the opening price.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    gap: Optional[float] = Field(
        default=None,
        description="Price gap percentage, from the previous close.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: Optional[Union[int, float]] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
    volume_avg: Optional[Union[int, float]] = Field(
        default=None,
        description="3-month average daily volume.",
    )
    volume_relative: Optional[float] = Field(
        default=None,
        description="Current volume relative to the average.",
    )
    average_true_range: Optional[float] = Field(
        default=None,
        description="Average true range (14).",
        json_schema_extra={"x-unit_measurement:": "currency"},
    )
    price_change_1w: Optional[float] = Field(
        default=None,
        description="One-week price return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    price_change_1m: Optional[float] = Field(
        default=None,
        description="One-month price return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    price_change_3m: Optional[float] = Field(
        default=None,
        description="Three-month price return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    price_change_6m: Optional[float] = Field(
        default=None,
        description="Six-month price return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    price_change_1y: Optional[float] = Field(
        default=None,
        description="One-year price return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    price_change_ytd: Optional[float] = Field(
        default=None,
        description="Year-to-date price return.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volatility_1w: Optional[float] = Field(
        default=None,
        description="One-week volatility.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volatility_1m: Optional[float] = Field(
        default=None,
        description="One-month volatility.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_high_percent: Optional[float] = Field(
        default=None,
        description="Percent difference from current price to the 52-week high.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    year_low_percent: Optional[float] = Field(
        default=None,
        description="Percent difference from current price to the 52-week low.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    sma20_percent: Optional[float] = Field(
        default=None,
        description="Percent difference from current price to the 20-day simple moving average.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    sma50_percent: Optional[float] = Field(
        default=None,
        description="Percent difference from current price to the 50-day simple moving average.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    sma200_percent: Optional[float] = Field(
        default=None,
        description="Percent difference from current price to the 200-day simple moving average.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    rsi: Optional[float] = Field(
        default=None,
        description="Relative strength index (14).",
    )
    shares_outstanding: Optional[Union[int, float]] = Field(
        default=None,
        description="Number of shares outstanding.",
    )
    shares_float: Optional[Union[int, float]] = Field(
        default=None,
        description="Number of shares available to trade.",
    )
    short_interest: Optional[float] = Field(
        default=None,
        description="Percent of float reported as short.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    short_ratio: Optional[float] = Field(
        default=None,
        description="Short interest ratio",
    )
    insider_ownership: Optional[float] = Field(
        default=None,
        description="Insider ownership as a percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    insider_ownership_change: Optional[float] = Field(
        default=None,
        description="6-month change in insider ownership percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    institutional_ownership: Optional[float] = Field(
        default=None,
        description="Institutional ownership as a percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    institutional_ownership_change: Optional[float] = Field(
        default=None,
        description="3-month change in institutional ownership percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    price_to_earnings: Optional[float] = Field(
        default=None,
        description="Price to earnings ratio.",
    )
    forward_pe: Optional[float] = Field(
        default=None,
        description="Forward price to earnings ratio.",
    )
    peg_ratio: Optional[float] = Field(
        default=None,
        description="Price/Earnings-To-Growth (PEG) ratio.",
    )
    price_to_sales: Optional[float] = Field(
        default=None,
        description="Price to sales ratio.",
    )
    price_to_book: Optional[float] = Field(
        default=None,
        description="Price to book ratio.",
    )
    price_to_cash: Optional[float] = Field(
        default=None,
        description="Price to cash ratio.",
    )
    price_to_fcf: Optional[float] = Field(
        default=None,
        description="Price to free cash flow ratio.",
    )
    eps_growth_past_1y: Optional[float] = Field(
        default=None,
        description="EPS growth for this year.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    eps_growth_next_1y: Optional[float] = Field(
        default=None,
        description="EPS growth next year.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    eps_growth_past_5y: Optional[float] = Field(
        default=None,
        description="EPS growth for the previous 5 years.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    eps_growth_next_5y: Optional[float] = Field(
        default=None,
        description="EPS growth for the next 5 years.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    sales_growth_past_5y: Optional[float] = Field(
        default=None,
        description="Sales growth for the previous 5 years.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="Annualized dividend yield.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_assets: Optional[float] = Field(
        default=None,
        description="Return on assets.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on equity.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_investment: Optional[float] = Field(
        default=None,
        description="Return on investment.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    current_ratio: Optional[float] = Field(
        default=None,
        description="Current ratio.",
    )
    quick_ratio: Optional[float] = Field(
        default=None,
        description="Quick ratio.",
    )
    long_term_debt_to_equity: Optional[float] = Field(
        default=None,
        description="Long term debt to equity ratio.",
    )
    debt_to_equity: Optional[float] = Field(
        default=None,
        description="Total debt to equity ratio.",
    )
    gross_margin: Optional[float] = Field(
        default=None,
        description="Gross margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    operating_margin: Optional[float] = Field(
        default=None,
        description="Operating margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    profit_margin: Optional[float] = Field(
        default=None,
        description="Profit margin.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class FinvizEquityScreenerFetcher(
    Fetcher[FinvizEquityScreenerQueryParams, List[FinvizEquityScreenerData]]
):
    """Finviz Equity Screener Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FinvizEquityScreenerQueryParams:
        """Transform query parameters."""
        transformed_params = params.copy()
        if not transformed_params.get("filters_dict"):
            transformed_params["filters_dict"] = {}
        return FinvizEquityScreenerQueryParams(**transformed_params)

    @staticmethod
    def extract_data(  # noqa = PRL0912
        query: FinvizEquityScreenerQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract data from Finviz."""
        # pylint: disable=import-outside-toplevel
        import configparser  # noqa
        from finvizfinance.screener import (
            financial,
            overview,
            ownership,
            performance,
            technical,
            valuation,
        )
        from numpy import nan
        from openbb_finviz.utils.screener_helper import (
            get_preset_choices,
            d_check_screener,
            d_signals,
        )
        from pandas import DataFrame

        preset = None

        try:
            data_dir = kwargs.get("preferences", {}).get("data_directory")
            preset_choices = get_preset_choices(data_dir)
            preset = query.preset
            if preset is not None and preset not in preset_choices:
                raise OpenBBError(
                    f"Invalid preset '{preset}'. Available presets are:\n{list(preset_choices)}"
                )
        except Exception as e:
            if preset is not None:
                raise e from e
            warn(f"Error loading presets: {e}")
            preset = None

        data_type = query.metric
        ascend = False
        limit = query.limit
        sleep = 0.1  # For optimized pagination speed without creating too many requests error from Finviz.
        sort_by = "Change"
        df_screen = DataFrame()
        screen_type = {
            "overview": overview.Overview,
            "valuation": valuation.Valuation,
            "financial": financial.Financial,
            "ownership": ownership.Ownership,
            "performance": performance.Performance,
            "technical": technical.Technical,
        }

        if data_type in screen_type:
            screen = screen_type[data_type]()

        if preset is not None:
            preset_filter = configparser.RawConfigParser()
            preset_filter.optionxform = str  # type: ignore
            preset_filter.read(preset_choices[preset])
            d_general = preset_filter["General"]
            d_filters = {
                **preset_filter["Descriptive"],
                **preset_filter["Fundamental"],
                **preset_filter["Technical"],
            }
            for section in ["General", "Descriptive", "Fundamental", "Technical"]:
                for key, val in {**preset_filter[section]}.items():
                    if key not in d_check_screener:
                        raise OpenBBError(
                            f"The screener variable {section}.{key} shouldn't exist!\n"
                        )

                    if val not in d_check_screener[key]:
                        raise OpenBBError(
                            f"Invalid [{section}] {key}={val}. "
                            f"Choose one of the following options:\n{', '.join(d_check_screener[key])}.\n"
                        )

            d_filters = {k: v for k, v in d_filters.items() if v is not None}
            screen.set_filter(filters_dict=d_filters)
            asc = None

            asc = d_general.get("Ascend")

            if asc is not None:
                ascend = asc == "true"

            df_screen = screen.screener_view(
                order=d_general.get("Order", "Change"),
                limit=limit if limit else 100000,
                ascend=ascend,
                sleep_sec=sleep,
                verbose=0,
            )
        # If no preset is supplied, then set the filters based on the query parameters.
        else:
            if query.signal is not None:
                screen.set_filter(signal=d_signals[query.signal])
                if query.signal in ["unusual_volume", "most_active"]:
                    sort_by = "Relative Volume"
                elif query.signal == "top_losers":
                    ascend = True
                elif query.signal in ["new_low", "multiple_bottom", "double_bottom"]:
                    sort_by = "52-Week Low (Relative)"
                    ascend = True
                elif query.signal in ["new_high", "multiple_top", "double_top"]:
                    sort_by = "52-Week High (Relative)"
                elif query.signal == "oversold":
                    sort_by = "Relative Strength Index (14)"
                    ascend = True
                elif query.signal == "overbought":
                    sort_by = "Relative Strength Index (14)"
                elif query.signal == "most_volatile":
                    sort_by = "Volatility (Week)"
                else:
                    pass

            filters_dict: Dict = {}

            if query.sector != "all":
                filters_dict["Sector"] = SECTOR_MAP[query.sector]

            if query.industry != "all":
                filters_dict["Industry"] = INDUSTRY_MAP[query.industry]  # type: ignore

            if query.exchange != "all":
                filters_dict["Exchange"] = EXCHANGE_MAP[query.exchange]

            if query.index != "all":
                filters_dict["Index"] = INDEX_MAP[query.index]

            if query.recommendation != "all":
                filters_dict["Analyst Recom."] = RECOMMENDATION_MAP[
                    query.recommendation
                ]

            if query.mktcap != "all":
                filters_dict["Market Cap."] = MARKET_CAP_MAP[query.mktcap]

            if query.filters_dict is not None:
                _filters_dict = query.filters_dict.copy()  # type: ignore
                order = _filters_dict.pop("Order", None)
                asc = _filters_dict.pop("Ascend", None)
                if asc:
                    ascend = asc == "true"
                if order:
                    sort_by = order
                filters_dict.update(_filters_dict)

            if filters_dict:
                screen.set_filter(filters_dict=filters_dict)

            if not filters_dict and query.signal is None:
                screen.set_filter(signal=d_signals["top_gainers"])
                warn(
                    "No filters or signal provided. Defaulting to 'top_gainers' signal."
                    + " Use the preset, 'all_stocks', to explicitly return every stock on Finviz."
                    + " Returning 10K symbols can take several minutes."
                )

            df_screen = screen.screener_view(
                order=sort_by,
                limit=limit if limit else 100000,
                ascend=ascend,
                sleep_sec=sleep,
                verbose=0,
            )

        if df_screen is None or df_screen.empty:
            raise EmptyDataError(
                "No tickers found for the supplied parameters. Try relaxing the constraints."
            )

        df_screen.columns = [val.strip("\n") for val in df_screen.columns]
        # Commas in the company name can cause issues with delimiters.
        if "Company" in df_screen.columns:
            df_screen["Company"] = df_screen["Company"].str.replace(",", "")

        return df_screen.convert_dtypes().replace({nan: None}).to_dict(orient="records")

    @staticmethod
    def transform_data(
        query: FinvizEquityScreenerQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FinvizEquityScreenerData]:
        """Transform data."""
        return [FinvizEquityScreenerData.model_validate(d) for d in data]
