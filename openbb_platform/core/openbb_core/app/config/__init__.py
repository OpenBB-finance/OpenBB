"""Layered configuration discovery for openbb-core.

Mirrors the resolution order ``openbb-cli`` ships with — pyproject →
user-global → project → explicit → .env → real-shell env vars — and
maps the merged result onto the existing ``SystemService`` and
``UserService`` singletons. New code should import from this
subpackage; the legacy ``user_settings.json`` / ``system_settings.json``
disk files keep working unchanged as one layer in the cascade.
"""

from openbb_core.app.config.loader import (
    apply_config_to_services,
    apply_settings_to_env,
    load_config,
    load_env_files,
    load_layered_config,
    render_config_template,
)

__all__ = [
    "apply_config_to_services",
    "apply_settings_to_env",
    "load_config",
    "load_env_files",
    "load_layered_config",
    "render_config_template",
]
