"""Curated COT market universe, pinned to exact CFTC contract market codes."""

COT_ASSET_CLASSES: dict[str, str] = {
    "indices_bonds": "Indices & Bonds",
    "currencies": "Currencies",
    "hard_commodities": "Hard Commodities",
    "soft_commodities": "Soft Commodities",
}

COT_MARKETS: tuple[dict[str, str], ...] = (
    {
        "code": "CFTC_13874+",
        "label": "S&P 500",
        "asset_class": "indices_bonds",
        "contract": "S&P 500 Consolidated",
    },
    {
        "code": "CFTC_20974+",
        "label": "Nasdaq",
        "asset_class": "indices_bonds",
        "contract": "NASDAQ-100 Consolidated",
    },
    {
        "code": "CFTC_12460+",
        "label": "Dow",
        "asset_class": "indices_bonds",
        "contract": "DJIA Consolidated",
    },
    {
        "code": "CFTC_239742",
        "label": "Russell",
        "asset_class": "indices_bonds",
        "contract": "RUSSELL E-MINI",
    },
    {
        "code": "CFTC_042601",
        "label": "2Y Note",
        "asset_class": "indices_bonds",
        "contract": "UST 2Y NOTE",
    },
    {
        "code": "CFTC_044601",
        "label": "5Y Note",
        "asset_class": "indices_bonds",
        "contract": "UST 5Y NOTE",
    },
    {
        "code": "CFTC_043602",
        "label": "10Y Treasury",
        "asset_class": "indices_bonds",
        "contract": "UST 10Y NOTE",
    },
    {
        "code": "CFTC_020601",
        "label": "30Y Bond",
        "asset_class": "indices_bonds",
        "contract": "UST BOND",
    },
    {
        "code": "CFTC_098662",
        "label": "US Dollar",
        "asset_class": "currencies",
        "contract": "USD INDEX",
    },
    {
        "code": "CFTC_099741",
        "label": "Euro",
        "asset_class": "currencies",
        "contract": "EURO FX",
    },
    {
        "code": "CFTC_097741",
        "label": "Yen",
        "asset_class": "currencies",
        "contract": "JAPANESE YEN",
    },
    {
        "code": "CFTC_096742",
        "label": "Pound",
        "asset_class": "currencies",
        "contract": "BRITISH POUND",
    },
    {
        "code": "CFTC_092741",
        "label": "Franc",
        "asset_class": "currencies",
        "contract": "SWISS FRANC",
    },
    {
        "code": "CFTC_133741",
        "label": "Bitcoin",
        "asset_class": "currencies",
        "contract": "BITCOIN",
    },
    {
        "code": "CFTC_088691",
        "label": "Gold",
        "asset_class": "hard_commodities",
        "contract": "GOLD",
    },
    {
        "code": "CFTC_084691",
        "label": "Silver",
        "asset_class": "hard_commodities",
        "contract": "SILVER",
    },
    {
        "code": "CFTC_085692",
        "label": "Copper",
        "asset_class": "hard_commodities",
        "contract": "COPPER- #1",
    },
    {
        "code": "CFTC_076651",
        "label": "Platinum",
        "asset_class": "hard_commodities",
        "contract": "PLATINUM",
    },
    {
        "code": "CFTC_075651",
        "label": "Palladium",
        "asset_class": "hard_commodities",
        "contract": "PALLADIUM",
    },
    {
        "code": "CFTC_023651",
        "label": "Nat Gas",
        "asset_class": "hard_commodities",
        "contract": "NAT GAS NYME",
    },
    {
        "code": "CFTC_111659",
        "label": "Gasoline",
        "asset_class": "hard_commodities",
        "contract": "GASOLINE RBOB",
    },
    {
        "code": "CFTC_067411",
        "label": "WTI Oil",
        "asset_class": "hard_commodities",
        "contract": "CRUDE OIL, LIGHT SWEET-WTI",
    },
    {
        "code": "CFTC_06765T",
        "label": "Brent Oil",
        "asset_class": "hard_commodities",
        "contract": "BRENT LAST DAY",
    },
    {
        "code": "CFTC_002602",
        "label": "Corn",
        "asset_class": "soft_commodities",
        "contract": "CORN",
    },
    {
        "code": "CFTC_005602",
        "label": "Soybeans",
        "asset_class": "soft_commodities",
        "contract": "SOYBEANS",
    },
    {
        "code": "CFTC_080732",
        "label": "Sugar",
        "asset_class": "soft_commodities",
        "contract": "SUGAR NO. 11",
    },
    {
        "code": "CFTC_001602",
        "label": "Wheat",
        "asset_class": "soft_commodities",
        "contract": "WHEAT-SRW",
    },
    {
        "code": "CFTC_007601",
        "label": "Bean Oil",
        "asset_class": "soft_commodities",
        "contract": "SOYBEAN OIL",
    },
    {
        "code": "CFTC_026603",
        "label": "Bean Meal",
        "asset_class": "soft_commodities",
        "contract": "SOYBEAN MEAL",
    },
    {
        "code": "CFTC_083731",
        "label": "Coffee",
        "asset_class": "soft_commodities",
        "contract": "COFFEE C",
    },
    {
        "code": "CFTC_073732",
        "label": "Cocoa",
        "asset_class": "soft_commodities",
        "contract": "COCOA",
    },
    {
        "code": "CFTC_033661",
        "label": "Cotton",
        "asset_class": "soft_commodities",
        "contract": "COTTON NO. 2",
    },
    {
        "code": "CFTC_058644",
        "label": "Lumber",
        "asset_class": "soft_commodities",
        "contract": "LUMBER",
    },
    {
        "code": "CFTC_040701",
        "label": "Orange Juice",
        "asset_class": "soft_commodities",
        "contract": "FRZN CONCENTRATED ORANGE JUICE",
    },
)


def markets_for(asset_class: str = "all") -> list[dict[str, str]]:
    """Return the curated markets in an asset class, or every market."""
    if asset_class == "all":
        return list(COT_MARKETS)

    return [m for m in COT_MARKETS if m["asset_class"] == asset_class]


def market_for_code(code: str) -> dict[str, str]:
    """Return a curated market by its CFTC code, or a bare entry for any other code."""
    wanted = (code or "").strip()

    for market in COT_MARKETS:
        if market["code"] == wanted:
            return market

    return {
        "code": wanted,
        "label": wanted,
        "asset_class": "all",
        "contract": wanted,
    }
