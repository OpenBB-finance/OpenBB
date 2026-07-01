"""Tests for the DDP catalog and client."""

import re
from unittest.mock import MagicMock

import pytest

from openbb_federal_reserve.utils import ddp

_PACKAGES_H15 = (
    '<input id="FreqRequest_0" type="radio" value="rel=H15&amp;'
    'series=aaaaaaaaaaaaaaaa&amp;type=package" checked="checked" />'
    '<label for="FreqRequest_0">Treasury Constant Maturities [csv, All Obs, 1 KB]'
    "</label>"
    '<option value="rel=H15&amp;series=bbbbbbbbbbbbbbbb&amp;type=package">'
    "Monthly Averages [csv, Last 5 Obs, 1 KB]</option>"
)


def _sdmx(
    period: str = "2024-01-01", value: str = "1.5", periods: list[str] | None = None
) -> str:
    """Build an SDMX document with one or more observations."""
    moments = periods or [period]
    obs = "".join(
        f'<Obs OBS_STATUS="A" OBS_VALUE="{value}" TIME_PERIOD="{p}"/>' for p in moments
    )
    return (
        "<MessageGroup><DataSet>"
        f'<Series SERIES_NAME="X" FREQ="9">{obs}</Series>'
        "</DataSet></MessageGroup>"
    )


_STRUCTURE = (
    "<Structure><CodeLists>"
    '<CodeList id="CL_SA">'
    '<Code value="SA"><Description>Seasonally adjusted</Description></Code>'
    '<Code value="NSA"><Description>Not seasonally adjusted</Description></Code>'
    "</CodeList>"
    '<CodeList id="CL_FREQ">'
    '<Code value="9"><Description>Business day</Description></Code>'
    "</CodeList></CodeLists>"
    "<KeyFamily><Components>"
    '<Dimension concept="SA" codelist="CL_SA"/>'
    '<Attribute concept="FREQ" codelist="CL_FREQ"/>'
    "</Components></KeyFamily></Structure>"
)


def _fake_request(url, *args, **kwargs):
    """Path-aware DDP fake covering the Choose page, payload, and structure file."""
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.status_code = 200
    if "Choose.aspx" in url:
        response.text = _PACKAGES_H15
    elif "_struct.xml" in url:
        response.content = _STRUCTURE.encode()
    else:
        response.content = _sdmx("2024-01-01").encode()
    return response


@pytest.fixture(autouse=True)
def _patch_network(monkeypatch):
    """Route every DDP HTTP call through the path-aware fake."""
    monkeypatch.setattr(
        "openbb_core.provider.utils.helpers.make_request", _fake_request
    )


class TestListReleases:
    """Tests for the fixed release catalog."""

    def test_returns_known_releases_without_network(self, monkeypatch):
        """The catalog is the fixed list and makes no HTTP calls."""

        def _boom(*a, **k):
            raise AssertionError("list_releases must not hit the network")

        monkeypatch.setattr("openbb_core.provider.utils.helpers.make_request", _boom)
        releases = ddp.list_releases()
        codes = {r["code"] for r in releases}
        assert {"H15", "Z1", "SLOOS"} <= codes
        assert "E2" not in codes
        assert all({"dataset", "code", "name"} <= set(r) for r in releases)
        by_code = {r["code"]: r["dataset"] for r in releases}
        assert by_code["H15"] == "H.15"
        assert by_code["H41"] == "H.4.1"


class TestReleasePackages:
    """Tests for ``release_packages``."""

    def test_parses_radio_and_option_layouts(self):
        """Both the radio and option package layouts are parsed."""
        packages = ddp.release_packages("H.15")
        names = [p["name"] for p in packages]
        assert names == ["Treasury Constant Maturities", "Monthly Averages"]
        assert packages[0]["package"] == "aaaaaaaaaaaaaaaa"

    def test_unknown_release_returns_empty(self):
        """An unknown release yields no packages."""
        assert ddp.release_packages("NOPE") == []


class TestListDatasets:
    """Tests for ``list_datasets``."""

    def test_lists_tables_for_release(self):
        """The release's tables are returned with their public dotted code."""
        catalog = ddp.list_datasets("h15")
        assert {d["table"] for d in catalog} == {
            "Treasury Constant Maturities",
            "Monthly Averages",
        }
        assert all(d["dataset"] == "H.15" for d in catalog)


class TestMatchReleaseTitle:
    """Tests for ``match_release_title``."""

    @pytest.mark.parametrize(
        ("title", "expected"),
        [
            ("H.15 - Selected Interest Rates", "H.15"),
            ("H.4.1 - Factors Affecting Reserve Balances", "H.4.1"),
            ("CP- Commercial Paper", "CP"),
            ("Commercial Paper", "CP"),
            (
                "Charge-Off and Delinquency Rates on Loans and Leases at Commercial"
                " Banks",
                "CHGDEL",
            ),
            (
                "Senior Loan Officer Opinion Survey on Bank Lending Practices (SLOOS)",
                "SLOOS",
            ),
            # leading non-DDP codes must not fall through to a same-named release
            ("G.5 - Foreign Exchange Rates", None),
            ("H.3 - Aggregate Reserves of Depository Institutions", None),
            ("Some Unrelated Conference", None),
        ],
    )
    def test_matches_or_rejects(self, title, expected):
        """Titles map to their DDP public code, and non-DDP codes are rejected."""
        assert ddp.match_release_title(title) == expected


class TestFetchReleaseSchedule:
    """Tests for ``fetch_release_schedule``."""

    def test_expands_events_to_dated_rows(self, monkeypatch):
        """Events expand to one matched, dated row per day, sorted by date."""
        import json

        feed = {
            "events": [
                {
                    "title": "H.15 - Selected Interest Rates",
                    "time": "4:15 p.m.",
                    "month": "2026-01",
                    # empty and non-numeric day tokens are skipped
                    "days": "12,5, ,x",
                    "type": "Stat",
                },
                {
                    "title": "G.5 - Foreign Exchange Rates",
                    "time": "4:15 p.m.",
                    "month": "2026-02",
                    "days": "2",
                    "type": "Stat",
                },
                {"title": "", "month": "2026-03", "days": "1", "type": "Stat"},
            ]
        }
        response = MagicMock()
        response.content = json.dumps(feed).encode("utf-8")
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: response,
        )
        rows = ddp.fetch_release_schedule()
        assert [r["date"] for r in rows] == [
            "2026-01-05",
            "2026-01-12",
            "2026-02-02",
        ]
        assert rows[0]["release"] == "H.15"
        assert rows[0]["event_type"] == "Stat"
        # a non-DDP release is listed but not clickable (release is None)
        assert rows[2]["release"] is None


class TestResolveDataset:
    """Tests for ``resolve_dataset``."""

    def test_bare_release_selects_first_table(self):
        """A bare release code selects its first table."""
        assert ddp.resolve_dataset("H.15") == ("H15", "aaaaaaaaaaaaaaaa")

    def test_resolves_table_by_exact_name(self):
        """An explicit table name resolves to that table's package."""
        assert ddp.resolve_dataset("H.15", "Monthly Averages") == (
            "H15",
            "bbbbbbbbbbbbbbbb",
        )

    def test_resolves_table_by_substring(self):
        """A partial table name resolves by case-insensitive substring."""
        assert ddp.resolve_dataset("H15", "treasury") == ("H15", "aaaaaaaaaaaaaaaa")

    def test_unmatched_table_raises(self):
        """A table reference matching nothing raises ``ValueError``."""
        with pytest.raises(ValueError, match="No table matching"):
            ddp.resolve_dataset("H15", "Nonexistent")

    def test_unknown_release_raises(self):
        """An unknown release raises ``ValueError``."""
        with pytest.raises(ValueError, match="Unknown release"):
            ddp.resolve_dataset("not_a_release")

    def test_release_with_no_tables_raises(self, monkeypatch):
        """A valid release that scrapes no packages raises ``ValueError``."""
        monkeypatch.setattr(ddp, "release_packages", lambda code: [])
        with pytest.raises(ValueError, match="No data tables found"):
            ddp.resolve_dataset("H.15")


class TestBuildUrl:
    """Tests for ``build_url``."""

    def test_includes_release_and_package(self):
        """The URL carries the release and package and requests SDMX."""
        url = ddp.build_url("H15", "abc")
        assert "rel=H15" in url and "series=abc" in url and "filetype=sdmx" in url

    def test_fills_missing_end_bound(self):
        """A start without an end fills the wide end sentinel."""
        url = ddp.build_url("H6", "abc", "2024-01-15", None)
        assert "01%2F15%2F2024" in url and "12%2F31%2F2099" in url

    def test_fills_missing_start_bound(self):
        """An end without a start fills the wide start sentinel."""
        url = ddp.build_url("H6", "abc", None, "2024-03-31")
        assert "01%2F01%2F1900" in url and "03%2F31%2F2024" in url


class TestFetchDataset:
    """Tests for ``fetch_dataset`` (download, parse, cache)."""

    def test_downloads_parses_and_caches(self, monkeypatch):
        """The payload is fetched once, parsed to rows, and cached."""
        calls: list[int] = []

        def _counting(url, *a, **k):
            calls.append(1)
            return _fake_request(url, *a, **k)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _counting
        )
        rows = ddp.fetch_dataset("H15", "pkg")
        assert rows == [
            {
                "date": "2024-01-01",
                "series_id": "X",
                "value": 1.5,
                "title": "X",
                "frequency": "Business day",
                "unit": None,
                "unit_multiplier": None,
                "seasonally_adjusted": None,
            }
        ]
        # The data payload and the structure file are each fetched once, then cached.
        ddp.fetch_dataset("H15", "pkg")
        assert calls == [1, 1]

    def test_empty_response_yields_no_rows(self, monkeypatch):
        """An empty body yields no rows rather than a parse error."""
        response = MagicMock()
        response.content = b""
        response.status_code = 200
        response.raise_for_status = MagicMock()
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: response,
        )
        assert ddp.fetch_dataset("H15", "empty") == []


class TestFetchStructure:
    """Tests for ``fetch_structure`` codelist retrieval."""

    def test_parses_codelists(self):
        """The structure file resolves into dimension codelists."""
        codelists = ddp.fetch_structure("H15")
        assert codelists["sa"]["SA"] == "Seasonally adjusted"

    def test_non_200_yields_empty(self, monkeypatch):
        """A non-200 structure response yields an empty mapping."""
        response = MagicMock()
        response.status_code = 404
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request",
            lambda *a, **k: response,
        )
        assert ddp.fetch_structure("ZZ") == {}


class TestLimit:
    """Tests for the ``limit`` (lastNObservations) handling."""

    _PERIODS = ["2024-01-01", "2024-02-01", "2024-03-01"]

    def _multi(self, url, *args, **kwargs):
        """Fake returning three observations, honoring the lastobs parameter."""
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.status_code = 200
        if "Choose.aspx" in url:
            response.text = _PACKAGES_H15
        elif "_struct.xml" in url:
            response.content = _STRUCTURE.encode()
        else:
            periods = self._PERIODS
            match = re.search(r"lastobs=(\d+)", url)
            if match:
                periods = periods[-int(match.group(1)) :]
            response.content = _sdmx(periods=periods).encode()
        return response

    def test_slices_recent_from_cache(self, monkeypatch):
        """With the full series cached, ``limit`` slices it without a new request."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", self._multi
        )
        assert len(ddp.fetch_dataset("H15", "pkg")) == 3

        seen: list[str] = []

        def _counting(url, *args, **kwargs):
            if "Output.aspx" in url:
                seen.append(url)
            return self._multi(url, *args, **kwargs)

        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", _counting
        )
        rows = ddp.fetch_dataset("H15", "pkg", limit=1)
        assert [r["date"] for r in rows] == ["2024-03-01"]
        assert seen == []

    def test_fetches_last_n_when_uncached(self, monkeypatch):
        """Without the full series cached, only the last N observations download."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", self._multi
        )
        rows = ddp.fetch_dataset("H15", "fresh", limit=2)
        assert [r["date"] for r in rows] == ["2024-02-01", "2024-03-01"]

    def test_zero_or_none_limit_returns_full_series(self, monkeypatch):
        """A limit of 0 or None returns the full series, not a slice."""
        monkeypatch.setattr(
            "openbb_core.provider.utils.helpers.make_request", self._multi
        )
        assert len(ddp.fetch_dataset("H15", "zero", limit=0)) == 3
        assert len(ddp.fetch_dataset("H15", "none", limit=None)) == 3


class TestLastNObservations:
    """Tests for the cache-slicing helper."""

    def test_keeps_last_n_per_series(self):
        """Only each series' most recent ``limit`` observations are kept."""
        rows = [
            {"series_id": series, "date": date}
            for series in ("A", "B")
            for date in ("2024-01-01", "2024-02-01", "2024-03-01")
        ]
        trimmed = ddp._last_n_observations(rows, 2)
        assert len(trimmed) == 4
        assert {r["date"] for r in trimmed} == {"2024-02-01", "2024-03-01"}
