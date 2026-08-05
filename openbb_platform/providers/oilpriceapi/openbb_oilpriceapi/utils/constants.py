"""OilPriceAPI constants."""

BASE_URL = "https://api.oilpriceapi.com/v1"

# Friendly aliases -> OilPriceAPI commodity codes.
#
# This is a convenience subset, not the catalogue. OilPriceAPI exposes 463 codes
# via GET /v1/commodities; any of them may be passed directly to `commodity` and
# is forwarded unchanged (upper-cased). These aliases exist so the common energy
# benchmarks are discoverable from the command signature.
COMMODITY_CHOICES: dict[str, str] = {
    # Crude benchmarks
    "brent": "BRENT_CRUDE_USD",
    "wti": "WTI_USD",
    "dubai": "DUBAI_CRUDE_USD",
    "urals": "URALS_CRUDE_USD",
    "opec_basket": "OPEC_BASKET_USD",
    "azeri_light": "AZERI_LIGHT_USD",
    "basrah_heavy": "BASRAH_HEAVY_USD",
    "basrah_medium": "BASRAH_MEDIUM_USD",
    # Natural gas
    "natural_gas": "NATURAL_GAS_USD",
    "dutch_ttf": "DUTCH_TTF_EUR",
    # Refined products
    "diesel": "DIESEL_USD",
    "diesel_retail": "DIESEL_RETAIL_USD",
    "gasoline": "GASOLINE_USD",
    "gasoline_rbob": "GASOLINE_RBOB_USD",
    # Coal
    "coal": "COAL_USD",
    "capp_coal": "CAPP_COAL_USD",
    "coking_coal": "COKING_COAL_USD",
    # Carbon
    "eu_carbon": "EU_CARBON_EUR",
}
