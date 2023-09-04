"""CBOE Helpers Module."""

from datetime import timedelta

import pandas as pd
import requests_cache
from openbb_provider.utils.helpers import to_snake_case

# Only used for obtaining all ETFs.
tmx_etfs_session = requests_cache.CachedSession(
    "OpenBB_TMX_ETFs", expire_after=timedelta(hours=4), use_cache_dir=True
)


def get_all_etfs() -> pd.DataFrame:
    """Gets a summary of the TMX Group ETFs universe.

    Returns
    -------
    pd.DataFrame
        DataFrame with a universe summary.
    """

    # Caches the request for 4 hours to make subsequent queries faster.
    r = tmx_etfs_session.get(
        "https://dgr53wu9i7rmp.cloudfront.net/etfs/etfs.json", timeout=10
    )

    if r.status_code != 200:
        raise RuntimeError(r.status_code)

    etfs = pd.DataFrame(r.json())

    etfs = etfs.rename(
        columns={
            "symbol": "Symbol",
            "shortname": "Short Name",
            "longname": "Name",
            "fundfamily": "Fund Family",
            "regions": "Regions",
            "sectors": "Sectors",
            "currency": "Currency",
            "inceptiondate": "Inception Date",
            "unitprice": "Unit Price",
            "prevClose": "Prev Close",
            "close": "Close",
            "esg": "ESG",
            "investmentstyle": "Investment Style",
            "avgdailyvolume": "Volume Avg Daily",
            "totalreturn1month": "Return 1M",
            "totalreturn3month": "Return 3M",
            "totalreturn1year": "Return 1Y",
            "totalreturn3year": "Return 3Y",
            "totalreturn5year": "Return 5Y",
            "totalreturnytd": "Return YTD",
            "totalreturnsinceinception": "Return From Inception",
            "distributionyeld": "Distribution Yield",
            "dividendfrequency": "Dividend Frequency",
            "pricetoearnings": "PE Ratio",
            "pricetobook": "PB Ratio",
            "assetclass": "Asset Class ID",
            "prospectobjective": "Investment Objectives",
            "beta1y": "Beta 1Y",
            "beta2y": "Beta 2Y",
            "beta3y": "Beta 3Y",
            "beta4y": "Beta 4Y",
            "beta5y": "Beta 5Y",
            "beta6y": "Beta 6Y",
            "beta7y": "Beta 7Y",
            "beta8y": "Beta 8Y",
            "beta9y": "Beta 9Y",
            "beta10y": "Beta 10Y",
            "beta11y": "Beta 11Y",
            "beta12y": "Beta 12Y",
            "beta13y": "Beta 13Y",
            "beta14y": "Beta 14Y",
            "beta15y": "Beta 15Y",
            "beta16y": "Beta 16Y",
            "beta17y": "Beta 17Y",
            "beta18y": "Beta 18Y",
            "beta19y": "Beta 19Y",
            "beta20y": "Beta 20Y",
            "avgvol30days": "Volume Avg 30 Days",
            "aum": "AUM",
            "top10holdings": "Holdings Top 10",
            "top10holdingsummary": "Holdings Top 10 Summary",
            "totalreturn6month": "Return 6M",
            "totalreturn10year": "Return 10Y",
            "managementfee": "Management Fee",
            "altData": "Additional Data",
        }
    )
    etfs.columns = [to_snake_case(c) for c in etfs.columns]

    return etfs.replace("-", None).convert_dtypes()
