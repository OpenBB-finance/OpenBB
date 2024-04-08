"""FRED provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_fred.models.ameribor_rates import FREDAMERIBORFetcher
from openbb_fred.models.cp import FREDCommercialPaperFetcher
from openbb_fred.models.cpi import FREDConsumerPriceIndexFetcher
from openbb_fred.models.dwpcr_rates import FREDDiscountWindowPrimaryCreditRateFetcher
from openbb_fred.models.ecb_interest_rates import (
    FREDEuropeanCentralBankInterestRatesFetcher,
)
from openbb_fred.models.estr_rates import FREDESTRFetcher
from openbb_fred.models.fed_projections import FREDPROJECTIONFetcher
from openbb_fred.models.fed_rates import FREDFEDFetcher
from openbb_fred.models.ffrmc import FREDSelectedTreasuryConstantMaturityFetcher
from openbb_fred.models.hqm import FREDHighQualityMarketCorporateBondFetcher
from openbb_fred.models.ice_bofa import FREDICEBofAFetcher
from openbb_fred.models.iorb_rates import FREDIORBFetcher
from openbb_fred.models.moody import FREDMoodyCorporateBondIndexFetcher
from openbb_fred.models.regional import FredRegionalDataFetcher
from openbb_fred.models.search import (
    FredSearchFetcher,
)
from openbb_fred.models.series import FredSeriesFetcher
from openbb_fred.models.sofr_rates import FREDSOFRFetcher
from openbb_fred.models.sonia_rates import FREDSONIAFetcher
from openbb_fred.models.spot import FREDSpotRateFetcher
from openbb_fred.models.tbffr import FREDSelectedTreasuryBillFetcher
from openbb_fred.models.tmc import FREDTreasuryConstantMaturityFetcher
from openbb_fred.models.us_yield_curve import FREDYieldCurveFetcher

fred_provider = Provider(
    name="fred",
    website="https://fred.stlouisfed.org/",
    description="""Federal Reserve Economic Data is a database maintained by the
     Research division of the Federal Reserve Bank of St. Louis that has more than
     816,000 economic time series from various sources.""",
    credentials=["api_key"],
    fetcher_dict={
        "ConsumerPriceIndex": FREDConsumerPriceIndexFetcher,
        "USYieldCurve": FREDYieldCurveFetcher,
        "SOFR": FREDSOFRFetcher,
        "ESTR": FREDESTRFetcher,
        "SONIA": FREDSONIAFetcher,
        "AMERIBOR": FREDAMERIBORFetcher,
        "FEDFUNDS": FREDFEDFetcher,
        "PROJECTIONS": FREDPROJECTIONFetcher,
        "IORB": FREDIORBFetcher,
        "DiscountWindowPrimaryCreditRate": FREDDiscountWindowPrimaryCreditRateFetcher,
        "EuropeanCentralBankInterestRates": FREDEuropeanCentralBankInterestRatesFetcher,
        "ICEBofA": FREDICEBofAFetcher,
        "MoodyCorporateBondIndex": FREDMoodyCorporateBondIndexFetcher,
        "CommercialPaper": FREDCommercialPaperFetcher,
        "FredSearch": FredSearchFetcher,
        "FredSeries": FredSeriesFetcher,
        "FredRegional": FredRegionalDataFetcher,
        "SpotRate": FREDSpotRateFetcher,
        "HighQualityMarketCorporateBond": FREDHighQualityMarketCorporateBondFetcher,
        "TreasuryConstantMaturity": FREDTreasuryConstantMaturityFetcher,
        "SelectedTreasuryConstantMaturity": FREDSelectedTreasuryConstantMaturityFetcher,
        "SelectedTreasuryBill": FREDSelectedTreasuryBillFetcher,
    },
)
