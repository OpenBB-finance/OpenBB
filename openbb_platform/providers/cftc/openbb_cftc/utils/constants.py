"""CFTC provider constants."""

reports_dict = {
    "legacy_futures_only": "6dca-aqww",
    "legacy_combined": "jun7-fc8e",
    "disaggregated_futures_only": "72hh-3qpy",
    "disaggregated_combined": "kh3c-gbw2",
    "tff_futures_only": "gpe5-46if",
    "tff_combined": "yw9f-hn96",
    "supplemental": "4zgm-a668",
}

PPD_API_URL = "https://pddata.dtcc.com/ppd/api"

JURISDICTION = "CFTC"

ASSET_CLASSES = {
    "rates": "IR",
    "credits": "CR",
    "equities": "EQ",
    "forex": "FX",
    "commodities": "CO",
}

PPD_EARLIEST_DATE = "2023-12-29"
PPD_RETENTION_DAYS = 366

DAY_COUNT_CODES = {
    "A001": "30/360 (ISDA)",
    "A002": "30/365",
    "A003": "30/Actual",
    "A004": "ACT/360",
    "A005": "ACT/365F",
    "A006": "ACT/ACT (ICMA)",
    "A007": "30E/360 (Eurobond)",
    "A008": "ACT/ACT (ISDA)",
    "A009": "ACT/365L",
    "A010": "ACT/ACT (AFB)",
    "A011": "30/360 (ICMA)",
    "A012": "30E2/360",
    "A013": "30E3/360",
    "A014": "ACT/365 (NL)",
    "NARR": "Narrative",
}

DAY_COUNT_BASIS = {
    "A004": 360.0,
    "A005": 365.0,
    "A009": 365.0,
    "A014": 365.0,
    "A001": 365.0,
    "A011": 365.0,
    "A006": 365.0,
    "A008": 365.0,
    "A007": 365.0,
}


def day_count_basis(code: str | None, default: str) -> float:
    """Resolve a fixed-leg day count code to its accrual denominator."""
    resolved = (code or "").strip() or default

    return DAY_COUNT_BASIS.get(resolved, DAY_COUNT_BASIS.get(default, 365.0))


SOFR_OIS_FISN = "NA/Swap OIS USD"
SOFR_FIXED_FLOAT_FISN = "NA/Swap Fxd Flt USD"

OIS_INDICES: dict[str, dict[str, str]] = {
    "USD": {"index": "SOFR", "central_bank": "Federal Reserve", "day_count": "A004"},
    "EUR": {
        "index": "ESTR",
        "central_bank": "European Central Bank",
        "day_count": "A004",
    },
    "GBP": {"index": "SONIA", "central_bank": "Bank of England", "day_count": "A005"},
    "JPY": {"index": "TONA", "central_bank": "Bank of Japan", "day_count": "A005"},
    "CAD": {"index": "CORRA", "central_bank": "Bank of Canada", "day_count": "A005"},
    "CHF": {
        "index": "SARON",
        "central_bank": "Swiss National Bank",
        "day_count": "A004",
    },
    "MXN": {"index": "TIIE", "central_bank": "Banco de Mexico", "day_count": "A004"},
    "SGD": {
        "index": "SORA",
        "central_bank": "Monetary Authority of Singapore",
        "day_count": "A005",
    },
    "INR": {
        "index": "MIBOR",
        "central_bank": "Reserve Bank of India",
        "day_count": "A005",
    },
    "COP": {
        "index": "IBR",
        "central_bank": "Banco de la Republica",
        "day_count": "A004",
    },
    "ZAR": {
        "index": "ZARONIA",
        "central_bank": "South African Reserve Bank",
        "day_count": "A005",
    },
    "CLP": {
        "index": "ICP",
        "central_bank": "Banco Central de Chile",
        "day_count": "A004",
    },
    "THB": {"index": "THOR", "central_bank": "Bank of Thailand", "day_count": "A005"},
    "ILS": {"index": "SHIR", "central_bank": "Bank of Israel", "day_count": "A005"},
    "AUD": {
        "index": "AONIA",
        "central_bank": "Reserve Bank of Australia",
        "day_count": "A005",
    },
    "NZD": {
        "index": "NZIONA",
        "central_bank": "Reserve Bank of New Zealand",
        "day_count": "A005",
    },
    "BRL": {
        "index": "CDI",
        "central_bank": "Banco Central do Brasil",
        "day_count": "A005",
    },
}


def ois_fisn(currency: str) -> str:
    """Return the UPI FISN of a currency's overnight index swap."""
    return f"NA/Swap OIS {currency.upper()}"


def currency_basis(currency: str) -> float:
    """Money-market accrual basis for a currency's rate leg, from its OIS day count."""
    return day_count_basis(
        OIS_INDICES.get(currency.upper(), {}).get("day_count"), "A004"
    )


def rate_curve_fisns(currency: str) -> list[str]:
    """Swap families that could price a currency's rate curve, deepest source first."""
    ccy = (currency or "").strip().upper()
    candidates = [ois_fisn(ccy)] if ccy in OIS_INDICES else []
    candidates.append(f"NA/Swap Fxd Flt {ccy}")
    candidates.append(f"NA/Swap Fxd Flt {ccy} USD")

    return candidates


CDS_INDEX_FISNS = ("NA/CDS Corp Idx", "NA/CDS Corp Idx Tra", "NA/CDS Sov Idx")

CDS_INDEX_UNDERLIERS = (
    "CDX.NA.HY",
    "CDX.NA.IG",
    "ITRAXX EUROPE",
    "ITRAXX EUROPE CROSSOVER",
    "CDX.EM",
    "ITRAXX EUROPE SENIOR FINANCIALS",
    "CMBX.NA.BBB-",
    "IBOXX USD LIQUID LEVERAGED LOANS INDEX",
    "ITRAXX ASIA EX-JAPAN IG",
    "CMBX.NA.BB",
    "ITRAXX JAPAN",
    "ITRAXX EUROPE SUB FINANCIALS",
    "CMBX.NA.AAA",
    "CDX.FINANCIALS",
    "ITRAXX AUSTRALIA",
)

CDS_STANDARD_TENORS = (1.0, 2.0, 3.0, 5.0, 7.0, 10.0)
CDS_TENOR_TOLERANCE_YEARS = 1.0
DAYS_PER_YEAR = 365.25

FX_PAIRS: dict[str, dict] = {
    "EURUSD": {
        "base": "EUR",
        "quote": "USD",
        "invert": False,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd EUR USD",
        "swap_fisn": "NA/Swaps EUR USD",
    },
    "GBPUSD": {
        "base": "GBP",
        "quote": "USD",
        "invert": False,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd GBP USD",
        "swap_fisn": "NA/Swaps GBP USD",
    },
    "AUDUSD": {
        "base": "AUD",
        "quote": "USD",
        "invert": False,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd AUD USD",
        "swap_fisn": "NA/Swaps AUD USD",
    },
    "NZDUSD": {
        "base": "NZD",
        "quote": "USD",
        "invert": False,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd NZD USD",
        "swap_fisn": "NA/Swaps NZD USD",
    },
    "USDJPY": {
        "base": "JPY",
        "quote": "USD",
        "invert": True,
        "pip": 100.0,
        "forward_fisn": "NA/Fwd JPY USD",
        "swap_fisn": "NA/Swaps JPY USD",
    },
    "USDCHF": {
        "base": "CHF",
        "quote": "USD",
        "invert": True,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd CHF USD",
        "swap_fisn": "NA/Swaps CHF USD",
    },
    "USDCAD": {
        "base": "CAD",
        "quote": "USD",
        "invert": True,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd CAD USD",
        "swap_fisn": "NA/Swaps CAD USD",
    },
    "USDKRW": {
        "base": "USD",
        "quote": "KRW",
        "invert": False,
        "ndf": True,
        "pip": 100.0,
        "forward_fisn": "NA/Fwd NDF KRW USD",
        "swap_fisn": "NA/Swaps NDS KRW USD",
    },
    "USDINR": {
        "base": "USD",
        "quote": "INR",
        "invert": False,
        "ndf": True,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd NDF INR USD",
        "swap_fisn": "NA/Swaps NDS INR USD",
    },
    "USDBRL": {
        "base": "USD",
        "quote": "BRL",
        "invert": False,
        "ndf": True,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd NDF BRL USD",
        "swap_fisn": "NA/Swaps NDS BRL USD",
    },
    "USDTWD": {
        "base": "USD",
        "quote": "TWD",
        "invert": False,
        "ndf": True,
        "pip": 1_000.0,
        "forward_fisn": "NA/Fwd NDF TWD USD",
        "swap_fisn": "NA/Swaps NDS TWD USD",
    },
    "USDIDR": {
        "base": "USD",
        "quote": "IDR",
        "invert": False,
        "ndf": True,
        "pip": 100.0,
        "forward_fisn": "NA/Fwd NDF IDR USD",
        "swap_fisn": "NA/Swaps NDS IDR USD",
    },
    "USDPHP": {
        "base": "USD",
        "quote": "PHP",
        "invert": False,
        "ndf": True,
        "pip": 1_000.0,
        "forward_fisn": "NA/Fwd NDF PHP USD",
        "swap_fisn": "NA/Swaps NDS PHP USD",
    },
    "USDCLP": {
        "base": "USD",
        "quote": "CLP",
        "invert": False,
        "ndf": True,
        "pip": 100.0,
        "forward_fisn": "NA/Fwd NDF CLP USD",
        "swap_fisn": "NA/Swaps NDS CLP USD",
    },
    "USDCOP": {
        "base": "USD",
        "quote": "COP",
        "invert": False,
        "ndf": True,
        "pip": 100.0,
        "forward_fisn": "NA/Fwd NDF COP USD",
        "swap_fisn": "NA/Swaps NDS COP USD",
    },
    "USDCNY": {
        "base": "USD",
        "quote": "CNY",
        "invert": False,
        "ndf": True,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd NDF CNY USD",
        "swap_fisn": "NA/Swaps NDS CNY USD",
    },
    "USDPEN": {
        "base": "USD",
        "quote": "PEN",
        "invert": False,
        "ndf": True,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd NDF PEN USD",
        "swap_fisn": "NA/Swaps NDS PEN USD",
    },
    "USDMYR": {
        "base": "USD",
        "quote": "MYR",
        "invert": False,
        "ndf": True,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd NDF MYR USD",
        "swap_fisn": "NA/Swaps NDS MYR USD",
    },
    "USDHKD": {
        "base": "HKD",
        "quote": "USD",
        "invert": True,
        "ndf": False,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd HKD USD",
        "swap_fisn": "NA/Swaps HKD USD",
    },
    "USDMXN": {
        "base": "MXN",
        "quote": "USD",
        "invert": True,
        "ndf": False,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd MXN USD",
        "swap_fisn": "NA/Swaps MXN USD",
    },
    "USDTHB": {
        "base": "THB",
        "quote": "USD",
        "invert": True,
        "ndf": False,
        "pip": 1_000.0,
        "forward_fisn": "NA/Fwd THB USD",
        "swap_fisn": "NA/Swaps THB USD",
    },
    "EURCHF": {
        "base": "CHF",
        "quote": "EUR",
        "invert": True,
        "ndf": False,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd CHF EUR",
        "swap_fisn": "NA/Swaps CHF EUR",
    },
    "AUDCNY": {
        "base": "AUD",
        "quote": "CNY",
        "invert": False,
        "ndf": True,
        "pip": 10_000.0,
        "forward_fisn": "NA/Fwd NDF AUD CNY",
        "swap_fisn": "NA/Swaps NDS AUD CNY",
    },
}

MAJOR_FX_PAIRS: dict[str, dict] = {
    "EURUSD": {"base": "EUR", "quote": "USD", "pip": 10_000.0},
    "GBPUSD": {"base": "GBP", "quote": "USD", "pip": 10_000.0},
    "USDJPY": {"base": "USD", "quote": "JPY", "pip": 100.0},
    "USDCHF": {"base": "USD", "quote": "CHF", "pip": 10_000.0},
    "USDCAD": {"base": "USD", "quote": "CAD", "pip": 10_000.0},
    "EURGBP": {"base": "EUR", "quote": "GBP", "pip": 10_000.0},
    "EURJPY": {"base": "EUR", "quote": "JPY", "pip": 100.0},
    "EURCHF": {"base": "EUR", "quote": "CHF", "pip": 10_000.0},
    "EURCAD": {"base": "EUR", "quote": "CAD", "pip": 10_000.0},
    "GBPJPY": {"base": "GBP", "quote": "JPY", "pip": 100.0},
    "GBPCHF": {"base": "GBP", "quote": "CHF", "pip": 10_000.0},
    "CADJPY": {"base": "CAD", "quote": "JPY", "pip": 100.0},
    "CHFJPY": {"base": "CHF", "quote": "JPY", "pip": 100.0},
    "USDBRL": {"base": "USD", "quote": "BRL", "pip": 10_000.0, "ndf": True},
    "USDKRW": {"base": "USD", "quote": "KRW", "pip": 100.0, "ndf": True},
    "USDINR": {"base": "USD", "quote": "INR", "pip": 10_000.0, "ndf": True},
    "USDTWD": {"base": "USD", "quote": "TWD", "pip": 1_000.0, "ndf": True},
    "USDCOP": {"base": "USD", "quote": "COP", "pip": 100.0, "ndf": True},
}

FX_TENOR_BUCKETS: list[tuple[str, int, int]] = [
    ("SPOT", 0, 2),
    ("1W", 3, 9),
    ("2W", 10, 20),
    ("1M", 21, 45),
    ("2M", 46, 75),
    ("3M", 76, 110),
    ("6M", 111, 200),
    ("9M", 201, 290),
    ("1Y", 291, 400),
    ("2Y", 401, 800),
]

BENCHMARK_TENORS: list[tuple[str, int]] = [
    ("1W", 7),
    ("2W", 14),
    ("1M", 30),
    ("2M", 61),
    ("3M", 91),
    ("4M", 122),
    ("6M", 182),
    ("9M", 273),
    ("1Y", 365),
    ("18M", 548),
    ("2Y", 730),
    ("3Y", 1095),
    ("4Y", 1461),
    ("5Y", 1826),
    ("6Y", 2191),
    ("7Y", 2556),
    ("8Y", 2922),
    ("9Y", 3287),
    ("10Y", 3652),
    ("12Y", 4383),
    ("15Y", 5478),
    ("20Y", 7305),
    ("25Y", 9131),
    ("30Y", 10957),
]

MAX_CURVE_DAYS = round(BENCHMARK_TENORS[-1][1] * 1.02)

_TENOR_DAYS: dict[str, int] = dict(BENCHMARK_TENORS)


def tenor_to_years(label: str) -> float:
    """Convert a benchmark tenor label to a year fraction."""
    from openbb_core.app.model.abstract.error import OpenBBError

    days = _TENOR_DAYS.get((label or "").strip().upper())

    if days is None:
        raise OpenBBError(
            f"Invalid tenor '{label}'. Valid tenors are: "
            + ", ".join(t for t, _ in BENCHMARK_TENORS)
        )

    return days / 365.0


OIS_PAYMENT_PERIOD_DAYS = 365
ZERO_RATE_BASIS = 365.0

SINGLE_PAYMENT_MAX_DAYS = 370

MAX_ABS_ZERO_RATE = 1.0

SLICE_HEADERS: tuple[str, ...] = (
    "Dissemination Identifier",
    "Original Dissemination Identifier",
    "Action type",
    "Event type",
    "Event timestamp",
    "Amendment indicator",
    "Asset Class",
    "Product name",
    "Cleared",
    "Mandatory clearing indicator",
    "Execution Timestamp",
    "Effective Date",
    "Expiration Date",
    "Maturity date of the underlier",
    "Non-standardized term indicator",
    "Platform identifier",
    "Prime brokerage transaction indicator",
    "Block trade election indicator",
    "Large notional off-facility swap election indicator",
    "Notional amount-Leg 1",
    "Notional amount-Leg 2",
    "Notional currency-Leg 1",
    "Notional currency-Leg 2",
    "Notional quantity-Leg 1",
    "Notional quantity-Leg 2",
    "Total notional quantity-Leg 1",
    "Total notional quantity-Leg 2",
    "Quantity frequency multiplier-Leg 1",
    "Quantity frequency multiplier-Leg 2",
    "Quantity unit of measure-Leg 1",
    "Quantity unit of measure-Leg 2",
    "Quantity frequency-Leg 1",
    "Quantity frequency-Leg 2",
    "Notional amount in effect on associated effective date-Leg 1",
    "Notional amount in effect on associated effective date-Leg 2",
    "Effective date of the notional amount-Leg 1",
    "Effective date of the notional amount-Leg 2",
    "End date of the notional amount-Leg 1",
    "End date of the notional amount-Leg 2",
    "Call amount",
    "Call currency",
    "Put amount",
    "Put currency",
    "Exchange rate",
    "Exchange rate basis",
    "First exercise date",
    "Fixed rate-Leg 1",
    "Fixed rate-Leg 2",
    "Option Premium Amount",
    "Option Premium Currency",
    "Price",
    "Price unit of measure",
    "Spread-Leg 1",
    "Spread-Leg 2",
    "Spread currency-Leg 1",
    "Spread currency-Leg 2",
    "Strike Price",
    "Strike price currency/currency pair",
    "Post-priced swap indicator",
    "Price currency",
    "Price notation",
    "Spread notation-Leg 1",
    "Spread notation-Leg 2",
    "Strike price notation",
    "Fixed rate day count convention-leg 1",
    "Fixed rate day count convention-leg 2",
    "Floating rate day count convention-leg 1",
    "Floating rate day count convention-leg 2",
    "Floating rate reset frequency period-leg 1",
    "Floating rate reset frequency period-leg 2",
    "Floating rate reset frequency period multiplier-leg 1",
    "Floating rate reset frequency period multiplier-leg 2",
    "Other payment amount",
    "Fixed rate payment frequency period-Leg 1",
    "Floating rate payment frequency period-Leg 1",
    "Fixed rate payment frequency period-Leg 2",
    "Floating rate payment frequency period-Leg 2",
    "Fixed rate payment frequency period multiplier-Leg 1",
    "Floating rate payment frequency period multiplier-Leg 1",
    "Fixed rate payment frequency period multiplier-Leg 2",
    "Floating rate payment frequency period multiplier-Leg 2",
    "Other payment type",
    "Other payment currency",
    "Settlement currency-Leg 1",
    "Settlement currency-Leg 2",
    "Settlement location",
    "Collateralisation category",
    "Custom basket indicator",
    "Index factor",
    "Underlier ID-Leg 1",
    "Underlier ID-Leg 2",
    "Underlier ID source-Leg 1",
    "Underlying Asset Name",
    "Underlying asset subtype or underlying contract subtype-Leg 1",
    "Underlying asset subtype or underlying contract subtype-Leg 2",
    "Embedded Option type",
    "Option Type",
    "Option Style",
    "Package indicator",
    "Package transaction price",
    "Package transaction price currency",
    "Package transaction price notation",
    "Package transaction spread",
    "Package transaction spread currency",
    "Package transaction spread notation",
    "Physical delivery location-Leg 1",
    "Delivery Type",
    "Unique Product Identifier",
    "UPI FISN",
    "UPI Underlier Name",
)
