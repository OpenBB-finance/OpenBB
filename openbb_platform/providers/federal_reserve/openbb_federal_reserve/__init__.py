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
    website="https://www.federalreserve.gov/data.htm",  #  Not a typo, it's really .htm
    description="""Access data provided by the Federal Reserve System,
the Central Bank of the United States.""",
    fetcher_dict={
        "TreasuryRates": FederalReserveTreasuryRatesFetcher,
        "MoneyMeasures": FederalReserveMoneyMeasuresFetcher,
        "FEDFUNDS": FederalReserveFEDFetcher,
    },
    repr_name="Federal Reserve (FED)",
    logo_url="https://upload.wikimedia.org/wikipedia/commons/thumb/1/1a/Seal_of_the_United_States_Federal_Reserve_System.svg/498px-Seal_of_the_United_States_Federal_Reserve_System.svg.png",  # noqa: E501  pylint: disable=line-too-long
)
