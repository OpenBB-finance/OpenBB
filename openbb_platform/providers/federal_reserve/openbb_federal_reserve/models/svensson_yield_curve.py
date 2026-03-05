"""Federal Reserve Svensson Yield Curve Model."""

# pylint: disable=unused-argument,too-many-lines

from datetime import date as dateType
from typing import Any, Literal, get_args

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from openbb_core.provider.utils.lru import ttl_cache
from pydantic import AliasGenerator, ConfigDict, Field, field_validator

SERIES_TYPE = Literal[
    "all",
    "zero_coupon",
    "par_yield",
    "forward_instantaneous",
    "forward_1y",
    "parameters",
    # Individual parameters
    "beta0",
    "beta1",
    "beta2",
    "beta3",
    "tau1",
    "tau2",
    # One-year forward rates
    "sven1f01",
    "sven1f04",
    "sven1f09",
    # Instantaneous forward rates (1-30 years)
    "svenf01",
    "svenf02",
    "svenf03",
    "svenf04",
    "svenf05",
    "svenf06",
    "svenf07",
    "svenf08",
    "svenf09",
    "svenf10",
    "svenf11",
    "svenf12",
    "svenf13",
    "svenf14",
    "svenf15",
    "svenf16",
    "svenf17",
    "svenf18",
    "svenf19",
    "svenf20",
    "svenf21",
    "svenf22",
    "svenf23",
    "svenf24",
    "svenf25",
    "svenf26",
    "svenf27",
    "svenf28",
    "svenf29",
    "svenf30",
    # Par yields (1-30 years)
    "svenpy01",
    "svenpy02",
    "svenpy03",
    "svenpy04",
    "svenpy05",
    "svenpy06",
    "svenpy07",
    "svenpy08",
    "svenpy09",
    "svenpy10",
    "svenpy11",
    "svenpy12",
    "svenpy13",
    "svenpy14",
    "svenpy15",
    "svenpy16",
    "svenpy17",
    "svenpy18",
    "svenpy19",
    "svenpy20",
    "svenpy21",
    "svenpy22",
    "svenpy23",
    "svenpy24",
    "svenpy25",
    "svenpy26",
    "svenpy27",
    "svenpy28",
    "svenpy29",
    "svenpy30",
    # Zero-coupon yields (1-30 years)
    "sveny01",
    "sveny02",
    "sveny03",
    "sveny04",
    "sveny05",
    "sveny06",
    "sveny07",
    "sveny08",
    "sveny09",
    "sveny10",
    "sveny11",
    "sveny12",
    "sveny13",
    "sveny14",
    "sveny15",
    "sveny16",
    "sveny17",
    "sveny18",
    "sveny19",
    "sveny20",
    "sveny21",
    "sveny22",
    "sveny23",
    "sveny24",
    "sveny25",
    "sveny26",
    "sveny27",
    "sveny28",
    "sveny29",
    "sveny30",
]


@ttl_cache(ttl=86400)
def download_csv() -> str:
    """Download the Federal Reserve Svensson Yield Curve CSV data.

    Returns:
        str: URL to the CSV data.
    """
    # pylint: disable=import-outside-toplevel
    from openbb_core.provider.utils.helpers import make_request

    url = "https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv"
    response = make_request(url)
    response.raise_for_status()

    return response.text


class FederalReserveSvenssonQueryParams(QueryParams):
    """Federal Reserve Svensson Yield Curve Query Parameters.

    This data represents the estimates of the term structure of interest rates
    using the Nelson-Siegel-Svensson model, as published by the Federal Reserve.

    Note: This is not an official Federal Reserve statistical release.
    Because this is a staff research product, it is subject to delay,
    revision, or methodological changes without advance notice.

    Source: https://www.federalreserve.gov/data/nominal-yield-curve.htm
    """

    __json_schema_extra__ = {
        "series_type": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "value": "zero_coupon",
            },
        }
    }

    series_type: SERIES_TYPE | str = Field(
        default="all",
        description="Type of yield curve series to return. "
        "Accepts a single value or comma-separated list for multiple selections. "
        "Group options:\n- 'all' (default)\n- 'zero_coupon' (SVENY, continuously compounded)\n- 'par_yield'"
        "(SVENPY, coupon-equivalent)\n- 'forward_instantaneous' (SVENF, continuously compounded)"
        "\n- 'forward_1y' (SVEN1F, coupon-equivalent)\n- 'parameters' (BETA0-BETA3, TAU1-TAU2)\n\n"
        "Individual columns can also be specified (e.g., 'sveny10,sveny20,beta0'). "
        "Used to filter columns after fetching.",
    )
    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", "")
        + " Used to filter results after fetching.",
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", "")
        + " Used to filter results after fetching.",
    )

    @field_validator("series_type")
    @classmethod
    def _validate_series_type(cls, v):
        """Validate series_type field."""
        if not v:
            raise ValueError("series_type cannot be empty.")

        series_list = v.split(",") if isinstance(v, str) else v
        series_list = [v.strip().lower() for v in series_list]

        if "all" in series_list:
            return "all"

        valid_options = get_args(SERIES_TYPE)

        for series in series_list:
            if series not in valid_options:
                raise ValueError(
                    f"Invalid series_type: {series} -> Valid options are: {valid_options}"
                )

        return ",".join(series_list)


class FederalReserveSvenssonData(Data):
    """Federal Reserve Svensson Yield Curve Data.

    This data contains Nelson-Siegel-Svensson model parameters and derived yield curve estimates:
    - Zero-coupon yields (SVENY): Continuously compounded, 1-30 year maturities
    - Par yields (SVENPY): Coupon-equivalent, 1-30 year maturities
    - Instantaneous forward rates (SVENF): Continuously compounded, 1-30 year horizons
    - One-year forward rates (SVEN1F): Coupon-equivalent, at select horizons
    - Model parameters (BETA0-BETA3, TAU1-TAU2): Nelson-Siegel-Svensson coefficients

    Note: This is not an official Federal Reserve statistical release.
    Because this is a staff research product, it is subject to delay,
    revision, or methodological changes without advance notice.

    Source: https://www.federalreserve.gov/data/nominal-yield-curve.htm
    """

    model_config = ConfigDict(
        json_schema_extra={
            "x-widget_config": {
                "$.description": "Nelson-Siegel-Svensson model parameters and derived yield curve estimates.",
                "$.refetchInterval": False,
            }
        },
        populate_by_name=True,
        alias_generator=AliasGenerator(
            serialization_alias=lambda x: x,  # Identity function to preserve field names
        ),
    )

    __alias_dict__: dict[str, str] = {
        "date": "Date",
        # Nelson-Siegel-Svensson Parameters
        "beta0": "BETA0",
        "beta1": "BETA1",
        "beta2": "BETA2",
        "beta3": "BETA3",
        "tau1": "TAU1",
        "tau2": "TAU2",
        # One-year forward rates
        "sven1f01": "SVEN1F01",
        "sven1f04": "SVEN1F04",
        "sven1f09": "SVEN1F09",
        # Instantaneous forward rates (1-30 years)
        "svenf01": "SVENF01",
        "svenf02": "SVENF02",
        "svenf03": "SVENF03",
        "svenf04": "SVENF04",
        "svenf05": "SVENF05",
        "svenf06": "SVENF06",
        "svenf07": "SVENF07",
        "svenf08": "SVENF08",
        "svenf09": "SVENF09",
        "svenf10": "SVENF10",
        "svenf11": "SVENF11",
        "svenf12": "SVENF12",
        "svenf13": "SVENF13",
        "svenf14": "SVENF14",
        "svenf15": "SVENF15",
        "svenf16": "SVENF16",
        "svenf17": "SVENF17",
        "svenf18": "SVENF18",
        "svenf19": "SVENF19",
        "svenf20": "SVENF20",
        "svenf21": "SVENF21",
        "svenf22": "SVENF22",
        "svenf23": "SVENF23",
        "svenf24": "SVENF24",
        "svenf25": "SVENF25",
        "svenf26": "SVENF26",
        "svenf27": "SVENF27",
        "svenf28": "SVENF28",
        "svenf29": "SVENF29",
        "svenf30": "SVENF30",
        # Par yields (1-30 years)
        "svenpy01": "SVENPY01",
        "svenpy02": "SVENPY02",
        "svenpy03": "SVENPY03",
        "svenpy04": "SVENPY04",
        "svenpy05": "SVENPY05",
        "svenpy06": "SVENPY06",
        "svenpy07": "SVENPY07",
        "svenpy08": "SVENPY08",
        "svenpy09": "SVENPY09",
        "svenpy10": "SVENPY10",
        "svenpy11": "SVENPY11",
        "svenpy12": "SVENPY12",
        "svenpy13": "SVENPY13",
        "svenpy14": "SVENPY14",
        "svenpy15": "SVENPY15",
        "svenpy16": "SVENPY16",
        "svenpy17": "SVENPY17",
        "svenpy18": "SVENPY18",
        "svenpy19": "SVENPY19",
        "svenpy20": "SVENPY20",
        "svenpy21": "SVENPY21",
        "svenpy22": "SVENPY22",
        "svenpy23": "SVENPY23",
        "svenpy24": "SVENPY24",
        "svenpy25": "SVENPY25",
        "svenpy26": "SVENPY26",
        "svenpy27": "SVENPY27",
        "svenpy28": "SVENPY28",
        "svenpy29": "SVENPY29",
        "svenpy30": "SVENPY30",
        # Zero-coupon yields (1-30 years)
        "sveny01": "SVENY01",
        "sveny02": "SVENY02",
        "sveny03": "SVENY03",
        "sveny04": "SVENY04",
        "sveny05": "SVENY05",
        "sveny06": "SVENY06",
        "sveny07": "SVENY07",
        "sveny08": "SVENY08",
        "sveny09": "SVENY09",
        "sveny10": "SVENY10",
        "sveny11": "SVENY11",
        "sveny12": "SVENY12",
        "sveny13": "SVENY13",
        "sveny14": "SVENY14",
        "sveny15": "SVENY15",
        "sveny16": "SVENY16",
        "sveny17": "SVENY17",
        "sveny18": "SVENY18",
        "sveny19": "SVENY19",
        "sveny20": "SVENY20",
        "sveny21": "SVENY21",
        "sveny22": "SVENY22",
        "sveny23": "SVENY23",
        "sveny24": "SVENY24",
        "sveny25": "SVENY25",
        "sveny26": "SVENY26",
        "sveny27": "SVENY27",
        "sveny28": "SVENY28",
        "sveny29": "SVENY29",
        "sveny30": "SVENY30",
    }

    # Date field
    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))

    # Nelson-Siegel-Svensson Model Parameters
    beta0: float | None = Field(
        default=None,
        title="Beta 0",
        description="Level component of the Nelson-Siegel-Svensson model. "
        "Represents the long-term asymptotic yield.",
    )
    beta1: float | None = Field(
        default=None,
        title="Beta 1",
        description="Slope component of the Nelson-Siegel-Svensson model. "
        "Represents the short-term component.",
    )
    beta2: float | None = Field(
        default=None,
        title="Beta 2",
        description="First curvature component of the Nelson-Siegel-Svensson model. "
        "Represents the medium-term component.",
    )
    beta3: float | None = Field(
        default=None,
        title="Beta 3",
        description="Second curvature component of the Nelson-Siegel-Svensson model. "
        "Provides additional flexibility for fitting the yield curve.",
    )
    tau1: float | None = Field(
        default=None,
        title="Tau 1",
        description="First decay factor of the Nelson-Siegel-Svensson model. "
        "Controls the rate of decay for beta1 and beta2 components.",
    )
    tau2: float | None = Field(
        default=None,
        title="Tau 2",
        description="Second decay factor of the Nelson-Siegel-Svensson model. "
        "Controls the rate of decay for the beta3 component.",
    )

    # One-year forward rates (coupon-equivalent)
    sven1f01: float | None = Field(
        default=None,
        title="1Y 1Y Forward",
        description="One-year forward rate starting 1 year ahead, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sven1f04: float | None = Field(
        default=None,
        title="1Y 4Y Forward",
        description="One-year forward rate starting 4 years ahead, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sven1f09: float | None = Field(
        default=None,
        title="1Y 9Y Forward",
        description="One-year forward rate starting 9 years ahead, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )

    # Instantaneous forward rates (continuously compounded, 1-30 years)
    svenf01: float | None = Field(
        default=None,
        title="IFR 01Y",
        description="Instantaneous forward rate at 1-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf02: float | None = Field(
        default=None,
        title="IFR 02Y",
        description="Instantaneous forward rate at 2-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf03: float | None = Field(
        default=None,
        title="IFR 03Y",
        description="Instantaneous forward rate at 3-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf04: float | None = Field(
        default=None,
        title="IFR 04Y",
        description="Instantaneous forward rate at 4-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf05: float | None = Field(
        default=None,
        title="IFR 05Y",
        description="Instantaneous forward rate at 5-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf06: float | None = Field(
        default=None,
        title="IFR 06Y",
        description="Instantaneous forward rate at 6-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf07: float | None = Field(
        default=None,
        title="IFR 07Y",
        description="Instantaneous forward rate at 7-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf08: float | None = Field(
        default=None,
        title="IFR 08Y",
        description="Instantaneous forward rate at 8-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf09: float | None = Field(
        default=None,
        title="IFR 09Y",
        description="Instantaneous forward rate at 9-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf10: float | None = Field(
        default=None,
        title="IFR 10Y",
        description="Instantaneous forward rate at 10-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf11: float | None = Field(
        default=None,
        title="IFR 11Y",
        description="Instantaneous forward rate at 11-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf12: float | None = Field(
        default=None,
        title="IFR 12Y",
        description="Instantaneous forward rate at 12-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf13: float | None = Field(
        default=None,
        title="IFR 13Y",
        description="Instantaneous forward rate at 13-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf14: float | None = Field(
        default=None,
        title="IFR 14Y",
        description="Instantaneous forward rate at 14-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf15: float | None = Field(
        default=None,
        title="IFR 15Y",
        description="Instantaneous forward rate at 15-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf16: float | None = Field(
        default=None,
        title="IFR 16Y",
        description="Instantaneous forward rate at 16-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf17: float | None = Field(
        default=None,
        title="IFR 17Y",
        description="Instantaneous forward rate at 17-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf18: float | None = Field(
        default=None,
        title="IFR 18Y",
        description="Instantaneous forward rate at 18-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf19: float | None = Field(
        default=None,
        title="IFR 19Y",
        description="Instantaneous forward rate at 19-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf20: float | None = Field(
        default=None,
        title="IFR 20Y",
        description="Instantaneous forward rate at 20-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf21: float | None = Field(
        default=None,
        title="IFR 21Y",
        description="Instantaneous forward rate at 21-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf22: float | None = Field(
        default=None,
        title="IFR 22Y",
        description="Instantaneous forward rate at 22-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf23: float | None = Field(
        default=None,
        title="IFR 23Y",
        description="Instantaneous forward rate at 23-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf24: float | None = Field(
        default=None,
        title="IFR 24Y",
        description="Instantaneous forward rate at 24-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf25: float | None = Field(
        default=None,
        title="IFR 25Y",
        description="Instantaneous forward rate at 25-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf26: float | None = Field(
        default=None,
        title="IFR 26Y",
        description="Instantaneous forward rate at 26-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf27: float | None = Field(
        default=None,
        title="IFR 27Y",
        description="Instantaneous forward rate at 27-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf28: float | None = Field(
        default=None,
        title="IFR 28Y",
        description="Instantaneous forward rate at 28-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf29: float | None = Field(
        default=None,
        title="IFR 29Y",
        description="Instantaneous forward rate at 29-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenf30: float | None = Field(
        default=None,
        title="IFR 30Y",
        description="Instantaneous forward rate at 30-year horizon, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )

    # Par yields (coupon-equivalent, 1-30 years)
    svenpy01: float | None = Field(
        default=None,
        title="Par Yield 01Y",
        description="Par yield at 1-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy02: float | None = Field(
        default=None,
        title="Par Yield 02Y",
        description="Par yield at 2-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy03: float | None = Field(
        default=None,
        title="Par Yield 03Y",
        description="Par yield at 3-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy04: float | None = Field(
        default=None,
        title="Par Yield 04Y",
        description="Par yield at 4-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy05: float | None = Field(
        default=None,
        title="Par Yield 05Y",
        description="Par yield at 5-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy06: float | None = Field(
        default=None,
        title="Par Yield 06Y",
        description="Par yield at 6-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy07: float | None = Field(
        default=None,
        title="Par Yield 07Y",
        description="Par yield at 7-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy08: float | None = Field(
        default=None,
        title="Par Yield 08Y",
        description="Par yield at 8-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy09: float | None = Field(
        default=None,
        title="Par Yield 09Y",
        description="Par yield at 9-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy10: float | None = Field(
        default=None,
        title="Par Yield 10Y",
        description="Par yield at 10-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy11: float | None = Field(
        default=None,
        title="Par Yield 11Y",
        description="Par yield at 11-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy12: float | None = Field(
        default=None,
        title="Par Yield 12Y",
        description="Par yield at 12-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy13: float | None = Field(
        default=None,
        title="Par Yield 13Y",
        description="Par yield at 13-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy14: float | None = Field(
        default=None,
        title="Par Yield 14Y",
        description="Par yield at 14-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy15: float | None = Field(
        default=None,
        title="Par Yield 15Y",
        description="Par yield at 15-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy16: float | None = Field(
        default=None,
        title="Par Yield 16Y",
        description="Par yield at 16-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy17: float | None = Field(
        default=None,
        title="Par Yield 17Y",
        description="Par yield at 17-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy18: float | None = Field(
        default=None,
        title="Par Yield 18Y",
        description="Par yield at 18-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy19: float | None = Field(
        default=None,
        title="Par Yield 19Y",
        description="Par yield at 19-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy20: float | None = Field(
        default=None,
        title="Par Yield 20Y",
        description="Par yield at 20-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy21: float | None = Field(
        default=None,
        title="Par Yield 21Y",
        description="Par yield at 21-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy22: float | None = Field(
        default=None,
        title="Par Yield 22Y",
        description="Par yield at 22-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy23: float | None = Field(
        default=None,
        title="Par Yield 23Y",
        description="Par yield at 23-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy24: float | None = Field(
        default=None,
        title="Par Yield 24Y",
        description="Par yield at 24-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy25: float | None = Field(
        default=None,
        title="Par Yield 25Y",
        description="Par yield at 25-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy26: float | None = Field(
        default=None,
        title="Par Yield 26Y",
        description="Par yield at 26-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy27: float | None = Field(
        default=None,
        title="Par Yield 27Y",
        description="Par yield at 27-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy28: float | None = Field(
        default=None,
        title="Par Yield 28Y",
        description="Par yield at 28-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy29: float | None = Field(
        default=None,
        title="Par Yield 29Y",
        description="Par yield at 29-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    svenpy30: float | None = Field(
        default=None,
        title="Par Yield 30Y",
        description="Par yield at 30-year maturity, coupon-equivalent.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )

    # Zero-coupon yields (continuously compounded, 1-30 years)
    sveny01: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 01Y",
        description="Zero-coupon yield at 1-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny02: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 02Y",
        description="Zero-coupon yield at 2-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny03: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 03Y",
        description="Zero-coupon yield at 3-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny04: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 04Y",
        description="Zero-coupon yield at 4-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny05: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 05Y",
        description="Zero-coupon yield at 5-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny06: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 06Y",
        description="Zero-coupon yield at 6-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny07: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 07Y",
        description="Zero-coupon yield at 7-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny08: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 08Y",
        description="Zero-coupon yield at 8-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny09: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 09Y",
        description="Zero-coupon yield at 9-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny10: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 10Y",
        description="Zero-coupon yield at 10-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny11: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 11Y",
        description="Zero-coupon yield at 11-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny12: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 12Y",
        description="Zero-coupon yield at 12-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny13: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 13Y",
        description="Zero-coupon yield at 13-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny14: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 14Y",
        description="Zero-coupon yield at 14-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny15: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 15Y",
        description="Zero-coupon yield at 15-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny16: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 16Y",
        description="Zero-coupon yield at 16-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny17: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 17Y",
        description="Zero-coupon yield at 17-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny18: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 18Y",
        description="Zero-coupon yield at 18-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny19: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 19Y",
        description="Zero-coupon yield at 19-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny20: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 20Y",
        description="Zero-coupon yield at 20-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny21: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 21Y",
        description="Zero-coupon yield at 21-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny22: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 22Y",
        description="Zero-coupon yield at 22-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny23: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 23Y",
        description="Zero-coupon yield at 23-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny24: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 24Y",
        description="Zero-coupon yield at 24-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny25: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 25Y",
        description="Zero-coupon yield at 25-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny26: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 26Y",
        description="Zero-coupon yield at 26-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny27: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 27Y",
        description="Zero-coupon yield at 27-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny28: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 28Y",
        description="Zero-coupon yield at 28-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny29: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 29Y",
        description="Zero-coupon yield at 29-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )
    sveny30: float | None = Field(
        default=None,
        title="Zero-Coupon Yield 30Y",
        description="Zero-coupon yield at 30-year maturity, continuously compounded.",
        json_schema_extra={"x-unit_measurement": "percent"},
    )

    @field_validator(
        "beta0",
        "beta1",
        "beta2",
        "beta3",
        "tau1",
        "tau2",
        "sven1f01",
        "sven1f04",
        "sven1f09",
        "svenf01",
        "svenf02",
        "svenf03",
        "svenf04",
        "svenf05",
        "svenf06",
        "svenf07",
        "svenf08",
        "svenf09",
        "svenf10",
        "svenf11",
        "svenf12",
        "svenf13",
        "svenf14",
        "svenf15",
        "svenf16",
        "svenf17",
        "svenf18",
        "svenf19",
        "svenf20",
        "svenf21",
        "svenf22",
        "svenf23",
        "svenf24",
        "svenf25",
        "svenf26",
        "svenf27",
        "svenf28",
        "svenf29",
        "svenf30",
        "svenpy01",
        "svenpy02",
        "svenpy03",
        "svenpy04",
        "svenpy05",
        "svenpy06",
        "svenpy07",
        "svenpy08",
        "svenpy09",
        "svenpy10",
        "svenpy11",
        "svenpy12",
        "svenpy13",
        "svenpy14",
        "svenpy15",
        "svenpy16",
        "svenpy17",
        "svenpy18",
        "svenpy19",
        "svenpy20",
        "svenpy21",
        "svenpy22",
        "svenpy23",
        "svenpy24",
        "svenpy25",
        "svenpy26",
        "svenpy27",
        "svenpy28",
        "svenpy29",
        "svenpy30",
        "sveny01",
        "sveny02",
        "sveny03",
        "sveny04",
        "sveny05",
        "sveny06",
        "sveny07",
        "sveny08",
        "sveny09",
        "sveny10",
        "sveny11",
        "sveny12",
        "sveny13",
        "sveny14",
        "sveny15",
        "sveny16",
        "sveny17",
        "sveny18",
        "sveny19",
        "sveny20",
        "sveny21",
        "sveny22",
        "sveny23",
        "sveny24",
        "sveny25",
        "sveny26",
        "sveny27",
        "sveny28",
        "sveny29",
        "sveny30",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def validate_float_fields(cls, v: Any) -> float | None:
        """Handle NA values and sentinel values, return None for missing data."""
        if v is None:
            return None
        if isinstance(v, str):
            v = v.strip()
            if v in ("", "NA", "ND", "N/A"):
                return None
        try:
            value = float(v)
            # -999.99 is used as a sentinel for missing TAU2 values
            if value == -999.99:
                return None
            return value
        except (ValueError, TypeError):
            return None


class FederalReserveSvenssonFetcher(
    Fetcher[FederalReserveSvenssonQueryParams, list[FederalReserveSvenssonData]]
):
    """Federal Reserve Svensson Yield Curve Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FederalReserveSvenssonQueryParams:
        """Transform input parameters into FederalReserveSvenssonQueryParams."""
        return FederalReserveSvenssonQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveSvenssonQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> str:
        """Download the CSV data from the Federal Reserve."""
        try:
            return download_csv()
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: FederalReserveSvenssonQueryParams,
        data: str,
        **kwargs: Any,
    ) -> list[FederalReserveSvenssonData]:
        """Transform the CSV data into a list of FederalReserveSvenssonData objects."""
        # pylint: disable=import-outside-toplevel
        import csv
        from datetime import datetime
        from io import StringIO

        csv_to_field = {
            v: k for k, v in FederalReserveSvenssonData.__alias_dict__.items()
        }
        allowed_fields: set[str] | None = None

        # Parse comma-separated series_type into a list
        series_types = [s.strip().lower() for s in query.series_type.split(",")]

        if "all" not in series_types:
            allowed_fields = {"date"}

            for series_type in series_types:
                if series_type == "zero_coupon":
                    allowed_fields.update(f"sveny{i:02d}" for i in range(1, 31))
                elif series_type == "par_yield":
                    allowed_fields.update(f"svenpy{i:02d}" for i in range(1, 31))
                elif series_type == "forward_instantaneous":
                    allowed_fields.update(f"svenf{i:02d}" for i in range(1, 31))
                elif series_type == "forward_1y":
                    allowed_fields.update({"sven1f01", "sven1f04", "sven1f09"})
                elif series_type == "parameters":
                    allowed_fields.update(
                        {"beta0", "beta1", "beta2", "beta3", "tau1", "tau2"}
                    )
                else:
                    # Individual column selection
                    allowed_fields.add(series_type)

        # Find the line starting with "Date," which is the real column header.
        lines = data.split("\n")
        header_index = next(
            (i for i, line in enumerate(lines) if line.startswith("Date,")),
            None,
        )

        if header_index is None:
            raise OpenBBError("Could not find the header row in the CSV data.")

        csv_content = "\n".join(lines[header_index:])
        reader = csv.DictReader(StringIO(csv_content))
        results: list[FederalReserveSvenssonData] = []

        for row in reader:
            date_str = row.get("Date", "")
            if not date_str:
                continue

            try:
                row_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                continue

            if query.start_date and row_date < query.start_date:
                continue

            if query.end_date and row_date > query.end_date:
                continue

            filtered_row: dict[str, Any] = {}
            for csv_col, value in row.items():
                field_name = csv_to_field.get(csv_col)

                if field_name is None:
                    continue

                if allowed_fields is not None and field_name not in allowed_fields:
                    continue

                filtered_row[field_name] = value

            if filtered_row:
                results.append(FederalReserveSvenssonData(**filtered_row))

        if not results:
            raise OpenBBError(
                "The query filters resulted in no data. Try again with different parameters."
            )

        return results
