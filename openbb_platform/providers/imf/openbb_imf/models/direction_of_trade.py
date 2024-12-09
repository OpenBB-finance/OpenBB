"""IMF Direction Of Trade Model."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Optional, Union

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.direction_of_trade import (
    DirectionOfTradeData,
    DirectionOfTradeQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_imf.utils.dot_helpers import (
    load_country_map,
    load_country_to_code_map,
    validate_countries,
)

dot_indicators_dict = {
    "exports": "TXG_FOB_USD",
    "imports": "TMG_CIF_USD",
    "balance": "TBG_USD",
    "all": "TXG_FOB_USD+TMG_CIF_USD+TBG_USD",
}

dot_titles_map = {
    "TXG_FOB_USD": "Goods, Value of Exports, Free on board (FOB), US Dollars",
    "TMG_CIF_USD": "Goods, Value of Imports, Cost, Insurance, Freight (CIF), US Dollars",
    "TBG_USD": "Goods, Value of Trade Balance, US Dollars",
}


class ImfDirectionOfTradeQueryParams(DirectionOfTradeQueryParams):
    """IMF Direction Of Trade Query Parameters."""

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": ["all"] + sorted(list(load_country_to_code_map())),
        },
        "counterpart": {
            "multiple_items_allowed": True,
            "choices": ["all"] + sorted(list(load_country_to_code_map())),
        },
    }


class ImfDirectionOfTradeData(DirectionOfTradeData):
    """IMF Direction Of Trade Data."""


class ImfDirectionOfTradeFetcher(
    Fetcher[ImfDirectionOfTradeQueryParams, list[ImfDirectionOfTradeData]]
):
    """IMF Direction Of Trade Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> ImfDirectionOfTradeQueryParams:
        """Transform query parameters."""
        countries = params.get("country", "")
        countries = countries.split(",") if countries else "all"
        if countries != "all":
            countries = validate_countries(countries)
        counterparts = params.get("counterpart", "")
        counterparts = counterparts.split(",") if params.get("counterpart") else "all"
        if counterparts != "all":
            counterparts = validate_countries(counterparts)
        now = datetime.now().date()

        if countries == "all" and counterparts == "all":
            raise OpenBBError(
                "Both 'country' and 'counterpart' cannot be None, or 'all'."
                + " Please supply lowercase country names or two-letter ISO codes."
            )
        if countries == counterparts:
            raise OpenBBError("The 'country' and 'counterpart' cannot be the same.")

        params["country"] = countries
        params["counterpart"] = counterparts

        if not params.get("end_date"):
            params["end_date"] = now.replace(month=12, day=31).strftime("%Y-%m-%d")

        if (countries == "all" or counterparts == "all") and not params.get(
            "start_date"
        ):
            params["start_date"] = now.replace(year=now.year - 1).strftime("%Y-%m-%d")

        return ImfDirectionOfTradeQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: ImfDirectionOfTradeQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list[dict]:
        """Extract the data from the IMF API."""
        # pylint: disable=import-outside-toplevel
        from aiohttp.client_exceptions import ContentTypeError  # noqa
        from json import JSONDecodeError
        from openbb_core.provider.utils.helpers import amake_request
        from pandas import to_datetime
        from pandas.tseries import offsets

        start_date = query.start_date
        end_date = query.end_date
        frequency = query.frequency[0].upper()
        country = query.country if query.country != "all" else ""
        counterpart = query.counterpart if query.counterpart != "all" else ""
        indicator = dot_indicators_dict[query.direction]
        # Adjust the dates to the date relative to frequency.
        # The API does not accept arbitrary dates, so we need to adjust them.
        if start_date:
            start_date = to_datetime(start_date)
            if frequency == "Q":
                start_date = offsets.QuarterBegin(startingMonth=1).rollback(start_date)
            elif frequency == "A":
                start_date = offsets.YearBegin().rollback(start_date)
            else:
                start_date = offsets.MonthBegin().rollback(start_date)
            start_date = start_date.strftime("%Y-%m-%d")  # type: ignore

        if end_date:
            end_date = to_datetime(end_date)
            if frequency == "Q":
                end_date = offsets.QuarterEnd().rollforward(end_date)
            elif frequency == "A":
                end_date = offsets.YearEnd().rollforward(end_date)
            else:
                end_date = offsets.MonthEnd().rollforward(end_date)
            end_date = end_date.strftime("%Y-%m-%d")  # type: ignore

        date_range = (  # type: ignore
            f"?startPeriod={start_date}&endPeriod={end_date}"
            if start_date and end_date
            else ""
        )
        base_url = "http://dataservices.imf.org/REST/SDMX_JSON.svc/"
        key = f"CompactData/DOT/{frequency}.{country}.{indicator}.{counterpart}"
        url = f"{base_url}{key}{date_range}"

        try:
            response = await amake_request(url, timeout=20)
        except (JSONDecodeError, ContentTypeError) as e:
            raise OpenBBError(
                "Error fetching data; This might be rate-limiting. Try again later."
            ) from e

        if "ErrorDetails" in response:
            raise OpenBBError(
                f"{response['ErrorDetails'].get('Code')} -> {response['ErrorDetails'].get('Message')}"  # type: ignore
            )

        series = response.get("CompactData", {}).get("DataSet", {}).pop("Series", {})  # type: ignore

        if not series:
            raise OpenBBError(f"No time series data found -> {url} -> {response}")

        # If there is only one series, they ruturn a dict instead of a list.
        if series and isinstance(series, dict):
            series = [series]

        return series

    @staticmethod
    def transform_data(
        query: ImfDirectionOfTradeQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[ImfDirectionOfTradeData]:
        """Transform the data."""
        # pylint: disable=import-outside-toplevel
        from openbb_imf.utils.constants import UNIT_MULTIPLIERS_MAP  # noqa
        from pandas import Categorical, DataFrame, to_datetime
        from pandas.tseries import offsets

        if not data:
            raise EmptyDataError()

        dot_code_to_country = load_country_map()
        series = data
        results: list = []

        for s in series:
            if "Obs" not in s:
                continue
            meta = {
                k.replace("@", "").lower(): (
                    UNIT_MULTIPLIERS_MAP.get(str(v), v) if k == "@UNIT_MULT" else v
                )
                for k, v in s.items()
                if k != "Obs"
            }
            _symbol = meta.get("indicator", "")
            _title = None

            _data = s.pop("Obs", [])

            if isinstance(_data, dict):
                _data = [_data]

            for d in _data:
                _date = d.pop("@TIME_PERIOD", None)
                val: Union[float, None] = d.pop("@OBS_VALUE", None)
                _ = d.pop("@OBS_STATUS", None)
                val = float(val) if val else None
                if not val:
                    continue

                if _date:
                    offset = (
                        offsets.QuarterEnd
                        if "Q" in _date
                        else (
                            offsets.YearEnd
                            if len(str(_date)) == 4
                            else offsets.MonthEnd
                        )
                    )
                    _date = to_datetime(_date)
                    _date = _date + offset(0)
                    _date = _date.strftime("%Y-%m-%d")
                vals = {
                    k: v
                    for k, v in {
                        "date": _date,
                        "symbol": _symbol,
                        "country": dot_code_to_country.get(
                            meta.get("ref_area"), meta.get("ref_area")
                        ),
                        "counterpart": dot_code_to_country.get(
                            meta.get("counterpart_area"), meta.get("counterpart_area")
                        ),
                        "title": dot_titles_map.get(_symbol),
                        "scale": meta.get("unit_mult"),
                        "value": val,
                    }.items()
                    if v
                }

                if (
                    vals.get("value")
                    and vals.get("date")
                    and vals.get("country") != vals.get("counterpart")
                ):
                    d.update(vals)

            if _data:
                results.extend([d for d in _data if d])

        df = DataFrame(results)
        df["symbol"] = Categorical(
            df["symbol"],
            categories=list(dot_titles_map),
            ordered=True,
        )
        df["country"] = Categorical(
            df["country"],
            categories=sorted(df.country.unique().tolist()),
            ordered=True,
        )
        df["counterpart"] = Categorical(
            df["counterpart"],
            categories=sorted(df.counterpart.unique().tolist()),
            ordered=True,
        )
        df = df.sort_values(by=["date", "country", "counterpart"])

        return [
            ImfDirectionOfTradeData.model_validate(r)
            for r in df.to_dict(orient="records")
        ]
