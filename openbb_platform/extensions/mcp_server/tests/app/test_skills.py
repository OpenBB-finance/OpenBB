"""Tests for skill providers, the skills system prompt, and ``install_skill``."""

from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi import FastAPI
from fastmcp import Client
from fastmcp.exceptions import ToolError
from fastmcp.server.providers.skills import (
    ClaudeSkillsProvider,
    CursorSkillsProvider,
    SkillsDirectoryProvider,
)

from openbb_mcp_server.app.app import _VENDOR_SKILLS_PROVIDERS, create_mcp_server
from openbb_mcp_server.models.settings import MCPSettings

SKILLS_DIR = Path(MCPSettings().default_skills_dir or "")
EXPECTED_SKILLS = {
    "develop_extension": "Build an OpenBB Platform Extension",
    "build_workspace_app": "Build and Run OpenBB Workspace Applications",
    "configure_mcp_server": "Configure and Build the OpenBB MCP Server",
    "work_with_server": "Working With the OpenBB MCP Server",
    "use_openbb_cli": "Using the openbb-cli",
}


class _RootlessSkillsProvider(SkillsDirectoryProvider):
    """Vendor-style provider constructed without any root directory."""

    def __init__(self, reload: bool = False) -> None:
        super().__init__(roots=[], reload=reload)


@pytest.fixture(autouse=True)
def isolated_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    return home


def _server(**settings):
    return create_mcp_server(MCPSettings(**settings), FastAPI())


def _skills_providers(server) -> list[SkillsDirectoryProvider]:
    return [p for p in server.providers if isinstance(p, SkillsDirectoryProvider)]


async def _install(server, **arguments) -> dict:
    async with Client(server) as client:
        result = await client.call_tool("install_skill", arguments)
    return result.structured_content or {}


async def _system_prompt_text(server) -> str | None:
    async with Client(server) as client:
        names = {prompt.name for prompt in await client.list_prompts()}
        if "system_prompt" not in names:
            return None
        result = await client.get_prompt("system_prompt")
    return result.messages[0].content.text


class TestSkillsProviders:
    """Bundled and vendor skill providers."""

    def test_bundled_provider_uses_package_skills_by_default(self):
        """Default settings load the skills shipped inside the installed package."""
        providers = _skills_providers(_server())
        assert [p._roots for p in providers] == [[SKILLS_DIR.resolve()]]

    def test_custom_skills_dir_provider(self, tmp_path):
        """A custom ``default_skills_dir`` becomes the bundled provider's root."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        providers = _skills_providers(_server(default_skills_dir=str(skills_dir)))
        assert [p._roots for p in providers] == [[skills_dir.resolve()]]
        assert providers[0]._reload is False

    def test_skills_reload_passed_to_provider(self, tmp_path):
        """``skills_reload=True`` is forwarded to the bundled provider."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        server = _server(default_skills_dir=str(skills_dir), skills_reload=True)
        assert _skills_providers(server)[0]._reload is True

    @pytest.mark.parametrize("skills_dir", [None, "", "missing"])
    def test_no_provider_without_skills_dir(self, tmp_path, skills_dir):
        """An unset, empty, or missing skills directory adds no provider."""
        value = str(tmp_path / skills_dir) if skills_dir == "missing" else skills_dir
        assert _skills_providers(_server(default_skills_dir=value)) == []

    def test_vendor_skills_provider_map_contains_expected_keys(self):
        """The vendor map contains every documented short name."""
        assert set(_VENDOR_SKILLS_PROVIDERS) == {
            "claude",
            "cursor",
            "vscode",
            "copilot",
            "codex",
            "gemini",
            "goose",
            "opencode",
        }

    def test_vendor_providers_added(self):
        """Each configured vendor name registers its provider, reload included."""
        server = _server(
            default_skills_dir=None,
            skills_providers=["claude", " Cursor "],
            skills_reload=True,
        )
        providers = _skills_providers(server)
        assert [type(p) for p in providers] == [
            ClaudeSkillsProvider,
            CursorSkillsProvider,
        ]
        assert all(p._reload for p in providers)

    def test_unknown_vendor_provider_logs_warning(self, app_caplog):
        """Unknown vendor names are skipped with a warning listing the supported ones."""
        server = _server(default_skills_dir=None, skills_providers=["nope"])
        assert _skills_providers(server) == []
        assert "Unknown skills provider 'nope'. Supported: claude" in app_caplog.text


class TestSkillsSystemPrompt:
    """The default system prompt added when skills are loaded."""

    @pytest.mark.asyncio
    async def test_added_when_bundled_skills_loaded(self):
        """Bundled skills add a ``system_prompt`` that points at ``skill://`` resources."""
        server = _server()
        text = await _system_prompt_text(server)
        assert text is not None
        assert "list_resources()" in text
        assert "skill://" in text
        assert server.instructions == text

    @pytest.mark.asyncio
    async def test_added_when_vendor_skills_loaded(self):
        """Vendor skills alone also add the default ``system_prompt``."""
        server = _server(default_skills_dir=None, skills_providers=["claude"])
        assert "skill://" in (await _system_prompt_text(server) or "")

    @pytest.mark.asyncio
    async def test_absent_without_skills(self):
        """No skills means no default prompt and no instructions."""
        server = _server(default_skills_dir=None)
        assert await _system_prompt_text(server) is None
        assert server.instructions is None

    @pytest.mark.asyncio
    async def test_custom_prompt_file_wins(self, tmp_path):
        """A configured ``system_prompt_file`` replaces the default skills prompt."""
        prompt_file = tmp_path / "custom_prompt.txt"
        prompt_file.write_text("Custom system prompt text.", encoding="utf-8")
        server = _server(system_prompt_file=str(prompt_file))
        assert await _system_prompt_text(server) == "Custom system prompt text."
        assert server.instructions == "Custom system prompt text."

    @pytest.mark.asyncio
    async def test_explicit_instructions_not_overridden(self):
        """Configured ``instructions`` survive the default skills prompt."""
        server = _server(instructions="My explicit instructions.")
        assert "skill://" in (await _system_prompt_text(server) or "")
        assert server.instructions == "My explicit instructions."


class TestInstallSkill:
    """The ``install_skill`` tool."""

    @pytest.mark.asyncio
    async def test_install_into_bundled_provider(self, tmp_path):
        """Files land in the bundled root and the skill is readable as a resource."""
        skills_root = tmp_path / "skills"
        skills_root.mkdir()
        server = _server(default_skills_dir=str(skills_root))

        out = await _install(
            server,
            skill_name="my_skill",
            files={"SKILL.md": "# My Skill\n", "docs/helper.py": "x = 1\n"},
        )

        skill_dir = skills_root.resolve() / "my_skill"
        assert out == {
            "status": "installed",
            "skill_name": "my_skill",
            "target": "bundled",
            "path": str(skill_dir),
            "files_written": ["SKILL.md", "docs/helper.py"],
            "uri": "skill://my_skill/SKILL.md",
        }
        assert (skill_dir / "docs" / "helper.py").read_text() == "x = 1\n"
        async with Client(server) as client:
            contents = await client.read_resource("skill://my_skill/SKILL.md")
        assert contents[0].text == "# My Skill\n"

    @pytest.mark.asyncio
    async def test_reinstall_reports_updated(self, tmp_path):
        """Installing an already-loaded skill rewrites it and reports ``updated``."""
        skills_root = tmp_path / "skills"
        skills_root.mkdir()
        server = _server(default_skills_dir=str(skills_root))

        await _install(server, skill_name="dup", files={"SKILL.md": "v1"})
        out = await _install(server, skill_name="dup", files={"SKILL.md": "v2"})

        assert out["status"] == "updated"
        assert (skills_root / "dup" / "SKILL.md").read_text() == "v2"

    @pytest.mark.asyncio
    async def test_install_into_vendor_provider(self, isolated_home):
        """A vendor target writes into that vendor's skills root."""
        server = _server(default_skills_dir=None, skills_providers=["claude"])

        out = await _install(
            server, skill_name="vendor_skill", files={"SKILL.md": "c"}, target="claude"
        )

        assert out["status"] == "installed"
        installed = isolated_home / ".claude" / "skills" / "vendor_skill" / "SKILL.md"
        assert installed.read_text() == "c"

    @pytest.mark.asyncio
    async def test_requires_skill_md(self, tmp_path):
        """A file set without ``SKILL.md`` is rejected."""
        server = _server(default_skills_dir=str(tmp_path))
        with pytest.raises(ToolError, match="must include a 'SKILL.md' entry"):
            await _install(server, skill_name="x", files={"helper.py": "x"})

    @pytest.mark.asyncio
    @pytest.mark.parametrize("skill_name", ["../escape", "/abs", "Bad Name", "_x", ""])
    async def test_rejects_invalid_skill_names(self, tmp_path, skill_name):
        """Skill names that are not plain lowercase directory names are refused."""
        skills_root = tmp_path / "skills"
        skills_root.mkdir()
        server = _server(default_skills_dir=str(skills_root))
        with pytest.raises(ToolError, match="Invalid skill name"):
            await _install(server, skill_name=skill_name, files={"SKILL.md": "x"})
        assert list(tmp_path.rglob("SKILL.md")) == []

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "filename", ["../outside.md", "docs/../../outside.md", "/tmp/abs.md"]
    )
    async def test_rejects_files_outside_the_skill(self, tmp_path, filename):
        """File paths that leave the skill directory are refused before anything is written."""
        skills_root = tmp_path / "skills"
        skills_root.mkdir()
        server = _server(default_skills_dir=str(skills_root))
        with pytest.raises(ToolError, match="must be a relative path inside the skill"):
            await _install(
                server, skill_name="ok", files={"SKILL.md": "x", filename: "y"}
            )
        assert list(tmp_path.rglob("*.md")) == []

    @pytest.mark.asyncio
    async def test_unknown_target_lists_loaded_targets(self):
        """An unknown target names every loaded provider in the error."""
        server = _server(skills_providers=["claude", "cursor"])
        with pytest.raises(
            ToolError, match="Available targets: bundled, claude, cursor"
        ):
            await _install(
                server, skill_name="x", files={"SKILL.md": "x"}, target="nope"
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("skills_dir", [None, "missing"])
    async def test_bundled_target_without_bundled_provider(self, tmp_path, skills_dir):
        """Targeting ``bundled`` fails when only vendor providers are loaded."""
        value = str(tmp_path / skills_dir) if skills_dir else None
        server = _server(default_skills_dir=value, skills_providers=["claude"])
        with pytest.raises(ToolError, match="'bundled' not found or not loaded"):
            await _install(server, skill_name="x", files={"SKILL.md": "x"})

    @pytest.mark.asyncio
    async def test_vendor_target_not_loaded(self):
        """Targeting a known vendor that is not loaded fails."""
        server = _server(default_skills_dir=None, skills_providers=["claude"])
        with pytest.raises(ToolError, match="'cursor' not found or not loaded"):
            await _install(
                server, skill_name="x", files={"SKILL.md": "x"}, target="cursor"
            )

    @pytest.mark.asyncio
    async def test_provider_without_roots(self):
        """A matched provider with no root directory is rejected."""
        with patch.dict(
            _VENDOR_SKILLS_PROVIDERS, {"rootless": _RootlessSkillsProvider}
        ):
            server = _server(default_skills_dir=None, skills_providers=["rootless"])
            with pytest.raises(ToolError, match="has no configured root directories"):
                await _install(
                    server, skill_name="x", files={"SKILL.md": "x"}, target="rootless"
                )


class TestBundledSkills:
    """The skill guides shipped with the package."""

    def test_all_expected_skills_present(self):
        """Every expected skill ships as a directory with a ``SKILL.md``."""
        shipped = {d.name for d in SKILLS_DIR.iterdir() if (d / "SKILL.md").is_file()}
        assert shipped == set(EXPECTED_SKILLS)

    @pytest.mark.parametrize(("skill_name", "heading"), EXPECTED_SKILLS.items())
    def test_skill_heading(self, skill_name, heading):
        """The first heading after the frontmatter is the skill's title."""
        lines = (SKILLS_DIR / skill_name / "SKILL.md").read_text("utf-8").splitlines()
        assert lines[0] == "---"
        body = lines[lines.index("---", 1) + 1 :]
        first_heading = next(line for line in body if line.startswith("#"))
        assert first_heading.lstrip("# ").strip() == heading

    @pytest.mark.asyncio
    @pytest.mark.parametrize("skill_name", EXPECTED_SKILLS)
    async def test_skill_served_verbatim(self, skill_name):
        """Each bundled skill is served unchanged at its ``skill://`` URI."""
        content = (SKILLS_DIR / skill_name / "SKILL.md").read_text("utf-8")
        async with Client(_server()) as client:
            served = await client.read_resource(f"skill://{skill_name}/SKILL.md")
        assert len(content) > 500
        assert served[0].text == content
