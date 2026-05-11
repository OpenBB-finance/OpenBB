"""Generate the ``providers/<provider_name>/__init__.py`` registration module.

The provider module instantiates a single ``Provider(...)`` with the union
of fetchers emitted by ``fetcher_gen``. Credential names sniffed from the
spec are listed under ``credentials=[...]`` so the OpenBB user-settings
machinery prompts for them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from openbb_cli.codegen.fetcher_gen import GeneratedFetcher


@dataclass
class GeneratedProvider:
    """Output of ``generate_provider_module``.

    Parameters
    ----------
    package_name : str
        Snake-case package name (used as Python import path).
    provider_name : str
        Snake-case provider identifier (matches the directory name).
    source : str
        Full source for ``providers/<provider_name>/__init__.py``.
    credential_keys : list of str
        Canonical credential names declared on the provider (e.g.
        ``["api_key", "authorization"]``). The OpenBB runtime accesses
        them via ``credentials.get(f"{provider_name}_{key}")``.
    """

    package_name: str
    provider_name: str
    source: str
    credential_keys: list[str]


def generate_provider_module(
    package_name: str,
    provider_name: str,
    description: str,
    website: str,
    fetchers: list[GeneratedFetcher],
) -> GeneratedProvider:
    """Render the provider's ``__init__.py``.

    Parameters
    ----------
    package_name : str
        Snake-case top-level package name (e.g. ``"openbb_congress"``).
    provider_name : str
        Snake-case provider identifier (e.g. ``"congress"``).
    description : str
        Provider description shown in OpenBB introspection.
    website : str
        Provider home page URL.
    fetchers : list of GeneratedFetcher
        Per-command fetchers — used to build the ``fetcher_dict`` and to
        union their declared credentials.

    Returns
    -------
    GeneratedProvider
        Module source plus the credential-key list (consumed by the
        ``pyproject.toml`` generator for documentation purposes).
    """
    cred_set: set[str] = set()
    for f in fetchers:
        cred_set.update(f.credentials_used)
    credential_keys = sorted(cred_set)

    parts: list[str] = []
    parts.append(
        f'"""Provider registration for {provider_name} — generated from spec."""'
    )
    parts.append("")
    parts.append("from openbb_core.provider.abstract.provider import Provider")
    parts.append("")

    for f in fetchers:
        parts.append(
            f"from {package_name}.providers.{provider_name}.models."
            f"{f.module_name} import {f.fetcher_class}"
        )
    parts.append("")
    parts.append("")

    fetcher_dict_lines = [f'    "{f.model_name}": {f.fetcher_class},' for f in fetchers]
    if credential_keys:
        cred_repr = (
            "[\n        "
            + ",\n        ".join(repr(k) for k in credential_keys)
            + ",\n    ]"
        )
        cred_block = f"    credentials={cred_repr},\n"
    else:
        cred_block = ""

    parts.append(
        f"{provider_name}_provider = Provider(\n"
        f'    name="{provider_name}",\n'
        f"    description={description!r},\n"
        f"{cred_block}"
        f'    website="{website}",\n'
        "    fetcher_dict={\n" + "\n".join(fetcher_dict_lines) + "\n    },\n)\n"
    )

    return GeneratedProvider(
        package_name=package_name,
        provider_name=provider_name,
        source="\n".join(parts),
        credential_keys=credential_keys,
    )
