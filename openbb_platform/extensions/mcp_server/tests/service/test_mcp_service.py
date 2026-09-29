"""Tests for ``openbb_mcp_server.service.mcp_service``."""

import json

import pytest

from openbb_mcp_server.models.settings import MCPSettings
from openbb_mcp_server.service.mcp_service import MCPService, _merge_nested_dict


@pytest.fixture
def settings_path(tmp_path, monkeypatch):
    """Point the settings file at a temporary path and reset the singleton."""
    path = tmp_path / "mcp_settings.json"
    monkeypatch.setattr(MCPService, "MCP_SETTINGS_PATH", path)
    MCPService._instances.pop(MCPService, None)
    yield path
    MCPService._instances.pop(MCPService, None)


@pytest.fixture
def service(settings_path):
    """Return a fresh ``MCPService`` backed by the temporary settings file."""
    return MCPService()


@pytest.fixture
def clean_env(monkeypatch):
    """Remove every ``OPENBB_MCP_*`` settings alias from the environment."""
    for field in MCPSettings.model_fields.values():
        if field.alias:
            monkeypatch.delenv(field.alias, raising=False)
    return monkeypatch


class TestMCPService:
    """Loading, merging, and persisting MCP settings."""

    def test_first_run_writes_default_settings(self, settings_path, service):
        """Without a settings file the defaults are loaded and written, minus the skills path."""
        expected = MCPSettings().model_dump(mode="json")
        del expected["default_skills_dir"]
        assert service.mcp_settings == MCPSettings()
        assert json.loads(settings_path.read_text()) == expected

    def test_bundled_skills_dir_follows_the_install(self, settings_path, service):
        """A rewritten default file keeps resolving skills from the running install."""
        service.mcp_settings = MCPSettings()
        assert MCPService().refresh_mcp_settings().default_skills_dir == (
            MCPSettings().default_skills_dir
        )
        assert "default_skills_dir" not in json.loads(settings_path.read_text())

    def test_custom_skills_dir_is_persisted(self, settings_path, service, tmp_path):
        """A user-chosen skills directory is written to the settings file."""
        service.mcp_settings = MCPSettings(default_skills_dir=str(tmp_path))
        assert json.loads(settings_path.read_text())["default_skills_dir"] == str(
            tmp_path
        )

    def test_reads_existing_file_with_init_overrides(self, settings_path):
        """An existing file is read, and constructor kwargs override it."""
        settings_path.write_text(json.dumps({"name": "From file", "version": "1"}))
        service = MCPService(version="2")
        assert (service.mcp_settings.name, service.mcp_settings.version) == (
            "From file",
            "2",
        )

    def test_corrupted_file_falls_back_to_defaults(self, settings_path, caplog):
        """An unreadable settings file logs a warning and uses the defaults."""
        settings_path.write_text("this is not json")
        service = MCPService()
        assert service.mcp_settings == MCPSettings()
        assert "Error reading MCP settings file" in caplog.text

    def test_refresh_rereads_the_file(self, settings_path, service):
        """``refresh_mcp_settings`` picks up changes made to the file."""
        settings_path.write_text(json.dumps({"name": "Edited"}))
        assert service.refresh_mcp_settings().name == "Edited"
        assert service.mcp_settings.name == "Edited"

    def test_setter_persists(self, settings_path, service):
        """Assigning ``mcp_settings`` writes the new settings to disk."""
        service.mcp_settings = MCPSettings(name="New settings")
        assert service.mcp_settings.name == "New settings"
        assert json.loads(settings_path.read_text())["name"] == "New settings"

    def test_write_to_file_logs_on_oserror(self, tmp_path, monkeypatch, caplog):
        """A settings path that cannot be created is logged, not raised."""
        blocker = tmp_path / "blocker"
        blocker.write_text("")
        monkeypatch.setattr(MCPService, "MCP_SETTINGS_PATH", blocker / "s.json")
        MCPService.write_to_file(MCPSettings())
        assert "Error writing MCP settings to file" in caplog.text

    def test_load_with_overrides_priority(self, settings_path, service, clean_env):
        """CLI overrides beat environment variables, which beat the file."""
        settings_path.write_text(json.dumps({"name": "File", "version": "1.0"}))
        service.refresh_mcp_settings()
        clean_env.setenv("OPENBB_MCP_NAME", "Env")
        clean_env.setenv("OPENBB_MCP_VERSION", "2.0")

        final = service.load_with_overrides(name="CLI", port=9000)

        assert (final.name, final.version) == ("CLI", "2.0")
        assert final.uvicorn_config == {"host": "127.0.0.1", "port": 9000}
        assert service.mcp_settings is final

    @pytest.mark.usefixtures("clean_env")
    def test_load_with_overrides_without_env_or_cli(self, service):
        """With no environment or CLI overrides the file settings are returned."""
        assert service.load_with_overrides() == service.mcp_settings


@pytest.mark.usefixtures("clean_env")
class TestLoadSettingsFromEnv:
    """Reading settings from ``OPENBB_MCP_*`` environment variables."""

    def test_empty_environment(self):
        """No aliases set yields no overrides."""
        assert MCPService._load_settings_from_env() == {}

    def test_scalar_and_list_values(self, clean_env):
        """Scalars pass through and comma lists are split."""
        clean_env.setenv("OPENBB_MCP_NAME", "Env Test")
        clean_env.setenv("OPENBB_MCP_DEFAULT_TOOL_CATEGORIES", "cat1,cat2")
        assert MCPService._load_settings_from_env() == {
            "name": "Env Test",
            "default_tool_categories": ["cat1", "cat2"],
        }

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ('{"host": "10.0.0.1", "port": 9100}', {"host": "10.0.0.1", "port": 9100}),
            ("host:127.0.0.1,port:9200", {"host": "127.0.0.1", "port": "9200"}),
        ],
        ids=["json", "colon-pairs"],
    )
    def test_dict_values(self, clean_env, raw, expected):
        """Dict fields accept JSON objects and ``key:value`` pairs."""
        clean_env.setenv("OPENBB_MCP_UVICORN_CONFIG", raw)
        assert MCPService._load_settings_from_env() == {"uvicorn_config": expected}

    def test_tuple_value_from_json_list(self, clean_env):
        """Optional tuple fields accept JSON lists."""
        clean_env.setenv("OPENBB_MCP_SERVER_AUTH", '["user", "pass"]')
        assert MCPService._load_settings_from_env() == {"server_auth": ("user", "pass")}

    @pytest.mark.parametrize(
        ("alias", "raw"),
        [
            ("OPENBB_MCP_UVICORN_CONFIG", "{not-json}"),
            ("OPENBB_MCP_UVICORN_CONFIG", "plain"),
            ("OPENBB_MCP_LIST_PAGE_SIZE", "not-an-int"),
        ],
        ids=["bad-json", "not-a-dict", "bad-int"],
    )
    def test_invalid_values_are_logged_and_dropped(self, clean_env, caplog, alias, raw):
        """Values that fail validation log a warning and yield no overrides."""
        clean_env.setenv(alias, raw)
        assert MCPService._load_settings_from_env() == {}
        assert "Error processing environment variables" in caplog.text


class TestMapCliArgsToSettings:
    """Mapping launcher keyword arguments to settings fields."""

    def test_routes_each_kind_of_argument(self):
        """Uvicorn, httpx, aliased, settings, and unknown keys each land in place."""
        mapped = MCPService._map_cli_args_to_settings(
            {
                "host": "10.10.10.10",
                "port": 9000,
                "allowed_categories": "stocks,crypto",
                "tool_discovery": True,
                "system-prompt": "/path/to/prompt.txt",
                "httpx_timeout": 30,
                "version": "1.2",
                "unknown_param": "some_value",
                "transport": "stdio",
                "log_level": None,
            }
        )
        assert mapped == {
            "allowed_tool_categories": "stocks,crypto",
            "enable_tool_discovery": True,
            "system_prompt_file": "/path/to/prompt.txt",
            "version": "1.2",
            "uvicorn_config": {
                "host": "10.10.10.10",
                "port": 9000,
                "unknown_param": "some_value",
            },
            "httpx_client_kwargs": {"timeout": 30},
        }

    def test_empty_arguments(self):
        """No arguments map to no overrides."""
        assert MCPService._map_cli_args_to_settings({}) == {}


class TestMergeNestedDict:
    """Merging nested settings dictionaries."""

    def test_merge_nested_dict_merges_inner_dicts(self):
        """Two-level merge keeps existing inner keys and adds new ones."""
        base = {"uvicorn_config": {"host": "0.0.0.0", "port": 8000}, "name": "a"}  # noqa: S104
        _merge_nested_dict(
            base, {"uvicorn_config": {"port": 9000, "log_level": "debug"}, "name": "b"}
        )
        assert base == {
            "uvicorn_config": {"host": "0.0.0.0", "port": 9000, "log_level": "debug"},  # noqa: S104
            "name": "b",
        }
