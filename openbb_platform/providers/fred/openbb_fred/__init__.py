"""FRED provider module."""
from openbb_fred.models.ameribor_rates import FREDAMERIBORFetcher
from openbb_fred.models.cpi import FREDCPIFetcher
from openbb_fred.models.estr_rates import FREDESTRFetcher
from openbb_fred.models.fed_projections import FREDPROJECTIONFetcher
from openbb_fred.models.fed_rates import FREDFEDFetcher
from openbb_fred.models.iorb_rates import FREDIORBFetcher
from openbb_fred.models.sofr_rates import FREDSOFRFetcher
from openbb_fred.models.sonia_rates import FREDSONIAFetcher
from openbb_fred.models.us_yield_curve import FREDYieldCurveFetcher
from openbb_provider.abstract.provider import Provider

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
        "AMERIBOR": FREDAMERIBORFetcher,
        "FEDFUNDS": FREDFEDFetcher,
        "PROJECTIONS": FREDPROJECTIONFetcher,
        "IORB": FREDIORBFetcher,
    },
)
