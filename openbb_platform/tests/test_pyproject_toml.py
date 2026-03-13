"""Test the pyproject.toml file for consistency and its dependencies."""

from pathlib import Path

from tomlkit import load

ROOT_DIR = Path(__file__).parent.parent


def test_optional_packages():
    """Ensure only required extensions are built and versions respect pyproject.toml"""
    with open(ROOT_DIR / "pyproject.toml") as f:
        data = load(f)
    dependencies = data["tool"]["poetry"]["dependencies"]  # type: ignore
    extras = data["tool"]["poetry"]["extras"]  # type: ignore
    all_packages = extras["all"]  # type: ignore

    default_packages = []
    optional_packages = []

    for package, details in dependencies.items():  # type: ignore
        if isinstance(details, dict) and details.get("optional") is True:
            optional_packages.append(package)
        else:
            default_packages.append(package)

    # check that optional packages have the same content as all_packages and extras
    assert sorted(optional_packages) == sorted(all_packages)  # type: ignore
    assert sorted(optional_packages) == sorted(extras["all"])  # type: ignore

    # assert that there is no overlap between default and optional packages
    assert set(default_packages).isdisjoint(set(optional_packages))


def test_extension_versions_match_main_pyproject():
    """Ensure every openbb- extension version in the main pyproject.toml matches its own pyproject.toml."""

    main_pyproject = ROOT_DIR / "pyproject.toml"
    with open(main_pyproject, encoding="utf-8") as f:
        main_data = load(f)
    main_deps = main_data["tool"]["poetry"]["dependencies"]  # type: ignore

    # Find all pyproject.toml files and build a map of package name -> file path
    pyproject_files = list(ROOT_DIR.rglob("pyproject.toml"))
    package_map = {}

    for file_path in pyproject_files:
        with open(file_path, encoding="utf-8") as f:
            data = load(f)
        pkg_name = data.get("tool", {}).get("poetry", {}).get("name", "")
        if pkg_name:
            package_map[pkg_name] = str(file_path)

    # Now check each openbb- dependency in main pyproject.toml
    for pkg, main_version in main_deps.items():  # type: ignore
        if pkg.startswith("openbb-"):
            assert (
                pkg in package_map
            ), f"{pkg} listed in main pyproject.toml but no pyproject.toml found with that name"

            # Load the extension's pyproject.toml
            with open(package_map[pkg], encoding="utf-8") as f:
                ext_data = load(f)
            ext_version = ext_data["tool"]["poetry"]["version"]  # type: ignore

            # Normalize main_version if it's a dict
            m_version = (
                main_version.get("version", "")
                if isinstance(main_version, dict)
                else main_version
            )
            m_version = str(m_version).lstrip("^")

            assert ext_version == m_version, (
                f"Version mismatch for {pkg}: main pyproject.toml has"
                f"{m_version}, extension pyproject.toml has {ext_version}"
            )
