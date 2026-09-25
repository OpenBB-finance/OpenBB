import asyncio
from datetime import date, datetime

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_cftc.models.cds_index_trades import (
    CftcCdsIndexTradesData,
    CftcCdsIndexTradesFetcher,
    CftcCdsIndexTradesQueryParams,
)

DISSEM = date(2026, 7, 15)


@pytest.fixture(name="patch_credits")
def patch_credits_fixture(monkeypatch, credits_records):

    async def _dates(asset_class):
        return ["2026-07-14", "2026-07-15"]

    async def _slice(asset_class, report_date, use_cache=True):
        return credits_records

    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_available_dates", _dates)
    monkeypatch.setattr("openbb_cftc.utils.dtcc.get_slice", _slice)


def _fetch(**params):
    return asyncio.run(CftcCdsIndexTradesFetcher.fetch_data(params, {}))


def test_transform_query():
    query = CftcCdsIndexTradesFetcher.transform_query({})

    assert isinstance(query, CftcCdsIndexTradesQueryParams)


def test_query_defaults_are_none():
    query = CftcCdsIndexTradesQueryParams()

    assert query.index is None
    assert query.date is None
    assert query.tenor is None
    assert query.min_notional is None
    assert query.limit is None
    assert query.use_cache is True


def test_data_normalizes_values():
    model = CftcCdsIndexTradesData.model_validate(
        {
            "dissemination_date": DISSEM,
            "Dissemination Identifier": "4202588328000000101",
            "UPI Underlier Name": "CDX.NA.HY",
            "Notional amount-Leg 1": "79,501,573+",
            "Fixed rate-Leg 1": "0.05",
            "Other payment amount": "1,234,567.89",
            "Other payment type": "UFRO",
            "Spread currency-Leg 1": "",
            "Expiration Date": "2031-06-20",
            "Execution Timestamp": "2026-07-15T13:00:00",
            "tenor": "5Y",
        }
    )

    assert model.dissemination_date == DISSEM
    assert model.index == "CDX.NA.HY"
    assert model.notional_amount == 79501573.0
    assert model.is_capped is True
    assert model.coupon == 0.05
    assert model.upfront_amount == 1234567.89
    assert model.upfront_type == "UFRO"
    assert model.spread_currency is None
    assert model.maturity_date == date(2031, 6, 20)
    assert model.execution_timestamp == datetime(2026, 7, 15, 13, 0, 0)
    assert model.tenor == "5Y"


def test_data_drops_unmapped_slice_columns():
    model = CftcCdsIndexTradesData.model_validate(
        {
            "dissemination_date": DISSEM,
            "UPI Underlier Name": "CDX.NA.IG",
            "Asset Class": "CR",
            "Mandatory clearing indicator": "TRUE",
            "Maturity date of the underlier": "2030-12-20",
            "Post-priced swap indicator": "false",
        }
    )
    emitted = set(model.model_dump())

    assert emitted == set(CftcCdsIndexTradesData.model_fields)
    assert not model.model_extra
    assert "Asset Class" not in emitted
    assert "Mandatory clearing indicator" not in emitted


def test_data_passes_through_non_str():
    model = CftcCdsIndexTradesData.model_validate(
        {
            "dissemination_date": DISSEM,
            "Notional amount-Leg 1": 100.0,
            "UPI FISN": "NA/CDS Corp Idx",
            "Cleared": None,
        }
    )

    assert model.notional_amount == 100.0
    assert model.upi_fisn == "NA/CDS Corp Idx"
    assert model.cleared is None
    assert model.is_capped is False


def test_data_passes_non_dict_payloads_through():
    from pydantic import ValidationError

    with pytest.raises(ValidationError, match="valid dictionary"):
        CftcCdsIndexTradesData.model_validate(["not", "a", "mapping"])


def test_data_drops_a_bare_cap_marker():
    model = CftcCdsIndexTradesData.model_validate(
        {"dissemination_date": DISSEM, "Notional amount-Leg 1": "+"}
    )

    assert model.notional_amount is None
    assert model.is_capped is True


def test_fetch_returns_the_curated_tape(patch_credits):
    result = _fetch(date=DISSEM)

    assert len(result.result) == 1338
    assert result.metadata["dissemination_date"] == "2026-07-15"
    assert result.metadata["prints"] == 1338
    assert len(result.metadata["indexes"]) == 15
    assert result.metadata["capped_prints"] == 178

    row = result.result[0]
    assert row.dissemination_date == DISSEM
    assert row.upi_fisn in ("NA/CDS Corp Idx", "NA/CDS Corp Idx Tra", "NA/CDS Sov Idx")


def test_fetch_prices_high_yield_by_coupon_and_upfront(patch_credits):
    result = _fetch(date=DISSEM, index="CDX.NA.HY")

    assert len(result.result) == 360
    assert {row.coupon for row in result.result} == {0.05}
    assert all(row.index == "CDX.NA.HY" for row in result.result)

    upfront = [row for row in result.result if row.upfront_type == "UFRO"]
    assert len(upfront) == 274
    assert all(row.upfront_amount is not None for row in upfront)


def test_fetch_spread_is_not_the_traded_level_for_high_yield(patch_credits):
    result = _fetch(date=DISSEM, index="CDX.NA.HY")

    decimal = [row.spread for row in result.result if row.spread_notation == "3"]
    assert len(decimal) == 236
    assert min(decimal) > 0.0107 and max(decimal) < 0.0109

    monetary = [row.spread for row in result.result if row.spread_notation == "1"]
    assert len(monetary) == 36
    assert min(monetary) > 107.9 and max(monetary) < 108.1
    assert {
        row.spread_currency for row in result.result if row.spread_notation == "1"
    } == {"USD"}


def test_fetch_investment_grade_coupon_and_spread_differ_from_high_yield(patch_credits):
    result = _fetch(date=DISSEM, index="CDX.NA.IG")

    assert len(result.result) == 359
    assert {row.coupon for row in result.result} == {0.01}

    spreads = [row.spread for row in result.result if row.spread_notation == "3"]
    assert max(spreads) < 0.01


def test_fetch_filters_by_tenor_and_notional_and_limit(patch_credits):
    assert len(_fetch(date=DISSEM, tenor="5Y").result) == 1266
    assert len(_fetch(date=DISSEM, limit=10).result) == 10

    large = _fetch(date=DISSEM, min_notional=100_000_000).result
    assert all(row.notional_amount >= 100_000_000 for row in large)
    assert len(large) < 1338


def test_fetch_maturity_pins_the_series(patch_credits):
    result = _fetch(date=DISSEM, index="CDX.NA.IG", tenor="5Y")
    maturities = {row.maturity_date for row in result.result}

    assert date(2031, 6, 20) in maturities
    assert date(2030, 12, 20) in maturities
    assert all(row.index == "CDX.NA.IG" for row in result.result)


def test_fetch_walks_back_to_the_latest_viable_file(patch_credits):
    result = _fetch()

    assert result.metadata["dissemination_date"] == "2026-07-15"
    assert result.metadata["prints"] == 1338


def test_fetch_raises_when_a_dated_query_matches_nothing(patch_credits):
    with pytest.raises(EmptyDataError, match="No CDS index prints matched"):
        _fetch(date=DISSEM, index="NOT.AN.INDEX")


def test_fetch_raises_when_no_file_holds_a_match(patch_credits):
    with pytest.raises(OpenBBError, match="usable data"):
        _fetch(index="NOT.AN.INDEX")


def test_upfront_payment_picks_the_upfront_out_of_a_joined_payment_list():
    from openbb_cftc.models.cds_index_trades import _upfront_payment

    joined = {
        "Other payment type": "UFRO;UWIN",
        "Other payment amount": "15947222.22222;3098611.11111",
        "Other payment currency": "EUR;EUR",
    }

    assert _upfront_payment(joined) == {
        "Other payment type": "UFRO",
        "Other payment amount": "15947222.22222",
        "Other payment currency": "EUR",
    }


def test_upfront_payment_falls_back_to_the_first_entry():
    from openbb_cftc.models.cds_index_trades import _upfront_payment

    joined = {
        "Other payment type": "UWIN;PEXH",
        "Other payment amount": "10.5;2.5",
        "Other payment currency": "EUR;EUR",
    }

    assert _upfront_payment(joined)["Other payment type"] == "UWIN"
    assert _upfront_payment(joined)["Other payment amount"] == "10.5"


def test_upfront_payment_leaves_a_single_payment_alone():
    from openbb_cftc.models.cds_index_trades import _upfront_payment

    single = {
        "Other payment type": "UFRO",
        "Other payment amount": "1,250.5",
        "Other payment currency": "USD",
    }

    assert _upfront_payment(single) == {}
    assert _upfront_payment({}) == {}


def test_data_validates_a_record_carrying_two_other_payments():
    record = {
        "Dissemination Identifier": "4435945463000001101",
        "Asset Class": "CR",
        "disseminationDate": "2026-07-28",
        "Event timestamp": "2026-07-28T13:53:42Z",
        "UPI Underlier Name": "CDX.NA.IG",
        "Expiration Date": "2031-06-20",
        "Effective Date": "2026-06-20",
        "Notional amount-Leg 1": "50,000,000",
        "Notional currency-Leg 1": "EUR",
        "Other payment type": "UFRO;UWIN",
        "Other payment amount": "15947222.22222;3098611.11111",
        "Other payment currency": "EUR;EUR",
    }
    model = CftcCdsIndexTradesData.model_validate(record)

    assert model.upfront_amount == 15947222.22222
    assert model.upfront_type == "UFRO"
    assert model.upfront_currency == "EUR"
