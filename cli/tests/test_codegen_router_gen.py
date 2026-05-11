"""Tests for openbb_cli.codegen.router_gen — router module emission."""

from __future__ import annotations

import ast
from dataclasses import dataclass

from openbb_cli.codegen import (
    namespace_tree as nt,
    router_gen as rg,
)


@dataclass
class _Fetcher:
    module_name: str
    fetcher_class: str
    model_name: str


@dataclass
class _PostCommand:
    module_name: str
    function_name: str


# --- _safe_segment / _module_name_for / _model_name_for ---


def test_safe_segment_handles_special_chars_and_empty():
    assert rg._safe_segment("Equity Price") == "equity_price"
    assert rg._safe_segment("___") == "ns"
    assert rg._safe_segment("Fixed-Income") == "fixed_income"


def test_module_name_for_joins_dotted_path():
    assert rg._module_name_for("equity") == "equity"
    assert rg._module_name_for("equity.price") == "equity_price"
    assert rg._module_name_for("equity.price.historical") == "equity_price_historical"


def test_model_name_for_camelcases_dotted_path():
    assert rg._model_name_for("equity.price.historical") == "EquityPriceHistorical"
    assert rg._model_name_for("equity.search") == "EquitySearch"
    assert rg._model_name_for("commodity.psd_report") == "CommodityPsdReport"


# --- _format_docstring ---


def test_format_docstring_single_line_appends_period():
    out = rg._format_docstring("Get historical data")
    assert out == '    """Get historical data."""'


def test_format_docstring_blank_text_renders_period_only():
    out = rg._format_docstring("   ")
    assert out == '    """."""'


def test_format_docstring_keeps_existing_terminator():
    out = rg._format_docstring("What is X?")
    assert out == '    """What is X?"""'


def test_format_docstring_multiline_uses_block_layout():
    out = rg._format_docstring("First line.\nSecond line.\n\nThird line.")
    assert out.startswith('    """First line.')
    assert out.endswith('    """')
    # Continuation lines are indented to four spaces; blank lines stay blank.
    assert "\n    Second line." in out
    assert "\n    Third line." in out


# --- generate_routers (full pipeline) ---


def test_generate_routers_emits_top_router_with_get_command():
    tree = nt.build_namespace_tree(
        {"equity.search": {"providers": ["fmp"], "description": "Search equities"}}
    )
    fetchers = {
        "equity.search": _Fetcher(
            module_name="equity_search",
            fetcher_class="EquitySearchFetcher",
            model_name="EquitySearch",
        )
    }
    out = rg.generate_routers(
        tree,
        package_name="openbb_codegen",
        provider_name="fmp",
        fetchers_by_command=fetchers,
        post_commands_by_command={},
    )

    assert isinstance(out, rg.GeneratedRouters)
    assert len(out.routers) == 1
    router = out.routers[0]
    assert router.module_name == "equity"
    assert router.entry_point_name == "equity"

    src = router.source
    assert 'router = Router(prefix="")' in src
    assert '@router.command(model="EquitySearch")' in src
    assert "async def search(" in src
    assert '"""Search equities."""' in src
    # Module parses
    ast.parse(src)


def test_generate_routers_nests_sub_routers_via_include_router():
    tree = nt.build_namespace_tree(
        {
            "equity.price.historical": {
                "providers": ["fmp"],
                "description": "OHLCV.",
            }
        }
    )
    fetchers = {
        "equity.price.historical": _Fetcher(
            module_name="equity_price_historical",
            fetcher_class="EquityPriceHistoricalFetcher",
            model_name="EquityPriceHistorical",
        )
    }
    out = rg.generate_routers(
        tree,
        package_name="openbb_codegen",
        provider_name="fmp",
        fetchers_by_command=fetchers,
        post_commands_by_command={},
    )

    by_module = {r.module_name: r for r in out.routers}
    # Both top-level (equity) and nested (equity_price) modules emitted
    assert {"equity", "equity_price"} <= set(by_module)
    # Only the top-level router gets an entry point
    assert by_module["equity"].entry_point_name == "equity"
    assert by_module["equity_price"].entry_point_name is None
    # Top-level router includes the nested one with the correct prefix
    assert (
        "from openbb_codegen.routers.equity_price import router as _price_router"
        in by_module["equity"].source
    )
    assert (
        'router.include_router(_price_router, prefix="/price")'
        in by_module["equity"].source
    )
    # The nested router defines the actual command
    assert "async def historical(" in by_module["equity_price"].source


def test_generate_routers_emits_post_command_re_decoration():
    tree = nt.build_namespace_tree(
        {"econometrics.regression": {"providers": [], "description": "Linear fit."}}
    )
    posts = {
        "econometrics.regression": _PostCommand(
            module_name="econometrics_regression",
            function_name="regression",
        )
    }
    out = rg.generate_routers(
        tree,
        package_name="openbb_codegen",
        provider_name="tools",
        fetchers_by_command={},
        post_commands_by_command=posts,
    )

    src = out.routers[0].source
    assert (
        "from openbb_codegen.providers.tools.models.econometrics_regression "
        "import regression as _regression"
    ) in src
    assert 'router.command(methods=["POST"])(_regression)' in src
    ast.parse(src)


def test_generate_routers_falls_back_to_model_name_when_description_missing():
    tree = nt.build_namespace_tree(
        {"equity.search": {"providers": ["fmp"]}},  # no description
    )
    fetchers = {
        "equity.search": _Fetcher(
            module_name="equity_search",
            fetcher_class="EquitySearchFetcher",
            model_name="EquitySearch",
        )
    }
    out = rg.generate_routers(
        tree,
        package_name="openbb_codegen",
        provider_name="fmp",
        fetchers_by_command=fetchers,
        post_commands_by_command={},
    )
    assert '"""EquitySearch command."""' in out.routers[0].source


def test_generate_routers_skips_command_without_matching_fetcher_or_post():
    tree = nt.build_namespace_tree(
        {"equity.search": {"providers": ["fmp"], "description": "Search."}}
    )
    out = rg.generate_routers(
        tree,
        package_name="openbb_codegen",
        provider_name="fmp",
        fetchers_by_command={},  # no fetcher registered
        post_commands_by_command={},  # no post command either
    )
    src = out.routers[0].source
    # No command body emitted; only the router declaration remains
    assert "async def" not in src
    assert "router.command" not in src
    ast.parse(src)
