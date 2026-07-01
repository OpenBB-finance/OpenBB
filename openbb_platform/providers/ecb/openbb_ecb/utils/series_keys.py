"""ECB SDMX series-key builders for the dedicated timeseries models."""

from __future__ import annotations

FREQUENCY_MAP: dict[str, str] = {
    "annual": "A",
    "business": "B",
    "daily": "D",
    "weekly": "W",
    "monthly": "M",
    "quarterly": "Q",
    "semi_annual": "S",
}


def exr_key(currency: str, freq: str = "D") -> str:
    """Build an EXR key for ``<currency>`` vs EUR."""
    return f"{freq}.{currency.upper()}.EUR.SP00.A"


FM_RATE_CODES: dict[str, str] = {
    "deposit": "DFR",
    "lending": "MLFR",
    "refinancing": "MRR_FR",
}


def fm_key(rate_code: str, freq: str = "B") -> str:
    """Build an FM key for a key ECB interest rate level."""
    return f"{freq}.U2.EUR.4F.KR.{rate_code}.LEV"


EST_BENCHMARK = "EU000A2X2A25"
EST_DATA_TYPES: dict[str, str] = {
    "WT": "rate",
    "R25": "percentile_25",
    "R75": "percentile_75",
    "TT": "volume",
    "NT": "transactions",
    "NB": "number_of_banks",
    "VL": "large_bank_share_of_volume",
}


def est_key(freq: str = "B") -> str:
    """Build the EST key fetching every €STR data type in one request."""
    return f"{freq}.{EST_BENCHMARK}.{'+'.join(EST_DATA_TYPES)}"


MIR_SERIES: dict[str, tuple[str, str, str, str]] = {
    "household_overnight_deposits": ("L21", "A", "2250", "N"),
    "household_deposits_with_agreed_maturity": ("L22", "A", "2250", "N"),
    "household_deposits_redeemable_at_notice": ("L23", "A", "2250", "N"),
    "household_loans_for_house_purchase": ("A2C", "A", "2250", "N"),
    "household_loans_for_house_purchase_cost_of_borrowing": ("A2C", "AM", "2250", "N"),
    "household_consumer_credit": ("A2B", "A", "2250", "N"),
    "household_other_loans": ("A2D", "A", "2250", "N"),
    "corporate_overnight_deposits": ("L21", "A", "2240", "N"),
    "corporate_deposits_with_agreed_maturity": ("L22", "A", "2240", "N"),
    "corporate_loans": ("A2A", "A", "2240", "N"),
    "corporate_loans_cost_of_borrowing": ("A2I", "AM", "2240", "N"),
    "household_loans_outstanding": ("A20", "A", "2250", "O"),
    "household_house_purchase_outstanding": ("A22", "A", "2250", "O"),
    "household_consumer_and_other_outstanding": ("A25", "A", "2250", "O"),
}


def mir_key(series: str, ref_area: str = "U2", freq: str = "M") -> str:
    """Build a MIR key for a curated headline bank-rate series."""
    bs_item, maturity, counterpart, coverage = MIR_SERIES[series]
    return f"{freq}.{ref_area}.B.{bs_item}.{maturity}.R.A.{counterpart}.EUR.{coverage}"
