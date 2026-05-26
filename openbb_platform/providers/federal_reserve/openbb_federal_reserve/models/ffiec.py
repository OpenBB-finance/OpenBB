"""FFIEC Bank Financial Data Models."""

import pandas as pd
from datetime import date as dateType
from io import StringIO
from typing import Optional

from pydantic import Field
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_federal_reserve.models.rssd_map import resolve_rssd
from curl_cffi import requests as curl_requests


class FfiecRiskQueryParams(QueryParams):
    """Query parameters for FFIEC FR Y-15 Report."""

    rssd_id: str = Field(
        description="The Federal Reserve RSSD ID of the institution (e.g., '1039502' for JPMorgan)."
    )
    date: Optional[dateType] = Field(
        default=None,
        description="The specific report date (YYYY-MM-DD). Defaults to the most recent filing."
    )


class FfiecRiskData(Data):
    """Data schema for FFIEC FR Y-15 Systemic Risk Report."""

    rssd_id: str = Field(description="The Federal Reserve RSSD ID.")
    report_date: dateType = Field(description="The date of the report.")
    total_assets: Optional[float] = Field(
        default=None,
        description="Total consolidated assets (RISK2170), in USD thousands."
    )


class FfiecRiskFetcher(
    Fetcher[
        FfiecRiskQueryParams,
        list[FfiecRiskData],
    ]
):
    """Fetcher for the FFIEC FR Y-15 Systemic Risk Report."""

    @staticmethod
    def extract_data(query: FfiecRiskQueryParams, credentials: dict, **kwargs) -> pd.DataFrame:
        """Downloads the FR Y-15 CSV from the FFIEC NIC web portal."""

        rssd_id = resolve_rssd(query.rssd_id)
        target_date = query.date.strftime("%Y%m%d") if query.date else "20241231"

        url = f"https://www.ffiec.gov/npw/FinancialReport/ReturnFinancialReportCSV?rpt=FRY15&id={rssd_id}&dt={target_date}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": f"https://www.ffiec.gov/npw/Institution/Profile/{rssd_id}",
            "Connection": "keep-alive"
        }

        try:
            session = curl_requests.Session()

            # Step 1: visit the profile page to establish a valid session cookie
            session.get(
                f"https://www.ffiec.gov/npw/Institution/Profile/{rssd_id}",
                headers=headers,
                impersonate="chrome124"
            )

            # Step 2: fetch the CSV with the active session
            response = session.get(url, headers=headers, impersonate="chrome124")
            response.raise_for_status()

            return pd.read_csv(StringIO(response.text))

        except Exception as e:
            raise EmptyDataError(f"Could not retrieve FFIEC data for RSSD {rssd_id}. Error: {e}")

    @staticmethod
    def transform_data(query: FfiecRiskQueryParams, data: pd.DataFrame, **kwargs) -> list[FfiecRiskData]:
        """Pivots the tall-format FFIEC CSV into a validated OpenBB model."""

        if data.empty:
            raise EmptyDataError("The FFIEC returned an empty report.")

        # The CSV is tall format: ItemName | Description | Value
        data.columns = data.columns.str.strip()
        tall = data.set_index("ItemName")["Value"]

        def get(key):
            return tall.get(key, None)

        def to_float(val):
            try:
                return float(val)
            except (TypeError, ValueError):
                return None

        raw_date = get("Report Date")
        if raw_date is None:
            raise EmptyDataError("Could not find Report Date in FFIEC response.")

        return [FfiecRiskData(
            rssd_id=str(int(float(get("ID_RSSD")))),
            report_date=pd.to_datetime(raw_date).date(),
            total_assets=to_float(get("RISK2170")),
        )]