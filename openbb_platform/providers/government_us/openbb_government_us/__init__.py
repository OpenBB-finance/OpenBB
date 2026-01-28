"""Government US provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_government_us.models.commodity_psd_data import (
    GovernmentUsCommodityPsdDataFetcher,
)
from openbb_government_us.models.commodity_psd_report import (
    GovernmentUsCommodityPsdReportFetcher,
)
from openbb_government_us.models.treasury_auctions import (
    GovernmentUSTreasuryAuctionsFetcher,
)
from openbb_government_us.models.treasury_prices import (
    GovernmentUSTreasuryPricesFetcher,
)
from openbb_government_us.models.weather_bulletin import (
    GovernmentUsWeatherBulletinFetcher,
)
from openbb_government_us.models.weather_bulletin_download import (
    GovernmentUsWeatherBulletinDownloadFetcher,
)

government_us_provider = Provider(
    name="government_us",
    website="https://data.gov",
    description="""Data.gov is the United States government's open data website.
It provides access to datasets published by agencies across the federal government.
Data.gov is intended to provide access to government open data to the public, achieve
agency missions, drive innovation, fuel economic activity, and uphold the ideals of
an open and transparent government. https://api.data.gov/signup/""",
    fetcher_dict={
        "CommodityPsdData": GovernmentUsCommodityPsdDataFetcher,
        "CommodityPsdReport": GovernmentUsCommodityPsdReportFetcher,
        "TreasuryAuctions": GovernmentUSTreasuryAuctionsFetcher,
        "TreasuryPrices": GovernmentUSTreasuryPricesFetcher,
        "WeatherBulletin": GovernmentUsWeatherBulletinFetcher,
        "WeatherBulletinDownload": GovernmentUsWeatherBulletinDownloadFetcher,
    },
    repr_name="Data.gov | United States Government",
)
