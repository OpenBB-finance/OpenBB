"""Options Chains Properties."""

# pylint: disable=too-many-lines, too-many-arguments, too-many-locals, too-many-statements, too-many-positional-arguments

from datetime import datetime
from functools import cached_property
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data

if TYPE_CHECKING:
    from pandas import DataFrame


class OptionsChainsProperties(Data):
    """Base Class For OptionsChainsData.

    Note: This class is not intended to be initialized directly and requires a validated instance of OptionsChainsData.
    """

    @property
    def last_price(self):
        """The manually-set price of the underlying asset."""
        if hasattr(self, "_last_price"):
            return self._last_price
        return None

    @last_price.setter
    def last_price(self, price: float):
        """Manually set the price of the underlying asset.

        Use this property to override the underlying price returned by the provider.

        Deleting the property will revert to the provider's underlying price.
        """
        self._last_price = price

    @last_price.deleter
    def last_price(self):
        """Delete the last price property."""
        if hasattr(self, "_last_price"):
            del self._last_price

    @cached_property
    def dataframe(self) -> "DataFrame":
        """Return all data as a Pandas DataFrame,
        with additional computed columns (Breakeven, GEX, DEX) if available.
        """
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import DataFrame, DatetimeIndex, Timedelta, concat, to_datetime

        chains_data = DataFrame(
            self.model_dump(
                exclude_unset=True,
                exclude_none=True,
            )
        )

        if "underlying_price" not in chains_data.columns and not self.last_price:
            raise OpenBBError(
                "'underlying_price' was not returned in the provider data."
                + "\n\n Please set the 'last_price' property and try again."
                + "\n\n Note: This error does not impact the standard OBBject `to_df()` method."
            )

        # Add the underlying price to the DataFrame, or override the existing price.
        if self.last_price:
            chains_data.loc[:, "underlying_price"] = self.last_price

        if chains_data.empty:
            raise OpenBBError("Error: No validated data was found.")

        if "dte" not in chains_data.columns and "eod_date" in chains_data.columns:
            _date = to_datetime(chains_data.eod_date)
            temp = DatetimeIndex(chains_data.expiration)
            temp_ = temp - _date  # type: ignore
            chains_data.loc[:, "dte"] = [Timedelta(_temp_).days for _temp_ in temp_]

        if "dte" in chains_data.columns:
            chains_data = DataFrame(chains_data[chains_data.dte >= 0])

        if "dte" not in chains_data.columns and "eod_date" not in chains_data.columns:
            today = datetime.today().date()
            chains_data.loc[:, "dte"] = chains_data.expiration - today

        # Add the breakeven price for each option, and the DEX and GEX for each option, if available.
        try:
            _calls = DataFrame(chains_data[chains_data.option_type == "call"])
            _puts = DataFrame(chains_data[chains_data.option_type == "put"])
            _ask = self._identify_price_col(  # pylint: disable=W0212
                chains_data, "call", "ask"
            )
            _calls.loc[:, ("Breakeven")] = _calls.strike + _calls.loc[:, (_ask)]
            _puts.loc[:, ("Breakeven")] = _puts.strike - _puts.loc[:, (_ask)]
            if "delta" in _calls.columns:
                _calls.loc[:, ("DEX")] = (
                    (
                        _calls.delta
                        * (
                            _calls.contract_size
                            if hasattr(_calls, "contract_size")
                            else 100
                        )
                        * _calls.open_interest
                        * _calls.underlying_price
                    )
                    .replace({nan: 0})
                    .astype("int64")
                )
                _puts.loc[:, ("DEX")] = (
                    (
                        _puts.delta
                        * (
                            _puts.contract_size
                            if hasattr(_puts, "contract_size")
                            else 100
                        )
                        * _puts.open_interest
                        * _puts.underlying_price
                    )
                    .replace({nan: 0})
                    .astype("int64")
                )

            if "gamma" in _calls.columns:
                _calls.loc[:, ("GEX")] = (
                    (
                        _calls.gamma
                        * (
                            _calls.contract_size
                            if hasattr(_calls, "contract_size")
                            else 100
                        )
                        * _calls.open_interest
                        * (_calls.underlying_price * _calls.underlying_price)
                        * 0.01
                    )
                    .replace({nan: 0})
                    .astype("int64")
                )
                _puts.loc[:, ("GEX")] = (
                    (
                        _puts.gamma
                        * (
                            _puts.contract_size
                            if hasattr(_puts, "contract_size")
                            else 100
                        )
                        * _puts.open_interest
                        * (_puts.underlying_price * _puts.underlying_price)
                        * 0.01
                        * (-1)
                    )
                    .replace({nan: 0})
                    .astype("int64")
                )

            _calls.set_index(keys=["expiration", "strike", "option_type"], inplace=True)
            _puts.set_index(keys=["expiration", "strike", "option_type"], inplace=True)
            df = concat([_puts, _calls])
            df = df.sort_index().reset_index()

            return df

        except Exception:  # pylint: disable=broad-exception-caught
            return chains_data

    @property
    def expirations(self) -> List[str]:
        """Return a list of unique expiration dates, as strings."""
        return sorted([d.strftime("%Y-%m-%d") for d in list(set(self.expiration))])  # type: ignore

    @property
    def strikes(self) -> List[float]:
        """Return a list of unique strike prices."""
        return sorted(list(set(self.strike)))  # type: ignore

    @property
    def has_iv(self) -> bool:
        """Return True if the data contains implied volatility."""
        return any([self.implied_volatility])  # type: ignore

    @property
    def has_greeks(self) -> bool:
        """Return True if the data contains greeks."""
        return any([self.delta, self.gamma, self.theta, self.vega, self.rho])  # type: ignore

    @property
    def total_oi(self) -> Dict:
        """Return open interest stats as a nested dictionary with keys: total, expiration, strike.

        Both, "expiration" and "strike", contain a list of records with fields:
        Calls, Puts, Total, Net Percent, PCR.
        """
        return self._get_stat("open_interest")

    @property
    def total_volume(self) -> Dict:
        """Return volume stats as a nested dictionary with keys: total, expiration, strike.

        Both, "expiration" and "strike", contain a list of records with fields:
        Calls, Puts, Total, Net Percent, PCR.
        """
        return self._get_stat("volume")

    @property
    def total_dex(self) -> Dict:
        """Return Delta Dollars (DEX) as a nested dictionary with keys: total, expiration, strike.

        Both, "expiration" and "strike", contain a list of records with fields:
        Calls, Puts, Total, Net Percent, PCR.
        """
        if not self.has_greeks:
            raise OpenBBError("Greeks are not available.")
        return self._get_stat("DEX")

    @property
    def total_gex(self) -> Dict:
        """Return Gamma Exposure stats as a nested dictionary with keys: total, expiration, strike.

        Both, "expiration" and "strike", contain a list of records with fields:
        Calls, Puts, Total, Net Percent, PCR.
        """
        if not self.has_greeks:
            raise OpenBBError("Greeks are not available.")
        return self._get_stat("GEX")

    @staticmethod
    def _identify_price_col(
        df: "DataFrame",
        option_type: Literal["call", "put"],
        bid_ask: Literal["bid", "ask"],
    ) -> str:
        """Select the bid or ask price for the given option type.
        This method is not intended to be called directly,
        it identifies the price column where the name may vary by provider.

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
        price_col = ""
        bid_fields = [
            "bid",
            "last_trade_price",
            "close",
            "close_bid",
            "prev_close",
            "mark",
            "settlement_price",
        ]
        ask_fields = [
            "ask",
            "last_trade_price",
            "close",
            "close_ask",
            "prev_close",
            "mark",
            "settlement_price",
        ]
        fields = bid_fields if bid_ask == "bid" else ask_fields
        new_df = df[df["option_type"] == option_type].copy()

        for field in fields:
            if field in new_df.columns:
                price_col = field
                break

        return price_col

    def filter_data(
        self,
        date: Optional[Union[str, int]] = None,
        option_type: Optional[Literal["call", "put"]] = None,
        moneyness: Optional[Literal["otm", "itm"]] = None,
        column: Optional[str] = None,
        value_min: Optional[float] = None,
        value_max: Optional[float] = None,
        stat: Optional[Literal["open_interest", "volume", "dex", "gex"]] = None,
        by: Literal["expiration", "strike"] = "expiration",
    ) -> "DataFrame":
        """Return statistics by strike or expiration; or, the filtered chains data.

        Parameters
        ----------
        date: Optional[Union[str, int]]
            The expiration date, or days until expiry, to use. This is applied before any filters.
        option_type: Optional[Literal["call", "put"]]
            The option type to filter by, None returns both.
            This is ignored if stat is not None.
        moneyness: Optional[Literal["otm", "itm"]]
            The moneyness to filter by, None returns both.
        column: Optional[str]
            The column to filter by.
            If no min/max are supplied it will sort all data by this column, in descending order.
            This is ignored if stat is not None.
        value_min: Optional[float]
            The minimum value to filter by. Column must be numeric.
            This is ignored if stat is not None.
        value_max: Optional[float]
            The maximum value to filter by. Column must be numeric.
            This is ignored if stat is not None.
        stat: Optional[Literal["open_interest", "volume", "dex", "gex"]]
            The statistical metric to filter by.
            Other fields are ignored if this is not None.
        by: Literal["expiration", "strike"]
            Filter the `stat` by expiration or strike, default is "expiration".
            If a date is supplied, "strike" is always returned.
            This is ignored if `stat` is None.
        """
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import DataFrame, concat

        stats = ["open_interest", "volume", "dex", "gex"]
        _stat = stat.upper() if stat in ["dex", "gex"] else stat
        by = "strike" if date is not None else by
        if stat is not None:
            if stat not in stats:
                raise OpenBBError(f"Error: stat must be one of {stats}")
            if stat in ["volume", "open_interest"]:
                return DataFrame(self._get_stat(stat, moneyness=moneyness, date=date)[by]).replace({nan: None})  # type: ignore
            if (
                _stat not in self.dataframe.columns
                and self.has_greeks
                and "underlying_price" not in self.dataframe.columns
            ):
                raise OpenBBError(
                    f"Error: '{stat}' could not be generated because"
                    + " the underlying price was not returned by the provider."
                    + " Set manually with 'underlying_price' property."
                )
            df = DataFrame(self._get_stat(_stat, moneyness=moneyness, date=date)[by])  # type: ignore
            return df.replace({nan: None})

        df = self.dataframe

        if moneyness is not None:
            df_calls = DataFrame(
                df[df.strike >= df.underlying_price].query("option_type == 'call'")
            )
            df_puts = DataFrame(
                df[df.strike <= df.underlying_price].query("option_type == 'put'")
            )
            df = concat([df_calls, df_puts])

        if date is not None:
            date = self._get_nearest_expiration(date)
            df = DataFrame(df[df.expiration.astype(str) == date])

        if option_type is not None:
            df = DataFrame(df[df.option_type == option_type])

        if column is not None:
            if column not in df.columns:
                raise OpenBBError(f"Error: column '{column}' not found in data")
            df = DataFrame(df[df[column].notnull()])
            if value_min is not None and value_max is not None:
                df = DataFrame(
                    df[
                        (df[column].abs() >= value_min)
                        & (df[column].abs() <= value_max)
                    ]
                )
            elif value_min is not None:
                df = DataFrame(df[df[column].abs() >= value_min])
            elif value_max is not None:
                df = DataFrame(df[df[column].abs() <= value_max])
            else:
                df = DataFrame(df.sort_values(by=column, ascending=False))

        return df.reset_index(drop=True)

    def _get_stat(
        self,
        metric: Literal["open_interest", "volume", "DEX", "GEX"],
        moneyness: Optional[Literal["otm", "itm"]] = None,
        date: Optional[str] = None,
    ) -> Dict:
        """Return the metric with keys: "total", "expiration", "strike".
        This method is not intended to be called directly.
        """
        # pylint: disable=import-outside-toplevel
        from numpy import inf, nan
        from pandas import DataFrame, concat

        df = self.dataframe

        if metric in ["DEX", "GEX"]:
            if not self.has_greeks:
                raise OpenBBError("Greeks were not found within the data.")
            df[metric] = abs(df[metric])

        total_calls = df[df.option_type == "call"][metric].sum()
        total_puts = df[df.option_type == "put"][metric].sum()
        total_metric = total_calls + total_puts
        total_metric_dict = {
            "Calls": total_calls,
            "Puts": total_puts,
            "Total": total_metric,
            "PCR": round(total_puts / total_calls, 4) if total_calls != 0 else 0,
        }

        df = DataFrame(df[df[metric].notnull()])  # type: ignore
        df["expiration"] = df.expiration.astype(str)

        if moneyness is not None:
            df_calls = DataFrame(
                df[df.strike >= df.underlying_price].query("option_type == 'call'")
                if moneyness == "otm"
                else df[df.strike <= df.underlying_price].query("option_type == 'call'")
            )
            df_puts = DataFrame(
                df[df.strike <= df.underlying_price].query("option_type == 'put'")
                if moneyness == "otm"
                else df[df.strike >= df.underlying_price].query("option_type == 'put'")
            )
            df = concat([df_calls, df_puts])

        if date is not None:
            date = self._get_nearest_expiration(date)
            df = DataFrame(df[df["expiration"].astype(str) == date])

        by_expiration = df.groupby("expiration")[[metric]].sum()[[metric]].copy()
        by_expiration = by_expiration.rename(columns={metric: "Total"})  # type: ignore
        by_expiration["Calls"] = df[df.option_type == "call"].groupby("expiration")[metric].sum().copy()  # type: ignore
        by_expiration["Puts"] = df[df.option_type == "put"].groupby("expiration")[metric].sum().copy()  # type: ignore
        by_expiration["PCR"] = round(by_expiration["Puts"] / by_expiration["Calls"], 4)
        by_expiration["Net Percent"] = round(
            (by_expiration["Total"] / total_metric) * 100, 4
        )
        by_expiration = (
            by_expiration[["Calls", "Puts", "Total", "Net Percent", "PCR"]]
            .replace({0: None, inf: None, nan: None})
            .dropna(how="all", axis=0)
        )
        by_expiration.index.name = "Expiration"
        by_expiration_dict = by_expiration.reset_index().to_dict(orient="records")
        by_strike = df.groupby("strike")[[metric]].sum()[[metric]].copy()
        by_strike = by_strike.rename(columns={metric: "Total"})  # type: ignore
        by_strike["Calls"] = df[df.option_type == "call"].groupby("strike")[metric].sum().copy()  # type: ignore
        by_strike["Puts"] = df[df.option_type == "put"].groupby("strike")[metric].sum().copy()  # type: ignore
        by_strike["PCR"] = round(by_strike["Puts"] / by_strike["Calls"], 4)
        by_strike["Net Percent"] = round((by_strike["Total"] / total_metric) * 100, 4)
        by_strike = (
            by_strike[["Calls", "Puts", "Total", "Net Percent", "PCR"]]
            .replace({0: None, inf: None, nan: None})
            .dropna(how="all", axis=0)
        )
        by_strike.index.name = "Strike"
        by_strike_dict = by_strike.reset_index().to_dict(orient="records")

        return {
            "total": total_metric_dict,
            "expiration": by_expiration_dict,
            "strike": by_strike_dict,
        }

    def _get_nearest_expiration(
        self, date: Optional[Union[str, int]] = None, df: Optional["DataFrame"] = None
    ) -> str:
        """Return the nearest expiration date to the given date or number of days until expiry.
        This method is not intended to be called directly.

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

        df = df if df is not None else self.dataframe
        if isinstance(date, int):
            if not hasattr(df, "dte"):
                date = (datetime.today() + timedelta(days=date)).strftime("%Y-%m-%d")
            else:
                dataframe = df
                dataframe = dataframe[dataframe.dte >= 0]
                days = -1 if date == 0 else date
                nearest = (dataframe.dte - days).abs().idxmin()  # type: ignore
                return dataframe.loc[nearest, "expiration"].strftime("%Y-%m-%d")
        elif date is None:
            date = to_datetime(
                df.eod_date.iloc[0]
                if hasattr(df, "eod_date")
                else datetime.today().strftime("%Y-%m-%d")
            )  # type: ignore
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
        """Get the nearest put and call strikes at a given percent OTM from the underlying price.
        This method is not intended to be called directly.

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
            raise OpenBBError(
                "Error: Moneyness must be expressed as a percentage between 0 and 100"
            )

        df = self.dataframe

        if underlying_price is None and not hasattr(df, "underlying_price"):
            raise OpenBBError(
                "Error: underlying_price must be provided if underlying_price is not available"
            )

        if date is not None:
            date = self._get_nearest_expiration(date)
            df = df[df.expiration.astype(str) == date]
            strikes = Series(df.strike.unique().tolist())

        last_price = (
            underlying_price
            if underlying_price is not None
            else df.underlying_price.iloc[0]
        )
        strikes = Series(self.strikes)

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
        days: Optional[Union[int, str]] = None,
        strike: Optional[float] = None,
        price_col: Optional[str] = None,
        force_otm: bool = True,
    ) -> Union[float, None]:
        """
        Get the strike to the target option type, price, and number of days until expiry.
        This method is not intended to be called directly.

        Parameters
        ----------
        option_type: Literal["call", "put"]
            The option type to use when selecting the bid or ask price.
        days: int
            The target number of days until expiry.  Default is 30 days.
        strike: float
            The target strike price.  Default is the last price of the underlying stock.
        price_col: str
            The price column to use for the calculation.
        force_otm: bool
            If True, the nearest OTM strike is returned.  Default is True.

        Returns
        -------
        float
            The closest strike price to the target price and number of days until expiry.
        """
        # pylint: disable=import-outside-toplevel
        from pandas import Series

        if option_type not in ["call", "put"]:
            raise OpenBBError("Error: option_type must be either 'call' or 'put'")

        chains = self.dataframe
        days = -1 if days == 0 else days

        if days is None:
            days = 30

        dte_estimate = self._get_nearest_expiration(days)
        df = (
            chains[chains.expiration.astype(str) == dte_estimate]
            .query("`option_type` == @option_type")
            .copy()
        )
        if strike is None:
            strike = df.underlying_price.iloc[0]

        if price_col is not None:
            df = df[df[price_col].notnull()]  # type: ignore

        if df.empty or len(df) == 0:
            return None

        if force_otm is False:
            strikes = Series(df.strike.unique().tolist())
            nearest = (strikes - strike).abs().idxmin()
            return strikes.iloc[nearest]

        nearest = (
            df[df.strike <= strike] if option_type == "put" else df[df.strike >= strike]
        )

        if nearest.empty or len(nearest) == 0:  # type: ignore
            return None

        nearest = (
            nearest.query("strike.idxmax()")  # type: ignore
            if option_type == "put"
            else nearest.query("strike.idxmin()")  # type: ignore
        )

        return nearest.strike

    def straddle(
        self,
        days: Optional[int] = None,
        strike: Optional[float] = None,
        underlying_price: Optional[float] = None,
    ) -> "DataFrame":
        """
        Calculate the cost of a straddle by DTE. Use a negative strike price for short options.

        Parameters
        ----------
        days: Optional[int]
            The target number of days until expiry. Default is 30 days.
        strike: Optional[float]
            The target strike price. Enter a negative value for short options.
            Default is the last price of the underlying stock.
        underlying_price: Optional[float]
            Only supply this is if the underlying price is not a returned field.

        Returns
        -------
        DataFrame
            Pandas DataFrame with the results.
                Strike 1 is the nearest call strike,
                Strike 2 is the nearest put strike.
        """
        # pylint: disable=import-outside-toplevel
        from numpy import inf
        from pandas import Series

        short: bool = False

        chains = self.dataframe

        if days is None:
            days = 30

        if days == 0:
            days = -1

        dte_estimate = self._get_nearest_expiration(days)

        chains = chains[chains.expiration.astype(str) == dte_estimate]

        if not hasattr(chains, "underlying_price") and underlying_price is None:
            raise OpenBBError(
                "Error: underlying_price must be provided if underlying_price is not available"
            )
        underlying_price = (
            underlying_price
            if underlying_price is not None
            else chains.underlying_price.iloc[0]
        )

        force_otm = True

        if strike is None and not hasattr(chains, "underlying_price"):
            raise OpenBBError(
                "Error: strike must be provided if underlying_price is not available"
            )

        if strike is not None:
            force_otm = False

        if strike is None:
            strike = underlying_price

        if strike is not None and strike < 0:
            short = True

        strike_price = abs(strike)  # type: ignore
        bid_ask = "bid" if short else "ask"
        call_price_col = self._identify_price_col(chains, "call", bid_ask)  # type: ignore
        put_price_col = self._identify_price_col(chains, "put", bid_ask)  # type: ignore
        call_strike_estimate = self._get_nearest_strike("call", days, strike_price, call_price_col, force_otm)  # type: ignore
        # If a strike price is supplied, the put strike is the same as the call strike.
        # Otherwise, the put strike is the nearest OTM put strike to the last price.

        put_strike_estimate = self._get_nearest_strike(
            "put", days, strike_price, put_price_col, force_otm
        )  # type: ignore
        call_premium = chains[chains.strike == call_strike_estimate].query(  # type: ignore
            "`option_type` == 'call'"
        )[
            call_price_col
        ]
        put_premium = chains[chains.strike == put_strike_estimate].query(  # type: ignore
            "`option_type` == 'put'"
        )[
            put_price_col
        ]
        if call_premium.empty or put_premium.empty:
            raise OpenBBError(
                "Error: No premium data found for the selected strikes."
                f" Call: {call_strike_estimate}, Put: {put_strike_estimate}"
            )
        put_premium = put_premium.values[0]
        call_premium = call_premium.values[0]
        dte = chains[chains.expiration.astype(str) == dte_estimate]["dte"].unique()[0]  # type: ignore
        straddle_cost = call_premium + put_premium  # type: ignore
        straddle_dict: Dict = {}

        # Includes the as-of date if it is historical EOD data.
        if hasattr(chains, "eod_date"):
            straddle_dict.update({"Date": chains.eod_date.iloc[0]})

        straddle_dict.update(
            {
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
                    ((call_strike_estimate + straddle_cost) / underlying_price * 100)
                    - 100,
                    ndigits=4,
                ),
                "Breakeven Lower": put_strike_estimate - straddle_cost,
                "Breakeven Lower Percent": round(
                    -100
                    + (put_strike_estimate - straddle_cost) / underlying_price * 100,
                    ndigits=4,
                ),
                "Max Profit": abs(straddle_cost) if short else inf,
                "Max Loss": inf if short else straddle_cost * -1,
            }
        )
        straddle = Series(
            data=straddle_dict.values(), index=list(straddle_dict)  # type: ignore
        )
        straddle.name = "Short Straddle" if short else "Long Straddle"
        straddle.loc["Payoff Ratio"] = round(
            abs(straddle.loc["Max Profit"] / straddle.loc["Max Loss"]), ndigits=4
        )

        return straddle.to_frame()

    def strangle(
        self,
        days: Optional[int] = None,
        moneyness: Optional[float] = None,
        underlying_price: Optional[float] = None,
    ) -> "DataFrame":
        """
        Calculate the cost of a strangle by DTE and % moneyness. Use a negative value for moneyness for short options.

        Parameters
        ----------
        days: int
            The target number of days until expiry.  Default is 30 days.
        moneyness: float
            The percentage of OTM moneyness, expressed as a percent between -100 < 0 < 100.
            Enter a negative number for short options. Default is 5%.
        underlying_price: Optional[float]
            Only supply this is if the underlying price is not a returned field.

        Returns
        -------
        DataFrame
            Pandas DataFrame with the results.
                Strike 1 is the nearest call strike.
                Strike 2 is the nearest put strike.
        """
        # pylint: disable=import-outside-toplevel
        from numpy import inf
        from pandas import Series

        if days is None:
            days = 30

        if moneyness is None:
            moneyness = 5

        short: bool = False

        if moneyness < 0:
            short = True
        moneyness = abs(moneyness)

        bid_ask = "bid" if short else "ask"

        chains = self.dataframe
        dte_estimate = self._get_nearest_expiration(days)
        chains = chains[chains["expiration"].astype(str) == dte_estimate]
        call_price_col = self._identify_price_col(chains, "call", bid_ask)  # type: ignore
        put_price_col = self._identify_price_col(chains, "put", bid_ask)  # type: ignore

        if underlying_price is None and not hasattr(chains, "underlying_price"):
            raise OpenBBError(
                "Error: underlying_price must be provided if underlying_price is not available"
            )

        underlying_price = (
            underlying_price
            if underlying_price is not None
            else chains.underlying_price.iloc[0]
        )

        strikes = self._get_nearest_otm_strikes(
            dte_estimate, underlying_price, moneyness
        )
        call_strike_estimate = self._get_nearest_strike(
            "call", days, strikes.get("call"), call_price_col, force_otm=False
        )
        put_strike_estimate = self._get_nearest_strike(
            "put", days, strikes.get("put"), put_price_col, force_otm=False
        )
        call_premium = chains[chains.strike == call_strike_estimate].query(  # type: ignore
            "`option_type` == 'call'"
        )[
            call_price_col
        ]
        put_premium = chains[chains.strike == put_strike_estimate].query(  # type: ignore
            "`option_type` == 'put'"
        )[
            put_price_col
        ]

        if call_premium.empty or put_premium.empty:
            raise OpenBBError(
                "Error: No premium data found for the selected strikes."
                f" Call: {call_strike_estimate}, Put: {put_strike_estimate}"
            )
        put_premium = put_premium.values[0]
        call_premium = call_premium.values[0]

        dte = chains[chains.expiration.astype(str) == dte_estimate]["dte"].unique()[0]  # type: ignore
        strangle_cost = call_premium + put_premium
        underlying_price = (
            underlying_price
            if underlying_price is not None
            else chains.underlying_price.iloc[0]
        )
        strangle_dict: Dict = {}
        # Includes the as-of date if it is historical EOD data.
        if hasattr(chains, "eod_date"):
            strangle_dict.update({"Date": chains.eod_date.iloc[0]})

        strangle_dict.update(
            {
                "Symbol": chains.underlying_symbol.unique()[0],
                "Underlying Price": underlying_price,
                "Expiration": dte_estimate,
                "DTE": dte,
                "Strike 1": call_strike_estimate,
                "Strike 2": put_strike_estimate,
                "Strike 1 Premium": call_premium,
                "Strike 2 Premium": put_premium,
                "Cost": strangle_cost * -1 if short else strangle_cost,
                "Cost Percent": round(
                    strangle_cost / underlying_price * 100, ndigits=4
                ),
                "Breakeven Upper": call_strike_estimate + strangle_cost,
                "Breakeven Upper Percent": round(
                    ((call_strike_estimate + strangle_cost) / underlying_price * 100)
                    - 100,
                    ndigits=4,
                ),
                "Breakeven Lower": put_strike_estimate - strangle_cost,
                "Breakeven Lower Percent": round(
                    (
                        -100
                        + (put_strike_estimate - strangle_cost) / underlying_price * 100
                    ),
                    ndigits=4,
                ),
                "Max Profit": abs(strangle_cost) if short else inf,
                "Max Loss": inf if short else strangle_cost * -1,
            }
        )
        strangle = Series(
            data=strangle_dict.values(),
            index=list(strangle_dict),  # type: ignore
        )
        strangle.name = "Short Strangle" if short else "Long Strangle"
        strangle.loc["Payoff Ratio"] = round(
            abs(strangle.loc["Max Profit"] / strangle.loc["Max Loss"]), ndigits=4
        )

        return strangle.to_frame()

    def vertical_call_spread(
        self,
        days: Optional[int] = None,
        sold: Optional[float] = None,
        bought: Optional[float] = None,
        underlying_price: Optional[float] = None,
    ) -> "DataFrame":
        """
        Calculate the vertical call spread for the target DTE.
        A bull call spread is when the sold strike is above the bought strike.

        Parameters
        ----------
        days: int
            The target number of days until expiry. This value will be used to get the nearest valid DTE.
            Default is 30 days.
        sold: float
            The target strike price for the short leg of the vertical call spread.
            Default is 7.5% above the last price of the underlying.
        bought: float
            The target strike price for the long leg of the vertical call spread.
            Default is 2.5% above the last price of the underlying.
        underlying_price: Optional[float]
            Only supply this is if the underlying price is not a returned field.

        Returns
        -------
        DataFrame
            Pandas DataFrame with the results.
                Strike 1 is the sold call strike.
                Strike 2 is the bought call strike.
        """
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import DataFrame, Series

        chains = self.dataframe

        if not hasattr(chains, "underlying_price") and underlying_price is None:
            raise OpenBBError(
                "Error: underlying_price must be provided if underlying_price is not available"
            )

        if days is None:
            days = 30

        if days == 0:
            days = -1

        dte_estimate = self._get_nearest_expiration(days)

        chains = chains[chains["expiration"].astype(str) == dte_estimate].query(
            "`option_type` == 'call'"
        )

        last_price = (
            underlying_price
            if underlying_price is not None
            else chains.underlying_price.iloc[0]
        )

        if bought is None:
            bought = last_price * 1.0250

        if sold is None:
            sold = last_price * 1.0750

        bid = self._identify_price_col(chains, "call", "bid")
        ask = self._identify_price_col(chains, "call", "ask")
        sold = self._get_nearest_strike("call", days, sold, bid, False)
        bought = self._get_nearest_strike("call", days, bought, ask, False)

        sold_premium = chains[chains.strike == sold][bid].iloc[0] * (-1)  # type: ignore
        bought_premium = chains[chains.strike == bought][ask].iloc[0]  # type: ignore
        dte = chains[chains.expiration.astype(str) == dte_estimate]["dte"].unique()[0]  # type: ignore
        spread_cost = bought_premium + sold_premium
        breakeven_price = bought + spread_cost
        max_profit = sold - bought - spread_cost  # type: ignore
        call_spread_: Dict = {}
        if sold != bought and spread_cost != 0:
            # Includes the as-of date if it is historical EOD data.
            if hasattr(chains, "eod_date"):
                call_spread_.update({"Date": chains.eod_date.iloc[0]})

            call_spread_.update(
                {
                    "Symbol": chains.underlying_symbol.unique()[0],
                    "Underlying Price": last_price,
                    "Expiration": dte_estimate,
                    "DTE": dte,
                    "Strike 1": sold,
                    "Strike 2": bought,
                    "Strike 1 Premium": sold_premium,
                    "Strike 2 Premium": bought_premium,
                    "Cost": spread_cost,
                    "Cost Percent": round(spread_cost / last_price * 100, ndigits=4),
                    "Breakeven Lower": breakeven_price,
                    "Breakeven Lower Percent": round(
                        (breakeven_price / last_price * 100) - 100, ndigits=4
                    ),
                    "Breakeven Upper": nan,
                    "Breakeven Upper Percent": nan,
                    "Max Profit": max_profit,
                    "Max Loss": spread_cost * -1,
                }
            )
            call_spread = Series(
                data=call_spread_.values(), index=list(call_spread_)  # type: ignore
            )
            call_spread.name = "Bull Call Spread"

            if call_spread.loc["Cost"] < 0:
                call_spread.loc["Max Profit"] = call_spread.loc["Cost"] * -1
                call_spread.loc["Max Loss"] = -1 * (
                    bought - sold + call_spread.loc["Cost"]  # type: ignore
                )
                lower = bought if sold > bought else sold  # type: ignore
                call_spread.loc["Breakeven Upper"] = (
                    lower + call_spread.loc["Max Profit"]
                )
                call_spread.loc["Breakeven Upper Percent"] = round(
                    (breakeven_price / last_price * 100) - 100, ndigits=4
                )
                call_spread.loc["Breakeven Lower"] = nan
                call_spread.loc["Breakeven Lower Percent"] = nan
                call_spread.name = "Bear Call Spread"

            call_spread.loc["Payoff Ratio"] = round(
                abs(call_spread.loc["Max Profit"] / call_spread.loc["Max Loss"]),
                ndigits=4,
            )

            return call_spread.to_frame()

        return DataFrame()

    def vertical_put_spread(
        self,
        days: Optional[int] = None,
        sold: Optional[float] = None,
        bought: Optional[float] = None,
        underlying_price: Optional[float] = None,
    ) -> "DataFrame":
        """
        Calculate the vertical put spread for the target DTE.
        A bear put spread is when the bought strike is above the sold strike.

        Parameters
        ----------
        days: int
            The target number of days until expiry. This value will be used to get the nearest valid DTE.
            Default is 30 days.
        sold: float
            The target strike price for the short leg of the vertical put spread.
            Default is 7.5% below the last price of the underlying.
        bought: float
            The target strike price for the long leg of the vertical put spread.
            Default is 2.5% below the last price of the underlying.
        underlying_price: Optional[float]
            Only supply this is if the underlying price is not a returned field.

        Returns
        -------
        DataFrame
            Pandas DataFrame with the results.
                Strike 1 is the sold strike.
                Strike 2 is the bought strike.
        """
        # pylint: disable=import-outside-toplevel
        from numpy import nan
        from pandas import DataFrame, Series

        chains = self.dataframe

        if not hasattr(chains, "underlying_price") and underlying_price is None:
            raise OpenBBError(
                "Error: underlying_price must be provided if underlying_price is not available"
            )

        if days is None:
            days = 30

        if days == 0:
            days = -1

        dte_estimate = self._get_nearest_expiration(days)

        chains = chains[chains["expiration"].astype(str) == dte_estimate].query(
            "`option_type` == 'put'"
        )

        last_price = (
            underlying_price
            if underlying_price is not None
            else chains.underlying_price.iloc[0]
        )

        if bought is None:
            bought = last_price * 0.9750

        if sold is None:
            sold = last_price * 0.9250

        bid = self._identify_price_col(chains, "put", "bid")
        ask = self._identify_price_col(chains, "put", "ask")
        sold = self._get_nearest_strike("put", days, sold, bid, False)
        bought = self._get_nearest_strike("put", days, bought, ask, False)

        sold_premium = chains[chains.strike == sold][bid].iloc[0] * (-1)  # type: ignore
        bought_premium = chains[chains.strike == bought][ask].iloc[0]  # type: ignore
        dte = chains[chains.expiration.astype(str) == dte_estimate]["dte"].unique()[0]  # type: ignore
        spread_cost = bought_premium + sold_premium
        max_profit = abs(spread_cost)
        breakeven_price = sold - max_profit
        max_loss = (sold - bought - max_profit) * -1  # type: ignore
        put_spread_: Dict = {}
        if sold != bought and max_loss != 0:
            # Includes the as-of date if it is historical EOD data.
            if hasattr(chains, "eod_date"):
                put_spread_.update({"Date": chains.eod_date.iloc[0]})

            put_spread_.update(
                {
                    "Symbol": chains.underlying_symbol.unique()[0],
                    "Underlying Price": last_price,
                    "Expiration": dte_estimate,
                    "DTE": dte,
                    "Strike 1": sold,
                    "Strike 2": bought,
                    "Strike 1 Premium": sold_premium,
                    "Strike 2 Premium": bought_premium,
                    "Cost": spread_cost,
                    "Cost Percent": round(max_profit / last_price * 100, ndigits=4),
                    "Breakeven Lower": nan,
                    "Breakeven Lower Percent": nan,
                    "Breakeven Upper": breakeven_price,
                    "Breakeven Upper Percent": (
                        100 - round((breakeven_price / last_price) * 100, ndigits=4)
                    ),
                    "Max Profit": max_profit,
                    "Max Loss": max_loss,
                }
            )

            put_spread = Series(data=put_spread_.values(), index=put_spread_)
            put_spread.name = "Bull Put Spread"
            if put_spread.loc["Cost"] > 0:
                put_spread.loc["Max Profit"] = bought - sold - spread_cost  # type: ignore
                put_spread.loc["Max Loss"] = spread_cost * (-1)
                put_spread.loc["Breakeven Lower"] = bought - spread_cost
                put_spread.loc["Breakeven Lower Percent"] = 100 - round(
                    (breakeven_price / last_price) * 100, ndigits=4
                )
                put_spread.loc["Breakeven Upper"] = nan
                put_spread.loc["Breakeven Upper Percent"] = nan
                put_spread.name = "Bear Put Spread"

            put_spread.loc["Payoff Ratio"] = round(
                abs(put_spread.loc["Max Profit"] / put_spread.loc["Max Loss"]),
                ndigits=4,
            )

            return put_spread.to_frame()

        return DataFrame()

    def synthetic_long(
        self,
        days: Optional[int] = 30,
        strike: float = 0,
        underlying_price: Optional[float] = None,
    ) -> "DataFrame":
        """
        Calculate the cost of a synthetic long position at a given strike.
        It is expressed as the difference between a bought call and a sold put.

        Parameters
        -----------
        days: int
            The target number of days until expiry. Default is 30 days.
        strike: float
            The target strike price. Default is the last price of the underlying stock.
        underlying_price: Optional[float]
            Only supply this is if the underlying price is not a returned field.

        Returns
        -------
        DataFrame
            Pandas DataFrame with the results.
                Strike1 is the purchased call strike.
                Strike2 is the sold put strike.
        """
        # pylint: disable=import-outside-toplevel
        from numpy import inf, nan
        from pandas import DataFrame

        chains = self.dataframe

        if not hasattr(chains, "underlying_price") and underlying_price is None:
            raise OpenBBError(
                "Error: underlying_price must be provided if underlying_price is not available"
            )

        if days is None:
            days = 30

        if days == 0:
            days = -1

        dte_estimate = self._get_nearest_expiration(days)
        chains = DataFrame(chains[chains["expiration"].astype(str) == dte_estimate])
        last_price = (
            underlying_price
            if underlying_price is not None
            else chains.underlying_price.iloc[0]
        )
        bid = self._identify_price_col(chains, "put", "bid")
        ask = self._identify_price_col(chains, "call", "ask")
        strike_price = last_price if strike == 0 else strike
        sold = self._get_nearest_strike("put", days, strike_price, bid, False)
        bought = self._get_nearest_strike("call", days, strike_price, ask, False)
        put_premium = chains[chains.strike == sold].query("`option_type` == 'put'")[bid]  # type: ignore
        call_premium = chains[chains.strike == bought].query("`option_type` == 'call'")[ask]  # type: ignore

        if call_premium.empty or put_premium.empty:
            raise OpenBBError(
                "Error: No premium data found for the selected strikes."
                f" Call: {bought}, Put: {sold}"
            )

        put_premium = put_premium.values[0] * (-1)
        call_premium = call_premium.values[0]
        dte = chains[chains.expiration.astype(str) == dte_estimate]["dte"].unique()[0]  # type: ignore
        position_cost = call_premium + put_premium
        breakeven = ((sold + bought) / 2) + position_cost  # type: ignore
        synthetic_long_dict: Dict = {}
        # Includes the as-of date if it is historical EOD data.
        if hasattr(chains, "eod_date"):
            synthetic_long_dict.update({"Date": chains.eod_date.iloc[0]})

        synthetic_long_dict.update(
            {
                "Symbol": chains.underlying_symbol.unique()[0],
                "Underlying Price": last_price,
                "Expiration": dte_estimate,
                "DTE": dte,
                "Strike 1": sold,
                "Strike 2": bought,
                "Strike 1 Premium": call_premium,
                "Strike 2 Premium": put_premium,
                "Cost": position_cost,
                "Cost Percent": round(position_cost / last_price * 100, ndigits=4),
                "Breakeven Lower": nan,
                "Breakeven Lower Percent": nan,
                "Breakeven Upper": breakeven,
                "Breakeven Upper Percent": round(
                    ((breakeven - last_price) / last_price) * 100, ndigits=4
                ),
                "Max Profit": inf,
                "Max Loss": breakeven * (-1),
            }
        )

        synthetic_long = DataFrame(
            data=synthetic_long_dict.values(), index=list(synthetic_long_dict)  # type: ignore
        ).rename(columns={0: "Synthetic Long"})

        return synthetic_long

    def synthetic_short(
        self,
        days: Optional[int] = None,
        strike: float = 0,
        underlying_price: Optional[float] = None,
    ) -> "DataFrame":
        """
        Calculate the cost of a synthetic short position at a given strike.
        It is expressed as the difference between a sold call and a purchased put.

        Parameters
        -----------
        days: int
            The target number of days until expiry. Default is 30 days.
        strike: float
            The target strike price. Default is the last price of the underlying stock.
        underlying_price: Optional[float]
            Only supply this is if the underlying price is not a returned field.

        Returns
        -------
        DataFrame
            Pandas DataFrame with the results.
                Strike 1 is the sold call strike.
                Strike 2 is the purchased put strike.
        """
        # pylint: disable=import-outside-toplevel
        from numpy import inf, nan
        from pandas import DataFrame

        chains = self.dataframe

        if not hasattr(chains, "underlying_price") and underlying_price is None:
            raise OpenBBError(
                "Error: underlying_price must be provided if underlying_price is not available"
            )

        if days is None:
            days = 30

        if days == 0:
            days = -1

        dte_estimate = self._get_nearest_expiration(days)
        chains = DataFrame(chains[chains["expiration"].astype(str) == dte_estimate])
        last_price = (
            underlying_price
            if underlying_price is not None
            else chains.underlying_price.iloc[0]
        )
        bid = self._identify_price_col(chains, "call", "bid")
        ask = self._identify_price_col(chains, "put", "ask")
        strike_price = last_price if strike == 0 else strike
        sold = self._get_nearest_strike("call", days, strike_price, bid, False)
        bought = self._get_nearest_strike("put", days, strike_price, ask, False)
        put_premium = chains[chains.strike == bought].query("`option_type` == 'put'")[ask]  # type: ignore
        call_premium = chains[chains.strike == sold].query("`option_type` == 'call'")[bid]  # type: ignore

        if call_premium.empty or put_premium.empty:
            raise OpenBBError(
                "Error: No premium data found for the selected strikes."
                f" Call: {bought}, Put: {sold}"
            )

        put_premium = put_premium.values[0]
        call_premium = call_premium.values[0] * (-1)
        dte = chains[chains.expiration.astype(str) == dte_estimate]["dte"].unique()[0]  # type: ignore
        position_cost = call_premium + put_premium
        breakeven = ((sold + bought) / 2) + position_cost  # type: ignore
        synthetic_short_dict: Dict = {}
        # Includes the as-of date if it is historical EOD data.
        if hasattr(chains, "eod_date"):
            synthetic_short_dict.update({"Date": chains.eod_date.iloc[0]})

        synthetic_short_dict.update(
            {
                "Symbol": chains.underlying_symbol.unique()[0],
                "Underlying Price": last_price,
                "Expiration": dte_estimate,
                "DTE": dte,
                "Strike 1": sold,
                "Strike 2": bought,
                "Strike 1 Premium": call_premium,
                "Strike 2 Premium": put_premium,
                "Cost": position_cost,
                "Cost Percent": round(position_cost / last_price * 100, ndigits=4),
                "Breakeven Lower": breakeven,
                "Breakeven Lower Percent": round(
                    ((breakeven - last_price) / last_price) * 100, ndigits=4
                ),
                "Breakeven Upper": nan,
                "Breakeven Upper Percent": nan,
                "Max Profit": breakeven,
                "Max Loss": inf,
            }
        )

        synthetic_short = DataFrame(
            data=synthetic_short_dict.values(), index=list(synthetic_short_dict)  # type: ignore
        ).rename(columns={0: "Synthetic Short"})

        return synthetic_short

    # pylint: disable=too-many-branches
    def strategies(  # noqa: PLR0912
        self,
        days: Optional[List] = None,
        straddle_strike: Optional[float] = None,
        strangle_moneyness: Optional[List[float]] = None,
        synthetic_longs: Optional[List[float]] = None,
        synthetic_shorts: Optional[List[float]] = None,
        vertical_calls: Optional[List[tuple]] = None,
        vertical_puts: Optional[List[tuple]] = None,
        underlying_price: Optional[float] = None,
    ) -> "DataFrame":
        """
        Get options strategies for all, or a list of, DTE(s).
        Currently supports straddles, strangles, synthetic long and shorts, and vertical spreads.

        Multiple strategies, expirations, and % moneyness can be returned.

        A negative value for `straddle_strike` or `strangle_moneyness` returns short options.

        A synthetic long/short position is a bought/sold call and sold/bought put at the same strike.

        A sold call strike that is lower than the bought strike,
        or a sold put strike that is higher than the bought strike,
        is a bearish vertical spread.

        The default state returns a long straddle for each expiry.

        Parameters
        ----------
        days: list[int]
            List of DTE(s) to get strategies for. Enter a single value, or multiple as a list.
            Select all dates by entering, -1. Large chains may take a few seconds to process all dates.
            Defaults to [20,40,60,90,180,360].
        straddle_strike: float
            The target strike price for the straddle. Defaults to the last price of the underlying stock,
            and both strikes will always be on OTM side.
            Enter a strike price to force call and put strikes to be the same.
        strangle_moneyness: List[float]
            List of OTM moneyness to target, expressed as a percent value between 0 and 100.
            Enter a single value, or multiple as a list.
        synthetic_long: List[float]
            List of strikes for a synthetic long position.
        synthetic_short: List[float]
            List of strikes for a synthetic short position.
        vertical_calls: List[tuple]
            Call strikes for vertical spreads, entered as a list of paired tuples - [(sold strike, bought strike)].
        vertical_puts: List[float]
            Put strikes for vertical spreads, entered as a list of paired tuples - [(sold strike, bought strike)].
        underlying_price: Optional[float]
            Only supply this is if the underlying price is not a returned field.

        Returns
        -------
        DataFrame
            Pandas DataFrame with the results.
        """
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame, concat

        def to_clean_list(x):
            if x is None:
                return None
            return [x] if not isinstance(x, list) else x

        def split_into_tuples(x):
            """Split a list into paired tuples."""
            if x is None:
                return None
            if isinstance(x, tuple):
                return [x]
            if isinstance(x, list) and isinstance(x[0], tuple):
                return x
            paired_tuples: List = []
            for i in range(0, len(x), 2):
                paired_tuples.append((x[i], x[i + 1]))
            return paired_tuples

        # Check if all items are False
        if (  # pylint: disable=too-many-boolean-expressions
            straddle_strike is None
            and strangle_moneyness is None
            and synthetic_longs is None
            and synthetic_shorts is None
            and vertical_calls is None
            and vertical_puts is None
        ):
            straddle_strike = 0

        chains = self.dataframe
        bid = self._identify_price_col(chains, "call", "bid")
        chains = chains[chains[bid].notnull()].query("`dte` >= 0")
        days = (
            chains.dte.unique().tolist()
            if days == -1
            else days if days else [20, 40, 60, 90, 180, 360]
        )
        # Allows a single input to be passed instead of a list.
        days = [days] if isinstance(days, int) else days  # type: ignore[list-item]

        strangle_moneyness = strangle_moneyness or [0.0]
        strangle_moneyness = to_clean_list(strangle_moneyness)  # type: ignore
        synthetic_longs = to_clean_list(synthetic_longs)  # type: ignore
        synthetic_shorts = to_clean_list(synthetic_shorts)  # type: ignore
        vertical_calls = split_into_tuples(vertical_calls)  # type: ignore
        vertical_puts = split_into_tuples(vertical_puts)  # type: ignore

        days_list: List = []
        strategies: DataFrame = DataFrame()
        straddles: DataFrame = DataFrame()
        strangles: DataFrame = DataFrame()
        strangles_: DataFrame = DataFrame()
        synthetic_longs_df: DataFrame = DataFrame()
        _synthetic_longs: DataFrame = DataFrame()
        synthetic_shorts_df: DataFrame = DataFrame()
        _synthetic_shorts: DataFrame = DataFrame()
        call_spreads: DataFrame = DataFrame()
        put_spreads: DataFrame = DataFrame()

        # Get the nearest expiration date for each supplied date and
        # discard any duplicates found - i.e, [29,30] will yield only one result.
        for day in days:  # type: ignore
            _day = day or -1
            days_list.append(self._get_nearest_expiration(_day))
        days = sorted(set(days_list))

        if vertical_calls is not None:
            for c in vertical_calls:
                c_strike1 = c[0]
                c_strike2 = c[1]
                for day in days:
                    call_spread = self.vertical_call_spread(
                        day, c_strike1, c_strike2, underlying_price
                    )
                    if not call_spread.empty:
                        call_spreads = concat([call_spreads, call_spread.transpose()])

        if vertical_puts:
            for c in vertical_puts:
                p_strike1 = c[0]
                p_strike2 = c[1]
            for day in days:
                put_spread = self.vertical_put_spread(
                    day, p_strike1, p_strike2, underlying_price
                )
                if not put_spread.empty:
                    put_spreads = concat([put_spreads, put_spread.transpose()])

        if straddle_strike or straddle_strike == 0:
            straddle_strike = None if straddle_strike == 0 else straddle_strike
            for day in days:
                straddle = self.straddle(
                    day, straddle_strike, underlying_price
                ).transpose()
                if not straddle.empty and straddle.iloc[0]["Cost"] != 0:
                    straddles = concat([straddles, straddle])

        if strangle_moneyness and strangle_moneyness[0] != 0:
            for day in days:
                for moneyness in strangle_moneyness:
                    strangle = self.strangle(
                        day, moneyness, underlying_price
                    ).transpose()
                    if strangle.iloc[0]["Cost"] != 0:
                        strangles_ = concat([strangles_, strangle])

            strangles = concat([strangles, strangles_])
            strangles = strangles.query("`Strike 1` != `Strike 2`").drop_duplicates()

        if synthetic_longs:
            strikes = synthetic_longs
            for day in days:
                for strike in strikes:
                    _synthetic_long = self.synthetic_long(
                        day, strike, underlying_price
                    ).transpose()
                    if (
                        not _synthetic_long.empty
                        and _synthetic_long.iloc[0]["Strike 1 Premium"] != 0
                    ):
                        _synthetic_longs = concat([_synthetic_longs, _synthetic_long])

            synthetic_longs_df = concat([synthetic_longs_df, _synthetic_longs])

        if synthetic_shorts:
            strikes = synthetic_shorts
            for day in days:
                for strike in strikes:
                    _synthetic_short = self.synthetic_short(
                        day, strike, underlying_price
                    ).transpose()
                    if (
                        not _synthetic_short.empty
                        and _synthetic_short.iloc[0]["Strike 1 Premium"] != 0
                    ):
                        _synthetic_shorts = concat(
                            [_synthetic_shorts, _synthetic_short]
                        )

            if not _synthetic_shorts.empty:
                synthetic_shorts_df = concat([synthetic_shorts_df, _synthetic_shorts])

        strategies = concat(
            [
                straddles,
                strangles,
                synthetic_longs_df,
                synthetic_shorts_df,
                call_spreads,
                put_spreads,
            ]
        )

        if strategies.empty:
            raise OpenBBError("No strategies found for the given parameters.")

        strategies = strategies.reset_index().rename(columns={"index": "Strategy"})
        strategies = (
            strategies.set_index(["Expiration", "DTE"])
            .sort_index()
            .drop(columns=["Symbol"])
        )
        return strategies.reset_index()

    def skew(
        self,
        date: Optional[Union[str, int]] = None,
        moneyness: Optional[float] = None,
        underlying_price: Optional[float] = None,
    ) -> "DataFrame":
        """Return skewness of the options, either vertical or horizontal.

        The vertical skew for each expiry and option is calculated by subtracting the IV of the ATM call or put.
        Returns only where the IV is greater than 0.

        Horizontal skew is returned if a value for moneyness is supplied.
        It is expressed as the difference between skews of two equidistant OTM strikes (the closest call and put).

        Default state is 20% moneyness with 30 days until expiry.

        Parameters
        -----------
        date: Optional[Union[str, int]]
            The expiration date, or days until expiry, to use. Enter -1 for all expirations.
            Large chains (SPY, SPX, etc.) may take a few seconds to process when using -1.
        moneyness: float
            The moneyness to target for calculating horizontal skew.
        underlying_price: Optional[float]
            Only supply this is if the underlying price is not a returned field.

        Returns
        --------
        DataFrame
            Pandas DataFrame with the results.
        """
        # pylint: disable=import-outside-toplevel
        from pandas import DataFrame, concat

        data = self.dataframe
        expiration: str = ""
        if self.has_iv is False:
            raise OpenBBError("Error: 'implied_volatility' field not found.")

        data = DataFrame(data[data.implied_volatility > 0])  # type: ignore
        call_price_col = self._identify_price_col(data, "call", "ask")
        put_price_col = self._identify_price_col(data, "put", "ask")

        if not hasattr(data, "underlying_price") and underlying_price is None:
            raise OpenBBError(
                "Error: underlying_price must be provided if underlying_price is not available"
            )

        if moneyness is not None and date is None:
            date = -1

        if moneyness is None and date is None:
            date = 30
            moneyness = 20

        if date is None:
            date = 30  # type: ignore

        if date == -1:
            date = None

        if date is not None:
            if date not in self.expirations:
                expiration = self._get_nearest_expiration(date, df=data)
            data = data[data.expiration.astype(str) == expiration]

        days = data.dte.unique().tolist()  # type: ignore

        call_skew = DataFrame()
        put_skew = DataFrame()
        skew_df = DataFrame()
        puts = DataFrame()
        calls = DataFrame()

        # Horizontal skew
        if moneyness is not None:
            atm_call_iv = DataFrame()
            atm_put_iv = DataFrame()
            for day in days:
                strikes = self._get_nearest_otm_strikes(
                    date=day, moneyness=moneyness, underlying_price=underlying_price
                )
                atm_call_strike = self._get_nearest_strike(  # noqa:F841
                    "call", day, underlying_price, call_price_col, False
                )
                call_strike = self._get_nearest_strike(  # noqa:F841
                    "call", day, strikes["call"], call_price_col, False
                )
                _calls = (
                    data[data.dte == day]
                    .query("`option_type` == 'call'")  # type: ignore
                    .copy()
                )
                last_price = (
                    underlying_price
                    if underlying_price is not None
                    else _calls.underlying_price.iloc[0]
                )
                if len(_calls) > 0:
                    call_iv = _calls[_calls.strike == call_strike][
                        ["expiration", "strike", "implied_volatility"]
                    ]
                    atm_call = _calls[_calls.strike == atm_call_strike][
                        ["expiration", "strike", "implied_volatility"]
                    ]
                    if len(atm_call) > 0:
                        calls = concat([calls, call_iv])  # type: ignore
                        atm_call_iv = concat([atm_call_iv, atm_call])  # type: ignore

                atm_put_strike = self._get_nearest_strike(  # noqa:F841
                    "put", day, last_price, put_price_col, False
                )
                put_strike = self._get_nearest_strike(  # noqa:F841
                    "put", day, strikes["put"], put_price_col, False
                )
                _puts = (
                    data[data.dte == day]
                    .query("`option_type` == 'put'")  # type: ignore
                    .copy()
                )
                if len(_puts) > 0:
                    put_iv = _puts[_puts.strike == put_strike][
                        ["expiration", "strike", "implied_volatility"]
                    ]
                    atm_put = _puts[_puts.strike == atm_put_strike][
                        ["expiration", "strike", "implied_volatility"]
                    ]
                    if len(atm_put) > 0:  # type: ignore
                        puts = concat([puts, put_iv])  # type: ignore
                        atm_put_iv = concat([atm_put_iv, atm_put])  # type: ignore

            if calls.empty or puts.empty:
                raise OpenBBError(
                    "Error: Not enough information to complete the operation."
                    " Likely due to zero values in the IV field of the expiration."
                )

            calls = calls.drop_duplicates(subset=["expiration"]).set_index("expiration")  # type: ignore
            atm_call_iv = atm_call_iv.drop_duplicates(subset=["expiration"]).set_index(  # type: ignore
                "expiration"
            )
            puts = puts.drop_duplicates(subset=["expiration"]).set_index("expiration")  # type: ignore
            atm_put_iv = atm_put_iv.drop_duplicates(subset=["expiration"]).set_index(  # type: ignore
                "expiration"
            )
            skew_df["Call Strike"] = calls["strike"]
            skew_df["Call IV"] = calls["implied_volatility"]
            skew_df["Call ATM IV"] = atm_call_iv["implied_volatility"]
            skew_df["Call Skew"] = skew_df["Call IV"] - skew_df["Call ATM IV"]
            skew_df["Put Strike"] = puts["strike"]
            skew_df["Put IV"] = puts["implied_volatility"]
            skew_df["Put ATM IV"] = atm_put_iv["implied_volatility"]
            skew_df["Put Skew"] = skew_df["Put IV"] - skew_df["Put ATM IV"]
            skew_df["ATM Skew"] = skew_df["Call ATM IV"] - skew_df["Put ATM IV"]
            skew_df["IV Skew"] = skew_df["Call Skew"] - skew_df["Put Skew"]
            skew_df = skew_df.reset_index().rename(columns={"expiration": "Expiration"})
            skew_df["Expiration"] = skew_df["Expiration"].astype(str)

            return skew_df

        # Vertical skew

        calls = data[data.option_type == "call"]
        puts = data[data.option_type == "put"]

        for day in days:
            atm_call_strike = self._get_nearest_strike(
                "call", day, underlying_price, force_otm=False
            )  # noqa:F841
            _calls = calls[calls["dte"] == day][
                ["expiration", "option_type", "strike", "implied_volatility"]
            ]

            if len(_calls) > 0:
                call = _calls.set_index("expiration").copy()  # type: ignore
                call_atm_iv = call.query("`strike` == @atm_call_strike")[
                    "implied_volatility"
                ]
                if len(call_atm_iv) > 0:
                    call["ATM IV"] = call_atm_iv.iloc[0]
                    call["Skew"] = call["implied_volatility"] - call["ATM IV"]
                    call_skew = concat([call_skew, call])

            atm_put_strike = self._get_nearest_strike(
                "put", day, force_otm=False
            )  # noqa:F841
            _puts = puts[puts["dte"] == day][
                ["expiration", "option_type", "strike", "implied_volatility"]
            ]

            if len(_puts) > 0:
                put = _puts.set_index("expiration").copy()  # type: ignore
                put_atm_iv = put.query("`strike` == @atm_put_strike")[
                    "implied_volatility"
                ]
                if len(put_atm_iv) > 0:
                    put["ATM IV"] = put_atm_iv.iloc[0]
                    put["Skew"] = put["implied_volatility"] - put["ATM IV"]
                    put_skew = concat([put_skew, put])
        if call_skew.empty or put_skew.empty:
            raise OpenBBError(
                "Error: Not enough information to complete the operation. Likely due to zero values in the IV field."
            )
        call_skew = call_skew.set_index(["strike", "option_type"], append=True)
        put_skew = put_skew.set_index(["strike", "option_type"], append=True)
        skew_df = concat([call_skew, put_skew]).sort_index().reset_index()
        cols = ["Expiration", "Strike", "Option Type", "IV", "ATM IV", "Skew"]
        skew_df.columns = cols
        skew_df["Expiration"] = skew_df["Expiration"].astype(str)

        return skew_df
