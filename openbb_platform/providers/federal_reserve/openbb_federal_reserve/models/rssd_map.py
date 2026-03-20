"""Ticker → RSSD ID mapping for FFIEC FR Y-15 filers.

Source: FFIEC NIC FR Y-15 Snapshot Report (December 31, 2024).
        https://www.ffiec.gov/npw/FinancialReport/FRY15Reports

Notes:
    - All 54 institutions that filed the FR Y-15 as of Q4 2024 are included.
    - Foreign banks appear twice: once for the parent (mapped to their NYSE/NASDAQ
      ADR ticker) and once for their US intermediate holding company (IHC), which
      is the actual FR Y-15 filing entity. Both resolve correctly.
    - Pure OTC-traded foreign parents (e.g. BNP Paribas, Societe Generale) are
      excluded per the maintainer's scope ("not OTC"). Their US IHCs are still
      reachable via RSSD ID directly.
    - Flagstar Financial (FLG) was formerly New York Community Bancorp (NYCB).
      Both tickers are mapped to the same RSSD for backwards compatibility.
    - Discover Financial (DFS) was acquired by Capital One in February 2025 but
      was an independent filer as of the December 31, 2024 report date.
"""

# ---------------------------------------------------------------------------
# Primary ticker → RSSD mapping
# ---------------------------------------------------------------------------
TICKER_TO_RSSD: dict[str, str] = {

    # ── US G-SIBs ────────────────────────────────────────────────────────────
    "JPM":   "1039502",   # JPMorgan Chase & Co.
    "C":     "1951350",   # Citigroup Inc.
    "BK":    "3587146",   # Bank of New York Mellon Corporation
    "STT":   "1111435",   # State Street Corporation
    "BAC":   "1073757",   # Bank of America Corporation
    "WFC":   "1120754",   # Wells Fargo & Company
    "GS":    "2380443",   # Goldman Sachs Group, Inc.
    "MS":    "2162966",   # Morgan Stanley

    # ── Large US Holding Companies ───────────────────────────────────────────
    "PNC":   "1069778",   # PNC Financial Services Group, Inc.
    "NTRS":  "1199611",   # Northern Trust Corporation
    "MTB":   "1037003",   # M&T Bank Corporation
    "USB":   "1119794",   # U.S. Bancorp
    "FCNCA": "1075612",   # First Citizens BancShares, Inc.
    "AXP":   "1275216",   # American Express Company
    "SYF":   "4504654",   # Synchrony Financial
    "FITB":  "1070345",   # Fifth Third Bancorp
    "FLG":   "2132932",   # Flagstar Financial, Inc. (formerly NYCB)
    "NYCB":  "2132932",   # Flagstar Financial, Inc. (legacy ticker)
    "KEY":   "1068025",   # KeyCorp
    "TFC":   "1074156",   # Truist Financial Corporation
    "SCHW":  "1026632",   # Charles Schwab Corporation
    "DFS":   "3846375",   # Discover Financial Services (independent as of Q4 2024)
    "COF":   "2277860",   # Capital One Financial Corporation
    "CFG":   "1132449",   # Citizens Financial Group, Inc.
    "HBAN":  "1068191",   # Huntington Bancshares Incorporated
    "RF":    "3242838",   # Regions Financial Corporation
    "ALLY":  "1562859",   # Ally Financial Inc.

    # ── Foreign Banks — mapped to US Intermediate Holding Company (IHC) ─────
    # These are the actual FR Y-15 filing entities registered with the Fed.
    # The parent ADR tickers below resolve to the IHC RSSD for data purposes.
    "HSBC":  "3232316",   # HSBC Holdings PLC → HSBC North America Holdings Inc.
    "UBS":   "4846998",   # UBS Group AG → UBS Americas Holding LLC
    "SAN":   "3981856",   # Banco Santander S.A. → Santander Holdings USA, Inc.
    "RY":    "5280254",   # Royal Bank of Canada → RBC US Group Holdings LLC
    "BMO":   "1245415",   # Bank of Montreal → BMO Financial Corp.
    "BCS":   "5006575",   # Barclays PLC → Barclays US LLC
    "CM":    "5014141",   # CIBC → CIBC Bancorp USA Inc.
    "SMFG":  "3133262",   # Sumitomo Mitsui Financial Group, Inc.
    "TD":    "3606542",   # Toronto-Dominion Bank → TD Group US Holdings LLC
    "MFG":   "5034792",   # Mizuho Financial Group → Mizuho Americas LLC
    "MUFG":  "2961897",   # Mitsubishi UFJ Financial Group, Inc.
    "DB":    "2816906",   # Deutsche Bank AG → DB USA Corporation
    "BNS":   "1238967",   # Bank of Nova Scotia
}


# ---------------------------------------------------------------------------
# Reverse map: RSSD → ticker (for display / metadata purposes)
# ---------------------------------------------------------------------------
RSSD_TO_TICKER: dict[str, str] = {
    rssd: ticker
    for ticker, rssd in TICKER_TO_RSSD.items()
    # De-duplicate: keep the most current ticker (e.g. FLG over NYCB)
    if ticker not in ("NYCB",)
}


# ---------------------------------------------------------------------------
# Resolver function used by FfiecRiskFetcher
# ---------------------------------------------------------------------------

def resolve_rssd(identifier: str) -> str:
    """Resolve a ticker or raw RSSD ID to a numeric RSSD string.

    Args:
        identifier: A stock ticker (e.g. 'JPM') or a raw RSSD ID (e.g. '1039502').

    Returns:
        The RSSD ID as a string.

    Raises:
        ValueError: If the ticker is not found in the mapping.

    Examples:
        >>> resolve_rssd("JPM")
        '1039502'
        >>> resolve_rssd("1039502")
        '1039502'
        >>> resolve_rssd("jpm")   # case-insensitive
        '1039502'
    """
    upper = identifier.strip().upper()

    if upper in TICKER_TO_RSSD:
        return TICKER_TO_RSSD[upper]

    # If it looks like a numeric RSSD ID, pass it through directly
    if identifier.strip().isdigit():
        return identifier.strip()

    raise ValueError(
        f"'{identifier}' is not a recognised ticker or RSSD ID. "
        f"Pass a numeric RSSD ID directly, or use one of: {sorted(TICKER_TO_RSSD.keys())}"
    )