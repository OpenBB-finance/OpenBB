"""Unit tests for the IMF maritime chokepoint info and volume models."""

# ruff: noqa: I001

from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_imf.models.maritime_chokepoint_info import (
    ImfMaritimeChokePointInfoData,
    ImfMaritimeChokePointInfoFetcher,
    ImfMaritimeChokePointInfoQueryParams,
)
from openbb_imf.models.maritime_chokepoint_volume import (
    ImfMaritimeChokePointVolumeData,
    ImfMaritimeChokePointVolumeFetcher,
    ImfMaritimeChokePointVolumeQueryParams,
)


class _FakeResponse:
    """Pretend aiohttp ``ClientResponse`` returning a fixed payload/status."""

    def __init__(self, payload: Any, status: int = 200):
        self.status = status
        self._payload = payload

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    async def json(self) -> Any:
        return self._payload


class _AwaitableContext:
    """Wrap a CM so ``await session.get(url)`` works."""

    def __init__(self, ctx):
        self._ctx = ctx

    def __await__(self):
        async def _do():
            return self._ctx

        return _do().__await__()


class _FakeSession:
    """Tiny aiohttp session double with configurable responses."""

    def __init__(self, payload: Any, status: int = 200):
        self._payload = payload
        self._status = status
        self.urls: list[str] = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False

    def get(self, url: str):
        self.urls.append(url)
        return _AwaitableContext(_FakeResponse(self._payload, status=self._status))


def _patch_session(payload: Any, status: int = 200):
    """Return (patcher, fake_session) suitable for ``async with`` use."""
    fake = _FakeSession(payload, status=status)

    class _Factory:
        async def __aenter__(self_):
            return fake

        async def __aexit__(self_, *args):
            return False

    async def _factory(*args, **kwargs):
        return _Factory()

    patcher = patch(
        "openbb_core.provider.utils.helpers.get_async_requests_session",
        side_effect=_factory,
    )
    return patcher, fake


class TestImfMaritimeChokePointInfoFetcher:
    """Tests for ``ImfMaritimeChokePointInfoFetcher``."""

    def test_transform_query_defaults(self):
        """Default theme is ``None``."""
        q = ImfMaritimeChokePointInfoFetcher.transform_query({})
        assert isinstance(q, ImfMaritimeChokePointInfoQueryParams)
        assert q.theme is None

    @pytest.mark.asyncio
    async def test_aextract_data_non_200_raises(self):
        """A non-200 response raises ``OpenBBError`` (covers lines 158, 162-163)."""
        patcher, _ = _patch_session({}, status=500)
        q = ImfMaritimeChokePointInfoFetcher.transform_query({})
        with patcher:
            with pytest.raises(OpenBBError):
                await ImfMaritimeChokePointInfoFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_aextract_data_returns_json_payload(self):
        """A 200 response returns the parsed JSON dict."""
        patcher, _ = _patch_session({"features": []})
        q = ImfMaritimeChokePointInfoFetcher.transform_query({})
        with patcher:
            out = await ImfMaritimeChokePointInfoFetcher.aextract_data(q, None)
        assert out == {"features": []}

    def test_transform_data_missing_features_raises(self):
        """Missing ``features`` raises ``OpenBBError`` (covers line 173)."""
        q = ImfMaritimeChokePointInfoFetcher.transform_query({})
        with pytest.raises(OpenBBError, match="No data found"):
            ImfMaritimeChokePointInfoFetcher.transform_data(q, {})

    def test_transform_data_builds_records(self):
        """A list of features round-trips through the data model."""
        q = ImfMaritimeChokePointInfoFetcher.transform_query({})
        data = {
            "features": [
                {
                    "properties": {
                        "portid": "chokepoint1",
                        "portname": "Suez Canal",
                        "lat": 30.0,
                        "lon": 32.5,
                        "vessel_count_total": 100,
                        "vessel_count_tanker": 30,
                        "vessel_count_container": 30,
                        "vessel_count_general_cargo": 10,
                        "vessel_count_dry_bulk": 25,
                        "vessel_count_RoRo": 5,
                    }
                }
            ]
        }
        out = ImfMaritimeChokePointInfoFetcher.transform_data(q, data)
        assert len(out) == 1
        assert isinstance(out[0], ImfMaritimeChokePointInfoData)
        assert out[0].name == "Suez Canal"
        assert out[0].vessel_count_roro == 5


class TestImfMaritimeChokePointVolumeQueryParams:
    """Tests for the ``chokepoint`` validator."""

    def test_chokepoint_none_returns_none(self):
        """Falsy input becomes ``None`` (covers line 49)."""
        q = ImfMaritimeChokePointVolumeQueryParams(chokepoint=None)
        assert q.chokepoint is None

    def test_chokepoint_comma_separated_valid(self):
        """Two valid choices are kept (covers comma branch 53-66)."""
        q = ImfMaritimeChokePointVolumeQueryParams(chokepoint="suez_canal,panama_canal")
        assert q.chokepoint == "suez_canal,panama_canal"

    def test_chokepoint_comma_separated_invalid_raises(self):
        """An unknown comma-separated value raises (covers lines 58-65)."""
        with pytest.raises(OpenBBError):
            ImfMaritimeChokePointVolumeQueryParams(chokepoint="suez_canal,bogus")

    def test_chokepoint_string_invalid_raises(self):
        """A single unknown value raises (covers line 73)."""
        with pytest.raises(OpenBBError):
            ImfMaritimeChokePointVolumeQueryParams(chokepoint="not_a_chokepoint")

    def test_chokepoint_list_input_resolves_names(self):
        """List inputs resolve through the name lookup (covers lines 88-98)."""
        q = ImfMaritimeChokePointVolumeQueryParams(
            chokepoint=["suez_canal", "chokepoint2", "ignored"]
        )
        assert q.chokepoint == "chokepoint1,chokepoint2"

    def test_chokepoint_invalid_type_raises(self):
        """An int (non-string, non-list) is rejected with ``OpenBBError`` (covers 98-103)."""
        with pytest.raises(OpenBBError):
            ImfMaritimeChokePointVolumeQueryParams(chokepoint=42)


class TestImfMaritimeChokePointVolumeFetcher:
    """Tests for ``ImfMaritimeChokePointVolumeFetcher``."""

    def test_transform_query(self):
        """``transform_query`` builds the model."""
        q = ImfMaritimeChokePointVolumeFetcher.transform_query({})
        assert isinstance(q, ImfMaritimeChokePointVolumeQueryParams)

    @pytest.mark.asyncio
    async def test_aextract_no_chokepoint_uses_all_helper(self):
        """No chokepoint passes to the all-chokepoints helper (covers lines 293-296)."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_all_daily_chokepoint_activity_data",
            new=AsyncMock(return_value=[{"date": "2024-01-01"}]),
        ) as mocked:
            q = ImfMaritimeChokePointVolumeFetcher.transform_query({})
            out = await ImfMaritimeChokePointVolumeFetcher.aextract_data(q, None)
        assert out == [{"date": "2024-01-01"}]
        mocked.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_aextract_no_chokepoint_helper_failure_wraps_error(self):
        """A helper exception is wrapped in ``OpenBBError`` (covers lines 297-298)."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_all_daily_chokepoint_activity_data",
            new=AsyncMock(side_effect=RuntimeError("boom")),
        ):
            q = ImfMaritimeChokePointVolumeFetcher.transform_query({})
            with pytest.raises(OpenBBError):
                await ImfMaritimeChokePointVolumeFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_aextract_per_chokepoint_invalid_id_raises(self):
        """An invalid post-validation id raises ``OpenBBError`` (covers lines 318-321)."""
        q = ImfMaritimeChokePointVolumeFetcher.transform_query(
            {"chokepoint": "suez_canal"}
        )
        object.__setattr__(q, "chokepoint", "not_real")
        with pytest.raises(OpenBBError, match="Invalid chokepoint name"):
            await ImfMaritimeChokePointVolumeFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_aextract_per_chokepoint_exception_propagates(self):
        """Per-task exceptions are raised wrapped in ``OpenBBError`` (covers line 331)."""

        async def boom(*args, **kwargs):
            raise RuntimeError("nope")

        with patch(
            "openbb_imf.utils.port_watch_helpers.get_daily_chokepoint_data",
            new=AsyncMock(side_effect=boom),
        ):
            q = ImfMaritimeChokePointVolumeFetcher.transform_query(
                {"chokepoint": "suez_canal"}
            )
            with pytest.raises(OpenBBError):
                await ImfMaritimeChokePointVolumeFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_aextract_empty_results_raises(self):
        """Empty results raise ``OpenBBError`` (covers line 334)."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_daily_chokepoint_data",
            new=AsyncMock(return_value=[]),
        ):
            q = ImfMaritimeChokePointVolumeFetcher.transform_query(
                {"chokepoint": "suez_canal"}
            )
            with pytest.raises(OpenBBError, match="empty"):
                await ImfMaritimeChokePointVolumeFetcher.aextract_data(q, None)

    @pytest.mark.asyncio
    async def test_aextract_per_chokepoint_returns_rows(self):
        """Per-chokepoint helper output is accumulated."""
        with patch(
            "openbb_imf.utils.port_watch_helpers.get_daily_chokepoint_data",
            new=AsyncMock(return_value=[{"date": "2024-01-01", "portid": "c1"}]),
        ):
            q = ImfMaritimeChokePointVolumeFetcher.transform_query(
                {"chokepoint": "chokepoint1"}
            )
            out = await ImfMaritimeChokePointVolumeFetcher.aextract_data(q, None)
        assert out and out[0]["portid"] == "c1"

    def test_transform_data_builds_records(self):
        """``transform_data`` validates each row through the model."""
        q = ImfMaritimeChokePointVolumeFetcher.transform_query({})
        data = [
            {
                "date": "2024-01-01",
                "portname": "Suez Canal",
                "n_total": 10,
                "n_cargo": 7,
                "n_tanker": 3,
                "n_container": 4,
                "n_general_cargo": 2,
                "n_dry_bulk": 1,
                "n_roro": 0,
                "capacity": 100.0,
                "capacity_cargo": 80.0,
                "capacity_tanker": 20.0,
                "capacity_container": 50.0,
                "capacity_general_cargo": 15.0,
                "capacity_dry_bulk": 10.0,
                "capacity_roro": 5.0,
            }
        ]
        out = ImfMaritimeChokePointVolumeFetcher.transform_data(q, data)
        assert isinstance(out[0], ImfMaritimeChokePointVolumeData)
        assert out[0].chokepoint == "Suez Canal"
