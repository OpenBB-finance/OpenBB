"""Tests for tool execution, prompt rendering, and bundled skill integration.

These tests exercise the actual closure-defined tools (discovery and prompt)
and verify that the real bundled skill files render correctly through the
StaticPrompt pipeline.
"""

# pylint: disable=protected-access,unused-argument

import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from mcp.types import TextContent
from openbb_mcp_server.app.app import create_mcp_server
from openbb_mcp_server.models.category_index import CategoryIndex
from openbb_mcp_server.models.prompts import StaticPrompt
from openbb_mcp_server.models.settings import MCPSettings

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SKILLS_DIR = Path(__file__).resolve().parent.parent.parent / (
    "openbb_mcp_server" + os.sep + "skills"
)


def _capture_decorated_tools(mock_mcp_instance):
    """Patch ``mock_mcp_instance.tool`` so the undecorated closures are captured.

    Returns a dict mapping ``func.__name__`` → the original function object.
    """
    decorated: dict[str, object] = {}

    def tool_decorator_factory(*args, **kwargs):
        def decorator(func):
            decorated[func.__name__] = func
            return MagicMock()

        return decorator

    mock_mcp_instance.tool = MagicMock(side_effect=tool_decorator_factory)
    return decorated


def _build_server(
    settings: MCPSettings,
    *,
    index: CategoryIndex | None = None,
    prompts_json: list | None = None,
):
    """Construct the MCP server with controlled mocks and return helpers.

    Returns ``(mcp_mock, decorated_functions, index)``.
    """
    fastapi_app = FastAPI()

    mock_processed_data = MagicMock()
    mock_processed_data.route_lookup = {}
    mock_processed_data.route_maps = []
    mock_processed_data.prompt_definitions = prompts_json or []

    mock_mcp_instance = MagicMock()
    mock_mcp_instance.render_prompt = AsyncMock()

    decorated = _capture_decorated_tools(mock_mcp_instance)

    if index is None:
        index = CategoryIndex()

    with (
        patch(
            "openbb_mcp_server.app.app.process_fastapi_routes_for_mcp",
            return_value=mock_processed_data,
        ),
        patch(
            "openbb_mcp_server.app.app.CategoryIndex",
            return_value=index,
        ),
        patch(
            "openbb_mcp_server.app.app.FastMCP.from_fastapi",
            return_value=mock_mcp_instance,
        ),
    ):
        create_mcp_server(settings, fastapi_app)

    return mock_mcp_instance, decorated, index


# ===================================================================
# Discovery tool execution tests
# ===================================================================


class TestAvailableCategories:
    """Tests for the ``available_categories`` discovery tool."""

    def test_returns_categories_with_subcategories(self):
        """Return categories with their subcategories and tool counts."""
        index = CategoryIndex()
        index.register(
            category="equity", subcategory="price", tool_name="equity_price_historical"
        )
        index.register(
            category="equity",
            subcategory="fundamental",
            tool_name="equity_fundamental_income",
        )
        index.register(
            category="economy", subcategory="general", tool_name="economy_cpi"
        )

        settings = MCPSettings(enable_tool_discovery=True)  # type: ignore
        _, decorated, _ = _build_server(settings, index=index)

        result = decorated["available_categories"]()
        names = {c.name for c in result}
        assert names == {"equity", "economy"}

        equity = next(c for c in result if c.name == "equity")
        assert equity.total_tools == 2
        subcat_names = {s.name for s in equity.subcategories}
        assert subcat_names == {"price", "fundamental"}

    def test_empty_index(self):
        """Return empty list when the index has no tools."""
        settings = MCPSettings(enable_tool_discovery=True)  # type: ignore
        _, decorated, _ = _build_server(settings, index=CategoryIndex())
        assert decorated["available_categories"]() == []

    def test_subcategory_tool_counts_are_correct(self):
        """Each subcategory reports the right tool count."""
        index = CategoryIndex()
        index.register(category="equity", subcategory="price", tool_name="t1")
        index.register(category="equity", subcategory="price", tool_name="t2")
        index.register(category="equity", subcategory="price", tool_name="t3")
        index.register(category="equity", subcategory="fundamental", tool_name="t4")

        settings = MCPSettings(enable_tool_discovery=True)  # type: ignore
        _, decorated, _ = _build_server(settings, index=index)

        result = decorated["available_categories"]()
        equity = result[0]
        assert equity.total_tools == 4
        by_subcat = {s.name: s.tool_count for s in equity.subcategories}
        assert by_subcat == {"fundamental": 1, "price": 3}


def _make_mock_tool(name: str, description: str = "desc"):
    """Create a minimal mock that looks like a FastMCP Tool (name + description)."""
    t = MagicMock()
    t.name = name
    t.description = description
    return t


def _make_mock_context():
    """Create a mock Context with async enable/disable_components."""
    ctx = MagicMock()
    ctx.enable_components = AsyncMock()
    ctx.disable_components = AsyncMock()
    return ctx


class TestAvailableTools:
    """Tests for the ``available_tools`` async discovery tool.

    These actually call the captured closure with mocked mcp.list_tools()
    and mcp.get_tool() to verify real output.
    """

    def _setup(self):
        index = CategoryIndex()
        index.register(
            category="equity",
            subcategory="price",
            tool_name="equity_price_historical",
            description="Get historical prices. Supports OHLCV.",
        )
        index.register(
            category="equity",
            subcategory="price",
            tool_name="equity_price_quote",
            description="Get the latest quote for a stock.",
        )
        index.register(
            category="equity",
            subcategory="fundamental",
            tool_name="equity_fundamental_income",
            description="Get income statement. Annual or quarterly.",
        )

        settings = MCPSettings(enable_tool_discovery=True)  # type: ignore
        mcp_mock, decorated, _ = _build_server(settings, index=index)
        return mcp_mock, decorated

    @pytest.mark.asyncio
    async def test_list_tools_in_category(self):
        """List all tools across all subcategories of a category."""
        mcp_mock, decorated = self._setup()
        mcp_mock.list_tools = AsyncMock(
            return_value=[
                _make_mock_tool("equity_price_historical", "Get historical prices"),
                _make_mock_tool("equity_price_quote", "Get quote"),
            ]
        )

        result = await decorated["available_tools"](category="equity")
        names = {t.name for t in result}
        assert names == {
            "equity_price_historical",
            "equity_price_quote",
            "equity_fundamental_income",
        }

    @pytest.mark.asyncio
    async def test_list_tools_in_subcategory(self):
        """List only tools in a specific subcategory."""
        mcp_mock, decorated = self._setup()
        mcp_mock.list_tools = AsyncMock(
            return_value=[
                _make_mock_tool("equity_price_historical"),
            ]
        )

        result = await decorated["available_tools"](
            category="equity", subcategory="price"
        )
        names = {t.name for t in result}
        assert names == {"equity_price_historical", "equity_price_quote"}

    @pytest.mark.asyncio
    async def test_reflects_active_state(self):
        """Tools in mcp.list_tools() are reported active=True, others active=False."""
        mcp_mock, decorated = self._setup()
        # Only historical is visible/active
        mcp_mock.list_tools = AsyncMock(
            return_value=[
                _make_mock_tool("equity_price_historical", "Get historical prices"),
            ]
        )

        result = await decorated["available_tools"](
            category="equity", subcategory="price"
        )
        by_name = {t.name: t for t in result}
        assert by_name["equity_price_historical"].active is True
        assert by_name["equity_price_quote"].active is False

    @pytest.mark.asyncio
    async def test_inactive_tools_get_cached_description(self):
        """Inactive tools use the cached first-sentence description from the index."""
        mcp_mock, decorated = self._setup()
        # Only historical is active
        mcp_mock.list_tools = AsyncMock(
            return_value=[
                _make_mock_tool("equity_price_historical", "Get historical prices."),
            ]
        )

        result = await decorated["available_tools"](
            category="equity", subcategory="price"
        )
        by_name = {t.name: t for t in result}
        # Active tool gets live description
        assert (
            by_name["equity_price_historical"].description == "Get historical prices."
        )
        # Inactive tool gets cached first-sentence from register()
        assert (
            by_name["equity_price_quote"].description
            == "Get the latest quote for a stock."
        )

    @pytest.mark.asyncio
    async def test_unknown_category_raises(self):
        """Raise ValueError when the requested category does not exist."""
        mcp_mock, decorated = self._setup()
        with pytest.raises(ValueError, match="not found"):
            await decorated["available_tools"](category="nonexistent")

    @pytest.mark.asyncio
    async def test_unknown_subcategory_raises(self):
        """Raise ValueError when the requested subcategory does not exist."""
        mcp_mock, decorated = self._setup()
        with pytest.raises(ValueError, match="not found"):
            await decorated["available_tools"](category="equity", subcategory="options")

    @pytest.mark.asyncio
    async def test_descriptions_strip_api_doc_sections(self):
        """Descriptions strip everything after **Query Parameters: or **Responses: sections."""
        mcp_mock, decorated = self._setup()
        mcp_mock.list_tools = AsyncMock(
            return_value=[
                _make_mock_tool(
                    "equity_price_historical",
                    "Get historical prices.\n\n**Query Parameters:\n- symbol: str",
                ),
            ]
        )

        result = await decorated["available_tools"](
            category="equity", subcategory="price"
        )
        hist = next(t for t in result if t.name == "equity_price_historical")
        assert hist.description == "Get historical prices."

    @pytest.mark.asyncio
    async def test_descriptions_preserve_body_without_api_sections(self):
        """Descriptions without API doc sections are returned in full."""
        mcp_mock, decorated = self._setup()
        mcp_mock.list_tools = AsyncMock(
            return_value=[
                _make_mock_tool(
                    "equity_price_historical",
                    "Get historical prices.\n\nThis returns OHLCV data with many parameters.",
                ),
            ]
        )

        result = await decorated["available_tools"](
            category="equity", subcategory="price"
        )
        hist = next(t for t in result if t.name == "equity_price_historical")
        assert (
            hist.description
            == "Get historical prices.\n\nThis returns OHLCV data with many parameters."
        )


class TestToggleTools:
    """Tests for ``activate_tools``, ``deactivate_tools``, and ``activate_category``.

    These actually call the async closures with a mocked Context and verify
    the return messages and that ctx.enable/disable_components was called
    with the right arguments.
    """

    def _setup(self):
        index = CategoryIndex()
        index.register(
            category="equity", subcategory="price", tool_name="equity_price_historical"
        )
        index.register(
            category="equity", subcategory="price", tool_name="equity_price_quote"
        )
        index.register(
            category="economy", subcategory="general", tool_name="economy_cpi"
        )

        settings = MCPSettings(enable_tool_discovery=True)  # type: ignore
        _, decorated, _ = _build_server(settings, index=index)
        return decorated

    @pytest.mark.asyncio
    async def test_activate_known_tools(self):
        """Activate known tools and confirm ctx.enable_components is called."""
        decorated = self._setup()
        ctx = _make_mock_context()

        msg = await decorated["activate_tools"](
            tool_names=["equity_price_historical", "economy_cpi"], ctx=ctx
        )
        assert "Activated" in msg
        assert "equity_price_historical" in msg
        assert "economy_cpi" in msg
        ctx.enable_components.assert_awaited_once_with(
            names={"equity_price_historical", "economy_cpi"}
        )

    @pytest.mark.asyncio
    async def test_activate_unknown_tools(self):
        """Report not-found for unknown tool names, don't call enable."""
        decorated = self._setup()
        ctx = _make_mock_context()

        msg = await decorated["activate_tools"](tool_names=["nonexistent"], ctx=ctx)
        assert "Not found" in msg
        assert "nonexistent" in msg
        ctx.enable_components.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_activate_mixed_known_and_unknown(self):
        """Report both activated and not-found in the same call."""
        decorated = self._setup()
        ctx = _make_mock_context()

        msg = await decorated["activate_tools"](
            tool_names=["equity_price_historical", "nonexistent"], ctx=ctx
        )
        assert "Activated" in msg
        assert "Not found" in msg
        ctx.enable_components.assert_awaited_once_with(
            names={"equity_price_historical"}
        )

    @pytest.mark.asyncio
    async def test_activate_empty_list(self):
        """Empty tool list returns 'No tools processed.'"""
        decorated = self._setup()
        ctx = _make_mock_context()

        msg = await decorated["activate_tools"](tool_names=[], ctx=ctx)
        assert msg == "No tools processed."
        ctx.enable_components.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_deactivate_known_tools(self):
        """Deactivate known tools and confirm ctx.disable_components is called."""
        decorated = self._setup()
        ctx = _make_mock_context()

        msg = await decorated["deactivate_tools"](
            tool_names=["equity_price_quote"], ctx=ctx
        )
        assert "Deactivated" in msg
        assert "equity_price_quote" in msg
        ctx.disable_components.assert_awaited_once_with(names={"equity_price_quote"})

    @pytest.mark.asyncio
    async def test_deactivate_unknown_tools(self):
        """Report not-found for unknown tool names, don't call disable."""
        decorated = self._setup()
        ctx = _make_mock_context()

        msg = await decorated["deactivate_tools"](tool_names=["fake"], ctx=ctx)
        assert "Not found" in msg
        ctx.disable_components.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_activate_category_all(self):
        """Activate all tools in a category."""
        decorated = self._setup()
        ctx = _make_mock_context()

        msg = await decorated["activate_category"](category="equity", ctx=ctx)
        assert "Activated 2 tools" in msg
        assert "equity_price_historical" in msg
        assert "equity_price_quote" in msg
        ctx.enable_components.assert_awaited_once()
        called_names = ctx.enable_components.call_args[1]["names"]
        assert called_names == {"equity_price_historical", "equity_price_quote"}

    @pytest.mark.asyncio
    async def test_activate_category_with_subcategory(self):
        """Activate only tools in a specific subcategory."""
        decorated = self._setup()
        ctx = _make_mock_context()

        msg = await decorated["activate_category"](
            category="equity", subcategory="price", ctx=ctx
        )
        assert "Activated 2 tools" in msg
        ctx.enable_components.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_activate_category_unknown_raises(self):
        """Raise ValueError for unknown category."""
        decorated = self._setup()
        ctx = _make_mock_context()

        with pytest.raises(ValueError, match="No tools found"):
            await decorated["activate_category"](category="nonexistent", ctx=ctx)
        ctx.enable_components.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_activate_category_unknown_subcategory_raises(self):
        """Raise ValueError for unknown subcategory within a valid category."""
        decorated = self._setup()
        ctx = _make_mock_context()

        with pytest.raises(ValueError, match="No tools found"):
            await decorated["activate_category"](
                category="equity", subcategory="options", ctx=ctx
            )
        ctx.enable_components.assert_not_awaited()

    def test_discovery_tools_not_registered_when_disabled(self):
        """Omit all discovery tools when tool discovery is disabled in settings."""
        settings = MCPSettings(enable_tool_discovery=False)  # type: ignore
        _, decorated, _ = _build_server(settings)
        assert "available_categories" not in decorated
        assert "available_tools" not in decorated
        assert "activate_tools" not in decorated
        assert "deactivate_tools" not in decorated
        assert "activate_category" not in decorated


# ===================================================================
# Prompt tool execution tests
# ===================================================================


# ===================================================================
# PromptsAsTools transform tests
# ===================================================================


class TestTransformsAdded:
    """Tests verifying that PromptsAsTools and ResourcesAsTools transforms are registered."""

    def test_transforms_are_added(self):
        """Both PromptsAsTools and ResourcesAsTools transforms are registered."""
        from fastmcp.server.transforms import PromptsAsTools, ResourcesAsTools

        settings = MCPSettings()  # type: ignore
        mock_mcp, _, _ = _build_server(settings)

        assert mock_mcp.add_transform.call_count == 2
        transforms = [call[0][0] for call in mock_mcp.add_transform.call_args_list]
        assert isinstance(transforms[0], PromptsAsTools)
        assert isinstance(transforms[1], ResourcesAsTools)

    def test_no_hand_rolled_prompt_or_resource_tools(self):
        """The old list_prompts / execute_prompt / list_resources / read_resource closures are no longer registered."""
        settings = MCPSettings()  # type: ignore
        _, decorated, _ = _build_server(settings)

        assert "list_prompts" not in decorated
        assert "execute_prompt" not in decorated
        assert "list_resources" not in decorated
        assert "read_resource" not in decorated

    def test_inline_prompt_stores_argument_defaults(self):
        """Inline prompt definitions store defaults on StaticPrompt.argument_defaults."""
        prompt_def = {
            "name": "my_prompt",
            "description": "Test",
            "content": "Hello {name}, focus on {aspect}",
            "arguments": [
                {"name": "name", "type": "str", "description": "Name"},
                {
                    "name": "aspect",
                    "type": "str",
                    "description": "Aspect",
                    "default": "fundamentals",
                },
            ],
        }
        settings = MCPSettings()  # type: ignore
        mock_mcp, _, _ = _build_server(settings, prompts_json=[prompt_def])

        # Find the StaticPrompt among add_prompt calls
        added_prompts = [
            call[0][0]
            for call in mock_mcp.add_prompt.call_args_list
            if isinstance(call[0][0], StaticPrompt)
        ]
        assert len(added_prompts) == 1
        assert added_prompts[0].argument_defaults == {"aspect": "fundamentals"}

    @pytest.mark.asyncio
    async def test_static_prompt_renders_with_defaults(self):
        """StaticPrompt.render() applies argument_defaults when caller omits them."""
        from fastmcp.prompts import PromptArgument

        prompt = StaticPrompt(
            name="greeting",
            content="Hello {name}, focus on {aspect}",
            arguments=[
                PromptArgument(name="name", required=True),
                PromptArgument(name="aspect", required=False),
            ],
            argument_defaults={"aspect": "fundamentals"},
        )

        rendered = await prompt.render(arguments={"name": "AAPL"})
        assert rendered[0].content.text == "Hello AAPL, focus on fundamentals"

    @pytest.mark.asyncio
    async def test_static_prompt_caller_overrides_defaults(self):
        """Caller-supplied values override argument_defaults."""
        from fastmcp.prompts import PromptArgument

        prompt = StaticPrompt(
            name="greeting",
            content="Hello {name}, focus on {aspect}",
            arguments=[
                PromptArgument(name="name", required=True),
                PromptArgument(name="aspect", required=False),
            ],
            argument_defaults={"aspect": "fundamentals"},
        )

        rendered = await prompt.render(
            arguments={"name": "AAPL", "aspect": "technicals"}
        )
        assert rendered[0].content.text == "Hello AAPL, focus on technicals"


# ===================================================================
# Bundled skill rendering tests
# ===================================================================


class TestBundledSkillRendering:
    """Verify each real skill file renders through StaticPrompt without error."""

    EXPECTED_SKILLS = {
        "develop_extension": "Build an OpenBB Platform Extension",
        "build_workspace_app": "Build and Run OpenBB Workspace Applications",
        "configure_mcp_server": "Configure and Build the OpenBB MCP Server",
        "work_with_server": "Working With the OpenBB MCP Server",
    }

    def test_skills_directory_exists(self):
        """Verify the skills directory exists at the expected path."""
        assert SKILLS_DIR.is_dir(), f"Skills directory not found: {SKILLS_DIR}"

    def test_all_expected_skills_present(self):
        """Confirm all expected skill subdirectories with SKILL.md are present."""
        skill_dirs = {
            d.name
            for d in SKILLS_DIR.iterdir()
            if d.is_dir() and (d / "SKILL.md").exists()
        }
        for name in self.EXPECTED_SKILLS:
            assert name in skill_dirs, f"Missing skill subdirectory: {name}/SKILL.md"

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "skill_name,expected_heading",
        list(EXPECTED_SKILLS.items()),
        ids=list(EXPECTED_SKILLS.keys()),
    )
    async def test_skill_renders_without_error(self, skill_name, expected_heading):
        """Each skill file renders to a PromptMessage with full content intact."""
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")
        assert len(content) > 100, f"Skill {skill_name} seems too short"

        prompt = StaticPrompt(
            name=skill_name,
            description=expected_heading,
            content=content,
            arguments=None,
            tags={"skill"},
        )
        rendered = await prompt.render()

        assert len(rendered) == 1
        assert rendered[0].role == "user"
        assert isinstance(rendered[0].content, TextContent)
        assert rendered[0].content.text == content

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "skill_name",
        list(EXPECTED_SKILLS.keys()),
        ids=list(EXPECTED_SKILLS.keys()),
    )
    async def test_skill_preserves_curly_braces(self, skill_name):
        """Skills with code blocks containing {} must not raise KeyError."""
        skill_file = SKILLS_DIR / skill_name / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")

        prompt = StaticPrompt(
            name=skill_name,
            description="test",
            content=content,
            arguments=None,
            tags={"skill"},
        )
        # This would raise KeyError if str.format() is incorrectly applied
        rendered = await prompt.render()
        assert rendered[0].content.text == content

    @pytest.mark.asyncio
    async def test_skill_render_with_empty_arguments(self):
        """Passing empty dict as arguments should still bypass str.format."""
        skill_file = SKILLS_DIR / "develop_extension" / "SKILL.md"
        content = skill_file.read_text(encoding="utf-8")

        prompt = StaticPrompt(
            name="develop_extension",
            description="test",
            content=content,
            arguments=None,
            tags={"skill"},
        )
        # Explicit empty dict should also be safe
        rendered = await prompt.render(arguments={})
        assert rendered[0].content.text == content

    def test_skill_description_from_first_heading(self):
        """Verify that each SKILL.md has the expected markdown heading (after YAML frontmatter)."""
        for skill_name, expected_heading in self.EXPECTED_SKILLS.items():
            skill_file = SKILLS_DIR / skill_name / "SKILL.md"
            content = skill_file.read_text(encoding="utf-8")
            # Skip YAML frontmatter block (--- ... ---)
            lines = content.splitlines()
            in_frontmatter = lines[0].strip() == "---" if lines else False
            heading = ""
            for i, line in enumerate(lines):
                if i == 0 and in_frontmatter:
                    continue
                if in_frontmatter and line.strip() == "---":
                    in_frontmatter = False
                    continue
                if not in_frontmatter and line.startswith("#"):
                    heading = line.lstrip("# ").strip()
                    break
            assert (
                heading == expected_heading
            ), f"Skill '{skill_name}' heading mismatch: got '{heading}', expected '{expected_heading}'"


# ===================================================================
# Integration: skills loaded and accessible via prompt tools
# ===================================================================


class TestSkillsIntegration:
    """Test skills loading end-to-end through create_mcp_server."""

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_bundled_skills_registered_via_provider(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """Bundled skills are registered via mcp.add_provider(SkillsDirectoryProvider)."""
        from fastmcp.server.providers.skills import SkillsDirectoryProvider

        settings = MCPSettings()  # type: ignore  (uses default skills dir)
        fastapi_app = FastAPI()

        mock_processed_data = MagicMock()
        mock_processed_data.route_lookup = {}
        mock_processed_data.route_maps = []
        mock_processed_data.prompt_definitions = []
        mock_process_routes.return_value = mock_processed_data

        mock_index_instance = MagicMock()
        mock_category_index.return_value = mock_index_instance

        mock_mcp_instance = MagicMock()
        mock_from_fastapi.return_value = mock_mcp_instance

        create_mcp_server(settings, fastapi_app)

        provider_calls = mock_mcp_instance.add_provider.call_args_list
        assert len(provider_calls) >= 1
        assert isinstance(provider_calls[0][0][0], SkillsDirectoryProvider)

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_skill_md_files_have_content(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """Each bundled SKILL.md file has non-trivial content."""
        for skill_name in [
            "develop_extension",
            "build_workspace_app",
            "configure_mcp_server",
            "work_with_server",
        ]:
            skill_file = SKILLS_DIR / skill_name / "SKILL.md"
            assert skill_file.exists(), f"Missing: {skill_file}"
            content = skill_file.read_text(encoding="utf-8")
            assert (
                len(content) > 500
            ), f"Skill '{skill_name}' SKILL.md is suspiciously short ({len(content)} chars)"

    @patch("openbb_mcp_server.app.app.process_fastapi_routes_for_mcp")
    @patch("openbb_mcp_server.app.app.CategoryIndex")
    @patch("openbb_mcp_server.app.app.FastMCP.from_fastapi")
    def test_no_skill_prompts_registered(
        self, mock_from_fastapi, mock_category_index, mock_process_routes
    ):
        """Skills are no longer registered as prompts with the 'skill' tag."""
        settings = MCPSettings()  # type: ignore
        fastapi_app = FastAPI()

        mock_processed_data = MagicMock()
        mock_processed_data.route_lookup = {}
        mock_processed_data.route_maps = []
        mock_processed_data.prompt_definitions = []
        mock_process_routes.return_value = mock_processed_data

        mock_index_instance = MagicMock()
        mock_category_index.return_value = mock_index_instance

        mock_mcp_instance = MagicMock()
        mock_from_fastapi.return_value = mock_mcp_instance

        create_mcp_server(settings, fastapi_app)

        skill_prompt_calls = [
            c
            for c in mock_mcp_instance.add_prompt.call_args_list
            if hasattr(c[0][0], "tags") and "skill" in c[0][0].tags
        ]
        assert (
            skill_prompt_calls == []
        ), "Skills should not be registered as prompts in FastMCP v3 — use add_provider instead"
