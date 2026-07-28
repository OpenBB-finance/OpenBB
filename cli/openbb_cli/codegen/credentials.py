"""Credential detection — separate user-facing params from auth secrets."""

from __future__ import annotations

from typing import Any, Literal

CredentialLocation = Literal["query", "header"]

_CREDENTIAL_NAMES: frozenset[str] = frozenset(
    {
        "api_key",
        "api_token",
        "apikey",
        "x_api_key",
        "x_apikey",
        "key",
        "subscription_key",
        "ocp_apim_subscription_key",
        "app_id",
        "app_key",
        "app_token",
        "appid",
        "client_id",
        "client_secret",
        "client_token",
        "token",
        "access_token",
        "auth_token",
        "x_auth_token",
        "bearer_token",
        "secret",
        "secret_key",
        "authorization",
        "consumer_key",
        "consumer_secret",
        "private_key",
        "session_token",
    }
)


def normalize_credential_key(name: str) -> str:
    """Canonicalize a parameter name for credential lookup."""
    return name.lower().replace("-", "_").strip("_")


def is_credential_name(name: str) -> bool:
    """Return ``True`` if ``name`` looks like a credential (not a request param)."""
    return normalize_credential_key(name) in _CREDENTIAL_NAMES


def classify_parameter(param: dict[str, Any]) -> CredentialLocation | None:
    """Return ``"query"`` / ``"header"`` for a credential param, ``None`` otherwise."""
    name = param.get("name") if isinstance(param, dict) else None
    if not isinstance(name, str) or not is_credential_name(name):
        return None
    location = param.get("in", "query")
    return "header" if location == "header" else "query"


def credentials_from_command(
    cmd_spec: dict[str, Any],
) -> dict[str, dict[str, str]]:
    """Walk a command spec entry; return ``{canonical_key: {name, in}}``."""
    out: dict[str, dict[str, str]] = {}
    for param in cmd_spec.get("parameters") or []:
        loc = classify_parameter(param)
        if loc is None:
            continue
        canonical = normalize_credential_key(param["name"])
        out[canonical] = {"name": param["name"], "in": loc}
    return out


def credentials_from_spec(spec_doc: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Aggregate every credential entry across an entire spec doc."""
    out: dict[str, dict[str, str]] = {}
    for cmd in (spec_doc.get("commands") or {}).values():
        for canonical, entry in credentials_from_command(cmd).items():
            out.setdefault(canonical, entry)
    return out


def filter_user_params(parameters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Strip credential params from a parameter list, leaving user-facing ones."""
    return [p for p in parameters or [] if classify_parameter(p) is None]
