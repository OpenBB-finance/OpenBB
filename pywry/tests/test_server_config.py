"""Tests for ServerSettings and notebook mode configuration."""
# pylint: disable=redefined-outer-name,unused-argument

from __future__ import annotations

import os

import pytest

from pywry.config import (
    PyWrySettings,
    ServerSettings,
    clear_settings,
    get_settings,
)
from pywry.models import WindowMode
from pywry.notebook import (
    NotebookEnvironment,
    clear_environment_cache,
    detect_notebook_environment,
    should_use_inline_rendering,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def clean_settings():
    """Clear settings cache before and after each test."""
    clear_settings()
    clear_environment_cache()
    yield
    clear_settings()
    clear_environment_cache()


@pytest.fixture
def clean_env():
    """Remove all PYWRY_SERVER__ environment variables."""
    # Save and remove all PYWRY_SERVER__ env vars
    env_vars = [k for k in os.environ if k.startswith("PYWRY_SERVER__")]
    old_values = {k: os.environ.pop(k) for k in env_vars}
    clear_settings()
    clear_environment_cache()
    yield
    # Remove any new vars set during test
    for k in list(os.environ.keys()):
        if k.startswith("PYWRY_SERVER__"):
            del os.environ[k]
    # Restore original values
    for k, v in old_values.items():
        os.environ[k] = v
    clear_settings()
    clear_environment_cache()


# =============================================================================
# WindowMode.NOTEBOOK Tests
# =============================================================================


class TestWindowModeNotebook:
    """Tests for WindowMode.NOTEBOOK enum value."""

    def test_notebook_mode_exists(self):
        """NOTEBOOK mode is available in WindowMode enum."""
        assert hasattr(WindowMode, "NOTEBOOK")

    def test_notebook_mode_value(self):
        """NOTEBOOK mode has correct string value."""
        assert WindowMode.NOTEBOOK.value == "notebook"

    def test_notebook_mode_is_string_enum(self):
        """NOTEBOOK mode can be compared to string."""
        assert WindowMode.NOTEBOOK == "notebook"

    def test_all_window_modes(self):
        """All expected window modes are present."""
        modes = [m.value for m in WindowMode]
        assert "new_window" in modes
        assert "single_window" in modes
        assert "multi_window" in modes
        assert "notebook" in modes


# =============================================================================
# ServerSettings Core Tests
# =============================================================================


class TestServerSettingsDefaults:
    """Tests for ServerSettings default values."""

    def test_default_host(self):
        """Default host is localhost."""
        settings = ServerSettings()
        assert settings.host == "127.0.0.1"

    def test_default_port(self):
        """Default port is 8765."""
        settings = ServerSettings()
        assert settings.port == 8765

    def test_default_auto_start(self):
        """Auto-start is enabled by default."""
        settings = ServerSettings()
        assert settings.auto_start is True

    def test_default_force_notebook(self):
        """Force notebook is disabled by default."""
        settings = ServerSettings()
        assert settings.force_notebook is False


class TestServerSettingsCustomValues:
    """Tests for ServerSettings with custom values."""

    def test_custom_host(self):
        """Custom host can be set."""
        settings = ServerSettings(host="0.0.0.0")
        assert settings.host == "0.0.0.0"

    def test_custom_port(self):
        """Custom port can be set."""
        settings = ServerSettings(port=9000)
        assert settings.port == 9000

    def test_custom_force_notebook(self):
        """Force notebook can be enabled."""
        settings = ServerSettings(force_notebook=True)
        assert settings.force_notebook is True


class TestServerSettingsPortValidation:
    """Tests for port validation."""

    def test_port_minimum(self):
        """Port must be at least 1."""
        with pytest.raises(ValueError):
            ServerSettings(port=0)

    def test_port_maximum(self):
        """Port must be at most 65535."""
        with pytest.raises(ValueError):
            ServerSettings(port=65536)

    def test_port_valid_low(self):
        """Port 1 is valid."""
        settings = ServerSettings(port=1)
        assert settings.port == 1

    def test_port_valid_high(self):
        """Port 65535 is valid."""
        settings = ServerSettings(port=65535)
        assert settings.port == 65535


# =============================================================================
# ServerSettings Uvicorn Tests
# =============================================================================


class TestServerSettingsUvicorn:
    """Tests for uvicorn-related settings."""

    def test_default_workers(self):
        """Default workers is 1."""
        settings = ServerSettings()
        assert settings.workers == 1

    def test_default_log_level(self):
        """Default log level is info."""
        settings = ServerSettings()
        assert settings.log_level == "info"

    def test_default_access_log(self):
        """Access log is enabled by default."""
        settings = ServerSettings()
        assert settings.access_log is True

    def test_default_reload(self):
        """Reload is disabled by default."""
        settings = ServerSettings()
        assert settings.reload is False

    def test_default_timeout_keep_alive(self):
        """Default keep-alive timeout is 5 seconds."""
        settings = ServerSettings()
        assert settings.timeout_keep_alive == 5

    def test_default_timeout_graceful_shutdown(self):
        """Default graceful shutdown timeout is None."""
        settings = ServerSettings()
        assert settings.timeout_graceful_shutdown is None

    def test_default_backlog(self):
        """Default backlog is 2048."""
        settings = ServerSettings()
        assert settings.backlog == 2048

    def test_custom_workers(self):
        """Custom workers can be set."""
        settings = ServerSettings(workers=4)
        assert settings.workers == 4

    def test_custom_log_level(self):
        """Custom log level can be set."""
        settings = ServerSettings(log_level="debug")
        assert settings.log_level == "debug"

    def test_valid_log_levels(self):
        """All valid log levels work."""
        for level in ["critical", "error", "warning", "info", "debug", "trace"]:
            settings = ServerSettings(log_level=level)
            assert settings.log_level == level


class TestServerSettingsLimits:
    """Tests for connection limit settings."""

    def test_default_limit_concurrency(self):
        """Default concurrency limit is None (unlimited)."""
        settings = ServerSettings()
        assert settings.limit_concurrency is None

    def test_default_limit_max_requests(self):
        """Default max requests is None (unlimited)."""
        settings = ServerSettings()
        assert settings.limit_max_requests is None

    def test_custom_limit_concurrency(self):
        """Custom concurrency limit can be set."""
        settings = ServerSettings(limit_concurrency=100)
        assert settings.limit_concurrency == 100

    def test_custom_limit_max_requests(self):
        """Custom max requests can be set."""
        settings = ServerSettings(limit_max_requests=1000)
        assert settings.limit_max_requests == 1000


# =============================================================================
# ServerSettings SSL Tests
# =============================================================================


class TestServerSettingsSSL:
    """Tests for SSL/TLS settings."""

    def test_default_ssl_certfile(self):
        """Default SSL certfile is None."""
        settings = ServerSettings()
        assert settings.ssl_certfile is None

    def test_default_ssl_keyfile(self):
        """Default SSL keyfile is None."""
        settings = ServerSettings()
        assert settings.ssl_keyfile is None

    def test_default_ssl_keyfile_password(self):
        """Default SSL keyfile password is None."""
        settings = ServerSettings()
        assert settings.ssl_keyfile_password is None

    def test_default_ssl_ca_certs(self):
        """Default CA certs is None."""
        settings = ServerSettings()
        assert settings.ssl_ca_certs is None

    def test_custom_ssl_certfile(self):
        """Custom SSL certfile can be set."""
        settings = ServerSettings(ssl_certfile="/path/to/cert.pem")
        assert settings.ssl_certfile == "/path/to/cert.pem"

    def test_custom_ssl_keyfile(self):
        """Custom SSL keyfile can be set."""
        settings = ServerSettings(ssl_keyfile="/path/to/key.pem")
        assert settings.ssl_keyfile == "/path/to/key.pem"

    def test_custom_ssl_keyfile_password(self):
        """Custom SSL keyfile password can be set."""
        settings = ServerSettings(ssl_keyfile_password="secret")
        assert settings.ssl_keyfile_password == "secret"


# =============================================================================
# ServerSettings CORS Tests
# =============================================================================


class TestServerSettingsCORS:
    """Tests for CORS settings."""

    def test_default_cors_origins(self):
        """Default CORS origins allows all."""
        settings = ServerSettings()
        assert settings.cors_origins == ["*"]

    def test_default_cors_allow_credentials(self):
        """CORS credentials are allowed by default."""
        settings = ServerSettings()
        assert settings.cors_allow_credentials is True

    def test_default_cors_allow_methods(self):
        """Default CORS methods allows all."""
        settings = ServerSettings()
        assert settings.cors_allow_methods == ["*"]

    def test_default_cors_allow_headers(self):
        """Default CORS headers allows all."""
        settings = ServerSettings()
        assert settings.cors_allow_headers == ["*"]

    def test_custom_cors_origins_list(self):
        """Custom CORS origins can be set as list."""
        settings = ServerSettings(cors_origins=["https://example.com", "https://api.example.com"])
        assert settings.cors_origins == ["https://example.com", "https://api.example.com"]

    def test_cors_origins_from_comma_string(self):
        """CORS origins can be parsed from comma-separated string."""
        settings = ServerSettings(cors_origins="https://a.com,https://b.com")
        assert settings.cors_origins == ["https://a.com", "https://b.com"]

    def test_cors_origins_strips_whitespace(self):
        """CORS origins strips whitespace from comma-separated string."""
        settings = ServerSettings(cors_origins="https://a.com , https://b.com")
        assert settings.cors_origins == ["https://a.com", "https://b.com"]

    def test_cors_methods_from_comma_string(self):
        """CORS methods can be parsed from comma-separated string."""
        settings = ServerSettings(cors_allow_methods="GET,POST,PUT")
        assert settings.cors_allow_methods == ["GET", "POST", "PUT"]

    def test_cors_headers_from_comma_string(self):
        """CORS headers can be parsed from comma-separated string."""
        settings = ServerSettings(cors_allow_headers="Content-Type,Authorization")
        assert settings.cors_allow_headers == ["Content-Type", "Authorization"]


# =============================================================================
# Environment Variable Tests
# =============================================================================


class TestServerSettingsEnvVars:
    """Tests for ServerSettings via environment variables."""

    def test_host_from_env(self, clean_env):
        """Host can be set via environment variable."""
        os.environ["PYWRY_SERVER__HOST"] = "0.0.0.0"
        settings = ServerSettings()
        assert settings.host == "0.0.0.0"

    def test_port_from_env(self, clean_env):
        """Port can be set via environment variable."""
        os.environ["PYWRY_SERVER__PORT"] = "9000"
        settings = ServerSettings()
        assert settings.port == 9000

    def test_force_notebook_from_env_true(self, clean_env):
        """Force notebook can be set to true via env."""
        os.environ["PYWRY_SERVER__FORCE_NOTEBOOK"] = "true"
        settings = ServerSettings()
        assert settings.force_notebook is True

    def test_force_notebook_from_env_false(self, clean_env):
        """Force notebook can be set to false via env."""
        os.environ["PYWRY_SERVER__FORCE_NOTEBOOK"] = "false"
        settings = ServerSettings()
        assert settings.force_notebook is False

    def test_log_level_from_env(self, clean_env):
        """Log level can be set via environment variable."""
        os.environ["PYWRY_SERVER__LOG_LEVEL"] = "debug"
        settings = ServerSettings()
        assert settings.log_level == "debug"

    def test_cors_origins_from_env(self, clean_env):
        """CORS origins can be set via environment variable."""
        os.environ["PYWRY_SERVER__CORS_ORIGINS"] = "https://a.com,https://b.com"
        settings = ServerSettings()
        assert settings.cors_origins == ["https://a.com", "https://b.com"]

    def test_ssl_certfile_from_env(self, clean_env):
        """SSL certfile can be set via environment variable."""
        os.environ["PYWRY_SERVER__SSL_CERTFILE"] = "/path/to/cert.pem"
        settings = ServerSettings()
        assert settings.ssl_certfile == "/path/to/cert.pem"

    def test_workers_from_env(self, clean_env):
        """Workers can be set via environment variable."""
        os.environ["PYWRY_SERVER__WORKERS"] = "4"
        settings = ServerSettings()
        assert settings.workers == 4


# =============================================================================
# PyWrySettings Integration Tests
# =============================================================================


class TestPyWrySettingsServer:
    """Tests for server settings in PyWrySettings."""

    def test_has_server_settings(self):
        """PyWrySettings has server attribute."""
        settings = PyWrySettings()
        assert hasattr(settings, "server")
        assert isinstance(settings.server, ServerSettings)

    def test_server_default_host(self):
        """Server host default via PyWrySettings."""
        settings = PyWrySettings()
        assert settings.server.host == "127.0.0.1"

    def test_server_default_port(self):
        """Server port default via PyWrySettings."""
        settings = PyWrySettings()
        assert settings.server.port == 8765

    def test_server_custom_values(self):
        """Server settings can be customized."""
        settings = PyWrySettings(server=ServerSettings(host="0.0.0.0", port=9000))
        assert settings.server.host == "0.0.0.0"
        assert settings.server.port == 9000

    def test_server_from_dict(self):
        """Server settings can be passed as dict."""
        settings = PyWrySettings(server={"host": "0.0.0.0", "port": 9000})
        assert settings.server.host == "0.0.0.0"
        assert settings.server.port == 9000


class TestPyWrySettingsServerExport:
    """Tests for server settings in export methods."""

    def test_server_in_toml_export(self):
        """Server settings appear in TOML export."""
        settings = PyWrySettings()
        toml = settings.to_toml()
        assert "[server]" in toml
        assert "host" in toml
        assert "port" in toml

    def test_server_in_env_export(self):
        """Server settings appear in env export."""
        settings = PyWrySettings()
        env = settings.to_env()
        assert "PYWRY_SERVER__HOST" in env
        assert "PYWRY_SERVER__PORT" in env

    def test_server_in_show_output(self):
        """Server settings appear in show output."""
        settings = PyWrySettings()
        output = settings.show()
        assert "Server" in output
        assert "host" in output
        assert "port" in output


class TestGetSettings:
    """Tests for get_settings() singleton."""

    def test_returns_settings(self, clean_env):
        """get_settings returns PyWrySettings."""
        settings = get_settings()
        assert isinstance(settings, PyWrySettings)

    def test_has_server(self, clean_env):
        """get_settings().server is available."""
        settings = get_settings()
        assert isinstance(settings.server, ServerSettings)

    def test_server_env_override(self, clean_env):
        """Environment variables override server settings."""
        os.environ["PYWRY_SERVER__PORT"] = "9999"
        clear_settings()
        settings = get_settings()
        assert settings.server.port == 9999


# =============================================================================
# Notebook Detection with force_notebook
# =============================================================================


class TestForceNotebookDetection:
    """Tests for force_notebook in notebook detection."""

    def test_force_notebook_enables_inline(self, clean_env):
        """force_notebook=True enables inline rendering."""
        os.environ["PYWRY_SERVER__FORCE_NOTEBOOK"] = "true"
        clear_settings()
        clear_environment_cache()
        assert should_use_inline_rendering() is True

    def test_no_force_notebook_in_terminal(self, clean_env):
        """Without force_notebook, terminal doesn't use inline."""
        clear_settings()
        clear_environment_cache()
        # In pytest, we're not in a notebook
        env = detect_notebook_environment()
        if env == NotebookEnvironment.NONE:
            assert should_use_inline_rendering() is False

    def test_force_notebook_overrides_detection(self, clean_env):
        """force_notebook overrides notebook detection."""
        os.environ["PYWRY_SERVER__FORCE_NOTEBOOK"] = "true"
        clear_settings()
        clear_environment_cache()
        # Even if not in notebook, force_notebook makes it return True
        assert should_use_inline_rendering() is True


# =============================================================================
# Integration Tests (mocked inline module)
# =============================================================================


class TestInlineServerConfig:
    """Tests for inline.py server configuration integration."""

    def test_start_server_uses_settings(self, clean_env):
        """_start_server uses settings for default port/host."""
        # Verify settings are accessible
        settings = get_settings()
        assert settings.server.port == 8765
        assert settings.server.host == "127.0.0.1"

    def test_cors_settings_available(self, clean_env):
        """CORS settings are available for middleware."""
        settings = get_settings()
        assert settings.server.cors_origins == ["*"]
        assert settings.server.cors_allow_credentials is True
        assert settings.server.cors_allow_methods == ["*"]
        assert settings.server.cors_allow_headers == ["*"]

    def test_ssl_settings_available(self, clean_env):
        """SSL settings are available for uvicorn config."""
        settings = get_settings()
        assert settings.server.ssl_certfile is None
        assert settings.server.ssl_keyfile is None

    def test_custom_cors_via_env(self, clean_env):
        """Custom CORS origins via environment."""
        os.environ["PYWRY_SERVER__CORS_ORIGINS"] = "https://myapp.com"
        clear_settings()
        settings = get_settings()
        assert settings.server.cors_origins == ["https://myapp.com"]


# =============================================================================
# WebSocket Security Settings Tests
# =============================================================================


class TestWebSocketSecurityDefaults:
    """Tests for WebSocket security settings defaults."""

    def test_default_allowed_origins_empty(self):
        """Default allowed origins is empty list (allow any, rely on token)."""
        settings = ServerSettings()
        assert settings.websocket_allowed_origins == []

    def test_default_require_token_true(self):
        """Token auth is enabled by default."""
        settings = ServerSettings()
        assert settings.websocket_require_token is True

    def test_default_internal_api_header(self):
        """Default internal API header name."""
        settings = ServerSettings()
        assert settings.internal_api_header == "X-PyWry-Token"

    def test_default_internal_api_token_none(self):
        """Internal API token defaults to None (auto-generated)."""
        settings = ServerSettings()
        assert settings.internal_api_token is None

    def test_default_strict_widget_auth_false(self):
        """Strict widget auth is disabled by default (notebook mode)."""
        settings = ServerSettings()
        assert settings.strict_widget_auth is False


class TestWebSocketSecurityCustom:
    """Tests for WebSocket security settings custom values."""

    def test_custom_allowed_origins_list(self):
        """Allowed origins can be set as list."""
        origins = ["http://localhost:8080", "https://app.example.com"]
        settings = ServerSettings(websocket_allowed_origins=origins)
        assert settings.websocket_allowed_origins == origins

    def test_custom_allowed_origins_comma_string(self):
        """Allowed origins can be parsed from comma-separated string."""
        settings = ServerSettings(websocket_allowed_origins="http://a.com,https://b.com")
        assert settings.websocket_allowed_origins == ["http://a.com", "https://b.com"]

    def test_disable_token_auth(self):
        """Token auth can be disabled."""
        settings = ServerSettings(websocket_require_token=False)
        assert settings.websocket_require_token is False

    def test_custom_internal_api_header(self):
        """Custom internal API header name."""
        settings = ServerSettings(internal_api_header="X-Custom-Auth")
        assert settings.internal_api_header == "X-Custom-Auth"

    def test_custom_internal_api_token(self):
        """Custom internal API token."""
        settings = ServerSettings(internal_api_token="my-secret-token")
        assert settings.internal_api_token == "my-secret-token"

    def test_enable_strict_widget_auth(self):
        """Strict widget auth can be enabled (browser mode)."""
        settings = ServerSettings(strict_widget_auth=True)
        assert settings.strict_widget_auth is True


class TestWebSocketSecurityEnvVars:
    """Tests for WebSocket security via environment variables."""

    def test_allowed_origins_from_env(self, clean_env):
        """Allowed origins from environment variable."""
        os.environ["PYWRY_SERVER__WEBSOCKET_ALLOWED_ORIGINS"] = (
            "http://localhost:8080,https://app.example.com"
        )
        settings = ServerSettings()
        assert settings.websocket_allowed_origins == [
            "http://localhost:8080",
            "https://app.example.com",
        ]

    def test_require_token_from_env(self, clean_env):
        """Token auth from environment variable."""
        os.environ["PYWRY_SERVER__WEBSOCKET_REQUIRE_TOKEN"] = "false"
        settings = ServerSettings()
        assert settings.websocket_require_token is False

    def test_internal_api_header_from_env(self, clean_env):
        """Internal API header from environment variable."""
        os.environ["PYWRY_SERVER__INTERNAL_API_HEADER"] = "X-My-Auth"
        settings = ServerSettings()
        assert settings.internal_api_header == "X-My-Auth"

    def test_internal_api_token_from_env(self, clean_env):
        """Internal API token from environment variable."""
        os.environ["PYWRY_SERVER__INTERNAL_API_TOKEN"] = "env-secret-token"
        settings = ServerSettings()
        assert settings.internal_api_token == "env-secret-token"

    def test_strict_widget_auth_from_env(self, clean_env):
        """Strict widget auth from environment variable."""
        os.environ["PYWRY_SERVER__STRICT_WIDGET_AUTH"] = "true"
        settings = ServerSettings()
        assert settings.strict_widget_auth is True


# =============================================================================
# Edge Cases
# =============================================================================


class TestServerSettingsEdgeCases:
    """Edge case tests for ServerSettings."""

    def test_empty_cors_origins(self):
        """Empty CORS origins list."""
        settings = ServerSettings(cors_origins=[])
        assert settings.cors_origins == []

    def test_empty_string_cors_origins(self):
        """Empty string for CORS origins."""
        settings = ServerSettings(cors_origins="")
        assert settings.cors_origins == []

    def test_single_cors_origin(self):
        """Single CORS origin as string."""
        settings = ServerSettings(cors_origins="https://example.com")
        assert settings.cors_origins == ["https://example.com"]

    def test_workers_minimum(self):
        """Workers must be at least 1."""
        with pytest.raises(ValueError):
            ServerSettings(workers=0)

    def test_backlog_minimum(self):
        """Backlog must be at least 1."""
        with pytest.raises(ValueError):
            ServerSettings(backlog=0)

    def test_timeout_keep_alive_minimum(self):
        """Keep-alive timeout must be at least 0."""
        settings = ServerSettings(timeout_keep_alive=0)
        assert settings.timeout_keep_alive == 0

    def test_none_cors_becomes_empty(self):
        """None for CORS fields becomes empty list."""
        settings = ServerSettings(cors_origins=None)
        assert settings.cors_origins == []

    def test_empty_allowed_origins(self):
        """Empty allowed origins list."""
        settings = ServerSettings(websocket_allowed_origins=[])
        assert settings.websocket_allowed_origins == []

    def test_empty_string_allowed_origins(self):
        """Empty string for allowed origins."""
        settings = ServerSettings(websocket_allowed_origins="")
        assert settings.websocket_allowed_origins == []

    def test_none_allowed_origins_becomes_empty(self):
        """None for allowed origins becomes empty list."""
        settings = ServerSettings(websocket_allowed_origins=None)
        assert settings.websocket_allowed_origins == []
