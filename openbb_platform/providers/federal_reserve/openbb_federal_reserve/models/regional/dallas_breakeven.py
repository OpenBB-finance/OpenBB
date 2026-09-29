"""Federal Reserve Bank of Dallas Oil Break-Even Prices Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import QUERY_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field

URL = (
    "https://www.dallasfed.org/-/media/documents/research/surveys/des"
    "/documents/breakeven.xlsx"
)

_SHEETS = {"existing": "Existing Wells", "new": "New Wells"}


class FederalReserveDallasBreakevenQueryParams(QueryParams):
    """Dallas Fed Oil Break-Even Prices Query Parameters."""

    __json_schema_extra__ = {
        "well_type": {
            "x-widget_config": {
                "options": [
                    {"label": sheet, "value": code} for code, sheet in _SHEETS.items()
                ]
            }
        },
    }

    well_type: Literal["existing", "new"] = Field(
        default="new",
        description="Break-even price to profitably operate existing wells or to"
        " profitably drill new wells.",
    )
    start_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date", "")
    )
    end_date: dateType | None = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date", "")
    )


class FederalReserveDallasBreakevenData(Data):
    """Dallas Fed Oil Break-Even Prices Data."""

    date: dateType = Field(description="The survey quarter-end date.")
    play: str = Field(description="The shale play or region.")
    value: float | None = Field(
        default=None,
        description="The average break-even WTI price, in dollars per barrel.",
    )


class FederalReserveDallasBreakevenFetcher(
    Fetcher[
        FederalReserveDallasBreakevenQueryParams,
        list[FederalReserveDallasBreakevenData],
    ]
):
    """Dallas Fed Oil Break-Even Prices Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FederalReserveDallasBreakevenQueryParams:
        """Transform the query params."""
        return FederalReserveDallasBreakevenQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FederalReserveDallasBreakevenQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Download the break-even prices workbook from the Dallas Fed."""
        from openbb_core.provider.utils.helpers import make_request

        from openbb_federal_reserve.utils.cache import (
            cached,
            seconds_until_next_release,
        )

        def _producer() -> bytes:
            """Fetch the raw break-even workbook bytes."""
            response = make_request(URL)
            response.raise_for_status()
            return response.content

        content = cached(
            "dallas_breakeven",
            lambda: seconds_until_next_release("quarterly"),
            _producer,
        )
        if not content:
            raise EmptyDataError("The request was returned empty.")
        return [{"_raw": content}]

    @staticmethod
    def transform_data(
        query: FederalReserveDallasBreakevenQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[FederalReserveDallasBreakevenData]:
        """Melt the play-by-quarter table to long records."""
        from io import BytesIO

        from pandas import isna, read_excel, to_numeric

        from openbb_federal_reserve.utils.dallas import (
            find_label_row,
            quarter_to_date,
        )

        sheet = _SHEETS[query.well_type]
        header = find_label_row(data[0]["_raw"], sheet, marker="play")
        frame = read_excel(BytesIO(data[0]["_raw"]), sheet_name=sheet, header=header)
        frame = frame.rename(columns={frame.columns[0]: "play"})
        frame = frame.dropna(subset=["play"])
        quarter_columns = [c for c in frame.columns if quarter_to_date(c) is not None]

        records: list[dict] = []
        for row in frame.to_dict(orient="records"):
            play = str(row["play"]).strip()
            for column in quarter_columns:
                observed = quarter_to_date(column)
                if observed is None:  # pragma: no cover - columns pre-filtered non-None
                    continue
                if query.start_date and observed < query.start_date:
                    continue
                if query.end_date and observed > query.end_date:
                    continue
                value = to_numeric(row[column], errors="coerce")
                if isna(value):
                    continue
                records.append(
                    {
                        "date": observed,
                        "play": play,
                        "value": float(value),
                    }
                )

        if not records:
            raise EmptyDataError("No data was found for the given query parameters.")

        return [
            FederalReserveDallasBreakevenData.model_validate(record)
            for record in sorted(records, key=lambda r: (r["date"], r["play"]))
        ]
