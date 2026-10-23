"""Tests for the Federal Reserve Data Download (DDP) fetcher model."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.utils.errors import EmptyDataError

from openbb_federal_reserve.models.fed_data import (
    FederalReserveDataDownloadData,
    FederalReserveDataDownloadFetcher,
    FederalReserveDataDownloadQueryParams,
)

_ROWS = [
    {
        "date": "2024-02-01",
        "series_id": "B",
        "value": 2.0,
        "title": "Series B",
        "frequency": "daily",
        "unit": "Percent",
        "maturity": "M3",
    },
    {
        "date": "2024-01-01",
        "series_id": "A",
        "value": 1.0,
        "title": "Series A",
        "frequency": "daily",
        "unit": "Percent",
        "maturity": "M1",
    },
]


def _patch_resolve(monkeypatch, release="H15", package="aaaaaaaaaaaaaaaa"):
    """Patch ``resolve_dataset`` to a fixed pair and capture its arguments."""
    captured: dict = {}
    monkeypatch.setattr(
        "openbb_federal_reserve.utils.ddp.resolve_dataset",
        lambda dataset, table: (
            captured.update(dataset=dataset, table=table) or (release, package)
        ),
    )
    return captured


class TestTransformQuery:
    """Tests for ``transform_query``."""

    def test_builds_query_params(self):
        """A literal release code produces validated query params."""
        query = FederalReserveDataDownloadFetcher.transform_query({"dataset": "H.15"})
        assert isinstance(query, FederalReserveDataDownloadQueryParams)
        assert query.dataset == "H.15"
        assert query.table is None


class TestExtractData:
    """Tests for ``extract_data``."""

    def test_fetches_resolved_dataset(self, monkeypatch):
        """A release resolves to a package and returns the fetched rows."""
        _patch_resolve(monkeypatch, "H15", "pkg")
        captured: dict = {}

        def _fetch(release, package, start, end, limit=None):
            captured.update(
                release=release, package=package, start=start, end=end, limit=limit
            )
            return list(_ROWS)

        monkeypatch.setattr("openbb_federal_reserve.utils.ddp.fetch_dataset", _fetch)
        query = FederalReserveDataDownloadFetcher.transform_query(
            {"dataset": "H.15", "limit": 5}
        )
        rows = FederalReserveDataDownloadFetcher.extract_data(query, None)
        assert len(rows) == 2
        assert captured["release"] == "H15"
        assert captured["package"] == "pkg"
        assert captured["limit"] == 5

    def test_limit_defaults_to_latest_observation(self, monkeypatch):
        """With no limit supplied, only the latest observation is requested."""
        _patch_resolve(monkeypatch, "H15", "pkg")
        captured: dict = {}

        def _fetch(release, package, start, end, limit=None):
            captured["limit"] = limit
            return list(_ROWS)

        monkeypatch.setattr("openbb_federal_reserve.utils.ddp.fetch_dataset", _fetch)
        query = FederalReserveDataDownloadFetcher.transform_query({"dataset": "H.15"})
        FederalReserveDataDownloadFetcher.extract_data(query, None)
        assert captured["limit"] == 1

    def test_zero_limit_is_accepted(self, monkeypatch):
        """A limit of 0 is valid and requests the full series."""
        _patch_resolve(monkeypatch, "H15", "pkg")
        captured: dict = {}

        def _fetch(release, package, start, end, limit=None):
            captured["limit"] = limit
            return list(_ROWS)

        monkeypatch.setattr("openbb_federal_reserve.utils.ddp.fetch_dataset", _fetch)
        query = FederalReserveDataDownloadFetcher.transform_query(
            {"dataset": "H.15", "limit": 0}
        )
        FederalReserveDataDownloadFetcher.extract_data(query, None)
        assert captured["limit"] == 0

    def test_series_takes_priority_and_ignores_limit(self, monkeypatch):
        """A selected series fetches its full history (limit forced to None)."""
        _patch_resolve(monkeypatch, "H15", "pkg")
        captured: dict = {}

        def _fetch(release, package, start, end, limit=None):
            captured["limit"] = limit
            return list(_ROWS)

        monkeypatch.setattr("openbb_federal_reserve.utils.ddp.fetch_dataset", _fetch)
        query = FederalReserveDataDownloadFetcher.transform_query(
            {"dataset": "H.15", "series": "A", "limit": 1}
        )
        rows = FederalReserveDataDownloadFetcher.extract_data(query, None)
        assert captured["limit"] is None
        assert all(row["series_id"] == "A" for row in rows)

    def test_table_is_forwarded_to_resolver(self, monkeypatch):
        """The optional table selection is passed through to the resolver."""
        captured = _patch_resolve(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ddp.fetch_dataset",
            lambda *a, **k: list(_ROWS),
        )
        query = FederalReserveDataDownloadFetcher.transform_query(
            {"dataset": "H.15", "table": "Monthly Averages"}
        )
        FederalReserveDataDownloadFetcher.extract_data(query, None)
        assert captured == {"dataset": "H.15", "table": "Monthly Averages"}

    def test_series_filter_subsets_rows(self, monkeypatch):
        """The optional series filter keeps only matching series ids."""
        _patch_resolve(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ddp.fetch_dataset",
            lambda *a, **k: list(_ROWS),
        )
        query = FederalReserveDataDownloadFetcher.transform_query(
            {"dataset": "H.15", "series": "A"}
        )
        rows = FederalReserveDataDownloadFetcher.extract_data(query, None)
        assert {r["series_id"] for r in rows} == {"A"}

    def test_seasonally_adjusted_filter_subsets_rows(self, monkeypatch):
        """The seasonally-adjusted filter keeps only matching rows."""
        _patch_resolve(monkeypatch)
        rows = [
            {"date": "2024-01-01", "series_id": "A", "seasonally_adjusted": True},
            {"date": "2024-01-01", "series_id": "B", "seasonally_adjusted": False},
        ]
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ddp.fetch_dataset",
            lambda *a, **k: list(rows),
        )
        query = FederalReserveDataDownloadFetcher.transform_query(
            {"dataset": "H.15", "seasonally_adjusted": True}
        )
        result = FederalReserveDataDownloadFetcher.extract_data(query, None)
        assert {r["series_id"] for r in result} == {"A"}

    def test_empty_result_raises(self, monkeypatch):
        """An empty fetch raises ``EmptyDataError``."""
        _patch_resolve(monkeypatch)
        monkeypatch.setattr(
            "openbb_federal_reserve.utils.ddp.fetch_dataset", lambda *a, **k: []
        )
        query = FederalReserveDataDownloadFetcher.transform_query({"dataset": "H.15"})
        with pytest.raises(EmptyDataError):
            FederalReserveDataDownloadFetcher.extract_data(query, None)

    def test_resolve_error_raises_openbb_error(self, monkeypatch):
        """A resolver ``ValueError`` is surfaced as an ``OpenBBError``."""

        def _boom(dataset, table):
            raise ValueError("No data tables found.")

        monkeypatch.setattr("openbb_federal_reserve.utils.ddp.resolve_dataset", _boom)
        query = FederalReserveDataDownloadFetcher.transform_query({"dataset": "H.15"})
        with pytest.raises(OpenBBError):
            FederalReserveDataDownloadFetcher.extract_data(query, None)


class TestTransformData:
    """Tests for ``transform_data``."""

    def test_validates_and_sorts(self):
        """Rows validate into the model, sorted by date then series id."""
        result = FederalReserveDataDownloadFetcher.transform_data(None, list(_ROWS))
        assert all(isinstance(r, FederalReserveDataDownloadData) for r in result)
        assert [r.series_id for r in result] == ["A", "B"]

    def test_passes_through_dimension_fields(self):
        """Release-specific dimensions survive as extra model fields."""
        result = FederalReserveDataDownloadFetcher.transform_data(None, list(_ROWS))
        dumped = result[0].model_dump()
        assert dumped["maturity"] == "M1"


class TestWidgetOptions:
    """Tests for the human-readable ``dataset`` dropdown labels."""

    def test_dataset_options_have_human_labels(self):
        """Every release code maps to a human label, not a bare code."""
        codes = set(
            FederalReserveDataDownloadQueryParams.model_fields[
                "dataset"
            ].annotation.__args__
        )
        options = FederalReserveDataDownloadQueryParams.__json_schema_extra__[
            "dataset"
        ]["x-widget_config"]["options"]
        # One labelled option per release code.
        assert {o["value"] for o in options} == codes
        for option in options:
            assert option["label"] and option["label"] != option["value"]
            # The label spells out the release name beyond the bare code.
            assert "—" in option["label"]
