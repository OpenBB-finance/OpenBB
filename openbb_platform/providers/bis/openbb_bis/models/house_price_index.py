"""BIS House Price Index Model."""

# pylint: disable=unused-argument

from datetime import date
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_bis.utils.constants import (
    CODE_FREQ_TO_KEY,
    CODE_TO_COUNTRY_HOUSE_PRICE_INDEX,
    COUNTRY_TO_CODE_HOUSE_PRICE_INDEX,
)
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.house_price_index import (
    HousePriceIndexData,
    HousePriceIndexQueryParams,
)
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import check_item
from pydantic import Field, field_validator

countries = tuple(CODE_TO_COUNTRY_HOUSE_PRICE_INDEX.values())
CountriesList = list(countries)  # type: ignore
FREQUENCY_TO_FREQ = {
    "monthly": "M",
    "quarter": "Q",
    "annual": "A",
}
FREQ_TO_FREQUENCY = {v: k for k, v in FREQUENCY_TO_FREQ.items()}
freqTuple = tuple(FREQUENCY_TO_FREQ.values())
# To do: The following feature from the Standard Model is not implemented
# transformDict = {"yoy": "PA", "period": "PC", "index": "IX"}


class BISHousePriceIndexQueryParams(HousePriceIndexQueryParams):
    """BIS House Price Index Query.

    Source: https://data.bis.org/
    """

    __json_schema_extra__ = {
        "country": {
            "multiple_items_allowed": True,
            "choices": CountriesList,
        }
    }

    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )

    @field_validator("country", mode="before", check_fields=False)
    @classmethod
    def validate_country(cls, c):
        """Validate country."""
        result: List = []
        values = c.replace(" ", "_").split(",")
        for v in values:
            if v.upper() in CODE_TO_COUNTRY_HOUSE_PRICE_INDEX:
                result.append(CODE_TO_COUNTRY_HOUSE_PRICE_INDEX.get(v.upper()))
                continue
            try:
                check_item(v.lower(), CountriesList)
            except Exception as e:
                if len(values) == 1:
                    raise e from e
                warn(f"Invalid country: {v}. Skipping...")
                continue
            result.append(v.lower())
        if result:
            return ",".join(result)
        raise OpenBBError(f"No valid country found. -> {values}")


class BISHousePriceIndexData(HousePriceIndexData):
    """BIS House Price Index Data."""


class BISHousePriceIndexFetcher(
    Fetcher[BISHousePriceIndexQueryParams, List[BISHousePriceIndexData]]
):
    """BIS House Price Index Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> BISHousePriceIndexQueryParams:
        """Transform the query."""
        transformed_params = params.copy()
        if transformed_params.get("start_date") is None:
            transformed_params["start_date"] = date(1819, 1, 1)
        if transformed_params.get("end_date") is None:
            transformed_params["end_date"] = date(date.today().year, 12, 31)
        if transformed_params.get("country") is None:
            transformed_params["country"] = "united_states"

        return BISHousePriceIndexQueryParams(**transformed_params)

    @staticmethod
    def extract_data(
        query: BISHousePriceIndexQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the BIS endpoint."""
        # pylint: disable=import-outside-toplevel
        from io import StringIO  # noqa
        from openbb_bis.utils.helpers import bis_date_to_python_date  # noqa
        from openbb_core.provider.utils.helpers import make_request  # noqa
        from pandas import read_csv  # noqa

        queryFreq = FREQUENCY_TO_FREQ.get(query.frequency, "Q")

        # Convert countries (comma-sep-string) to codes
        countriesCodeList = [
            COUNTRY_TO_CODE_HOUSE_PRICE_INDEX[country]
            for country in query.country.split(",")
        ]

        def fnCodeFreqKeyStr(countriesCodeList: List) -> str:
            """Convert country code with frequency to item(s) download key(s), as merged string"""
            _keysList: List = []
            for code in countriesCodeList:
                # Find the closest data frequency available
                # Scenario 1: user wants DE.M but only DE.Q is there
                # Scenario 2: user wants TH.Q but only TH.M is there
                iLastFound = -1
                for i, f in enumerate(freqTuple):
                    if code + "." + f in CODE_FREQ_TO_KEY:
                        iLastFound += 1  # For Scenario 2
                        freq = f
                        if freq == queryFreq:
                            break  # For Scenario 1
                if freq != queryFreq:
                    warn(
                        f"({code}) {CODE_TO_COUNTRY_HOUSE_PRICE_INDEX[code]}: "
                        + FREQ_TO_FREQUENCY[queryFreq]
                        + " data not found. Switching to "
                        + FREQ_TO_FREQUENCY[freq]
                        + "."
                    )
                codeFreq = code + "." + freq
                _keysList.append(CODE_FREQ_TO_KEY[codeFreq])
            return ",".join(_keysList)

        keysStr = fnCodeFreqKeyStr(countriesCodeList)
        start_date = query.start_date.strftime("%Y-%m") if query.start_date else ""
        end_date = query.end_date.strftime("%Y-%m") if query.end_date else ""

        filterStr = ""
        filterStr += "?c%5BTIME_PERIOD%5D=" if start_date or end_date else ""
        if start_date != end_date:
            filterStr += "ge%3A" + start_date if start_date else ""
            filterStr += "%2B" if start_date and end_date else ""
            filterStr += "le%3A" + end_date if end_date else ""
        else:
            filterStr += "eq%3A" + start_date if start_date else ""

        # Example:
        # https://stats.bis.org/api/v2/data/dataflow/BIS/WS_DPP/%2B/M.AU.0.1.1.2.6.0,M.JP.0.1.0.3.6.0?c%5BTIME_PERIOD%5D=ge%3A2020-01%2Ble%3A2020-12
        url = (
            "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_DPP/%2B/"
            + f"{keysStr}"
            + f"{filterStr}"
        )
        headers = {"accept": "application/vnd.sdmx.data+csv;version=1.0.0"}
        response = make_request(url, headers=headers, timeout=20)
        if response.status_code == 404:
            raise OpenBBError(
                "Data not found. Please try different key(s) or constraint(s): "
                + f"{url}"
            )
        if response.status_code != 200:
            raise OpenBBError(
                f"Error with the BIS request (HTTP {response.status_code}): `{response.text}`"
            )
        df = read_csv(StringIO(response.text)).get(
            ["REF_AREA", "TIME_PERIOD", "OBS_VALUE"]
        )
        if df.empty:
            raise EmptyDataError()
        df = df.rename(
            columns={"REF_AREA": "country", "TIME_PERIOD": "date", "OBS_VALUE": "value"}
        )
        df.country = df.country.map(CODE_TO_COUNTRY_HOUSE_PRICE_INDEX)
        df.date = df.date.apply(bis_date_to_python_date)
        df = (
            df.query("value.notnull()")
            .set_index(["date", "country"])
            .sort_index()
            .reset_index()
        )

        return df.to_dict("records")

    @staticmethod
    def transform_data(
        query: BISHousePriceIndexQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[BISHousePriceIndexData]:
        """Transform the data from the BIS endpoint."""
        return [BISHousePriceIndexData.model_validate(d) for d in data]
