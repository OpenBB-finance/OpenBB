"""FRED Economic Calendar Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.economic_calendar import (
    EconomicCalendarData,
    EconomicCalendarQueryParams,
)
from pydantic import Field


class FredEconomicCalendarQueryParams(EconomicCalendarQueryParams):
    """FRED Economic Calendar Query.

    Source: https://fred.stlouisfed.org/releases/calendar
    """

    release_id: int | None = Field(default=None, description="Filter by release ID.")


class FredEconomicCalendarData(EconomicCalendarData):
    """FRED Economic Calendar Data."""

    release_id: int | None = Field(
        default=None, description="Release ID associated with the economic event."
    )


class FredEconomicCalendarFetcher(
    Fetcher[FredEconomicCalendarQueryParams, list[FredEconomicCalendarData]]
):
    """FRED Economic Calendar Fetcher."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FredEconomicCalendarQueryParams:
        """Transform query parameters."""
        return FredEconomicCalendarQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FredEconomicCalendarQueryParams,
        credentials: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> list:
        """Extract data from the source."""
        # pylint: disable=import-outside-toplevel
        import asyncio
        import json
        from datetime import datetime, timedelta
        from io import StringIO
        from math import ceil

        from openbb_core.provider.utils.helpers import amake_request
        from pandas import (
            DataFrame,
            concat,
            date_range as pd_date_range,
            read_html,
        )

        def process_pager(pager: str, date: str = "") -> DataFrame:
            """Process a page of events HTML into a DataFrame."""
            buf = StringIO(pager)
            df = read_html(buf, extract_links="all")[0]
            df.columns = ["date", "event"]
            df["date"] = df.date.apply(lambda x: x[0].replace("N/A", "") or None)

            # Extract release_id from link; rows without a link are date-header rows.
            df["release_id"] = df.event.apply(
                lambda x: x[1].split("rid=")[-1] if x[1] else None
            )
            df["event"] = df.event.apply(lambda x: x[0])

            is_header = df["release_id"].isna()

            if is_header.any():
                # Header rows carry full date strings like
                # "Wednesday February 05, 2025 Updated".
                # Event rows carry times like "7:30 AM ET".
                # Clean header dates.
                df.loc[is_header, "date"] = (
                    df.loc[is_header, "date"]
                    .str.replace(r"\s*(Updated|Revised)\s*$", "", regex=True)
                    .str.strip()
                )
                # Forward-fill header dates so each event row knows its date.
                df["_event_date"] = (
                    df["date"]
                    .where(is_header)
                    .ffill()
                    .astype("datetime64[ns]")
                    .dt.strftime("%Y-%m-%d")
                )
                # Forward-fill times among event rows (handles N/A time rows).
                df["_time"] = df["date"].where(~is_header).ffill().fillna("")

                # Build full datetime: "YYYY-MM-DD HH:MM AM ET"
                df.loc[~is_header, "date"] = (
                    df.loc[~is_header, "_event_date"]
                    + " "
                    + df.loc[~is_header, "_time"]
                ).str.strip()

                # Drop header rows and temp columns.
                df = (
                    df[~is_header]
                    .drop(columns=["_event_date", "_time"])
                    .reset_index(drop=True)
                )
            else:
                # Fallback: all rows are events with time values (no headers present).
                df["date"] = df["date"].ffill()
                if date:
                    df["date"] = df["date"].apply(lambda x: f"{date} {x}")

            df["date"] = (
                df["date"].astype("datetime64[ns]").dt.tz_localize("US/Central")
            )

            return df

        async def response_callback(response, _):
            """Process the response text."""
            text = await response.text()
            return json.loads(text)

        async def fetch_date_pages(
            start_date: str,
            end_date: str = "",
            rid: str = "",
        ) -> DataFrame:
            """Fetch all pages of the FRED releases calendar for a single date or date range."""
            end_date = end_date or start_date
            base_url = (
                "https://fred.stlouisfed.org/releases/calendar"
                f"?po=1&ptic=0&vs={start_date}&ve={end_date}&rid={rid}"
            )
            first_page = await amake_request(
                base_url, response_callback=response_callback
            )
            n_results = first_page.get("ptic", 0)  # type: ignore

            if n_results == 0:
                return DataFrame()

            records = [process_pager(first_page["pager"], date=start_date)]  # type: ignore

            if len(records[0]) >= n_results:
                return records[0]

            # Build URLs for remaining pages (50 results per page).
            total_pages = ceil(n_results / 50)
            remaining_urls = [
                f"{base_url}&pageID={page}" for page in range(2, total_pages + 1)
            ]

            async def _fetch_page(url: str):
                return await amake_request(url, response_callback=response_callback)

            responses = await asyncio.gather(*[_fetch_page(u) for u in remaining_urls])

            for resp in responses:
                records.append(process_pager(resp["pager"], date=start_date))  # type: ignore

            result = concat(records, ignore_index=True)

            return result

        async def fetch_all_pages(
            start_date: str,
            end_date: str = "",
            rid: str = "",
        ) -> DataFrame:
            """Fetch all pages of the FRED releases calendar for each date in a range.

            If a release ID is supplied, the entire date range is fetched in a single
            paginated call. Otherwise, each date is fetched individually to ensure
            complete results.
            """
            end_date = end_date or start_date

            if rid:
                # A specific release ID can be fetched across the full range at once.
                return await fetch_date_pages(start_date, end_date, rid)

            # Without a release ID, fetch each date individually.
            dates = [
                d.strftime("%Y-%m-%d") for d in pd_date_range(start_date, end_date)
            ]

            results = await asyncio.gather(*[fetch_date_pages(d) for d in dates])

            frames = [r for r in results if not r.empty]

            if not frames:
                return DataFrame()

            return concat(frames, ignore_index=True).sort_values(by="date")

        start_date = (
            query.start_date.isoformat()
            if query.start_date
            else (datetime.today() - timedelta(days=1)).isoformat()
        )
        end_date = (
            query.end_date.isoformat()
            if query.end_date
            else (
                (query.start_date + timedelta(days=7)).isoformat()
                if query.start_date
                else (datetime.today() + timedelta(days=1)).isoformat()
            )
        )
        rid = str(query.release_id) if query.release_id else ""

        try:
            all_results = await fetch_all_pages(start_date, end_date, rid)
        except Exception as e:
            raise OpenBBError(e) from e

        if all_results.empty:
            raise OpenBBError(
                "The requested returned no data. Check the parameters and try again."
            )

        return all_results.to_dict("records")

    @staticmethod
    def transform_data(
        query: FredEconomicCalendarQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[FredEconomicCalendarData]:
        """Transform and validate the response."""
        return [FredEconomicCalendarData.model_validate(d) for d in data]
