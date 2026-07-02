"""Generate router modules that mirror the spec's hierarchical namespace."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from openbb_cli.codegen.namespace_tree import NamespaceNode

if TYPE_CHECKING:
    from openbb_cli.codegen.fetcher_gen import GeneratedFetcher
    from openbb_cli.codegen.post_gen import GeneratedPostCommand


@dataclass
class GeneratedRouter:
    """One router module emitted by ``generate_routers``.

    Parameters
    ----------
    module_name : str
        Snake-case module filename without ``.py``.
    entry_point_name : str | None
        When set, this router is registered as an ``openbb_core_extension`` entry point.
    source : str
        Full module source ready to write to ``routers/<module_name>.py``.
    """

    module_name: str
    entry_point_name: str | None
    source: str


@dataclass
class GeneratedRouters:
    """Collection of router modules covering every namespace in the tree.

    Parameters
    ----------
    routers : list of GeneratedRouter
        All emitted router modules.
    """

    routers: list[GeneratedRouter] = field(default_factory=list)


def _safe_segment(name: str) -> str:
    """Lower-case + replace non-alphanumerics with underscores."""
    cleaned = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_")
    return cleaned.lower() or "ns"


def _module_name_for(path: str) -> str:
    """Convert a dotted namespace path to a router module name.

    Parameters
    ----------
    path : str
        Dotted namespace path.

    Returns
    -------
    str
        Snake-case module identifier.
    """
    return "_".join(_safe_segment(p) for p in path.split(".") if p)


def _model_name_for(path: str) -> str:
    """Convert a dotted command path to a CamelCase model identifier."""
    return "".join(
        seg[:1].upper() + seg[1:]
        for seg in (re.split(r"[^0-9a-zA-Z]+", part) for part in path.split("."))
        for seg in seg
        if seg
    )


def generate_routers(
    root: NamespaceNode,
    *,
    package_name: str,
    provider_name: str,
    fetchers_by_command: dict[str, GeneratedFetcher],
    post_commands_by_command: dict[str, GeneratedPostCommand],
) -> GeneratedRouters:
    """Emit router modules for every namespace in ``root``.

    Parameters
    ----------
    root : NamespaceNode
        The synthetic root node returned by ``build_namespace_tree``.
    package_name : str
        Top-level Python package name.
    provider_name : str
        Snake-case provider identifier.
    fetchers_by_command : dict
        Map ``{dotted_command: GeneratedFetcher}`` for every GET command.
    post_commands_by_command : dict
        Map ``{dotted_command: GeneratedPostCommand}`` for every POST command.

    Returns
    -------
    GeneratedRouters
        One ``GeneratedRouter`` per namespace node.
    """
    out = GeneratedRouters()
    for top_name, top_node in sorted(root.children.items()):
        _emit_router(
            top_node,
            package_name=package_name,
            provider_name=provider_name,
            fetchers_by_command=fetchers_by_command,
            post_commands_by_command=post_commands_by_command,
            collected=out,
            is_top_level=True,
        )
    return out


def _emit_router(
    node: NamespaceNode,
    *,
    package_name: str,
    provider_name: str,
    fetchers_by_command: dict[str, GeneratedFetcher],
    post_commands_by_command: dict[str, GeneratedPostCommand],
    collected: GeneratedRouters,
    is_top_level: bool,
) -> str:
    """Recursively emit one router module per namespace node.

    Parameters
    ----------
    node : NamespaceNode
        The namespace this call emits a router for.
    package_name : str
        Top-level Python package name.
    provider_name : str
        Provider identifier for ``providers/<name>/`` imports.
    fetchers_by_command : dict
        GET-command fetcher modules.
    post_commands_by_command : dict
        POST-command modules.
    collected : GeneratedRouters
        Output accumulator.
    is_top_level : bool
        Whether this namespace is at the top of the tree.

    Returns
    -------
    str
        The module name of the emitted router.
    """
    module_name = _module_name_for(node.full_path)
    parts: list[str] = []
    parts.append(f'"""Router for {node.full_path} commands — generated from spec."""')
    parts.append("")
    parts.append("from openbb_core.app.model.command_context import CommandContext")
    parts.append("from openbb_core.app.model.obbject import OBBject")
    parts.append(
        "from openbb_core.app.provider_interface import "
        "ExtraParams, ProviderChoices, StandardParams"
    )
    parts.append("from openbb_core.app.query import Query")
    parts.append("from openbb_core.app.router import Router")

    has_stream = any(
        (fetcher := fetchers_by_command.get(child.full_path)) is not None
        and fetcher.is_streaming
        for child in node.children.values()
        if child.is_command and child.cmd_spec is not None
    )
    if has_stream:
        parts.append("from openbb_core.app.model.stream import OBBStream")

    sub_imports: list[tuple[str, str, str]] = []
    for sub_name, sub_node in sorted(node.children.items()):
        if not sub_node.is_namespace:
            continue
        sub_module = _emit_router(
            sub_node,
            package_name=package_name,
            provider_name=provider_name,
            fetchers_by_command=fetchers_by_command,
            post_commands_by_command=post_commands_by_command,
            collected=collected,
            is_top_level=False,
        )
        sub_imports.append((sub_module, _safe_segment(sub_name), sub_node.full_path))

    post_imports: list[tuple[str, str]] = []
    for child in node.children.values():
        if child.is_command and child.cmd_spec is not None:
            post = post_commands_by_command.get(child.full_path)
            if post is not None:
                post_module = (
                    f"{package_name}.providers.{provider_name}.models."
                    f"{post.module_name}"
                )
                post_imports.append((post_module, post.function_name))

    if post_imports:
        parts.append("")
        for module_path, function_name in post_imports:
            parts.append(
                f"from {module_path} import {function_name} as _{function_name}"
            )

    if sub_imports:
        parts.append("")
        for sub_module, sub_segment, _full in sub_imports:
            parts.append(
                f"from {package_name}.routers.{sub_module} import "
                f"router as _{sub_segment}_router"
            )

    parts.append("")
    parts.append("")
    parts.append('router = Router(prefix="")')
    parts.append("")

    for _, sub_segment, _full in sub_imports:
        parts.append(
            f'router.include_router(_{sub_segment}_router, prefix="/{sub_segment}")'
        )
    if sub_imports:
        parts.append("")

    for child_name, child in sorted(node.children.items()):
        if not child.is_command or child.cmd_spec is None:
            continue
        function_name = _safe_segment(child_name)
        description = (child.cmd_spec.get("description") or "").strip()
        fetcher = fetchers_by_command.get(child.full_path)
        if fetcher is not None:
            renderer = (
                _render_stream_command if fetcher.is_streaming else _render_get_command
            )
            parts.append(
                renderer(
                    fetcher,
                    function_name=function_name,
                    description=description,
                )
            )
        else:
            post = post_commands_by_command.get(child.full_path)
            if post is not None:
                parts.append(
                    f'router.command(methods=["POST"])(_{post.function_name})\n'
                )

    source = "\n".join(parts).rstrip() + "\n"
    collected.routers.append(
        GeneratedRouter(
            module_name=module_name,
            entry_point_name=node.name if is_top_level else None,
            source=source,
        )
    )
    return module_name


def _render_get_command(
    fetcher: GeneratedFetcher,
    *,
    function_name: str,
    description: str,
) -> str:
    """Render one ``@router.command(model=...)`` block for a GET endpoint.

    Parameters
    ----------
    fetcher : GeneratedFetcher
        Per-command fetcher metadata.
    function_name : str
        Leaf segment of the dotted path used as the function identifier.
    description : str
        Spec-supplied command description.

    Returns
    -------
    str
        The decorator + ``async def`` block.
    """
    summary = description or f"{fetcher.model_name} command."
    docstring = _format_docstring(summary)
    return (
        f'@router.command(model="{fetcher.model_name}")\n'
        f"async def {function_name}(\n"
        "    cc: CommandContext,\n"
        "    provider_choices: ProviderChoices,\n"
        "    standard_params: StandardParams,\n"
        "    extra_params: ExtraParams,\n"
        ") -> OBBject:\n"
        f"{docstring}\n"
        "    return await OBBject.from_query(Query(**locals()))\n"
    )


def _render_stream_command(
    fetcher: GeneratedFetcher,
    *,
    function_name: str,
    description: str,
) -> str:
    """Render one ``@router.command(model=...)`` block for a streaming endpoint.

    Parameters
    ----------
    fetcher : GeneratedFetcher
        Per-command fetcher metadata.
    function_name : str
        Leaf segment of the dotted path used as the function identifier.
    description : str
        Spec-supplied command description.

    Returns
    -------
    str
        The decorator and ``async def`` block returning an OBBStream.
    """
    summary = description or f"{fetcher.model_name} stream."
    docstring = _format_docstring(summary)
    return (
        f'@router.command(model="{fetcher.model_name}")\n'
        f"async def {function_name}(\n"
        "    cc: CommandContext,\n"
        "    provider_choices: ProviderChoices,\n"
        "    standard_params: StandardParams,\n"
        "    extra_params: ExtraParams,\n"
        ") -> OBBStream:\n"
        f"{docstring}\n"
        "    return await OBBStream.from_query(Query(**locals()))\n"
    )


def _format_docstring(text: str) -> str:
    """Render ``text`` as an indented function docstring.

    Parameters
    ----------
    text : str
        Source description from the spec.

    Returns
    -------
    str
        Triple-quoted docstring body indented four spaces.
    """
    cleaned = text.strip()
    if not cleaned:
        cleaned = "."
    if not cleaned.endswith((".", "!", "?")):
        cleaned += "."
    if "\n" not in cleaned:
        return f'    """{cleaned}"""'
    first, _, rest = cleaned.partition("\n")
    rest_indented = "\n".join(
        f"    {line}" if line.strip() else "" for line in rest.split("\n")
    )
    return f'    """{first}\n\n{rest_indented}\n    """'
