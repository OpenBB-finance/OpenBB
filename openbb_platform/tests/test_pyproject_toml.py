import toml


def test_optional_packages():
    data = toml.load("openbb_platform/pyproject.toml")
    dependencies = data["tool"]["poetry"]["dependencies"]
    extras = data["tool"]["poetry"]["extras"]
    all_packages = extras["all"]

    default_packages = []
    optional_packages = []

    for package, details in dependencies.items():
        if isinstance(details, dict) and details.get("optional") is True:
            optional_packages.append(package)
        else:
            default_packages.append(package)

    # check that optional packages have the same content as all_packages and extras
    assert sorted(optional_packages) == sorted(all_packages)
    assert sorted(optional_packages) == sorted(extras["all"])

    # assert that there is no overlap between default and optional packages
    assert set(default_packages).isdisjoint(set(optional_packages))
