"""Tests for the packaged release map generator."""

import pytest

from openbb_fred.utils import generate_release_map as generator


def _elements(*nodes) -> dict:
    """Return a release tables payload carrying the given elements."""
    return {"elements": {str(i): node for i, node in enumerate(nodes)}}


class TestGet:
    """Reading one endpoint, giving up only after every try."""

    async def test_a_payload_is_returned(self, monkeypatch):
        async def answer(url, **kwargs):
            return {"ok": True}

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)

        assert await generator._get("https://x/a") == {"ok": True}

    async def test_an_empty_payload_reads_as_empty(self, monkeypatch):
        async def answer(url, **kwargs):
            return None

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)

        assert await generator._get("https://x/a") == {}

    async def test_a_failure_is_retried(self, monkeypatch):
        calls: list = []

        async def answer(url, **kwargs):
            calls.append(url)

            if len(calls) < 3:
                raise RuntimeError("boom")

            return {"ok": True}

        async def instant(_):
            return None

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)
        monkeypatch.setattr(generator.asyncio, "sleep", instant)

        assert await generator._get("https://x/a") == {"ok": True}
        assert len(calls) == 3

    async def test_a_node_that_never_answers_reads_as_unknown(
        self, monkeypatch, capsys
    ):
        async def answer(url, **kwargs):
            raise RuntimeError("boom")

        async def instant(_):
            return None

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)
        monkeypatch.setattr(generator.asyncio, "sleep", instant)

        assert await generator._get("https://x/a?b=1&api_key=secret") is None
        assert "secret" not in capsys.readouterr().out

    async def test_a_reader_with_no_tries_reads_nothing(self, monkeypatch):
        calls: list = []

        async def answer(url, **kwargs):
            calls.append(url)
            return {"ok": True}

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)
        monkeypatch.setattr(generator, "TRIES", 0)

        assert await generator._get("https://x/a") is None
        assert calls == []

    async def test_giving_up_takes_every_try(self, monkeypatch):
        calls: list = []

        async def answer(url, **kwargs):
            calls.append(url)
            raise RuntimeError("boom")

        async def instant(_):
            return None

        monkeypatch.setattr("openbb_fred.utils.rate_limiter.fred_get", answer)
        monkeypatch.setattr(generator.asyncio, "sleep", instant)
        await generator._get("https://x/a")

        assert len(calls) == generator.TRIES


class TestElements:
    """The sections and tables directly under one node."""

    async def test_only_sections_and_tables_are_kept(self, monkeypatch):
        async def answer(url):
            return _elements(
                {"element_id": 1, "name": "A", "type": "table"},
                {"element_id": 2, "name": "B", "type": "section"},
                {"element_id": 3, "name": "C", "type": "release"},
            )

        monkeypatch.setattr(generator, "_get", answer)
        found = await generator._elements("abc", "50", None)

        assert [e["element_id"] for e in found] == ["1", "2"]

    async def test_an_element_without_an_id_is_dropped(self, monkeypatch):
        async def answer(url):
            return _elements({"element_id": None, "name": "A", "type": "table"})

        monkeypatch.setattr(generator, "_get", answer)

        assert await generator._elements("abc", "50", None) == []

    async def test_an_empty_element_is_dropped(self, monkeypatch):
        async def answer(url):
            return _elements(None)

        monkeypatch.setattr(generator, "_get", answer)

        assert await generator._elements("abc", "50", None) == []

    async def test_a_node_without_a_name_reads_as_unnamed(self, monkeypatch):
        async def answer(url):
            return _elements({"element_id": 1, "type": "table"})

        monkeypatch.setattr(generator, "_get", answer)

        assert (await generator._elements("abc", "50", None))[0]["name"] == ""

    async def test_an_unreadable_node_reads_as_nothing(self, monkeypatch):
        async def answer(url):
            return None

        monkeypatch.setattr(generator, "_get", answer)

        assert await generator._elements("abc", "50", None) == []

    async def test_the_release_and_element_are_asked_for(self, monkeypatch):
        seen: list = []

        async def answer(url):
            seen.append(url)
            return {}

        monkeypatch.setattr(generator, "_get", answer)
        await generator._elements("abc", "50", "123")

        assert "release_id=50" in seen[0]
        assert "element_id=123" in seen[0]


class TestTree:
    """Walking a release down to the depth the picker offers."""

    async def test_a_flat_release_is_read_at_one_depth(self, monkeypatch):
        async def answer(api_key, release_id, element_id):
            if element_id is not None:
                return []
            return [{"element_id": "1", "name": "A", "type": "table"}]

        monkeypatch.setattr(generator, "_elements", answer)
        found = await generator._tree("abc", "50")

        assert found == [{"element_id": "1", "name": "A", "type": "table", "depth": 0}]

    async def test_a_section_is_followed(self, monkeypatch):
        async def answer(api_key, release_id, element_id):
            if element_id is None:
                return [{"element_id": "1", "name": "A", "type": "section"}]
            if element_id == "1":
                return [{"element_id": "2", "name": "B", "type": "table"}]
            return []

        monkeypatch.setattr(generator, "_elements", answer)
        found = await generator._tree("abc", "50")

        assert [(e["element_id"], e["depth"]) for e in found] == [("1", 0), ("2", 1)]

    async def test_the_walk_stops_at_the_offered_depth(self, monkeypatch):
        async def answer(api_key, release_id, element_id):
            return [{"element_id": "x", "name": "A", "type": "section"}]

        monkeypatch.setattr(generator, "_elements", answer)
        found = await generator._tree("abc", "50")

        assert max(e["depth"] for e in found) == generator.DEPTH


class TestBuild:
    """Resolving every release that is still publishing."""

    @pytest.fixture
    def served(self, monkeypatch):
        """Serve two releases, one of them retired."""

        async def get(url):
            return {
                "releases": [
                    {"id": 50, "name": "Employment Situation"},
                    {"id": 9, "name": "Advance Retail Sales"},
                    {"id": 7, "name": ""},
                ]
            }

        async def release_series(release_id, credentials, **kwargs):
            if release_id == "9":
                return [{"series_id": "RETIRED"}]
            return [{"series_id": f"S{release_id}"}]

        def current(series):
            return series["series_id"] != "RETIRED"

        async def tree(api_key, release_id):
            if release_id == "7":
                return []
            return [
                {"element_id": "1", "name": "A", "type": "table", "depth": 0},
            ]

        monkeypatch.setattr(generator, "_get", get)
        monkeypatch.setattr(generator, "_tree", tree)
        monkeypatch.setattr(
            "openbb_fred.utils.release_tables.release_series", release_series
        )
        monkeypatch.setattr("openbb_fred.utils.release_tables.current", current)

        return generator

    async def test_a_publishing_release_is_kept(self, served):
        resolved = await served.build({"fred_api_key": "abc"})

        assert "50" in resolved
        assert resolved["50"]["name"] == "Employment Situation"

    async def test_a_retired_release_is_dropped(self, served):
        assert "9" not in await served.build({"fred_api_key": "abc"})

    async def test_a_release_without_a_name_takes_its_id(self, served):
        assert (await served.build({"fred_api_key": "abc"}))["7"]["name"] == "7"

    async def test_the_releases_run_in_numeric_order(self, served):
        assert list(await served.build({"fred_api_key": "abc"})) == ["7", "50"]

    async def test_the_elements_are_carried(self, served):
        resolved = await served.build({"fred_api_key": "abc"})

        assert resolved["50"]["elements"][0]["element_id"] == "1"

    async def test_a_release_with_sections_but_no_table_is_reported(
        self, served, monkeypatch, capsys
    ):
        async def tree(api_key, release_id):
            return [{"element_id": "1", "name": "A", "type": "section", "depth": 0}]

        monkeypatch.setattr(generator, "_tree", tree)
        await served.build({"fred_api_key": "abc"})

        assert "sections but no table" in capsys.readouterr().out

    async def test_a_key_is_not_required_to_ask(self, served):
        assert await served.build({})

    async def test_progress_is_reported_every_twenty_five_releases(
        self, monkeypatch, capsys
    ):
        async def get(url):
            return {"releases": [{"id": i, "name": f"R{i}"} for i in range(1, 26)]}

        async def release_series(release_id, credentials, **kwargs):
            return [{"series_id": f"S{release_id}"}]

        def current(series):
            return True

        async def tree(api_key, release_id):
            return [{"element_id": "1", "name": "A", "type": "table", "depth": 0}]

        monkeypatch.setattr(generator, "_get", get)
        monkeypatch.setattr(generator, "_tree", tree)
        monkeypatch.setattr(
            "openbb_fred.utils.release_tables.release_series", release_series
        )
        monkeypatch.setattr("openbb_fred.utils.release_tables.current", current)
        resolved = await generator.build({"fred_api_key": "abc"})

        assert len(resolved) == 25
        assert "[25/25] resolved" in capsys.readouterr().out


class TestMain:
    """Writing the map to the packaged asset."""

    def test_a_key_is_required(self, monkeypatch):
        monkeypatch.setattr(
            "openbb_core.app.service.user_service.UserService",
            _service({}),
        )

        with pytest.raises(SystemExit, match="A FRED API key is required"):
            generator.main()

    def test_the_map_is_written(self, monkeypatch, tmp_path, capsys):
        async def build(credentials):
            return {"50": {"name": "Employment Situation", "elements": [{"a": 1}]}}

        asset = tmp_path / "release_map.json"
        monkeypatch.setattr(
            "openbb_core.app.service.user_service.UserService",
            _service({"fred_api_key": "abc"}),
        )
        monkeypatch.setattr(generator, "build", build)
        monkeypatch.setattr(generator, "ASSET", asset)
        generator.main()

        import json

        assert json.loads(asset.read_text())["50"]["name"] == "Employment Situation"
        assert "1 releases, 1 elements" in capsys.readouterr().out

    @pytest.mark.filterwarnings("ignore:.*found in sys.modules.*:RuntimeWarning")
    def test_running_the_module_as_a_script_builds_the_map(self, monkeypatch):
        import runpy

        monkeypatch.setattr(
            "openbb_core.app.service.user_service.UserService",
            _service({}),
        )

        with pytest.raises(SystemExit, match="A FRED API key is required"):
            runpy.run_module(
                "openbb_fred.utils.generate_release_map", run_name="__main__"
            )


def _service(credentials: dict):
    """Return a stand-in user service carrying the given credentials."""

    class _Credentials:
        def model_dump(self, mode=None):
            return credentials

    class _Settings:
        credentials = _Credentials()

    class _Service:
        default_user_settings = _Settings()

    def service():
        """Return the stand-in service."""
        return _Service()

    return service
