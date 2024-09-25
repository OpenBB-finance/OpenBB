"""OpenBB EIA Provider Module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_eia.models.petroleum_status_report import EiaPetroleumStatusReportFetcher

eia_provider = Provider(
    name="eia",
    website="https://eia.gov/",
    description="""The U.S. Energy Information Administration is committed to its free and open data by making it available through an Application Programming Interface (API) and its open data tools. See https://www.eia.gov/opendata/ for more information.""",
    credentials=[
        "api_key"
    ],  # This is not required for the Weekly Petroleum Status Report
    fetcher_dict={
        "PetroleumStatusReport": EiaPetroleumStatusReportFetcher,
    },
    repr_name="U.S. Energy Information Administration (EIA) Open Data and API",
    instructions="""Credentials are required for functions calling the EIA's API.
    Register for a free key here: https://www.eia.gov/opendata/register.php""",
)
