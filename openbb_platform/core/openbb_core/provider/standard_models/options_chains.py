"""Options Chains Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)

if TYPE_CHECKING:
    from pandas import DataFrame

class OptionsChainsQueryParams(QueryParams):
    """Options Chains Query."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def to_upper(cls, v: str) -> str:
        """Return the symbol in uppercase."""
        return v.upper()


class OptionsChainsData(Data):
    """Options Chains Data."""

    underlying_symbol: List[Union[str, None]] = Field(
        default_factory=list,
        description="Underlying symbol for the option.",
    )
    underlying_price: List[Union[float, None]] = Field(
        default_factory=list,
        description="Price of the underlying stock.",
    )
    contract_symbol: List[str] = Field(description="Contract symbol for the option.")
    eod_date: List[Union[dateType, None]] = Field(
        default_factory=list, description="Date for which the options chains are returned."
    )
    expiration: List[dateType] = Field(description="Expiration date of the contract.")
    dte: List[Union[int, None]] = Field(
        default_factory=list, description="Days to expiration of the contract."
    )
    strike: List[float] = Field(description="Strike price of the contract.")
    option_type: List[str] = Field(description="Call or Put.")
    open_interest: List[Union[int, None]] = Field(
        default=0, description="Open interest on the contract."
    )
    volume: List[Union[int, None]] = Field(
        default=0, description=DATA_DESCRIPTIONS.get("volume", "")
    )
    theoretical_price: List[Union[float, None]] = Field(
        default_factory=list, description="Theoretical value of the option."
    )
    last_trade_price: List[Union[float, None]] = Field(
        default_factory=list, description="Last trade price of the option."
    )
    last_trade_size: List[Union[int, None]] = Field(
        default_factory=list, description="Last trade size of the option."
    )
    last_trade_time: List[Union[datetime, None]] = Field(
        default_factory=list,
        description="The timestamp of the last trade.",
    )
    tick: List[Union[str, None]] = Field(
        default_factory=list, description="Whether the last tick was up or down in price."
    )
    bid: List[Union[float, None]] = Field(
        default_factory=list, description="Current bid price for the option."
    )
    bid_size: List[Union[int, None]] = Field(
        default_factory=list, description="Bid size for the option."
    )
    bid_time: List[Union[datetime, None]] = Field(
        default_factory=list,
        description="The timestamp of the bid price.",
    )
    bid_exchange: List[Union[str, None]] = Field(
        default_factory=list, description="The exchange of the bid price."
    )
    ask: List[Union[float, None]] = Field(
        default_factory=list, description="Current ask price for the option."
    )
    ask_size: List[Union[int, None]] = Field(
        default_factory=list, description="Ask size for the option."
    )
    ask_time: List[Union[datetime, None]] = Field(
        default_factory=list,
        description="The timestamp of the ask price.",
    )
    ask_exchange: List[Union[str, None]] = Field(
        default_factory=list, description="The exchange of the ask price."
    )
    mark: List[Union[float, None]] = Field(
        default_factory=list, description="The mid-price between the latest bid and ask."
    )
    open: List[Union[float, None]] = Field(
        default_factory=list, description=DATA_DESCRIPTIONS.get("open", "")
    )
    open_bid: List[Union[float, None]] = Field(
        default_factory=list, description="The opening bid price for the option that day."
    )
    open_ask: List[Union[float, None]] = Field(
        default_factory=list, description="The opening ask price for the option that day."
    )
    high: List[Union[float, None]] = Field(
        default_factory=list, description=DATA_DESCRIPTIONS.get("high", "")
    )
    bid_high: List[Union[float, None]] = Field(
        default_factory=list, description="The highest bid price for the option that day."
    )
    ask_high: List[Union[float, None]] = Field(
        default_factory=list, description="The highest ask price for the option that day."
    )
    low: List[Union[float, None]] = Field(
        default_factory=list, description=DATA_DESCRIPTIONS.get("low", "")
    )
    bid_low: List[Union[float, None]] = Field(
        default_factory=list, description="The lowest bid price for the option that day."
    )
    ask_low: List[Union[float, None]] = Field(
        default_factory=list, description="The lowest ask price for the option that day."
    )
    close: List[Union[float, None]] = Field(
        default_factory=list, description=DATA_DESCRIPTIONS.get("close", "")
    )
    close_size: List[Union[int, None]] = Field(
        default_factory=list, description="The closing trade size for the option that day."
    )
    close_time: List[Union[datetime, None]] = Field(
        default_factory=list,
        description="The time of the closing price for the option that day.",
    )
    close_bid: List[Union[float, None]] = Field(
        default_factory=list, description="The closing bid price for the option that day."
    )
    close_bid_size: List[Union[int, None]] = Field(
        default_factory=list, description="The closing bid size for the option that day."
    )
    close_bid_time: List[Union[datetime, None]] = Field(
        default_factory=list,
        description="The time of the bid closing price for the option that day.",
    )
    close_ask: List[Union[float, None]] = Field(
        default_factory=list, description="The closing ask price for the option that day."
    )
    close_ask_size: List[Union[int, None]] = Field(
        default_factory=list, description="The closing ask size for the option that day."
    )
    close_ask_time: List[Union[datetime, None]] = Field(
        default_factory=list,
        description="The time of the ask closing price for the option that day.",
    )
    prev_close: List[Union[float, None]] = Field(
        default_factory=list, description=DATA_DESCRIPTIONS.get("prev_close", "")
    )
    change: List[Union[float, None]] = Field(
        default_factory=list, description="The change in the price of the option."
    )
    change_percent: List[Union[float, None]] = Field(
        default_factory=list,
        description="Change, in normalized percentage points, of the option.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    implied_volatility: List[Union[float, None]] = Field(
        default_factory=list, description="Implied volatility of the option."
    )
    delta: List[Union[float, None]] = Field(default_factory=list, description="Delta of the option.")
    gamma: List[Union[float, None]] = Field(default_factory=list, description="Gamma of the option.")
    theta: List[Union[float, None]] = Field(default_factory=list, description="Theta of the option.")
    vega: List[Union[float, None]] = Field(default_factory=list, description="Vega of the option.")
    rho: List[Union[float, None]] = Field(default_factory=list, description="Rho of the option.")

    @field_validator("expiration", mode="before", check_fields=False)
    @classmethod
    def _date_validate(cls, v):
        """Return the datetime object from the date string."""
        if isinstance(v[0], datetime):
            return [datetime.strftime(d, "%Y-%m-%d") if d else None for d in v]
        if isinstance(v[0], str):
            return [datetime.strptime(d, "%Y-%m-%d") if d else None for d in v]
        return v

    @property
    def dataframe(cls) -> "DataFrame":
        """Return the data as a DataFrame."""
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame

        return DataFrame(cls.model_dump(
            exclude_unset=True,
            exclude_none=True,
        ))

    @property
    def expirations(cls) -> List[str]:
        """Return a list of unique expiration dates, as strings."""
        return [d.strftime("%Y-%m-%d") for d in list(set(cls.expiration))]

    @property
    def strikes(cls) -> List[float]:
        """Return a list of unique strike prices."""
        return list(set(cls.strike))

    @property
    def has_iv(cls) -> bool:
        """Return True if the data contains implied volatility."""
        return any([cls.implied_volatility])

    @property
    def has_greeks(cls) -> bool:
        """Return True if the data contains greeks."""
        return any([cls.delta, cls.gamma, cls.theta, cls.vega, cls.rho])

    def _get_nearest_expiration(
        self,
        date: Optional[Union[str, int]] = None
    ) -> str:
        """Return the nearest expiration date to the given date or number of days until expiry.

        Parameters
        ----------
        date: Optional[Union[str, int]]
            The expiration date, or days until expiry, to use.

        Returns
        -------
        str
            The nearest expiration date.
        """
        # pylint: disable=import-outside-toplevel
        from datetime import timedelta  # noqa
        from pandas import DataFrame, Series, to_datetime

        if isinstance(date, int):
            if not hasattr(self.dataframe, "dte"):
                date = (datetime.today() + timedelta(days=date)).strftime("%Y-%m-%d")
            else:
                dataframe = self.dataframe
                dataframe = dataframe[dataframe.dte >= 0]
                days = -1 if date == 0 else date
                nearest = (dataframe["dte"] - days).abs().idxmin()  # type: ignore
                return dataframe.loc[nearest, "expiration"].strftime("%Y-%m-%d")
        elif date is None:
            date = to_datetime(
                self.dataframe.eod_date[0]
                if hasattr(self.dataframe, "eod_date")
                else datetime.today().strftime("%Y-%m-%d")
            ) # type: ignore
        else:
            date = to_datetime(date)  # type: ignore

        expirations = Series(to_datetime(self.expirations))  # type: ignore
        nearest = DataFrame(expirations - date)
        nearest_exp = abs(nearest[0].astype("int64")).idxmin()

        return expirations.loc[nearest_exp].strftime("%Y-%m-%d")  # type: ignore

    def _get_nearest_otm_strikes(
        self,
        date: Optional[Union[str, int]] = None,
        underlying_price: Optional[float] = None,
        moneyness: Optional[float] = None,
    ) -> Dict:
        """Gets the nearest put and call strikes at a given percent OTM from the underlying price.

        Parameters
        ----------
        date: Optional[Union[str, int]]
            The expiration date, or days until expiry, to use.
        moneyness: Optional[float]
            The target percent OTM, expressed as a percent between 0 and 100.  Default is 0.25%.
        underlying_price: Optional[float]
            Only supply this is if the underlying price is not a returned field.

        Returns
        -------
        Dict[str, float]
            Dictionary of the upper (call) and lower (put) strike prices.
        """
        # pylint: disable=import-outside-toplevel
        from pandas import Series

        if moneyness is None:
            moneyness = 0.25

        if 0 < moneyness < 100:
            moneyness = moneyness / 100

        if moneyness > 100 or moneyness < 0:
            raise ValueError(
                "Error: Moneyness must be expressed as a percentage between 0 and 100"
            )

        df = self.dataframe

        if underlying_price is None and not hasattr(df, "underlying_price"):
            raise ValueError("Error: underlying_price must be provided if underlying_price is not available")

        last_price = underlying_price if underlying_price is not None else df.underlying_price.iloc[0]
        strikes = Series(self.strikes)

        if date is not None:
            date = self._get_nearest_expiration(date)
            df = df[df["expiration"].astype(str) == date]  # type: ignore
            strikes = Series(df.strike.unique().tolist())  # type: ignore

        upper = last_price * (1 + moneyness)  # type: ignore
        lower = last_price * (1 - moneyness)  # type: ignore
        nearest_call = (upper - strikes).abs().idxmin()
        call = strikes[nearest_call]
        nearest_put = (lower - strikes).abs().idxmin()
        put = strikes[nearest_put]
        otm_strikes = {"call": call, "put": put}

        return otm_strikes


    def _get_nearest_strike(
        self,
        option_type: Literal["call", "put"],
        days: Optional[int] = None,
        strike: Optional[float] = None,
        price_col: Optional[str] = None,
    ) -> Union[float, None]:
        """
        Gets the strike to the target option type, price, and number of days until expiry.

        Parameters
        ----------
        option_type: Literal["call", "put"]
            The option type to use when selecting the bid or ask price.
        days: int
            The target number of days until expiry.  Default is 30 days.
        strike_price: float
            The target strike price.  Default is the last price of the underlying stock.

        Returns
        -------
        float
            The closest strike price to the target price and number of days until expiry.
        """
        if option_type not in ["call", "put"]:
            raise ValueError("Error: option_type must be either 'call' or 'put'")

        chains = self.dataframe
        days = -1 if days == 0 else days

        if days is None:
            days = 30

        if strike is None:
            strike = chains.underlying_price.iloc[0]

        dte_estimate = self._get_nearest_expiration(days)
        df = chains[chains.expiration.astype(str) == dte_estimate][chains.option_type == option_type]

        if price_col is not None:
            df = df[df[price_col].notnull()]  # type: ignore

        if len(df) == 0:
            return None
        nearest = (
            df[df["strike"] <= strike].query("strike.idxmax()")  # type: ignore
            if option_type == "put"
            else df[df["strike"] >= strike].query("strike.idxmin()")  # type: ignore
        )

        return nearest.strike

    @staticmethod
    def _identify_price_col(
        df: "DataFrame",
        option_type: Literal["call", "put"],
        bid_ask: Literal["bid", "ask"],
    ) -> str:
        """Select the bid or ask price for the given option type.
        This method is used to identify the price column where the name may vary by provider.

        Parameters
        ----------
        df: DataFrame
            The DataFrame containing the option data.
        option_type: str
            The option type to use when selecting the bid or ask price.
        bid_ask: Literal["bid", "ask"]
            The side of the trade to get the price for.

        Returns
        -------
        str
            Name of the price column to use.
        """
        bid_fields = [
            "bid",
            "last_trade_price",
            "close_bid",
            "close",
            "prev_close",
        ]
        ask_fields = [
            "ask",
            "last_trade_price",
            "close_ask",
            "close",
            "prev_close",
        ]
        fields = bid_fields if bid_ask == "bid" else ask_fields
        new_df = df[df["option_type"] == option_type].copy()

        for field in fields:
            if field in new_df.columns:
                price_col = field
                break

        return price_col

    def calculate_straddle(
        self,
        days: Optional[int] = None,
        strike: Optional[float] = None,
        underlying_price: Optional[float] = None,
    ) -> "DataFrame":
        """
        Calculates the cost of a straddle and its payoff profile.
        Use a negative strike price for short options.

        Parameters
        ----------
        days: Optional[int]
            The target number of days until expiry. Default is 30 days.
        strike: Optional[float]
            The target strike price. Enter a negative value for short options.
            Default is the last price of the underlying stock.
        underlying_price: Optional[float]
            The price of the underlying stock. Default is the first value in the underlying_price column.

        Returns
        -------
        DataFrame
            Pandas DataFrame with the results.
                Strike 1 is the nearest call strike,
                Strike 2 is the nearest put strike.
        """
        # pylint: disable=import-outside-toplevel
        from numpy import inf
        from pandas import DataFrame

        short: bool = False

        chains = self.dataframe
        chains.expiration = chains.expiration.astype(str)

        if not hasattr(chains, "underlying_price") and underlying_price is None:
            raise ValueError("Error: underlying_price must be provided if underlying_price is not available")
        underlying_price = underlying_price if underlying_price is not None else chains.underlying_price[0]

        if days is None:
            days = 30

        if days == 0:
            days = -1

        dte_estimate = self._get_nearest_expiration(days)

        chains = chains[chains["expiration"] == dte_estimate]

        if strike is None and not hasattr(chains, "underlying_price"):
            raise ValueError("Error: strike must be provided if underlying_price is not available")

        if strike is None:
            strike = underlying_price

        if strike is not None and strike < 0:
            short = True

        strike_price = abs(strike)  # type: ignore
        bidAsk = "bid" if short else "ask"
        call_price_col = self._identify_price_col(chains, "call", bidAsk)  # type: ignore
        put_price_col = self._identify_price_col(chains, "put", bidAsk)  # type: ignore
        call_strike_estimate = self._get_nearest_strike("call", days, strike_price, call_price_col)  # type: ignore
        put_strike_estimate = self._get_nearest_strike("put", days, strike_price, put_price_col)  # type: ignore
        call_premium = chains.query(
            "`strike` == @call_strike_estimate and `option_type` == 'call'"
        )[call_price_col].values[0]
        put_premium = chains.query(
            "`strike` == @put_strike_estimate and `expiration` == @dte_estimate and `option_type` == 'put'"
        )[put_price_col].values[0]
        dte = chains.query("`expiration` == @dte_estimate")["dte"].unique()[0]
        straddle_cost = call_premium + put_premium  # type: ignore
        straddle_dict = {
            "Symbol": chains.underlying_symbol.unique()[0],
            "Underlying Price": underlying_price,
            "Expiration": dte_estimate,
            "DTE": dte,
            "Strike 1": call_strike_estimate,
            "Strike 2": put_strike_estimate,
            "Strike 1 Premium": call_premium,
            "Strike 2 Premium": put_premium,
            "Cost": straddle_cost * -1 if short else straddle_cost,
            "Cost Percent": round(
                straddle_cost / underlying_price * 100, ndigits=4
            ),
            "Breakeven Upper": call_strike_estimate + straddle_cost,
            "Breakeven Upper Percent": round(
                ((call_strike_estimate + straddle_cost) / underlying_price * 100) - 100,
                ndigits=4,
            ),
            "Breakeven Lower": put_strike_estimate - straddle_cost,
            "Breakeven Lower Percent": round(-100
            +
                (put_strike_estimate - straddle_cost) / underlying_price * 100,
                ndigits=4,
            ),
            "Max Profit": abs(straddle_cost) if short else inf,
            "Max Loss": inf if short else straddle_cost * -1,
        }
        straddle = DataFrame(
            data=straddle_dict.values(),
            index=list(straddle_dict)  # type: ignore
        ).rename(
            columns={0: "Short Straddle" if short else "Long Straddle"}
        )
        straddle.loc["Payoff Ratio"] = round(
            abs(straddle.loc["Max Profit"].iloc[0] / straddle.loc["Max Loss"].iloc[0]), ndigits=4
        )

        return straddle

