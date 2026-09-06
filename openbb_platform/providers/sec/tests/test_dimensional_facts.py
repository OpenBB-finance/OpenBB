"""Tests for the class-dimensioned per-share companyfacts fallback."""

# flake8: noqa: D103

import pytest
from openbb_sec.utils._dimensional_facts import (
    _decimal_value,
    _instance_url,
    _select_filings,
    merge_dimensional_per_share_facts,
)

_START = "2026-04-04"
_END = "2026-07-03"


def _fact(value, member, start=_START, end=_END, axis="StatementClassOfStockAxis"):
    return {
        "start": start,
        "end": end,
        "value": str(value),
        "dimensions": {
            f"us-gaap:{axis}": {
                "member": member,
                "label": member,
            }
        },
    }


def _multi_axis_fact(value, members, start=_START, end=_END):
    """Build a fact carrying one member on each of several axes."""
    return {
        "start": start,
        "end": end,
        "value": str(value),
        "dimensions": {
            f"us-gaap:{axis}": {"member": member, "label": member}
            for axis, member in members.items()
        },
    }


def _cover(*members):
    """Cover-page facts that enumerate the issuer's common-stock classes."""
    return {
        "dei_EntityCommonStockSharesOutstanding": [
            {
                "value": str(1_000 + index),
                "dimensions": {
                    "us-gaap:StatementClassOfStockAxis": {
                        "member": member,
                        "label": member,
                    }
                },
            }
            for index, member in enumerate(members)
        ]
    }


def _facts_json(cik, start=_START, end=_END):
    return {
        "cik": cik,
        "entityName": "Test Company",
        "facts": {
            "us-gaap": {
                "Revenues": {
                    "units": {
                        "USD": [
                            {
                                "start": start,
                                "end": end,
                                "val": 1,
                                "accn": "0000000000-26-000001",
                                "fy": 2026,
                                "fp": "Q2",
                                "form": "10-Q",
                                "filed": "2026-08-01",
                                "frame": "CY2026Q2",
                            }
                        ]
                    }
                }
            }
        },
    }


def _filing(form="10-Q", accession="0000000000-26-000001", filed="2026-08-01"):
    return {
        "accessionNumber": accession,
        "form": form,
        "filingDate": filed,
        "reportDate": _END,
        "primaryDocument": "test-20260703.htm",
    }


def _values(facts_json, tag, unit):
    return facts_json["facts"]["us-gaap"][tag]["units"][unit]


def test_coke_sums_basic_shares_but_not_diluted_shares():
    """COKE basic counts sum classes while diluted uses its senior class."""
    facts_json = _facts_json(317540)
    instance_facts = {
        **_cover("coke:CommonClassUndefinedMember", "us-gaap:CommonClassBMember"),
        "us-gaap_EarningsPerShareBasic": [
            _fact("2.39", "coke:CommonClassUndefinedMember"),
            _fact("2.39", "us-gaap:CommonClassBMember"),
        ],
        "us-gaap_EarningsPerShareDiluted": [
            _fact("2.38", "coke:CommonClassUndefinedMember"),
            _fact("2.38", "us-gaap:CommonClassBMember"),
        ],
        "us-gaap_WeightedAverageNumberOfSharesOutstandingBasic": [
            _fact(56_517_000, "coke:CommonClassUndefinedMember"),
            _fact(10_047_000, "us-gaap:CommonClassBMember"),
        ],
        "us-gaap_WeightedAverageNumberOfDilutedSharesOutstanding": [
            _fact(66_649_000, "coke:CommonClassUndefinedMember"),
            _fact(10_132_000, "us-gaap:CommonClassBMember"),
        ],
    }

    added = merge_dimensional_per_share_facts(
        facts_json, instance_facts, _filing(), "COKE"
    )

    assert added == 4
    assert _values(facts_json, "EarningsPerShareBasic", "USD/shares")[0]["val"] == 2.39
    assert (
        _values(facts_json, "EarningsPerShareDiluted", "USD/shares")[0]["val"] == 2.38
    )
    assert (
        _values(facts_json, "WeightedAverageNumberOfSharesOutstandingBasic", "shares")[
            0
        ]["val"]
        == 66_564_000
    )
    assert (
        _values(
            facts_json, "WeightedAverageNumberOfDilutedSharesOutstanding", "shares"
        )[0]["val"]
        == 66_649_000
    )
    assert (
        _values(facts_json, "EarningsPerShareBasic", "USD/shares")[0]["frame"]
        == "CY2026Q2"
    )


def test_existing_companyfact_wins_over_dimensional_fallback():
    """Never replace an SEC-provided undimensioned value."""
    facts_json = _facts_json(317540)
    facts_json["facts"]["us-gaap"]["EarningsPerShareBasic"] = {
        "units": {
            "USD/shares": [
                {
                    "start": _START,
                    "end": _END,
                    "val": 9.99,
                    "form": "10-Q",
                    "filed": "2026-08-01",
                }
            ]
        }
    }

    added = merge_dimensional_per_share_facts(
        facts_json,
        {
            **_cover("coke:CommonClassUndefinedMember", "us-gaap:CommonClassBMember"),
            "us-gaap_EarningsPerShareBasic": [
                _fact("2.39", "coke:CommonClassUndefinedMember")
            ],
        },
        _filing(),
        "COKE",
    )

    assert added == 0
    assert _values(facts_json, "EarningsPerShareBasic", "USD/shares")[0]["val"] == 9.99


def test_newer_vintage_is_appended_not_suppressed():
    """A later restatement must not be blocked by an earlier vintage.

    COKE's 10-for-1 split means the FY2024 10-K reports pre-split figures that
    the FY2025 10-K restates.  Both vintages have to reach ``facts_json`` so
    ``compute_ref_filings`` can pick the newest by filing date.
    """
    facts_json = _facts_json(317540)
    cover = _cover("coke:CommonClassUndefinedMember", "us-gaap:CommonClassBMember")

    merge_dimensional_per_share_facts(
        facts_json,
        {
            **cover,
            "us-gaap_EarningsPerShareBasic": [
                _fact("70.10", "coke:CommonClassUndefinedMember")
            ],
        },
        _filing(accession="0000000000-25-000001", filed="2025-02-20"),
        "COKE",
    )
    merge_dimensional_per_share_facts(
        facts_json,
        {
            **cover,
            "us-gaap_EarningsPerShareBasic": [
                _fact("7.01", "coke:CommonClassUndefinedMember")
            ],
        },
        _filing(accession="0000000000-26-000002", filed="2026-02-18"),
        "COKE",
    )

    entries = _values(facts_json, "EarningsPerShareBasic", "USD/shares")
    assert [entry["val"] for entry in entries] == [70.10, 7.01]
    assert max(entries, key=lambda entry: entry["filed"])["val"] == 7.01


def test_brk_b_uses_class_b_equivalent_values_without_adding_classes():
    """BRK-B selects its equivalent class instead of summing representations."""
    facts_json = _facts_json(1067983)
    instance_facts = {
        **_cover("us-gaap:CommonClassAMember", "us-gaap:CommonClassBMember"),
        "us-gaap_EarningsPerShareBasic": [
            _fact(17_868, "brka:EquivalentClassAMember"),
            _fact("11.91", "brka:EquivalentClassBMember"),
        ],
        "us-gaap_WeightedAverageNumberOfSharesOutstandingBasic": [
            _fact(1_436_443, "brka:EquivalentClassAMember"),
            _fact(2_154_664_073, "brka:EquivalentClassBMember"),
        ],
    }

    merge_dimensional_per_share_facts(facts_json, instance_facts, _filing(), "BRK.B")

    assert _values(facts_json, "EarningsPerShareBasic", "USD/shares")[0]["val"] == 11.91
    assert (
        _values(facts_json, "WeightedAverageNumberOfSharesOutstandingBasic", "shares")[
            0
        ]["val"]
        == 2_154_664_073
    )
    assert "EarningsPerShareDiluted" not in facts_json["facts"]["us-gaap"]


def test_uhal_b_adds_distributed_and_undistributed_eps():
    """UHAL-B basic EPS combines both two-class-method components."""
    facts_json = _facts_json(4457, start="2026-04-01", end="2026-06-30")
    filing = _filing()
    filing["reportDate"] = "2026-06-30"
    instance_facts = {
        **_cover("us-gaap:CommonClassAMember", "us-gaap:NonvotingCommonStockMember"),
        "us-gaap_EarningsPerShareBasicUndistributed": [
            _fact(
                "0.58",
                "us-gaap:NonvotingCommonStockMember",
                "2026-04-01",
                "2026-06-30",
            )
        ],
        "us-gaap_EarningsPerShareBasicDistributed": [
            _fact(
                "0.05",
                "us-gaap:NonvotingCommonStockMember",
                "2026-04-01",
                "2026-06-30",
            )
        ],
    }

    merge_dimensional_per_share_facts(facts_json, instance_facts, filing, "UHAL-B")

    assert _values(facts_json, "EarningsPerShareBasic", "USD/shares")[0]["val"] == 0.63


def test_class_member_matches_on_member_not_axis():
    """U-Haul moves its voting class onto the equity-components axis.

    In the Sep/Dec 10-Qs the voting class is tagged on
    ``StatementEquityComponentsAxis`` and the company-wide total carries both
    axes.  Matching on the member rather than the axis is what keeps the summed
    total at the real 196,077,880 instead of a single class's 176,470,092.
    """
    facts_json = _facts_json(4457)
    instance_facts = {
        **_cover("us-gaap:CommonStockMember", "us-gaap:NonvotingCommonStockMember"),
        "us-gaap_WeightedAverageNumberOfSharesOutstandingBasic": [
            _fact(
                19_607_788,
                "us-gaap:CommonStockMember",
                axis="StatementEquityComponentsAxis",
            ),
            _fact(176_470_092, "us-gaap:NonvotingCommonStockMember"),
            _multi_axis_fact(
                196_077_880,
                {
                    "StatementClassOfStockAxis": "us-gaap:NonvotingCommonStockMember",
                    "StatementEquityComponentsAxis": "us-gaap:CommonStockMember",
                },
            ),
        ],
    }

    merge_dimensional_per_share_facts(facts_json, instance_facts, _filing(), "UHAL")

    values = _values(
        facts_json, "WeightedAverageNumberOfSharesOutstandingBasic", "shares"
    )
    assert [entry["val"] for entry in values] == [196_077_880]


def test_sum_members_skips_period_with_incomplete_class_coverage():
    """A partial sum must degrade to None rather than a wrong total."""
    facts_json = _facts_json(317540)
    instance_facts = {
        **_cover("coke:CommonClassUndefinedMember", "us-gaap:CommonClassBMember"),
        "us-gaap_WeightedAverageNumberOfSharesOutstandingBasic": [
            _fact(56_517_000, "coke:CommonClassUndefinedMember")
        ],
    }

    added = merge_dimensional_per_share_facts(
        facts_json, instance_facts, _filing(), "COKE"
    )

    assert added == 0
    assert (
        "WeightedAverageNumberOfSharesOutstandingBasic"
        not in facts_json["facts"]["us-gaap"]
    )


def test_unconfigured_cik_is_a_no_op():
    """Issuers without a rule must not be touched."""
    facts_json = _facts_json(320193)
    before = str(facts_json)

    added = merge_dimensional_per_share_facts(
        facts_json,
        {
            **_cover("us-gaap:CommonClassAMember"),
            "us-gaap_EarningsPerShareBasic": [
                _fact("1.23", "us-gaap:CommonClassAMember")
            ],
        },
        _filing(),
        "AAPL",
    )

    assert added == 0
    assert str(facts_json) == before


def test_merge_without_cover_page_is_a_no_op():
    """Without a cover page the class set is unknown, so nothing is synthesized."""
    facts_json = _facts_json(317540)

    added = merge_dimensional_per_share_facts(
        facts_json,
        {
            "us-gaap_EarningsPerShareBasic": [
                _fact("2.39", "coke:CommonClassUndefinedMember")
            ]
        },
        _filing(),
        "COKE",
    )

    assert added == 0


@pytest.mark.parametrize(
    "value", ["NaN", "sNaN", "Infinity", "-Infinity", "junk", None]
)
def test_decimal_value_rejects_non_numeric_and_non_finite(value):
    """``int(value)`` on the shares branch must never see NaN or Infinity."""
    assert _decimal_value(value) is None


def test_select_filings_uses_one_annual_and_four_quarterly_by_default():
    """Quarterly enrichment stays bounded to the useful recent filings."""
    submissions = {
        "filings": {
            "recent": {
                "form": ["10-Q", "10-Q", "10-K", "10-Q", "10-Q", "10-Q"],
                "reportDate": [
                    "2026-06-30",
                    "2026-03-31",
                    "2025-12-31",
                    "2025-09-30",
                    "2025-06-30",
                    "2025-03-31",
                ],
                "filingDate": [
                    "2026-08-01",
                    "2026-05-01",
                    "2026-02-01",
                    "2025-11-01",
                    "2025-08-01",
                    "2025-05-01",
                ],
                "accessionNumber": [f"0000000000-26-00000{i}" for i in range(6)],
                "primaryDocument": [f"filing-{i}.htm" for i in range(6)],
                "isInlineXBRL": [1, 1, 1, 1, 1, 1],
            }
        }
    }

    selected = _select_filings(submissions, "quarterly", None)

    assert len(selected) == 5
    assert sum(record["form"] == "10-K" for record in selected) == 1
    assert sum(record["form"] == "10-Q" for record in selected) == 4
    assert selected == sorted(selected, key=lambda record: record["filingDate"])


def test_select_filings_always_reads_the_newest_annual_for_a_past_fiscal_year():
    """A past-year request must still read the newest 10-K.

    Otherwise the only vintage available is the pre-restatement one and a stock
    split silently changes the value of a fiscal year.
    """
    submissions = {
        "filings": {
            "recent": {
                "form": ["10-K", "10-K", "10-K"],
                "reportDate": ["2025-12-31", "2024-12-31", "2023-12-31"],
                "filingDate": ["2026-02-18", "2025-02-20", "2024-02-22"],
                "accessionNumber": [f"0000000000-2{i}-000001" for i in (6, 5, 4)],
                "primaryDocument": [f"coke-{y}.htm" for y in (2025, 2024, 2023)],
                "isInlineXBRL": [1, 1, 1],
            }
        }
    }

    selected = _select_filings(submissions, "annual", [2024])
    report_dates = [record["reportDate"] for record in selected]

    assert "2025-12-31" in report_dates
    assert "2024-12-31" in report_dates
    assert selected == sorted(selected, key=lambda record: record["filingDate"])


def test_instance_url_uses_sec_extracted_instance_filename():
    """Derive the standard SEC extracted-instance filename."""
    assert _instance_url("0000317540", _filing()) == (
        "https://www.sec.gov/Archives/edgar/data/317540/"
        "000000000026000001/test-20260703_htm.xml"
    )
