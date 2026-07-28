"""Group spec commands into a hierarchical namespace tree."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NamespaceNode:
    """One node in the per-spec namespace tree.

    Parameters
    ----------
    name : str
        The leaf segment of this node's dotted path.
    full_path : str
        The full dotted path from the root.
    cmd_spec : dict, optional
        The spec command entry when this node is a leaf command.
    children : dict[str, NamespaceNode]
        Sub-nodes keyed by their ``name``.
    """

    name: str
    full_path: str
    cmd_spec: dict[str, Any] | None = None
    children: dict[str, NamespaceNode] = field(default_factory=dict)

    @property
    def is_command(self) -> bool:
        """Whether this node corresponds to an actual spec command."""
        return self.cmd_spec is not None

    @property
    def is_namespace(self) -> bool:
        """Whether this node has nested children (acts as a menu / sub-router)."""
        return bool(self.children)


def build_namespace_tree(commands: dict[str, dict[str, Any]]) -> NamespaceNode:
    """Build a hierarchical tree from the spec's flat command dict.

    Parameters
    ----------
    commands : dict
        Mapping of dotted command path to spec entry.

    Returns
    -------
    NamespaceNode
        Synthetic root node whose ``children`` are the top-level namespaces.
    """
    root = NamespaceNode(name="", full_path="")
    for dotted, cmd_spec in commands.items():
        if not dotted:
            continue
        parts = dotted.split(".")
        node = root
        path_so_far: list[str] = []
        for segment in parts:
            path_so_far.append(segment)
            child = node.children.get(segment)
            if child is None:
                child = NamespaceNode(name=segment, full_path=".".join(path_so_far))
                node.children[segment] = child
            node = child
        node.cmd_spec = cmd_spec
    return root


def filter_tree_by_provider(root: NamespaceNode, provider: str) -> NamespaceNode:
    """Return a copy of ``root`` keeping only commands that include ``provider``.

    Parameters
    ----------
    root : NamespaceNode
        The full namespace tree.
    provider : str
        Provider identifier to filter by.

    Returns
    -------
    NamespaceNode
        New tree containing only the surviving commands.
    """
    return _filter_node(root, lambda providers: provider in providers) or NamespaceNode(
        name="", full_path=""
    )


def filter_tree_local_only(root: NamespaceNode) -> NamespaceNode:
    """Return a copy of ``root`` keeping only commands with no provider list.

    Parameters
    ----------
    root : NamespaceNode
        The full namespace tree.

    Returns
    -------
    NamespaceNode
        New tree containing only commands whose ``providers`` list is empty.
    """
    return _filter_node(root, lambda providers: not providers) or NamespaceNode(
        name="", full_path=""
    )


def _filter_node(node: NamespaceNode, predicate) -> NamespaceNode | None:
    """Recursive helper that keeps commands matching ``predicate(providers)``."""
    keep_self = False
    new_cmd: dict[str, Any] | None = None
    if node.cmd_spec is not None:
        providers_list = node.cmd_spec.get("providers") or []
        if predicate(providers_list):
            keep_self = True
            new_cmd = node.cmd_spec

    new_children: dict[str, NamespaceNode] = {}
    for name, child in node.children.items():
        kept = _filter_node(child, predicate)
        if kept is not None:
            new_children[name] = kept

    if not keep_self and not new_children:
        return None

    return NamespaceNode(
        name=node.name,
        full_path=node.full_path,
        cmd_spec=new_cmd,
        children=new_children,
    )


def iter_commands(root: NamespaceNode) -> list[tuple[str, dict[str, Any]]]:
    """Walk the tree and return ``[(dotted_path, cmd_spec), ...]`` for every command."""
    out: list[tuple[str, dict[str, Any]]] = []
    _walk_commands(root, out)
    return out


def _walk_commands(node: NamespaceNode, out: list[tuple[str, dict[str, Any]]]) -> None:
    """Depth-first command collector."""
    if node.cmd_spec is not None:
        out.append((node.full_path, node.cmd_spec))
    for child in node.children.values():
        _walk_commands(child, out)


def providers_from_tree(root: NamespaceNode) -> set[str]:
    """Collect every provider mentioned across the tree's commands."""
    out: set[str] = set()
    for _, cmd_spec in iter_commands(root):
        for p in cmd_spec.get("providers") or []:
            out.add(str(p))
    return out
