from openbb_core.provider.abstract.provider import Provider
from openbb_eodhd.models.equity_historical import EODHDEquityHistoricalFetcher

eodhd_provider = Provider(
    name="eodhd",
    description="EODHD Provider for historical equity candles data.",
    website="https://eodhd.com",
    credentials=["api_key"],
    fetcher_dict={
        "EquityHistorical": EODHDEquityHistoricalFetcher
    }
)
