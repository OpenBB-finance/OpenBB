"""Government US Weather Bulletin Model"""

# pylint: disable=unused-argument
from datetime import datetime
from typing import Any

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.weather_bulletin import (
    WeatherBulletinData,
    WeatherBulletinQueryParams,
)
from pydantic import ConfigDict, field_validator


class GovernmentUsWeatherBulletinQueryParams(WeatherBulletinQueryParams):
    """US Government Weather Bulletin Query Params.

    Source: https://esmis.nal.usda.gov/publication/weekly-weather-and-crop-bulletin
    """

    @field_validator("year")
    @classmethod
    def _validate_year(cls, value: int) -> int:
        """Validate year."""
        if value < 1974:
            raise ValueError("Year must not be before 1974.")
        if value > datetime.now().year:
            raise OpenBBError(ValueError("Invalid year. Year cannot be in the future."))
        return value


class GovernmentUsWeatherBulletinData(WeatherBulletinData):
    """US Government Weather Bulletin Data.

    The Weekly Weather and Crop Bulletin is released by 4:00 p.m. on the second workday of each week.

    The Bulletin includes the National Summary, State Stories, current data for weather, temperature and precipitation
    and international agricultural weather. The full report is jointly published by the National Oceanic
    and Atmospheric Administration of the U.S. Department of Commerce, the National Agricultural Statistics Service,
    and the World Agricultural Outlook Board.
    """

    model_config = ConfigDict(
        extra="ignore",
    )


class GovernmentUsWeatherBulletinFetcher(
    Fetcher[
        GovernmentUsWeatherBulletinQueryParams,
        list[GovernmentUsWeatherBulletinData],
    ]
):
    """US Government Weather Bulletin Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> GovernmentUsWeatherBulletinQueryParams:
        """Transform params into the query params model."""
        return GovernmentUsWeatherBulletinQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: GovernmentUsWeatherBulletinQueryParams,
        credentials: dict[str, str] | None = None,
        **kwargs: Any,
    ) -> list:
        """Asynchronously extract data from the US Government Weather Bulletin API."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        import re
        from openbb_core.provider.utils.helpers import get_async_requests_session

        BASE_URL = "https://esmis.nal.usda.gov"
        PUBLICATION_URL = f"{BASE_URL}/publication/weekly-weather-and-crop-bulletin"
        months_to_fetch = (
            [query.month] if query.month is not None else list(range(1, 13))
        )
        year = query.year
        week = query.week
        month = query.month

        try:
            async with await get_async_requests_session() as session:
                session._max_field_size = 32768  # pylint: disable=protected-access

                async def fetch_month(m: int) -> list[dict]:
                    """Fetch bulletins for a single month."""
                    url = f"{PUBLICATION_URL}?date={year}-{m:02d}"
                    bulletins = []

                    try:
                        resp = await session.get(url)
                        if resp.status != 200:
                            return []
                        html = await resp.text()
                    except Exception:
                        return []

                    pattern = (
                        r'href="(/sites/default/release-files/[^"]+\.pdf)"[^>]*>.*?'
                        r'<time datetime="(\d{4}-\d{2}-\d{2})T'
                    )
                    matches = re.findall(pattern, html, re.DOTALL)

                    for pdf_path, date_str in matches:
                        # Skip the "latest release" which appears on every page
                        if pdf_path == "/sites/default/release-files/795708/wwcb.pdf":
                            continue

                        # Parse the date
                        try:
                            dt = datetime.strptime(date_str, "%Y-%m-%d")
                        except ValueError:
                            continue

                        # Only include if it matches the requested year/month
                        if dt.year != year:
                            continue
                        if month is not None and dt.month != m:
                            continue

                        # Calculate week of month (1-5)
                        week_of_month = (dt.day - 1) // 7 + 1

                        # Filter by week if specified
                        if week is not None and week_of_month != week:
                            continue

                        # Extract filename from path
                        filename = pdf_path.split("/")[-1]

                        # Create human-readable label
                        label = f"Weekly Weather Bulletin - {dt.strftime('%Y-%m-%d')}"

                        bulletins.append(
                            {
                                "label": label,
                                "date": dt,
                                "year": dt.year,
                                "month": dt.month,
                                "day": dt.day,
                                "week_of_month": week_of_month,
                                "pdf_url": f"{BASE_URL}{pdf_path}",
                                "filename": filename,
                            }
                        )

                    return bulletins

                results = await asyncio.gather(
                    *[fetch_month(m) for m in months_to_fetch], return_exceptions=True
                )

                all_bulletins = []
                for result in results:
                    if isinstance(result, list):
                        all_bulletins.extend(result)

                # Sort by date descending (most recent first)
                all_bulletins.sort(key=lambda x: x["date"], reverse=True)

                # Remove duplicates (same date can appear in adjacent month pages)
                seen_dates = set()
                unique_bulletins = []
                for b in all_bulletins:
                    date_key = b["date"].strftime("%Y-%m-%d")
                    if date_key not in seen_dates:
                        seen_dates.add(date_key)
                        unique_bulletins.append(b)

                return unique_bulletins
        except Exception as e:
            raise OpenBBError(e) from e

    @staticmethod
    def transform_data(
        query: GovernmentUsWeatherBulletinQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[GovernmentUsWeatherBulletinData]:
        """Transform data into the standard model."""
        return [
            GovernmentUsWeatherBulletinData(
                label=item["label"],
                value=item["pdf_url"],
            )
            for item in data
        ]
