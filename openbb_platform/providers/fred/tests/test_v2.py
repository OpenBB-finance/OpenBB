"""Test the FRED v2 transport."""

import pytest


class TestV2Transport:
    """The bearer-authenticated, cursor-paged v2 endpoint."""

    def test_the_key_travels_in_a_header(self):
        from openbb_fred.utils.v2 import headers

        sent = headers("abc")

        assert sent["Authorization"] == "Bearer abc"
        assert sent["Accept-Encoding"] == "gzip, deflate"
        assert "User-Agent" in sent

    async def test_a_series_split_across_pages_is_folded(self, monkeypatch):
        """A cursor can land mid-series, so the halves have to be joined."""
        pages = [
            {
                "has_more": True,
                "next_cursor": "AAA,2026-02-01",
                "release": {"release_id": 1, "name": "One"},
                "series": [
                    {
                        "series_id": "AAA",
                        "title": "A",
                        "observations": [{"date": "2026-01-01", "value": "1"}],
                    }
                ],
            },
            {
                "has_more": False,
                "release": {"release_id": 1, "name": "One"},
                "series": [
                    {
                        "series_id": "AAA",
                        "title": "A",
                        "observations": [{"date": "2026-02-01", "value": "2"}],
                    }
                ],
            },
        ]
        seen: list = []

        async def paged(url, use_cache=True, **kwargs):
            seen.append(url)
            return pages[len(seen) - 1]

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", paged)

        from openbb_fred.utils.v2 import release_observations

        release, series = await release_observations("1", "key")

        assert len(seen) == 2
        assert "next_cursor=AAA%2C2026-02-01" in seen[1]
        assert release["name"] == "One"
        assert len(series["AAA"]["observations"]) == 2

    async def test_a_cursor_that_never_runs_out_stops_at_the_ceiling(self, monkeypatch):
        """A release still answering 'has_more' must not be read without bound."""
        from openbb_fred.utils.v2 import MAX_PAGES, release_observations

        seen: list = []

        async def endless(url, use_cache=True, **kwargs):
            page = len(seen) + 1
            seen.append(url)

            return {
                "has_more": True,
                "next_cursor": f"AAA,page-{page}",
                "release": {"release_id": 1, "name": "One"},
                "series": [
                    {
                        "series_id": "AAA",
                        "title": "A",
                        "observations": [
                            {"date": f"2026-01-{page:02d}", "value": str(page)}
                        ],
                    }
                ],
            }

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", endless)

        release, series = await release_observations("1", "key")

        assert len(seen) == MAX_PAGES
        assert "next_cursor" not in seen[0]
        assert f"next_cursor=AAA%2Cpage-{MAX_PAGES - 1}" in seen[-1]
        assert release["name"] == "One"
        assert len(series["AAA"]["observations"]) == MAX_PAGES
        assert series["AAA"]["observations"][-1] == {
            "date": f"2026-01-{MAX_PAGES:02d}",
            "value": str(MAX_PAGES),
        }

    async def test_a_rejected_request_is_reported(self, monkeypatch):
        from openbb_core.app.model.abstract.error import OpenBBError

        async def refused(url, use_cache=True, **kwargs):
            return {"code": 401, "message": "Missing or invalid credentials."}

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", refused)

        from openbb_fred.utils.v2 import release_observations

        with pytest.raises(OpenBBError, match="Missing or invalid"):
            await release_observations("1", "")

    async def test_a_payload_that_is_not_an_object_ends_the_paging(self, monkeypatch):
        from openbb_core.app.model.abstract.error import OpenBBError

        seen: list = []

        async def unreadable(url, use_cache=True, **kwargs):
            seen.append(url)
            return []

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", unreadable)

        from openbb_fred.utils.v2 import release_observations

        with pytest.raises(OpenBBError, match="No series are published"):
            await release_observations("1", "key")

        assert len(seen) == 1

    async def test_an_empty_release_is_reported(self, monkeypatch):
        from openbb_core.app.model.abstract.error import OpenBBError

        async def nothing(url, use_cache=True, **kwargs):
            return {"has_more": False, "release": {}, "series": []}

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", nothing)

        from openbb_fred.utils.v2 import release_observations

        with pytest.raises(OpenBBError, match="No series are published"):
            await release_observations("999", "key")

    def test_only_published_values_are_kept(self):
        from openbb_fred.utils.v2 import published

        kept = published(
            [
                {"date": "2026-01-01", "value": "1"},
                {"date": "2026-02-01", "value": "."},
                {"date": "2026-03-01", "value": "3"},
            ]
        )

        assert kept == {"2026-01-01": 1.0, "2026-03-01": 3.0}
