"""Federal Reserve provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_federal_reserve.models.fed_rates import FederalReserveFEDFetcher
from openbb_federal_reserve.models.money_measures import (
    FederalReserveMoneyMeasuresFetcher,
)
from openbb_federal_reserve.models.treasury_rates import (
    FederalReserveTreasuryRatesFetcher,
)

federal_reserve_provider = Provider(
    name="federal_reserve",
    website="https://www.federalreserve.gov/data.htm",
    description=(),
    fetcher_dict={
        "TreasuryRates": FederalReserveTreasuryRatesFetcher,
        "MoneyMeasures": FederalReserveMoneyMeasuresFetcher,
        "FEDFUNDS": FederalReserveFEDFetcher,
    },
)
