"""OpenBB EIA Provider Module."""

from importlib.util import find_spec

from openbb_core.provider.abstract.provider import Provider

from openbb_us_eia.models.data_browser import EiaDataBrowserFetcher
from openbb_us_eia.models.petroleum_status_report import EiaPetroleumStatusReportFetcher
from openbb_us_eia.models.registry import DATASET_FETCHERS
from openbb_us_eia.models.short_term_energy_outlook import (
    EiaShortTermEnergyOutlookFetcher,
)

COMMODITY_INSTALLED = find_spec("openbb_commodity") is not None

eia_provider = Provider(
    name="eia",
    website="https://eia.gov/",
    description="The U.S. Energy Information Administration is committed to its free and open data"
    + " by making it available through an Application Programming Interface (API) and its open data tools."
    + " See https://www.eia.gov/opendata/ for more information.",
    credentials=["api_key"],
    fetcher_dict={
        "EiaDataBrowser": EiaDataBrowserFetcher,
        "PetroleumStatusReport": EiaPetroleumStatusReportFetcher,
        "ShortTermEnergyOutlook": EiaShortTermEnergyOutlookFetcher,
        **DATASET_FETCHERS,
    },
    repr_name="U.S. Energy Information Administration (EIA) Open Data and API",
    instructions="""Credentials are required for functions calling the EIA's API.
    Register for a free key here: https://www.eia.gov/opendata/register.php""",
)
