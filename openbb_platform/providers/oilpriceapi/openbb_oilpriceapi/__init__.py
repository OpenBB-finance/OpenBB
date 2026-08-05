"""OilPriceAPI Provider module."""

from openbb_core.provider.abstract.provider import Provider
from openbb_oilpriceapi.models.commodity_spot_prices import (
    OilPriceAPICommoditySpotPricesFetcher,
)

oilpriceapi_provider = Provider(
    name="oilpriceapi",
    website="https://www.oilpriceapi.com",
    description="""OilPriceAPI provides source-timestamped energy and commodity price
data through a single normalized REST API. Coverage includes crude benchmarks,
natural gas, refined products, coal, carbon, marine fuels and drilling activity —
463 series in the public catalogue, each carrying its own source timestamp and
freshness metadata.""",
    credentials=["api_key"],
    fetcher_dict={
        "CommoditySpotPrices": OilPriceAPICommoditySpotPricesFetcher,
    },
    repr_name="OilPriceAPI",
    instructions="""Sign up at https://www.oilpriceapi.com/auth/signup for a free key
(200 requests/month, no card required), then set `oilpriceapi_api_key`.
A keyless demo endpoint is available at https://api.oilpriceapi.com/v1/demo/prices""",
)
