import asyncio
from datetime import date

import pytest
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.models import swap_summary as ss
from openbb_cftc.models.swap_summary import (
    CftcSwapSummaryFetcher,
    CftcSwapSummaryQueryParams,
)
from openbb_cftc.utils import fixings

RECORD = {
    "Dissemination Identifier": "4402190022000000101",
    "Asset Class": "FX",
    "UPI FISN": "NA/Fwd NDF KRW USD",
    "Dissemination Timestamp": "2026-07-26T23:59:00Z",
}

VALUED = {
    "dissemination_identifier": "4402190022000000101",
    "trade_type": "fx_forward",
    "pair": "USDKRW",
    "base": "USD",
    "quote": "KRW",
    "currency": "KRW",
    "notional": 1_000_000.0,
    "traded_rate": 1457.15,
    "spot": 1464.62,
    "market_rate": 1458.27,
    "npv": 1_120_663.11,
    "days": 36,
    "effective_date": date(2026, 7, 27),
    "expiration_date": date(2026, 8, 31),
    "product": "Non-Deliverable Forward",
    "upi_fisn": "NA/Fwd NDF KRW USD",
    "trade_date": "2026-07-26",
    "curve_date": "2026-07-26",
}


def _rows(metadata=None, side="pay"):
    return ss._fx_summary_rows({**VALUED, **(metadata or {})}, side)


def test_fx_summary_rows_cover_the_forward_economics():
    metrics = {r["metric"]: r["value"] for r in _rows()}

    assert metrics["Product"] == "NA/Fwd NDF KRW USD"
    assert metrics["Notional"] == "1,000,000.00 USD"
    assert metrics["Traded Rate"] == "1,457.150000"
    assert metrics["Spot (Now)"] == "1,464.620000"
    assert metrics["Forward (Now)"] == "1,458.270000"
    assert metrics["NPV (Now)"] == "1,120,663.11 KRW"
    assert metrics["Winning Side"] == "long USD"


def test_fx_summary_rows_flip_with_the_side():
    rows = {r["metric"]: r for r in _rows(side="receive")}

    assert rows["NPV (Now)"]["value"] == "-1,120,663.11 KRW"
    assert "short USD" in rows["NPV (Now)"]["detail"]


@pytest.mark.parametrize(
    ("npv", "expected"),
    [(1.0, "long USD"), (-1.0, "short USD"), (0.0, "flat")],
)
def test_fx_summary_rows_name_the_winning_side(npv, expected):
    metrics = {r["metric"]: r["value"] for r in _rows({"npv": npv})}

    assert metrics["Winning Side"] == expected


def test_fx_summary_rows_add_option_economics():
    metrics = {
        r["metric"]: r["value"]
        for r in _rows(
            {
                "trade_type": "fx_option",
                "strike": 1.1425,
                "traded_rate": None,
                "implied_vol": 0.0912,
                "premium": 20_000.0,
            }
        )
    }

    assert metrics["Implied Volatility"] == "9.12 %"
    assert metrics["Premium Paid"] == "20,000.00 KRW"
    assert metrics["Traded Rate"] == "1.142500"


def _patch_slices(monkeypatch, forex=None, rates=None):
    async def _slice(asset, day, use_cache=True):
        return forex if asset == "forex" else rates

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)


def test_fx_metadata_values_the_print(monkeypatch):
    _patch_slices(monkeypatch, forex=[RECORD], rates=[])
    monkeypatch.setattr(
        "openbb_cftc.utils.fx_valuation.value_fx_trade",
        lambda *a, **k: dict(VALUED),
    )
    query = CftcSwapSummaryQueryParams(
        dissemination_identifier="FX:4402190022000000101"
    )
    metadata = asyncio.run(ss._fx_metadata(query, RECORD))

    assert metadata["trade_date"] == "2026-07-26"
    assert metadata["curve_date"] == "2026-07-26"
    assert metadata["npv"] == pytest.approx(1_120_663.11)


def test_fx_metadata_needs_a_dissemination_date(monkeypatch):
    query = CftcSwapSummaryQueryParams(dissemination_identifier="FX:1")

    with pytest.raises(EmptyDataError, match="carries no dissemination date"):
        asyncio.run(ss._fx_metadata(query, {"Dissemination Identifier": "1"}))


def test_fx_metadata_raises_when_unpriceable(monkeypatch):
    _patch_slices(monkeypatch, forex=[RECORD], rates=[])
    monkeypatch.setattr(
        "openbb_cftc.utils.fx_valuation.value_fx_trade", lambda *a, **k: None
    )
    query = CftcSwapSummaryQueryParams(
        dissemination_identifier="FX:4402190022000000101"
    )

    with pytest.raises(EmptyDataError, match="no priceable FX terms"):
        asyncio.run(ss._fx_metadata(query, RECORD))


def test_fetcher_routes_an_fx_print_through_the_fx_path(monkeypatch):
    monkeypatch.setattr(
        "openbb_cftc.utils.store.get_trade_record", lambda identifier: RECORD
    )

    async def _metadata(query, record):
        return dict(VALUED)

    monkeypatch.setattr(ss, "_fx_metadata", _metadata)
    query = CftcSwapSummaryQueryParams(
        dissemination_identifier="FX:4402190022000000101"
    )
    data = asyncio.run(CftcSwapSummaryFetcher.aextract_data(query, None))

    assert data[0] == "fx"

    result = CftcSwapSummaryFetcher.transform_data(query, data)

    assert result.metadata["pair"] == "USDKRW"
    assert any(row.metric == "Winning Side" for row in result.result)


def test_fetcher_falls_through_to_the_rates_path(monkeypatch):
    monkeypatch.setattr(
        "openbb_cftc.utils.store.get_trade_record", lambda identifier: None
    )
    called: list = []

    async def _rates(query, credentials):
        called.append(query.dissemination_identifier)

        return ("rates-shaped",)

    monkeypatch.setattr(
        "openbb_cftc.models.swap_valuation.CftcSwapValuationFetcher.aextract_data",
        _rates,
    )
    query = CftcSwapSummaryQueryParams(
        dissemination_identifier="IR:4402189952000004401"
    )
    data = asyncio.run(CftcSwapSummaryFetcher.aextract_data(query, None))

    assert called == ["4402189952000004401"]
    assert data == ("rates-shaped",)


def test_fetcher_uses_the_rates_path_without_an_identifier(monkeypatch):
    async def _rates(query, credentials):
        return ("rates-shaped",)

    monkeypatch.setattr(
        "openbb_cftc.models.swap_valuation.CftcSwapValuationFetcher.aextract_data",
        _rates,
    )
    query = CftcSwapSummaryQueryParams()

    assert asyncio.run(CftcSwapSummaryFetcher.aextract_data(query, None)) == (
        "rates-shaped",
    )


def test_keep_priceable_forex_returns_nothing_when_the_rates_slice_fails(monkeypatch):
    from openbb_core.app.model.abstract.error import OpenBBError

    from openbb_cftc.models import swap_trades as st

    async def _slice(*args, **kwargs):
        raise OpenBBError("no rates slice")

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)
    query = st.CftcSwapTradesQueryParams(asset_class="forex")

    assert (
        asyncio.run(st._keep_priceable_forex([{"a": 1}], [], "2026-07-15", query)) == []
    )
    assert asyncio.run(st._keep_priceable([{"a": 1}], [], "2026-07-15", query)) == []


def test_cnb_skips_rows_shorter_than_the_column(monkeypatch):
    from tests.test_fixings_sources import _patch

    body = "Date|PRIBID|PRIBOR\n23 Jul 2026||1\n22 Jul 2026||1||2||3||4||5||3.85\n"
    _patch(monkeypatch, [("year.txt", body)])
    rates = asyncio.run(fixings._fetch_cnb("12", "2026-01-01", "2026-12-31"))

    assert rates == {"2026-07-22": pytest.approx(0.0385)}


@pytest.mark.parametrize(
    ("underlier", "expected"),
    [
        ("MYR-MYOR-OIS Compound", "MYOR"),
        ("KRW-KOFR-OIS Compound", "KOFR"),
        ("PLN-POLSTR", "POLSTR"),
        ("TWD-TAIBOR-Reuters", "TAIBOR"),
    ],
)
def test_index_for_underlier_covers_the_newest_benchmarks(underlier, expected):
    assert fixings.index_for_underlier(underlier) == expected


def test_taibor_falls_through_encodings(monkeypatch):
    import io
    import zipfile

    from tests.test_fixings_sources import TAIBOR_INDEX, _patch

    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w") as bundle:
        bundle.writestr(
            "JUL2026.csv",
            "日期,a,b,c,d,e\n27JUL26,1,2,3,4,1.68\n".encode("utf-8-sig"),
        )

    _patch(
        monkeypatch,
        [("taiborDaily/index", TAIBOR_INDEX), ("DownloadAll", buffer.getvalue())],
    )
    rates = asyncio.run(fixings._fetch_taibor("5", "2026-01-01", "2026-12-31"))

    assert rates["2026-07-27"] == pytest.approx(0.0168)


def test_bok_skips_unparseable_values(monkeypatch):
    import json

    from tests.test_fixings_sources import _patch

    content = json.dumps([{"20260724": "n/a", "20260723": 2.91}])
    _patch(monkeypatch, [("httpService", json.dumps({"data": {"jsonCtnt": content}}))])
    rates = asyncio.run(
        fixings._fetch_bok("817Y002/010502000", "2026-07-01", "2026-07-27")
    )

    assert rates == {"2026-07-23": pytest.approx(0.0291)}


def test_cnb_skips_unparseable_rates(monkeypatch):
    from tests.test_fixings_sources import _patch

    body = (
        "Date|PRIBID|PRIBOR|a|b|c|d|e|f|g|h|i|j\n"
        "23 Jul 2026||1||2||3||4||5||n/a\n"
        "22 Jul 2026||1||2||3||4||5||3.85\n"
    )
    _patch(monkeypatch, [("year.txt", body)])
    rates = asyncio.run(fixings._fetch_cnb("12", "2026-01-01", "2026-12-31"))

    assert rates == {"2026-07-22": pytest.approx(0.0385)}


def test_bbk_skips_unparseable_rows(monkeypatch):
    from tests.test_fixings_sources import _patch

    body = '"",S,F\n2026-07-24,n/a,\n2026-07-23,2.472,\n'
    _patch(monkeypatch, [("rest/download", body)])
    rates = asyncio.run(fixings._fetch_bbk("BBIG1/D.S", "2026-07-01", "2026-07-31"))

    assert rates == {"2026-07-23": pytest.approx(0.02472)}
