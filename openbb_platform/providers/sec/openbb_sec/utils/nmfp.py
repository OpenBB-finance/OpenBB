"""SEC N-MFP (money market fund) filing parser."""


def _to_float(value) -> float | None:
    """Coerce a value to float, returning None when not parseable."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_nmfp(response: dict) -> tuple[list[dict], dict]:
    """Parse an N-MFP money market fund filing into holdings and series metrics."""
    form = response.get("edgarSubmission", {}).get("formData", {}) or {}
    general = form.get("generalInfo", {}) or {}
    series = form.get("seriesLevelInfo", {}) or {}

    schedule = form.get("scheduleOfPortfolioSecuritiesInfo")
    items = schedule if isinstance(schedule, list) else [schedule] if schedule else []

    holdings: list[dict] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        weight = _to_float(item.get("percentageOfMoneyMarketFundNetAssets"))
        security_yield = _to_float(item.get("yieldOfTheSecurityAsOfReportingDate"))
        holdings.append(
            {
                "name": item.get("nameOfIssuer"),
                "title": item.get("titleOfIssuer"),
                "cusip": item.get("CUSIPMember"),
                "isin": item.get("ISINId"),
                "lei": item.get("LEIID"),
                "asset_category": item.get("investmentCategory"),
                "maturity_date": item.get("finalLegalInvestmentMaturityDate"),
                "value": _to_float(item.get("includingValueOfAnySponsorSupport")),
                "weight": weight * 100 if weight is not None else None,
                "annualized_return": (
                    security_yield * 100 if security_yield is not None else None
                ),
                "currency": "USD",
            }
        )
    holdings.sort(
        key=lambda d: (d["weight"] is not None, d["weight"] or 0), reverse=True
    )

    yields = series.get("sevenDayGrossYield") or []
    if isinstance(yields, (dict, str)):
        yields = [yields]
    latest = yields[-1] if yields else None
    seven_day_yield = _to_float(
        latest.get("sevenDayGrossYieldValue") if isinstance(latest, dict) else latest
    )

    metadata = {
        "fund_name": general.get("nameOfSeries"),
        "series_id": general.get("seriesId"),
        "period_ending": general.get("reportDate"),
        "net_assets": _to_float(series.get("netAssetOfSeries")),
        "total_assets": _to_float(series.get("totalValuePortfolioSecurities")),
        "cash_and_equivalents": _to_float(series.get("cash")),
        "seven_day_gross_yield": seven_day_yield,
        "weighted_average_maturity": _to_float(series.get("averagePortfolioMaturity")),
        "weighted_average_life": _to_float(series.get("averageLifeMaturity")),
    }
    return holdings, metadata
