"""Gap-fill tests for the remaining branches in query_builder."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from openbb_core.app.model.abstract.error import OpenBBError
from requests.exceptions import HTTPError

from openbb_oecd.utils.metadata import OecdMetadata
from openbb_oecd.utils.query_builder import OecdQueryBuilder, _make_request

_FULL_ID = "DSD_TEST@DF_TEST"
_SHORT_ID = "DF_TEST"


@pytest.fixture
def qb(monkeypatch):
    """Fresh OecdMetadata + builder with one minimal dataflow seeded."""
    OecdMetadata._reset()
    monkeypatch.setattr(OecdMetadata, "_load_from_cache", lambda self: True)
    m = OecdMetadata()
    m.dataflows[_FULL_ID] = {
        "id": _FULL_ID,
        "short_id": _SHORT_ID,
        "agency_id": "OECD",
        "version": "1.0",
        "name": "T",
        "description": "",
        "structure_ref": "",
    }
    m._short_id_map[_SHORT_ID] = _FULL_ID
    m._full_catalogue_loaded = True
    m.datastructures[_FULL_ID] = {
        "dsd_id": "DSD_TEST",
        "agency_id": "OECD",
        "version": "1.0",
        "dimensions": [
            {
                "id": "REF_AREA",
                "position": 1,
                "codelist_id": "OECD:CL_AREA(1.0)",
                "concept_id": "REF_AREA",
                "name": "Reference Area",
            }
        ],
        "attributes": [],
        "has_time_dimension": True,
    }
    m.codelists["OECD:CL_AREA(1.0)"] = {"USA": "United States"}
    builder = OecdQueryBuilder()
    yield builder
    OecdMetadata._reset()


class TestValidateMultiValueBranches:
    """Branches in ``validate_dimension_constraints`` for separators."""

    def test_comma_separator_handled(self, qb):
        qb.metadata.get_constrained_values = MagicMock(
            return_value={"REF_AREA": [{"value": "USA", "label": "USA"}]}
        )
        qb.validate_dimension_constraints(_SHORT_ID, REF_AREA="USA, USA")

    def test_wildcard_only_value_skipped(self, qb):
        qb.metadata.get_constrained_values = MagicMock(
            return_value={"REF_AREA": [{"value": "USA", "label": "USA"}]}
        )
        qb.validate_dimension_constraints(_SHORT_ID, REF_AREA="*")

    def test_dimension_without_entries_skipped(self, qb):
        qb.metadata.get_constrained_values = MagicMock(return_value={"REF_AREA": []})
        qb.validate_dimension_constraints(_SHORT_ID, REF_AREA="ZZZ")


class TestFetchDataErrors:
    """Branches in ``fetch_data`` covering bad responses."""

    def test_validation_invoked_when_not_skipped(self, qb):
        mock_resp = MagicMock()
        mock_resp.text = "REF_AREA,TIME_PERIOD,OBS_VALUE\nUSA,2024,1.0\n"
        with (
            patch.object(qb, "validate_dimension_constraints") as validator,
            patch(
                "openbb_oecd.utils.query_builder._make_request", return_value=mock_resp
            ),
        ):
            qb.fetch_data(_SHORT_ID, REF_AREA="USA")
        validator.assert_called_once()

    def test_csv_parse_failure_raises(self, qb):
        mock_resp = MagicMock()
        mock_resp.text = "REF_AREA,TIME_PERIOD,OBS_VALUE\nUSA,2024,1.0\n"
        with patch(
            "openbb_oecd.utils.query_builder._make_request", return_value=mock_resp
        ):
            with patch("pandas.read_csv", side_effect=ValueError("bad csv")):
                with pytest.raises(OpenBBError, match="Failed to parse"):
                    qb.fetch_data(_SHORT_ID, _skip_validation=True)

    def test_empty_dataframe_raises(self, qb):
        mock_resp = MagicMock()
        mock_resp.text = "REF_AREA,TIME_PERIOD,OBS_VALUE\n"
        with patch(
            "openbb_oecd.utils.query_builder._make_request", return_value=mock_resp
        ):
            with pytest.raises(OpenBBError, match="No data rows"):
                qb.fetch_data(_SHORT_ID, _skip_validation=True)


class TestFallbackPerValueEdges:
    """Branches inside ``_fetch_with_multi_value_fallback`` per-value loop."""

    def test_single_value_request_failure_skipped(self, qb):
        calls = [0]

        def fake(url, **kwargs):
            calls[0] += 1
            if calls[0] == 1:
                err = HTTPError("404")
                err.response = MagicMock(status_code=404)
                raise err
            if calls[0] == 2:
                raise OpenBBError("split request failure")
            resp = MagicMock()
            resp.text = "REF_AREA,TIME_PERIOD,OBS_VALUE\nGBR,2024,1.0\n"
            return resp

        with patch("openbb_oecd.utils.query_builder._make_request", side_effect=fake):
            with patch.object(qb, "build_url", return_value="http://single"):
                text = qb._fetch_with_multi_value_fallback(
                    "http://test",
                    {},
                    _SHORT_ID,
                    None,
                    None,
                    None,
                    {"REF_AREA": "USA+GBR"},
                )
        assert "GBR" in text

    def test_empty_per_value_response_skipped(self, qb):
        calls = [0]

        def fake(url, **kwargs):
            calls[0] += 1
            resp = MagicMock()
            if calls[0] == 1:
                err = HTTPError("404")
                err.response = MagicMock(status_code=404)
                raise err
            if calls[0] == 2:
                resp.text = ""
            else:
                resp.text = "REF_AREA,TIME_PERIOD,OBS_VALUE\nGBR,2024,1.0\n"
            return resp

        with patch("openbb_oecd.utils.query_builder._make_request", side_effect=fake):
            with patch.object(qb, "build_url", return_value="http://single"):
                text = qb._fetch_with_multi_value_fallback(
                    "http://test",
                    {},
                    _SHORT_ID,
                    None,
                    None,
                    None,
                    {"REF_AREA": "USA+GBR"},
                )
        assert "GBR" in text

    def test_all_per_value_requests_fail_raises(self, qb):
        def fake(url, **kwargs):
            err = HTTPError("404")
            err.response = MagicMock(status_code=404)
            raise err

        with patch("openbb_oecd.utils.query_builder._make_request", side_effect=fake):
            with patch.object(qb, "build_url", return_value="http://single"):
                with pytest.raises(OpenBBError, match="failed for all values"):
                    qb._fetch_with_multi_value_fallback(
                        "http://test",
                        {},
                        _SHORT_ID,
                        None,
                        None,
                        None,
                        {"REF_AREA": "USA+GBR"},
                    )


class TestSplitLabelColumnsEdgeBranches:
    """Branches inside ``_split_label_columns``."""

    def test_dimension_with_all_nan_skipped(self, qb):
        df = pd.DataFrame(
            {
                "REF_AREA": pd.array([None, None], dtype="string"),
                "TIME_PERIOD": ["2024", "2025"],
                "OBS_VALUE": [1.0, 2.0],
            }
        )
        result = qb._split_label_columns(df, _SHORT_ID)
        assert "REF_AREA" in result.columns

    def test_single_column_split_label_fallback(self, qb):
        df = pd.DataFrame(
            {
                "REF_AREA": ["USA:"],
                "TIME_PERIOD": ["2024"],
                "OBS_VALUE": [1.0],
            }
        )
        result = qb._split_label_columns(df, _SHORT_ID)
        assert "REF_AREA_label" in result.columns


class TestMakeRequest:
    """The retry-aware ``_make_request`` helper."""

    def test_returns_response_on_success(self):
        session = MagicMock()
        session.send.return_value = MagicMock(
            status_code=200, raise_for_status=lambda: None
        )
        with patch("requests.Session", return_value=session):
            with patch("requests.Request") as req_cls:
                req_cls.return_value.prepare.return_value = MagicMock()
                resp = _make_request("http://x")
        assert resp.status_code == 200

    def test_retries_on_429_then_succeeds(self):
        ok = MagicMock(status_code=200)
        ok.raise_for_status = lambda: None
        rate = MagicMock(status_code=429, headers={"Retry-After": "1"})
        responses = [rate, ok]

        session = MagicMock()
        session.send.side_effect = responses
        with patch("requests.Session", return_value=session):
            with patch("requests.Request") as req_cls:
                req_cls.return_value.prepare.return_value = MagicMock()
                with patch("time.sleep", return_value=None):
                    resp = _make_request("http://x")
        assert resp.status_code == 200

    def test_exhausts_retries_raises(self):
        rate = MagicMock(status_code=429, headers={"Retry-After": "1"})

        def _raise():
            raise HTTPError("429")

        rate.raise_for_status = _raise
        session = MagicMock()
        session.send.return_value = rate
        with patch("requests.Session", return_value=session):
            with patch("requests.Request") as req_cls:
                req_cls.return_value.prepare.return_value = MagicMock()
                with patch("time.sleep", return_value=None):
                    with pytest.raises(HTTPError):
                        _make_request("http://x")
