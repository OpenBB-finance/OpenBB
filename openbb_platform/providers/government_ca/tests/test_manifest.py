"""Government of Canada pyproject.toml manifest smoke tests."""

from pathlib import Path

try:
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib  # type: ignore[no-redef]


def _load_manifest() -> dict:
    """Parse the package pyproject.toml into a dict."""
    import openbb_government_ca

    root = Path(openbb_government_ca.__file__).parent.parent
    with (root / "pyproject.toml").open("rb") as file:
        return tomllib.load(file)


def test_build_system():
    """The build-system uses Hatchling and requires requests."""
    build_system = _load_manifest()["build-system"]

    assert build_system["build-backend"] == "hatchling.build"
    requires = build_system["requires"]
    assert any(req.startswith("hatchling") for req in requires)
    assert any(req.startswith("requests") for req in requires)


def test_project_metadata():
    """The project metadata matches the V5 packaging contract."""
    project = _load_manifest()["project"]

    assert project["name"] == "openbb-government-ca"
    assert project["version"] == "2.0.0"
    assert project["license"]["text"] == "AGPL-3.0-only"
    assert project["requires-python"] == ">=3.10,<4"


def test_runtime_dependency():
    """The runtime depends on openbb-core[pandas]>=2.0.0."""
    dependencies = _load_manifest()["project"]["dependencies"]

    assert "openbb-core[pandas]>=2.0.0" in dependencies


def test_uv_sources():
    """uv.sources maps core and devtools to editable local paths."""
    sources = _load_manifest()["tool"]["uv"]["sources"]

    assert sources["openbb-core"]["path"] == "../../core"
    assert sources["openbb-core"]["editable"] is True
    assert sources["openbb-devtools"]["path"] == "../../extensions/devtools"
    assert sources["openbb-devtools"]["editable"] is True


def test_ruff_config():
    """ruff is configured for line-length 88, py310, aliases, and PLC0415."""
    ruff = _load_manifest()["tool"]["ruff"]

    assert ruff["line-length"] == 88
    assert ruff["target-version"] == "py310"

    aliases = ruff["lint"]["flake8-import-conventions"]["aliases"]
    assert aliases["pandas"] == "pd"
    assert aliases["numpy"] == "np"
    assert aliases["openbb"] == "obb"

    assert "PLC0415" in ruff["lint"]["ignore"]


def test_ty_config():
    """ty targets python 3.10 and warns on unresolved imports."""
    ty = _load_manifest()["tool"]["ty"]

    assert ty["environment"]["python-version"] == "3.10"
    assert ty["rules"]["unresolved-import"] == "warn"


def test_pytest_config():
    """pytest discovers tests under the tests directory."""
    pytest_options = _load_manifest()["tool"]["pytest"]["ini_options"]

    assert pytest_options["testpaths"] == ["tests"]


def test_hatch_build_hook():
    """The custom build hook points at hatch_build.py."""
    hooks = _load_manifest()["tool"]["hatch"]["build"]["hooks"]

    assert hooks["custom"]["path"] == "hatch_build.py"


def test_wheel_target():
    """The wheel target packages the importable package."""
    wheel = _load_manifest()["tool"]["hatch"]["build"]["targets"]["wheel"]

    assert wheel["packages"] == ["openbb_government_ca"]


def test_sdist_target():
    """The sdist target ships package, asset, hook, README, and manifest."""
    sdist = _load_manifest()["tool"]["hatch"]["build"]["targets"]["sdist"]
    include = sdist["include"]

    assert "openbb_government_ca" in include
    assert (
        "openbb_government_ca/assets/government_ca_cache.json.xz" in include
    )
    assert "hatch_build.py" in include
    assert "README.md" in include
    assert "pyproject.toml" in include


def test_entry_points():
    """Both provider and core extension entry points are declared."""
    entry_points = _load_manifest()["project"]["entry-points"]

    provider = entry_points["openbb_provider_extension"]
    assert provider["government_ca"] == "openbb_government_ca:government_ca_provider"

    core = entry_points["openbb_core_extension"]
    assert (
        core["government_ca"]
        == "openbb_government_ca.government_ca_router:router"
    )


def test_cache_console_script():
    """The cache generation console script resolves to the generator main."""
    scripts = _load_manifest()["project"]["scripts"]

    assert (
        scripts["generate-government-ca-cache"]
        == "openbb_government_ca.utils.generate_cache:main"
    )


def test_no_credentials_configuration():
    """No credentials configuration appears anywhere in the manifest."""
    manifest = _load_manifest()
    rendered = str(manifest).lower()

    assert "credential" not in rendered
    assert "api_key" not in rendered
    assert "apikey" not in rendered
