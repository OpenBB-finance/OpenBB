"""Credential detection — separate user-facing params from auth secrets.

API keys, app tokens, bearer credentials, and friends shouldn't surface as
``QueryParams`` fields. The OpenBB Platform routes them through
``Provider(credentials=[...])`` and the Fetcher reads them from the
``credentials`` dict at dispatch time.

This module recognizes the common spellings (``api_key``, ``apikey``,
``app_token``, ``X-API-Key``, ``Authorization``, ...) and tells the codegen
which parameter names to demote into the credentials registry.
"""

from __future__ import annotations

from typing import Any, Literal

# Where in the HTTP request a credential lives once registered with the Fetcher.
CredentialLocation = Literal["query", "header"]

# Canonical credential names (compared case- and separator-insensitively).
# Each entry is the lowercased, underscore-normalized form of a name that
# providers commonly use for the same secret.
_CREDENTIAL_NAMES: frozenset[str] = frozenset(
    {
        # API key family
        "api_key",
        "apikey",
        "x_api_key",
        "x_apikey",
        "key",
        "subscription_key",
        "ocp_apim_subscription_key",
        # App / client credentials
        "app_id",
        "app_key",
        "app_token",
        "appid",
        "client_id",
        "client_secret",
        "client_token",
        # Generic tokens
        "token",
        "access_token",
        "auth_token",
        "x_auth_token",
        "bearer_token",
        "secret",
        "secret_key",
        # Bearer / authorization headers
        "authorization",
        # Legacy / vendor-specific
        "consumer_key",
        "consumer_secret",
        "private_key",
        "session_token",
    }
)


def normalize_credential_key(name: str) -> str:
    """Canonicalize a parameter name for credential lookup.

    Lowercases, swaps ``-`` for ``_``, and strips redundant separators so
    ``X-API-Key``, ``api_key``, and ``API-KEY`` all resolve to the same
    canonical key. The returned form is what callers should use as the
    ``credentials`` registry key (sans provider prefix).
    """
    return name.lower().replace("-", "_").strip("_")


def is_credential_name(name: str) -> bool:
    """Return ``True`` if ``name`` looks like a credential (not a request param).

    Matches the canonical credential vocabulary case- and separator-
    insensitively. Used by the codegen to decide whether a parameter ends
    up in ``QueryParams`` (no) or ``Provider(credentials=...)`` (yes).
    """
    return normalize_credential_key(name) in _CREDENTIAL_NAMES


def classify_parameter(param: dict[str, Any]) -> CredentialLocation | None:
    """Return ``"query"`` / ``"header"`` for a credential param, ``None`` otherwise.

    The returned location matches the spec's parameter ``in`` field — the
    Fetcher emitter reads it to know whether to inject the credential as a
    URL query param or as an HTTP header.
    """
    name = param.get("name") if isinstance(param, dict) else None
    if not isinstance(name, str) or not is_credential_name(name):
        return None
    location = param.get("in", "query")
    return "header" if location == "header" else "query"


def credentials_from_command(
    cmd_spec: dict[str, Any],
) -> dict[str, dict[str, str]]:
    """Walk a command spec entry; return ``{canonical_key: {name, in}}``.

    Each entry records the original parameter name (for HTTP transmission)
    and where it goes (``query`` / ``header``). Useful for the Fetcher
    emitter, which needs both the wire-format spelling and the location.
    """
    out: dict[str, dict[str, str]] = {}
    for param in cmd_spec.get("parameters") or []:
        loc = classify_parameter(param)
        if loc is None:
            continue
        canonical = normalize_credential_key(param["name"])
        out[canonical] = {"name": param["name"], "in": loc}
    return out


def credentials_from_spec(spec_doc: dict[str, Any]) -> dict[str, dict[str, str]]:
    """Aggregate every credential entry across an entire spec doc.

    Returns ``{canonical_key: {name, in}}``. When the same canonical key
    appears in multiple commands with different on-the-wire spellings, the
    first occurrence wins — collisions are unlikely in practice (an API
    typically picks one spelling per credential).
    """
    out: dict[str, dict[str, str]] = {}
    for cmd in (spec_doc.get("commands") or {}).values():
        for canonical, entry in credentials_from_command(cmd).items():
            out.setdefault(canonical, entry)
    return out


def filter_user_params(parameters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Strip credential params from a parameter list, leaving user-facing ones.

    Returns a new list — the original is not mutated. Used by the
    QueryParams generator so credentials never appear as command-line
    flags or Pydantic fields.
    """
    return [p for p in parameters or [] if classify_parameter(p) is None]
