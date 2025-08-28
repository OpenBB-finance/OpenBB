"""Configuration service for MCP Server."""

import json
import logging
import os
from pathlib import Path
from typing import Any, Union, get_args, get_origin

from openbb_core.app.constants import OPENBB_DIRECTORY
from openbb_core.app.model.abstract.singleton import SingletonMeta

from openbb_mcp_server.models.settings import MCPSettings


def _merge_nested_dict(base: dict[str, Any], override: dict[str, Any]) -> None:
    """Merge override dict into base dict."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            # Merge nested dictionaries
            base[key].update(value)
        else:
            # Direct replacement for non-dict values or new keys
            base[key] = value


class MCPService(metaclass=SingletonMeta):
    """MCP Service. This class is a singleton.

    Manages the MCP settings and merging with command line arguments.
    It handles loading settings from the ~/.openbb_platform/mcp_settings.json file,
    environment variables, and command-line arguments, giving priority to the latter.

    Priority order (highest to lowest):
        1. Command line arguments (cli_overrides)
        2. Environment variables
        3. Configuration file (already loaded in self._mcp_settings)
        4. Default values (from MCPSettings model)
    """

    MCP_SETTINGS_PATH: Path = OPENBB_DIRECTORY / "mcp_settings.json"

    def __init__(self, **kwargs: Any) -> None:
        """Initialize MCP service, loading settings from the configuration file."""
        self._mcp_settings = self._read_from_file(**kwargs)

    @classmethod
    def _read_from_file(cls, **kwargs: Any) -> MCPSettings:
        """
        Read MCP settings from the configuration file.

        If the file exists, it is loaded and validated.
        Any additional keys present in the file are preserved.
        Keyword arguments can be used to override values defined in the `mcp_settings.json` file.
        """
        settings_dict: dict[str, Any] = {}
        if cls.MCP_SETTINGS_PATH.exists():
            try:
                with cls.MCP_SETTINGS_PATH.open(mode="r", encoding="utf-8") as f:
                    settings_dict = json.load(f)
            except (json.JSONDecodeError, OSError) as e:
                logging.warning(
                    "Error reading MCP settings file at %s: %s. Starting with default settings.",
                    cls.MCP_SETTINGS_PATH,
                    e,
                )
        else:
            logging.info(
                "Creating default MCP settings file at %s", cls.MCP_SETTINGS_PATH
            )
            default_settings = MCPSettings()
            cls.write_to_file(default_settings)
            settings_dict = default_settings.model_dump()

        # kwargs will override values from the file
        settings_dict.update(kwargs)

        return MCPSettings.model_validate(settings_dict)

    @classmethod
    def write_to_file(cls, settings: MCPSettings) -> None:
        """Write MCP settings to the configuration file."""
        try:
            cls.MCP_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
            settings_json = json.dumps(
                settings.model_dump(mode="json"), indent=4, ensure_ascii=False
            )
            with cls.MCP_SETTINGS_PATH.open(mode="w", encoding="utf-8") as f:
                f.write(settings_json)
        except OSError as e:
            logging.error("Error writing MCP settings to file: %s", e)

    @property
    def mcp_settings(self) -> MCPSettings:
        """Get the current MCP settings."""
        return self._mcp_settings

    @mcp_settings.setter
    def mcp_settings(self, settings: MCPSettings) -> None:
        """Set the MCP settings and persist them to the configuration file."""
        self._mcp_settings = settings
        self.write_to_file(settings)

    def refresh_mcp_settings(self) -> MCPSettings:
        """Refresh MCP settings from the configuration file."""
        self._mcp_settings = self._read_from_file()
        return self._mcp_settings

    def load_with_overrides(self, **cli_overrides: Any) -> MCPSettings:
        """
        Load MCP settings with proper priority handling.

        Priority order (highest to lowest):
        1. Command line arguments (cli_overrides)
        2. Environment variables
        3. Configuration file (already loaded in self._mcp_settings)
        4. Default values (from MCPSettings model)

        Returns:
            The combined MCPSettings instance.
        """
        # Start with config file as base
        combined_dict = self._mcp_settings.model_dump()

        # Load and apply environment variable overrides
        env_overrides = self._load_settings_from_env()
        if env_overrides:
            _merge_nested_dict(combined_dict, env_overrides)

        # Map and apply command line overrides
        mapped_cli_overrides = self._map_cli_args_to_settings(cli_overrides)
        if mapped_cli_overrides:
            _merge_nested_dict(combined_dict, mapped_cli_overrides)

        # Create final settings instance and update the service state
        final_settings = MCPSettings(**combined_dict)
        self._mcp_settings = final_settings
        return final_settings

    @staticmethod
    def _load_settings_from_env() -> dict[str, Any]:
        """Load MCP settings from environment variables."""
        env_vars: dict = {}
        for field_name, field_info in MCPSettings.model_fields.items():
            alias = getattr(field_info, "alias", None)
            if alias and alias in os.environ:
                value = os.environ[alias]
                annotation = getattr(field_info, "annotation", None)
                origin = get_origin(annotation)

                is_json_field = False
                if origin in (dict, list, tuple):
                    is_json_field = True
                elif origin is Union:
                    is_json_field = any(
                        get_origin(arg) in (dict, list, tuple)
                        for arg in get_args(annotation)
                    )

                if is_json_field:
                    try:
                        if (value.startswith("{") and value.endswith("}")) or (
                            value.startswith("[") and value.endswith("]")
                        ):
                            env_vars[field_name] = json.loads(value)
                        elif ":" in value and all(
                            ":" in part for part in value.split(",")
                        ):
                            env_vars[field_name] = {
                                k.strip(): v.strip()
                                for k, v in (p.split(":", 1) for p in value.split(","))
                            }
                        else:
                            env_vars[field_name] = value
                    except (json.JSONDecodeError, ValueError):
                        env_vars[field_name] = value
                else:
                    env_vars[field_name] = value

        if not env_vars:
            return {}

        try:
            # Use MCPSettings to validate and process env vars
            temp_settings = MCPSettings(**env_vars)
            return temp_settings.model_dump(exclude_unset=True)
        except Exception as e:
            logging.warning("Error processing environment variables: %s", e)
            return {}

    @staticmethod
    def _map_cli_args_to_settings(server_kwargs: dict[str, Any]) -> dict[str, Any]:
        """
        Map command line arguments to MCPSettings field names.

        This handles the translation between CLI argument names and settings field names,
        and separates out Uvicorn and httpx-specific configurations.
        """
        mcp_settings_fields = set(MCPSettings.model_fields.keys())
        cli_to_settings_map = {
            "allowed_categories": "allowed_tool_categories",
            "default_categories": "default_tool_categories",
            "no_tool_discovery": "enable_tool_discovery",
            "system_prompt": "system_prompt_file",
            "system-prompt": "system_prompt_file",
            "server_prompts": "server_prompts_file",
            "server-prompts": "server_prompts_file",
        }
        uvicorn_fields = {
            "host",
            "port",
            "log_level",
            "debug",
            "uds",
            "fd",
            "workers",
            "loop",
            "http",
            "env_file",
            "log_config",
            "access_log",
            "use_colors",
            "proxy_headers",
            "server_header",
            "date_header",
            "forwarded_allow_ips",
            "ssl_keyfile",
            "ssl_certfile",
            "ssl_keyfile_password",
            "ssl_version",
            "ssl_cert_reqs",
            "ssl_ca_certs",
            "ssl_ciphers",
            "header",
            "version",
        }
        excluded_fields = {"transport"}
        httpx_fields = {k for k in server_kwargs if k.startswith("httpx_")}

        settings_overrides: dict[str, Any] = {}
        uvicorn_config: dict[str, Any] = {}
        httpx_config: dict[str, Any] = {}

        for key, value in server_kwargs.items():
            if key in excluded_fields or value is None:
                continue

            if key in httpx_fields:
                httpx_key = key.replace("httpx_", "", 1)
                httpx_config[httpx_key] = value
            elif key in uvicorn_fields:
                uvicorn_config[key] = value
            elif key in cli_to_settings_map:
                mapped_key = cli_to_settings_map[key]
                if mapped_key == "enable_tool_discovery":
                    settings_overrides[mapped_key] = not value
                else:
                    settings_overrides[mapped_key] = value
            elif key in mcp_settings_fields:
                settings_overrides[key] = value
            else:
                # Fallback for unknown fields to uvicorn_config
                uvicorn_config[key] = value

        if uvicorn_config:
            settings_overrides.setdefault("uvicorn_config", {}).update(uvicorn_config)
        if httpx_config:
            settings_overrides.setdefault("httpx_client_kwargs", {}).update(
                httpx_config
            )

        return settings_overrides
