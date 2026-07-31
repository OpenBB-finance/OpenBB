from openbb_ecb.utils.helpers import (
    parse_sdmx_csv,
    parse_sdmx_json,
    parse_sdmx_period,
    parse_series_keys,
    period_end,
)


def test_parse_sdmx_csv():
    text = (
        "KEY,FREQ,OBS_VALUE,TIME_PERIOD,EXTRA\n"
        "EXR.D.USD,D,1.5,2024-01-01,\n"
        "OTHER,M,,2024-02,keep\n"
        "ZZZ.A.B,A,bad,2024,x\n"
    )
    rows = parse_sdmx_csv(text, "EXR")
    assert rows[0]["series_key"] == "D.USD"
    assert rows[0]["FREQ"] == "D" and rows[0]["OBS_VALUE"] == 1.5
    assert "EXTRA" not in rows[0] and "KEY" not in rows[0]
    assert rows[0]["date"] == "2024-01-01"
    assert rows[1]["series_key"] == "OTHER" and rows[1]["OBS_VALUE"] is None
    assert rows[1]["EXTRA"] == "keep"
    assert rows[2]["series_key"] == "ZZZ.A.B" and rows[2]["OBS_VALUE"] is None


def test_parse_sdmx_period_all_formats():
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
    assert parse_sdmx_period("") == ""
    assert parse_sdmx_period("garbage-Q9") == "garbage-Q9"


def test_period_end_all_formats():
    assert period_end("2024-Q3") == "2024-09-30"
    assert period_end("2024-02") == "2024-02-29"
    assert period_end("2023") == "2023-12-31"
    assert period_end("2024-06-15", end="2024-06-30T00:00:00") == "2024-06-30"


def test_period_end_fallbacks():
    assert period_end("") == ""
    assert period_end("2024-W10") == parse_sdmx_period("2024-W10")
    assert period_end("bad-Q9") == "bad-Q9"


def test_parse_sdmx_json_empty():
    assert parse_sdmx_json({}) == []
    assert parse_sdmx_json({"dataSets": []}) == []


def test_parse_sdmx_json_dimensions_and_attributes():
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
    message = {
        "dataSets": [{"series": {"0": {"observations": {"0": [1.0]}}}}],
        "structure": {"dimensions": {"series": [{"id": "FREQ", "values": ["D"]}]}},
    }
    rows = parse_sdmx_json(message)
    assert rows[0]["FREQ"] == "D"
    assert rows[0]["OBS_VALUE"] == 1.0


def test_parse_sdmx_json_edge_branches():
    message = {
        "dataSets": [
            {
                "series": {
                    "0:0:0": {"observations": {}},
                    "0:5": {
                        "observations": {
                            "0": [],
                            "1": [2.0, 9],
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
    assert out_of_range
    assert out_of_range[0]["series_key"] == "D"
    assert any(r["OBS_VALUE"] is None for r in out_of_range)
    assert all("OBS_STATUS" not in r for r in out_of_range)


def test_parse_series_keys_empty():
    assert parse_series_keys({}) == []
    assert parse_series_keys({"dataSets": []}) == []


def test_parse_series_keys_decodes_records():
    message = {
        "dataSets": [
            {
                "series": {
                    "0:0": {},
                    "0:1:0": {},
                    "0:5": {},
                    "": {},
                }
            }
        ],
        "structure": {
            "dimensions": {
                "series": [
                    {"id": "FREQ", "values": [{"id": "D", "name": "Daily"}]},
                    {
                        "id": "CURRENCY",
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
    assert plain["name"] == "Daily"

    out_of_range = by_key["D"]
    assert out_of_range["CURRENCY"] is None

    empty = by_key[""]
    assert empty["name"] == ""
