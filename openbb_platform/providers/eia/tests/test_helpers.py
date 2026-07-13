"""Tests for the EIA provider helpers."""

import pytest
from openbb_core.app.model.abstract.error import OpenBBError

from openbb_us_eia.utils import helpers


class FakeResponse:
    """Minimal aiohttp-like response."""

    def __init__(self, payload, status=200):
        self.status = status
        self._payload = payload

    async def json(self):
        return self._payload


class TestResponseCallback:
    """API error surfacing in the response callback."""

    @pytest.mark.asyncio
    async def test_returns_payload(self):
        payload = {"response": {"data": []}}
        assert await helpers.response_callback(FakeResponse(payload), None) == payload

    @pytest.mark.asyncio
    async def test_403_raises(self):
        payload = {"error": {"code": "API_KEY_INVALID", "message": "bad key"}}
        with pytest.raises(OpenBBError, match="API_KEY_INVALID -> bad key"):
            await helpers.response_callback(FakeResponse(payload, status=403), None)

    @pytest.mark.asyncio
    async def test_error_payload_raises(self):
        payload = {"error": {"message": "invalid frequency"}}
        with pytest.raises(OpenBBError, match="invalid frequency"):
            await helpers.response_callback(FakeResponse(payload), None)

    @pytest.mark.asyncio
    async def test_plain_error_string_raises(self):
        with pytest.raises(OpenBBError, match="nope"):
            await helpers.response_callback(FakeResponse({"error": "nope"}), None)


class TestDownloadExcelFile:
    """Session caching and error wrapping for Excel downloads."""

    @pytest.mark.asyncio
    async def test_downloads_and_caches(self, monkeypatch):
        from io import BytesIO

        from openbb_core.provider.utils import helpers as core_helpers
        from pandas import DataFrame, ExcelFile

        buffer = BytesIO()
        DataFrame({"a": [1]}).to_excel(buffer, index=False)
        content = buffer.getvalue()
        calls = {"n": 0}

        class RawResponse:
            async def read(self):
                calls["n"] += 1
                return content

        async def fake_amake_request(url, response_callback=None, **kwargs):
            return await response_callback(RawResponse(), None)

        monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
        helpers.download_excel_file.cache_clear()
        first = await helpers.download_excel_file("https://ir.eia.gov/x.xls")
        second = await helpers.download_excel_file("https://ir.eia.gov/x.xls")
        assert isinstance(first, ExcelFile)
        assert second is first
        assert calls["n"] == 1
        third = await helpers.download_excel_file("https://ir.eia.gov/x.xls", False)
        assert calls["n"] == 2
        assert isinstance(third, ExcelFile)

    @pytest.mark.asyncio
    async def test_wraps_download_errors(self, monkeypatch):
        from openbb_core.provider.utils import helpers as core_helpers

        async def fake_amake_request(url, response_callback=None, **kwargs):
            raise ValueError("boom")

        monkeypatch.setattr(core_helpers, "amake_request", fake_amake_request)
        helpers.download_excel_file.cache_clear()
        with pytest.raises(OpenBBError, match="Error downloading the file"):
            await helpers.download_excel_file("https://ir.eia.gov/y.xls")
