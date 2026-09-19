"""Tests for openbb_cli.codegen.namespace_tree — flat-spec → tree conversion."""

from __future__ import annotations

from openbb_cli.codegen import namespace_tree as nt

# --- build_namespace_tree ---


def test_build_namespace_tree_creates_nested_hierarchy():
    commands = {
        "equity.price.historical": {"providers": ["fmp"]},
        "equity.price.quote": {"providers": ["fmp", "intrinio"]},
        "equity.search": {"providers": ["fmp"]},
        "crypto.price.historical": {"providers": ["fmp"]},
    }
    root = nt.build_namespace_tree(commands)

    assert root.name == ""
    assert root.full_path == ""
    assert root.cmd_spec is None
    assert set(root.children) == {"equity", "crypto"}

    equity = root.children["equity"]
    assert equity.full_path == "equity"
    assert equity.cmd_spec is None
    assert equity.is_namespace
    assert not equity.is_command
    assert set(equity.children) == {"price", "search"}

    historical = equity.children["price"].children["historical"]
    assert historical.full_path == "equity.price.historical"
    assert historical.is_command
    assert not historical.is_namespace
    assert historical.cmd_spec == {"providers": ["fmp"]}


def test_build_namespace_tree_supports_hybrid_command_and_namespace_node():
    commands = {
        "bill": {"providers": ["congress"]},
        "bill.actions": {"providers": ["congress"]},
    }
    root = nt.build_namespace_tree(commands)

    bill = root.children["bill"]
    # ``bill`` is both a command (has cmd_spec) and a namespace (has children)
    assert bill.is_command
    assert bill.is_namespace
    assert "actions" in bill.children


def test_build_namespace_tree_skips_empty_dotted_paths():
    commands = {"": {"providers": ["x"]}, "equity": {"providers": ["fmp"]}}
    root = nt.build_namespace_tree(commands)
    assert "" not in root.children
    assert "equity" in root.children


# --- filter_tree_by_provider ---


def _sample_tree():
    return nt.build_namespace_tree(
        {
            "equity.price.historical": {"providers": ["fmp", "intrinio"]},
            "equity.price.quote": {"providers": ["intrinio"]},
            "equity.search": {"providers": ["fmp"]},
            "econometrics.regression": {"providers": []},
        }
    )


def test_filter_tree_by_provider_keeps_only_matching_commands():
    root = _sample_tree()
    fmp_tree = nt.filter_tree_by_provider(root, "fmp")

    cmds = {p for p, _ in nt.iter_commands(fmp_tree)}
    assert cmds == {"equity.price.historical", "equity.search"}


def test_filter_tree_by_provider_prunes_empty_branches():
    root = _sample_tree()
    intrinio_tree = nt.filter_tree_by_provider(root, "intrinio")
    cmds = {p for p, _ in nt.iter_commands(intrinio_tree)}
    assert cmds == {"equity.price.historical", "equity.price.quote"}
    # ``econometrics`` and ``equity.search`` should have been pruned away
    assert "econometrics" not in intrinio_tree.children
    assert "search" not in intrinio_tree.children["equity"].children


def test_filter_tree_by_provider_returns_empty_root_when_nothing_matches():
    root = _sample_tree()
    out = nt.filter_tree_by_provider(root, "no_such_provider")
    assert out.name == ""
    assert out.full_path == ""
    assert out.children == {}


# --- filter_tree_local_only ---


def test_filter_tree_local_only_keeps_commands_without_providers():
    root = _sample_tree()
    locals_only = nt.filter_tree_local_only(root)
    cmds = {p for p, _ in nt.iter_commands(locals_only)}
    assert cmds == {"econometrics.regression"}


def test_filter_tree_local_only_returns_empty_root_when_no_local_commands():
    root = nt.build_namespace_tree(
        {"equity.search": {"providers": ["fmp"]}},
    )
    out = nt.filter_tree_local_only(root)
    assert out.children == {}


# --- iter_commands & providers_from_tree ---


def test_iter_commands_yields_all_command_nodes():
    root = _sample_tree()
    commands = dict(nt.iter_commands(root))
    assert set(commands) == {
        "equity.price.historical",
        "equity.price.quote",
        "equity.search",
        "econometrics.regression",
    }


def test_providers_from_tree_collects_unique_provider_set():
    root = _sample_tree()
    assert nt.providers_from_tree(root) == {"fmp", "intrinio"}


def test_providers_from_tree_skips_commands_with_empty_provider_list():
    root = nt.build_namespace_tree(
        {"econometrics.regression": {"providers": []}},
    )
    assert nt.providers_from_tree(root) == set()
