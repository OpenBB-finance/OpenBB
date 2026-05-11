"""Tests for openbb_cli.codegen.package_gen — top-level orchestrator."""

from __future__ import annotations

from openbb_cli.codegen import package_gen as pkg

# --- _slugify ---


def test_slugify_lowercases_and_collapses_special_chars():
    assert pkg._slugify("US-Congress") == "us_congress"
    assert pkg._slugify("Foo Bar/Baz") == "foo_bar_baz"


def test_slugify_falls_back_when_only_separators():
    assert pkg._slugify("___") == "extension"
    assert pkg._slugify("") == "extension"


# --- generate_packages (orchestrator) ---


def _spec_with_get_command():
    return {
        "base_url": "https://api.example.com/",
        "api_prefix": "api/v1",
        "commands": {
            "equity.search": {
                "providers": ["fmp"],
                "method": "get",
                "url_path": "/equity/search",
                "description": "Search.",
                "parameters": [
                    {
                        "name": "scope",
                        "type": "string",
                        "required": True,
                        "choices": ["all", "active"],
                    },
                ],
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "results": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"symbol": {"type": "string"}},
                            },
                        }
                    },
                },
            }
        },
    }


def test_generate_packages_returns_single_package_with_provider_and_router(tmp_path):
    out = pkg.generate_packages(
        _spec_with_get_command(),
        output_root=tmp_path,
        provider_name="fmp",
    )
    assert isinstance(out, pkg.GeneratedPackageSet)
    assert len(out.packages) == 1
    package = out.packages[0]
    assert isinstance(package, pkg.GeneratedPackage)

    # Project metadata
    assert package.project.project_name == "openbb-fmp"
    assert package.project.package_name == "openbb_fmp"
    # Provider entry registered
    provider_names = [p.provider_name for p in package.providers]
    assert "fmp" in provider_names
    # Single root router named after the provider — every namespace mounts
    # under ``obb.fmp.*`` so the extension never shadows openbb-core's
    # first-party ``obb.equity.*`` etc.
    assert package.top_level_routers == ["fmp"]
    # The per-namespace router file still exists; it's just not an entry point
    sub_module_names = {r.module_name for r in package.routers.routers}
    assert {"fmp", "equity"} <= sub_module_names
    # Fetcher registered for fmp
    assert package.fetchers_by_provider["fmp"][0].model_name == "EquitySearch"


def test_generate_packages_skips_coverage_namespace(tmp_path):
    spec = {
        "base_url": "https://api.example.com",
        "api_prefix": "",
        "commands": {
            "coverage.providers": {"providers": ["openbb"], "method": "get"},
            "equity.search": {
                "providers": ["fmp"],
                "method": "get",
                "url_path": "/equity/search",
                "response_schema": {"type": "object"},
            },
        },
    }
    out = pkg.generate_packages(spec, output_root=tmp_path, provider_name="fmp")
    assert "coverage" not in out.packages[0].top_level_routers


def test_generate_packages_emits_post_command_under_tools_provider(tmp_path):
    spec = {
        "base_url": "https://api.example.com",
        "api_prefix": "",
        "commands": {
            "econometrics.regression": {
                "providers": [],  # local-compute
                "method": "post",
                "url_path": "/econometrics/regression",
                "description": "OLS.",
                "request_body_schema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"v": {"type": "number"}},
                            },
                        }
                    },
                    "required": ["data"],
                },
                "response_schema": {"type": "object"},
            }
        },
    }
    out = pkg.generate_packages(spec, output_root=tmp_path, provider_name="tools")
    pack = out.packages[0]
    # Synthetic ``tools`` provider added when there are POST commands
    assert any(p.provider_name == "tools" for p in pack.providers)
    assert len(pack.post_commands) == 1
    assert pack.post_commands[0].function_name == "econometrics_regression"


def test_generate_packages_falls_back_to_synthetic_provider_when_spec_has_none(
    tmp_path,
):
    spec = {
        "base_url": "https://api.example.com",
        "api_prefix": "",
        "commands": {
            "equity.search": {
                "providers": [],  # no provider on the command either
                "method": "get",
                "url_path": "/equity/search",
                "response_schema": {"type": "object"},
            }
        },
    }
    out = pkg.generate_packages(spec, output_root=tmp_path, provider_name="myprov")
    pack = out.packages[0]
    # Synthetic provider takes the slugified provider_name
    assert any(p.provider_name == "myprov" for p in pack.providers)


def test_generate_packages_skips_command_with_provider_list_no_owners(tmp_path):
    spec = {
        "base_url": "https://api.example.com",
        "api_prefix": "",
        "commands": {
            "equity.search": {
                "providers": ["nope"],  # ``nope`` not in target_providers
                "method": "get",
                "url_path": "/equity/search",
                "response_schema": {"type": "object"},
            },
            # second command keeps ``fmp`` in target_providers so the
            # ``no owners`` branch (line 290) actually fires
            "equity.quote": {
                "providers": ["fmp"],
                "method": "get",
                "url_path": "/equity/quote",
                "response_schema": {"type": "object"},
            },
        },
    }
    out = pkg.generate_packages(spec, output_root=tmp_path, provider_name="x")
    pack = out.packages[0]
    # ``equity.search`` has no owners (no ``nope`` in targets) → skipped
    # ``equity.quote`` belongs to fmp → only that fetcher emitted
    fmp_fetchers = pack.fetchers_by_provider.get("fmp", [])
    assert {f.model_name for f in fmp_fetchers} == {"EquityQuote"}


def test_generate_packages_respects_explicit_project_overrides(tmp_path):
    out = pkg.generate_packages(
        _spec_with_get_command(),
        output_root=tmp_path,
        provider_name="fmp",
        project_name="my-custom-name",
        package_name="my_pkg",
        description="Custom desc.",
        website="https://custom.example",
        version="1.2.3",
    )
    project = out.packages[0].project
    assert project.project_name == "my-custom-name"
    assert project.package_name == "my_pkg"
    assert "Custom desc." in project.source
    assert "1.2.3" in project.source


# --- GeneratedPackage.write + _readme + GeneratedPackageSet.write ---


def test_generated_package_set_write_materializes_full_project_on_disk(tmp_path):
    out = pkg.generate_packages(
        _spec_with_get_command(),
        output_root=tmp_path,
        provider_name="fmp",
    )
    written_paths = out.write()
    assert len(written_paths) == 1
    project_root = written_paths[0]
    assert project_root.exists()

    # pyproject.toml + README + package layout
    assert (project_root / "pyproject.toml").exists()
    assert (project_root / "README.md").exists()
    pkg_dir = project_root / "openbb_fmp"
    assert (pkg_dir / "__init__.py").exists()
    assert (pkg_dir / "providers" / "__init__.py").exists()
    assert (pkg_dir / "routers" / "__init__.py").exists()
    # Provider source written
    fmp_init = pkg_dir / "providers" / "fmp" / "__init__.py"
    assert fmp_init.exists()
    assert "fmp_provider" in fmp_init.read_text()
    # Fetcher module written
    assert (pkg_dir / "providers" / "fmp" / "models" / "equity_search.py").exists()
    # Router written
    assert (pkg_dir / "routers" / "equity.py").exists()


def test_generated_package_write_creates_tools_dir_when_post_commands_present(tmp_path):
    spec = {
        "base_url": "https://api.example.com",
        "api_prefix": "",
        "commands": {
            "econometrics.regression": {
                "providers": [],
                "method": "post",
                "url_path": "/r",
                "description": "OLS.",
                "request_body_schema": {
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {"v": {"type": "number"}},
                            },
                        }
                    },
                    "required": ["data"],
                },
                "response_schema": {"type": "object"},
            }
        },
    }
    out = pkg.generate_packages(spec, output_root=tmp_path, provider_name="tools")
    out.write()
    project_root = out.packages[0].root
    tools_models = project_root / "openbb_tools" / "providers" / "tools" / "models"
    assert tools_models.exists()
    assert (tools_models / "econometrics_regression.py").exists()


def test_generated_package_write_does_not_overwrite_existing_init_files(tmp_path):
    out = pkg.generate_packages(
        _spec_with_get_command(),
        output_root=tmp_path,
        provider_name="fmp",
    )
    package = out.packages[0]
    package.root.mkdir(parents=True, exist_ok=True)
    pkg_dir = package.root / "openbb_fmp"
    pkg_dir.mkdir(parents=True, exist_ok=True)
    custom_init = pkg_dir / "__init__.py"
    custom_init.write_text("# user-edited content\n")

    package.write()

    # The pre-existing init file is preserved (write skips when file exists)
    assert custom_init.read_text() == "# user-edited content\n"


def test_generated_package_readme_lists_providers_and_routers(tmp_path):
    out = pkg.generate_packages(
        _spec_with_get_command(),
        output_root=tmp_path,
        provider_name="fmp",
    )
    readme = out.packages[0]._readme()
    assert "openbb-fmp" in readme
    assert "**fmp**" in readme
    assert "obb.fmp.*" in readme
    assert "pip install -e ." in readme


def test_generated_package_set_write_with_no_packages_returns_empty_list():
    empty = pkg.GeneratedPackageSet(packages=[])
    assert empty.write() == []


# --- README content + ruff post-processing ---


def _spec_with_credentials():
    spec = _spec_with_get_command()
    spec["commands"]["equity.search"]["parameters"].append(
        {"name": "apikey", "type": "string", "in": "query"}
    )
    return spec


def test_generated_package_readme_renders_command_tree_and_quick_start(tmp_path):
    out = pkg.generate_packages(
        _spec_with_get_command(),
        output_root=tmp_path,
        provider_name="fmp",
    )
    readme = out.packages[0]._readme()
    # Quick start block points at the actual command surface
    assert "from openbb import obb" in readme
    assert "obb.fmp.equity.search" in readme
    # Commands section includes the dotted path under the right top group
    assert "## Commands" in readme
    assert "### `obb.fmp.equity`" in readme
    assert "`obb.fmp.equity.search` — provider: `fmp`" in readme


def test_generated_package_readme_renders_credentials_section(tmp_path):
    out = pkg.generate_packages(
        _spec_with_credentials(),
        output_root=tmp_path,
        provider_name="fmp",
    )
    readme = out.packages[0]._readme()
    assert "## Credentials" in readme
    assert "`apikey`" in readme


def test_generated_package_readme_handles_provider_with_no_commands(tmp_path):
    """``_first_command_example`` skips providers whose command list is empty."""
    out = pkg.generate_packages(
        _spec_with_get_command(),
        output_root=tmp_path,
        provider_name="fmp",
    )
    package = out.packages[0]
    # Inject an empty-command provider — the example helper must keep walking.
    package.commands_by_provider = {"empty_prov": [], **package.commands_by_provider}
    example = package._first_command_example("fmp")
    assert example is not None
    assert example[0] == "equity.search"


def test_generated_package_readme_returns_none_when_no_commands_at_all(tmp_path):
    out = pkg.generate_packages(
        _spec_with_get_command(),
        output_root=tmp_path,
        provider_name="fmp",
    )
    package = out.packages[0]
    package.commands_by_provider = {}
    assert package._first_command_example("fmp") is None
    # README still renders; just no Quick start snippet
    readme = package._readme()
    assert "from openbb import obb" not in readme


def test_generated_package_write_runs_ruff_when_available(tmp_path, monkeypatch):
    """The post-write step shells out to ``ruff check`` and ``ruff format``."""
    calls: list[list[str]] = []

    def _fake_run(cmd, **kwargs):
        calls.append(list(cmd))

        class _Result:
            returncode = 0

        return _Result()

    monkeypatch.setattr(pkg, "_find_ruff", lambda: "/fake/ruff")
    monkeypatch.setattr(pkg.subprocess, "run", _fake_run)

    out = pkg.generate_packages(
        _spec_with_get_command(),
        output_root=tmp_path,
        provider_name="fmp",
    )
    out.write()

    assert any("check" in c for c in calls)
    assert any("format" in c for c in calls)
    assert all(c[0] == "/fake/ruff" for c in calls)


def test_generated_package_write_skips_ruff_when_not_installed(tmp_path, monkeypatch):
    """Missing ``ruff`` binary -> silent no-op."""
    monkeypatch.setattr(pkg, "_find_ruff", lambda: None)
    called: list[list[str]] = []
    monkeypatch.setattr(
        pkg.subprocess,
        "run",
        lambda cmd, **k: called.append(list(cmd)),
    )

    out = pkg.generate_packages(
        _spec_with_get_command(),
        output_root=tmp_path,
        provider_name="fmp",
    )
    out.write()
    assert called == []


def test_find_ruff_prefers_sibling_binary(tmp_path, monkeypatch):
    """``ruff`` next to the running Python wins over the PATH lookup."""
    fake_python = tmp_path / "python"
    fake_python.write_text("")
    fake_ruff = tmp_path / "ruff"
    fake_ruff.write_text("")
    monkeypatch.setattr(pkg.sys, "executable", str(fake_python))
    monkeypatch.setattr(pkg.shutil, "which", lambda name: "/elsewhere/ruff")
    assert pkg._find_ruff() == str(fake_ruff)


def test_find_ruff_falls_back_to_path_lookup(tmp_path, monkeypatch):
    """No sibling ruff -> shutil.which result is returned."""
    fake_python = tmp_path / "python"
    fake_python.write_text("")
    monkeypatch.setattr(pkg.sys, "executable", str(fake_python))
    monkeypatch.setattr(pkg.shutil, "which", lambda name: "/found/on/path/ruff")
    assert pkg._find_ruff() == "/found/on/path/ruff"


def test_find_ruff_returns_none_when_unavailable(tmp_path, monkeypatch):
    fake_python = tmp_path / "python"
    fake_python.write_text("")
    monkeypatch.setattr(pkg.sys, "executable", str(fake_python))
    monkeypatch.setattr(pkg.shutil, "which", lambda name: None)
    assert pkg._find_ruff() is None
