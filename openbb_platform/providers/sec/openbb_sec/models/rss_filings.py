"""SEC Filings RSS Feed Fetcher."""

from datetime import datetime
from typing import Dict, List

import pandas as pd
import requests
import xmltodict
from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_sec.utils.definitions import SEC_HEADERS
from pydantic import Field


class SecRssFilingsQueryParams(QueryParams):
    """SEC Filings RSS Feed Query Params."""


class SecRssFilingsData(Data):
    """SEC Filings RSS Feed Data."""

    acceptance_date: datetime = Field(description="The timestamp of the filing.")
    filer: str = Field(description="The name of the filing entity.")
    cik: str = Field(description="The CIK of the filing entity.")
    form_type: str = Field(description="The SEC form type that was filed.")
    accession_number: str = Field(description="The accession number of the filing.")
    file_number: str = Field(description="The file number of the filing.")
    url: str = Field(description="URL to the main filing page.")
    zip: str = Field(description="URL to the zip file of the xbrl filing.")
    xbrl_filing: List[Dict] = Field(
        description="List of the individual files within the filing."
    )


def get_latest_filings() -> List[Dict]:
    """This is a list of up to 200 of the latest filings containing financial statements or
    US Mutual Fund Risk/Return Taxonomy updated every 10 minutes.

    Parameters
    ----------
    filing_type: str = "all"
        The type of filings to get.  Choices are, ["financialStatements", "mututalFund", "all"].
        Defaults to "all".

    Returns
    -------
    pd.DataFrame: Pandas DataFrame with up to 200 results.

    Examples
    --------
    >>> filings = get_latest_filings(filing_type = "mutualFund")

    >>> latest_filings = get_latest_filings()
    """

    r = requests.get(
        "https://www.sec.gov/Archives/edgar/xbrlrss.all.xml",
        headers=SEC_HEADERS,
        timeout=5,
    )

    if r.status_code != 200:
        raise RuntimeError(f"Request failed with status code {r.status_code}")

    data = xmltodict.parse(r.content.decode())

    data_df = pd.DataFrame.from_records(data["rss"]["channel"]["item"])

    results_df = pd.DataFrame()
    results_df["acceptance_date"] = pd.DatetimeIndex(data_df["pubDate"])
    results_df["filer"] = data_df.title
    results_df["cik"] = data_df["edgar:xbrlFiling"].apply(
        lambda x: x["edgar:cikNumber"]
    )
    results_df["form_type"] = data_df["description"]
    results_df["accession_number"] = data_df["edgar:xbrlFiling"].apply(
        lambda x: x["edgar:accessionNumber"]
    )
    results_df["file_number"] = data_df["edgar:xbrlFiling"].apply(
        lambda x: x["edgar:fileNumber"]
    )
    results_df["url"] = data_df.link
    results_df["zip"] = data_df.guid
    results_df["xbrl_filing"] = data_df["edgar:xbrlFiling"].apply(
        lambda x: x["edgar:xbrlFiles"]["edgar:xbrlFile"]
    )

    return results_df.to_dict("records")
