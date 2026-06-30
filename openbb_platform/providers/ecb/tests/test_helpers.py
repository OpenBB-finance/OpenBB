"""Unit tests for ``openbb_ecb.utils.helpers``."""

from openbb_ecb.utils.helpers import (
    parse_sdmx_json,
    parse_sdmx_period,
    parse_series_keys,
    period_end,
)


def test_parse_sdmx_period_all_formats():
    """Every SDMX period format and the start override are handled."""
    assert parse_sdmx_period("2024-06-23") == "2024-06-23"
    assert parse_sdmx_period("2024-06") == "2024-06-01"
    assert parse_sdmx_period("2024-Q2") == "2024-04-01"
    assert parse_sdmx_period("2024-S1") == "2024-01-01"
    assert parse_sdmx_period("2024-S2") == "2024-07-01"
    assert parse_sdmx_period("2024-W23") == "2024-06-03"
    assert parse_sdmx_period("2024") == "2024-01-01"
    assert (
        parse_sdmx_period("2024-06", start="2024-06-30T00:00:00+02:00") == "2024-06-30"
    )


def test_parse_sdmx_period_fallbacks():
    """Empty input and unparseable input return as-is."""
    assert parse_sdmx_period("") == ""
    assert parse_sdmx_period("garbage-Q9") == "garbage-Q9"


def test_period_end_all_formats():
    """Period-ending dates and the end override."""
    assert period_end("2024-Q3") == "2024-09-30"
    assert period_end("2024-02") == "2024-02-29"
    assert period_end("2023") == "2023-12-31"
    assert period_end("2024-06-15", end="2024-06-30T00:00:00") == "2024-06-30"


def test_period_end_fallbacks():
    """Empty, weekly (delegates to start) and unparseable inputs."""
    assert period_end("") == ""
    assert period_end("2024-W10") == parse_sdmx_period("2024-W10")
    assert period_end("bad-Q9") == "bad-Q9"


def test_parse_sdmx_json_empty():
    """No dataSets returns an empty list."""
    assert parse_sdmx_json({}) == []
    assert parse_sdmx_json({"dataSets": []}) == []


def test_parse_sdmx_json_dimensions_and_attributes():
    """Series/observation attributes decode; out-of-range indices are skipped."""
    message = {
        "dataSets": [
            {
                "series": {
                    "0": {
                        "attributes": [0, None, 9],
                        "observations": {"0": [2.0, 0, None]},
                    }
                }
            }
        ],
        "structure": {
            "dimensions": {
                "series": [{"id": "FREQ", "values": [{"id": "D", "name": "Daily"}]}],
                "observation": [
                    {"id": "TIME_PERIOD", "values": [{"id": "2024-01-01"}]}
                ],
            },
            "attributes": {
                "series": [
                    {"id": "UNIT", "values": [{"id": "EUR", "name": "Euro"}]},
                    {"id": "EMPTY", "values": []},
                    {"id": "OOR", "values": []},
                ],
                "observation": [
                    {"id": "OBS_STATUS", "values": [{"id": "A", "name": "Normal"}]}
                ],
            },
        },
    }
    rows = parse_sdmx_json(message)
    assert len(rows) == 1
    row = rows[0]
    assert row["FREQ"] == "D"
    assert row["FREQ__label"] == "Daily"
    assert row["series_key"] == "D"
    assert row["_dim_ids"] == ["FREQ"]
    assert row["UNIT"] == "EUR"
    assert row["OBS_STATUS"] == "A"
    assert row["OBS_VALUE"] == 2.0


def test_parse_sdmx_json_plain_values_and_no_obs_dims():
    """Plain (non-dict) codelist values and absent observation dims work."""
    message = {
        "dataSets": [{"series": {"0": {"observations": {"0": [1.0]}}}}],
        "structure": {"dimensions": {"series": [{"id": "FREQ", "values": ["D"]}]}},
    }
    rows = parse_sdmx_json(message)
    assert rows[0]["FREQ"] == "D"
    assert rows[0]["OBS_VALUE"] == 1.0


def test_parse_sdmx_json_edge_branches():
    """Key overflow, out-of-range codes, empty observations and null obs attrs."""
    message = {
        "dataSets": [
            {
                "series": {
                    "0:0:0": {"observations": {}},  # more indices than dims -> break
                    "0:5": {  # CURRENCY index out of range -> code None
                        "observations": {
                            "0": [],  # empty obs -> OBS_VALUE None; obs attr loop short-circuit
                            "1": [2.0, 9],  # obs attr index out of range -> code None
                        }
                    },
                }
            }
        ],
        "structure": {
            "dimensions": {
                "series": [
                    {"id": "FREQ", "values": [{"id": "D", "name": "Daily"}]},
                    {"id": "CURRENCY", "values": [{"id": "USD", "name": "US dollar"}]},
                ],
                "observation": [
                    {
                        "id": "TIME_PERIOD",
                        # second value is a plain string (non-dict) -> exercises the guard
                        "values": [{"id": "2024-01-01"}, "2024-01-02"],
                    }
                ],
            },
            "attributes": {
                "series": [],
                "observation": [
                    {"id": "OBS_STATUS", "values": [{"id": "A", "name": "Normal"}]}
                ],
            },
        },
    }
    rows = parse_sdmx_json(message)
    out_of_range = [r for r in rows if r["FREQ"] == "D" and r["CURRENCY"] is None]
    assert out_of_range  # the 0:5 series parsed despite the bad index
    assert out_of_range[0]["series_key"] == "D"  # None code excluded from key
    assert any(r["OBS_VALUE"] is None for r in out_of_range)  # empty observation
    assert all("OBS_STATUS" not in r for r in out_of_range)  # null obs attr skipped


def test_parse_series_keys_empty():
    """No dataSets returns an empty list."""
    assert parse_series_keys({}) == []
    assert parse_series_keys({"dataSets": []}) == []


def test_parse_series_keys_decodes_records():
    """One record per series: decoded codes/labels, key, and composed name."""
    message = {
        "dataSets": [
            {
                "series": {
                    "0:0": {},  # FREQ=D, CURRENCY=USD
                    "0:1:0": {},  # plain-string CURRENCY value; 3rd index -> break
                    "0:5": {},  # CURRENCY index out of range -> code/label None
                    "": {},  # empty key -> empty codes/name
                }
            }
        ],
        "structure": {
            "dimensions": {
                "series": [
                    {"id": "FREQ", "values": [{"id": "D", "name": "Daily"}]},
                    {
                        "id": "CURRENCY",
                        # second value is a plain string (no name)
                        "values": [{"id": "USD", "name": "US dollar"}, "JPY"],
                    },
                ]
            }
        },
    }
    by_key = {r["series_key"]: r for r in parse_series_keys(message)}

    full = by_key["D.USD"]
    assert full["FREQ"] == "D"
    assert full["CURRENCY"] == "USD"
    assert full["FREQ__label"] == "Daily"
    assert full["name"] == "Daily — US dollar"

    plain = by_key["D.JPY"]
    assert plain["CURRENCY"] == "JPY"
    assert plain["CURRENCY__label"] is None
    assert plain["name"] == "Daily"  # label-less code omitted from the name

    out_of_range = by_key["D"]
    assert out_of_range["CURRENCY"] is None  # bad index excluded from the key

    empty = by_key[""]
    assert empty["name"] == ""
