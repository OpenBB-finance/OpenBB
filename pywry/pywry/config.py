"""Configuration system for PyWry using pydantic-settings.

Supports layered configuration:
1. Built-in defaults (lowest priority)
2. pyproject.toml [tool.pywry] section (project-level)
3. ./pywry.toml (project-level, explicit)
4. ~/.config/pywry/config.toml (user-level, overrides project)
5. Environment variables (highest priority)

Environment variables use PYWRY_ prefix with nested delimiter __.
Example: PYWRY_CSP__CONNECT_SRC, PYWRY_TIMEOUT__STARTUP
"""

from __future__ import annotations

import os
import sys

from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any, ClassVar, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib  # type: ignore[import-not-found]
    except ImportError:
        tomllib = None


def _find_config_files() -> list[Path]:
    """Find all configuration files in order of precedence (lowest first)."""
    files = []

    # Project-level pyproject.toml [tool.pywry] (lowest file priority)
    pyproject = Path("pyproject.toml")
    if pyproject.exists():
        files.append(pyproject)

    # Explicit pywry.toml (project-level)
    pywry_toml = Path("pywry.toml")
    if pywry_toml.exists():
        files.append(pywry_toml)

    # User-level config (overrides project configs)
    if sys.platform == "win32":
        user_config = Path(os.environ.get("APPDATA", "~")) / "pywry" / "config.toml"
    else:
        user_config = Path("~/.config/pywry/config.toml")
    user_config = user_config.expanduser()
    if user_config.exists():
        files.append(user_config)

    # Environment variable override for config file (highest file priority)
    env_config = os.environ.get("PYWRY_CONFIG_FILE")
    if env_config:
        env_path = Path(env_config)
        if env_path.exists():
            files.append(env_path)

    return files


def _load_toml_config() -> dict[str, Any]:
    """Load and merge all TOML configuration files."""
    if tomllib is None:
        return {}

    merged: dict[str, Any] = {}

    for config_file in _find_config_files():
        try:
            content = config_file.read_text(encoding="utf-8")
            data = tomllib.loads(content)

            # Handle pyproject.toml [tool.pywry] section
            if config_file.name == "pyproject.toml":
                data = data.get("tool", {}).get("pywry", {})

            # Deep merge
            merged = _deep_merge(merged, data)
        except Exception:
            pass  # Silently ignore invalid config files

    return merged


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Deep merge two dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class SecuritySettings(BaseSettings):
    """Content Security Policy settings.

    Environment prefix: PYWRY_CSP__
    Example: PYWRY_CSP__CONNECT_SRC="'self' https://api.example.com"
    """

    model_config = SettingsConfigDict(
        env_prefix="PYWRY_CSP__",
        extra="ignore",
    )

    default_src: str = "'self' 'unsafe-inline' 'unsafe-eval' data: blob:"
    connect_src: str = "'self' http://*:* https://*:* ws://*:* wss://*:* data: blob:"
    script_src: str = "'self' 'unsafe-inline' 'unsafe-eval'"
    style_src: str = "'self' 'unsafe-inline'"
    img_src: str = "'self' http://*:* https://*:* data: blob:"
    font_src: str = "'self' data:"

    def build_csp(self) -> str:
        """Build the complete CSP meta tag content."""
        directives = [
            f"default-src {self.default_src}",
            f"connect-src {self.connect_src}",
            f"script-src {self.script_src}",
            f"style-src {self.style_src}",
            f"img-src {self.img_src}",
            f"font-src {self.font_src}",
        ]
        return "; ".join(directives)

    @classmethod
    def permissive(cls) -> SecuritySettings:
        """Create permissive CSP settings for development mode."""
        return cls()

    @classmethod
    def strict(cls) -> SecuritySettings:
        """Create strict CSP settings for production mode.

        Removes unsafe-eval, restricts to self and specific CDNs.
        """
        return cls(
            default_src="'self' 'unsafe-inline' data: blob:",
            connect_src="'self' data: blob:",
            script_src="'self' 'unsafe-inline'",
            style_src="'self' 'unsafe-inline'",
            img_src="'self' data: blob:",
            font_src="'self' data:",
        )

    @classmethod
    def localhost(cls, ports: list[int] | None = None) -> SecuritySettings:
        """Create localhost-only CSP settings.

        Parameters
        ----------
        ports : list of int or None, optional
            Specific ports to allow. If None, allows all localhost ports.

        Returns
        -------
        SecuritySettings
            Configured security settings for localhost.
        """
        if ports:
            port_list = " ".join(
                f"http://localhost:{p} http://127.0.0.1:{p} ws://localhost:{p} ws://127.0.0.1:{p}"
                for p in ports
            )
            connect = f"'self' {port_list} data: blob:"
        else:
            connect = (
                "'self' http://localhost:* http://127.0.0.1:* "
                "ws://localhost:* ws://127.0.0.1:* data: blob:"
            )

        return cls(
            default_src="'self' 'unsafe-inline' data: blob:",
            connect_src=connect,
            script_src="'self' 'unsafe-inline'",
            style_src="'self' 'unsafe-inline'",
            img_src="'self' http://localhost:* http://127.0.0.1:* data: blob:",
            font_src="'self' data:",
        )


class ThemeSettings(BaseSettings):
    """Theme and styling settings.

    Controls the visual appearance of PyWry windows and widgets.
    The mode setting determines light/dark theme behavior.

    Environment prefix: PYWRY_THEME__
    Example: PYWRY_THEME__MODE=dark
    Example: PYWRY_THEME__CSS_FILE=/path/to/custom.css
    """

    model_config = SettingsConfigDict(
        env_prefix="PYWRY_THEME__",
        extra="ignore",
    )

    mode: Literal["system", "dark", "light"] = Field(
        default="system",
        description="Theme mode: 'system' follows browser/OS preference, 'dark' or 'light' forces theme",
    )
    css_file: str | None = Field(
        default=None,
        description="Path to external CSS file for custom styling",
    )


class TimeoutSettings(BaseSettings):
    """Timeout settings for IPC and subprocess.

    Environment prefix: PYWRY_TIMEOUT__
    Example: PYWRY_TIMEOUT__STARTUP=15.0
    """

    model_config = SettingsConfigDict(
        env_prefix="PYWRY_TIMEOUT__",
        extra="ignore",
    )

    startup: float = Field(default=10.0, ge=1.0, description="Subprocess ready timeout in seconds")
    response: float = Field(default=5.0, ge=0.5, description="IPC response timeout in seconds")
    create_window: float = Field(
        default=5.0, ge=0.5, description="Window creation timeout in seconds"
    )
    set_content: float = Field(default=5.0, ge=0.5, description="Content update timeout in seconds")
    shutdown: float = Field(default=2.0, ge=0.5, description="Graceful shutdown timeout in seconds")


class AssetSettings(BaseSettings):
    """Asset and library settings.

    Environment prefix: PYWRY_ASSET__
    Example: PYWRY_ASSET__PLOTLY_VERSION="3.4.0"
    """

    model_config = SettingsConfigDict(
        env_prefix="PYWRY_ASSET__",
        extra="ignore",
    )

    # Library versions
    plotly_version: str = "3.3.1"
    aggrid_version: str = "35.0.0"

    # Custom asset directory
    path: str = ""

    # Default CSS/JS files to load
    css_files: list[str] = Field(default_factory=list)
    script_files: list[str] = Field(default_factory=list)

    @field_validator("css_files", "script_files", mode="before")
    @classmethod
    def parse_comma_separated(cls, v: Any) -> list[str]:
        """Parse comma-separated strings from env vars."""
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v or []


class LogSettings(BaseSettings):
    """Logging settings.

    Environment prefix: PYWRY_LOG__
    Example: PYWRY_LOG__LEVEL=DEBUG
    """

    model_config = SettingsConfigDict(
        env_prefix="PYWRY_LOG__",
        extra="ignore",
    )

    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
    format: str = "%(name)s - %(levelname)s - %(message)s"


class WindowSettings(BaseSettings):
    """Default window settings.

    These settings correspond to WindowConfig fields and are used
    when creating native windows via the window manager.

    Environment prefix: PYWRY_WINDOW__
    Example: PYWRY_WINDOW__TITLE="My App"
    """

    model_config = SettingsConfigDict(
        env_prefix="PYWRY_WINDOW__",
        extra="ignore",
    )

    # Window basics
    title: str = "PyWry"
    width: int = Field(default=1280, ge=200, description="Window width in pixels")
    height: int = Field(default=720, ge=150, description="Window height in pixels")
    min_width: int = Field(default=400, ge=100, description="Minimum window width")
    min_height: int = Field(default=300, ge=100, description="Minimum window height")

    # Window behavior
    center: bool = Field(default=True, description="Center window on screen")
    resizable: bool = Field(default=True, description="Allow window resizing")
    decorations: bool = Field(
        default=True, description="Show window decorations (title bar, borders)"
    )
    always_on_top: bool = Field(default=False, description="Keep window above others")
    devtools: bool = Field(default=False, description="Open developer tools on start")
    allow_network: bool = Field(default=True, description="Allow network requests")

    # Window close behavior
    on_window_close: Literal["hide", "close"] = Field(
        default="hide",
        description="What happens when user clicks X: 'hide' keeps window alive, 'close' destroys it",
    )

    # Library integration
    enable_plotly: bool = Field(default=False, description="Include Plotly.js in window")
    enable_aggrid: bool = Field(default=False, description="Include AG Grid in window")
    plotly_theme: Literal[
        "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white"
    ] = Field(default="plotly_dark", description="Default Plotly theme")
    aggrid_theme: Literal["quartz", "alpine", "balham", "material"] = Field(
        default="alpine", description="Default AG Grid theme"
    )


class HotReloadSettings(BaseSettings):
    """Hot reload settings.

    Environment prefix: PYWRY_HOT_RELOAD__
    Example: PYWRY_HOT_RELOAD__ENABLED=true
    """

    model_config = SettingsConfigDict(
        env_prefix="PYWRY_HOT_RELOAD__",
        extra="ignore",
    )

    enabled: bool = False
    debounce_ms: int = Field(
        default=100, ge=10, description="Debounce time for file changes in milliseconds"
    )
    css_reload: Literal["inject", "refresh"] = "inject"  # CSS: hot-swap or full reload
    script_reload: Literal["refresh"] = "refresh"  # JS: always full reload
    preserve_scroll: bool = True
    watch_directories: list[str] = Field(default_factory=list)

    @field_validator("watch_directories", mode="before")
    @classmethod
    def parse_comma_separated(cls, v: Any) -> list[str]:
        """Parse comma-separated strings from env vars."""
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v or []


class ServerSettings(BaseSettings):
    """Inline server settings for notebook/web mode.

    Exposes full uvicorn configuration for deployment.

    Environment prefix: PYWRY_SERVER__
    Example: PYWRY_SERVER__PORT=8080
    """

    model_config = SettingsConfigDict(
        env_prefix="PYWRY_SERVER__",
        extra="ignore",
    )

    # Core server settings
    host: str = Field(default="127.0.0.1", description="Server bind address")
    port: int = Field(default=8765, ge=1, le=65535, description="Server port")
    widget_prefix: str = Field(
        default="/widget",
        description="URL prefix for widget routes (e.g., '/widget' -> /widget/{id})",
    )
    auto_start: bool = Field(default=True, description="Auto-start server when needed")
    force_notebook: bool = Field(
        default=False,
        description="Force notebook mode even in headless environments (for web deployments)",
    )

    # Uvicorn settings
    workers: int = Field(default=1, ge=1, description="Number of worker processes")
    log_level: Literal["critical", "error", "warning", "info", "debug", "trace"] = Field(
        default="warning", description="Uvicorn log level"
    )
    access_log: bool = Field(default=False, description="Enable access logging")
    reload: bool = Field(default=False, description="Enable auto-reload (dev mode)")

    # Timeouts
    timeout_keep_alive: int = Field(default=5, ge=0, description="Keep-alive timeout in seconds")
    timeout_graceful_shutdown: int | None = Field(
        default=None, description="Graceful shutdown timeout (None = wait forever)"
    )

    # SSL/TLS settings (for HTTPS)
    ssl_keyfile: str | None = Field(default=None, description="SSL key file path")
    ssl_certfile: str | None = Field(default=None, description="SSL certificate file path")
    ssl_keyfile_password: str | None = Field(default=None, description="SSL key file password")
    ssl_ca_certs: str | None = Field(default=None, description="CA certificates file")

    # CORS settings - use NoDecode to disable JSON parsing and use our validator
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["*"], description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow credentials in CORS")
    cors_allow_methods: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["*"], description="Allowed CORS methods"
    )
    cors_allow_headers: Annotated[list[str], NoDecode] = Field(
        default_factory=lambda: ["*"], description="Allowed CORS headers"
    )

    # Limits
    limit_concurrency: int | None = Field(default=None, description="Max concurrent connections")
    limit_max_requests: int | None = Field(
        default=None, description="Max requests before worker restart"
    )
    backlog: int = Field(default=2048, ge=1, description="Socket backlog size")

    @field_validator("cors_origins", "cors_allow_methods", "cors_allow_headers", mode="before")
    @classmethod
    def parse_comma_separated(cls, v: Any) -> list[str]:
        """Parse comma-separated strings from env vars."""
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        return v or []


class PyWrySettings(BaseSettings):
    """Main settings aggregating all configuration sections.

    Environment prefix: PYWRY__

    Configuration sources (in order of precedence):
    1. Built-in defaults
    2. pyproject.toml [tool.pywry] section
    3. ./pywry.toml (project-level)
    4. ~/.config/pywry/config.toml (user-level, overrides project)
    5. Environment variables (highest priority)
    """

    model_config = SettingsConfigDict(
        env_prefix="PYWRY__",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Nested settings
    csp: SecuritySettings = Field(default_factory=SecuritySettings)
    theme: ThemeSettings = Field(default_factory=ThemeSettings)
    timeout: TimeoutSettings = Field(default_factory=TimeoutSettings)
    asset: AssetSettings = Field(default_factory=AssetSettings)
    log: LogSettings = Field(default_factory=LogSettings)
    window: WindowSettings = Field(default_factory=WindowSettings)
    hot_reload: HotReloadSettings = Field(default_factory=HotReloadSettings)
    server: ServerSettings = Field(default_factory=ServerSettings)

    # Tracks where each value came from (for CLI display)
    _sources: ClassVar[dict[str, str]] = {}

    def __init__(self, **data: Any) -> None:
        # Load TOML configuration first
        toml_config = _load_toml_config()

        # Merge TOML config with explicit data (explicit takes precedence)
        merged = _deep_merge(toml_config, data)

        super().__init__(**merged)

    def to_toml(self) -> str:
        """Export settings as TOML string."""
        lines = ["# PyWry Configuration", "# Generated by: pywry config --toml", ""]

        sections = [
            ("csp", self.csp),
            ("theme", self.theme),
            ("timeout", self.timeout),
            ("asset", self.asset),
            ("log", self.log),
            ("window", self.window),
            ("hot_reload", self.hot_reload),
            ("server", self.server),
        ]

        for section_name, section in sections:
            lines.append(f"[{section_name}]")
            for field_name, field_value in section.model_dump().items():
                if isinstance(field_value, list):
                    value_str = "[" + ", ".join(f'"{v}"' for v in field_value) + "]"
                elif isinstance(field_value, bool):
                    value_str = "true" if field_value else "false"
                elif isinstance(field_value, str):
                    value_str = f'"{field_value}"'
                else:
                    value_str = str(field_value)
                lines.append(f"{field_name} = {value_str}")
            lines.append("")

        return "\n".join(lines)

    def to_env(self) -> str:
        """Export settings as shell environment variables."""
        lines = ["# PyWry Environment Variables", "# Generated by: pywry config --env", ""]

        sections = [
            ("CSP", self.csp),
            ("THEME", self.theme),
            ("TIMEOUT", self.timeout),
            ("ASSET", self.asset),
            ("LOG", self.log),
            ("WINDOW", self.window),
            ("HOT_RELOAD", self.hot_reload),
            ("SERVER", self.server),
        ]

        for section_name, section in sections:
            for field_name, field_value in section.model_dump().items():
                env_name = f"PYWRY_{section_name}__{field_name.upper()}"
                if isinstance(field_value, list):
                    value_str = ",".join(str(v) for v in field_value)
                elif isinstance(field_value, bool):
                    value_str = "true" if field_value else "false"
                else:
                    value_str = str(field_value)
                lines.append(f'export {env_name}="{value_str}"')

        return "\n".join(lines)

    def show(self) -> str:
        """Format settings as a readable table."""
        lines = ["PyWry Configuration", "=" * 60, ""]

        sections = [
            ("Security (CSP)", self.csp),
            ("Theme", self.theme),
            ("Timeouts", self.timeout),
            ("Assets", self.asset),
            ("Logging", self.log),
            ("Window Defaults", self.window),
            ("Hot Reload", self.hot_reload),
            ("Server (Notebook/Web)", self.server),
        ]

        for section_name, section in sections:
            lines.append(f"\n{section_name}")
            lines.append("-" * 40)
            for field_name, field_value in section.model_dump().items():
                # Truncate long values
                value_str = str(field_value)
                if len(value_str) > 50:
                    value_str = value_str[:47] + "..."
                lines.append(f"  {field_name:20} = {value_str}")

        return "\n".join(lines)


@lru_cache(maxsize=1)
def get_settings() -> PyWrySettings:
    """Get the global settings instance (cached).

    Call clear_settings() to reload configuration.
    """
    return PyWrySettings()


def clear_settings() -> None:
    """Clear the cached settings to force reload."""
    get_settings.cache_clear()


def reload_settings() -> PyWrySettings:
    """Reload settings from all sources."""
    clear_settings()
    return get_settings()
