"""FRED provider module."""
from openbb_provider.abstract.provider import Provider

from openbb_fred.models.cpi import FREDCPIFetcher
from openbb_fred.models.us_yield_curve import FREDYieldCurveFetcher
from openbb_fred.models.sofr_rates import FREDSOFRFetcher
from openbb_fred.models.estr_rates import FREDESTRFetcher
from openbb_fred.models.sonia_rates import FREDSONIAFetcher


fred_provider = Provider(
    name="fred",
    website="https://fred.stlouisfed.org/",
    description="""Federal Reserve Economic Data is a database maintained by the
     Research division of the Federal Reserve Bank of St. Louis that has more than
     816,000 economic time series from various sources.""",
    required_credentials=["api_key"],
    fetcher_dict={
        "CPI": FREDCPIFetcher,
        "USYieldCurve": FREDYieldCurveFetcher,
        "SOFR": FREDSOFRFetcher,
        "ESTR": FREDESTRFetcher,
        "SONIA": FREDSONIAFetcher,
    },
)
