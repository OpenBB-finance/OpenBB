import nox

test_locations = [
    "openbb_platform/tests",
    "openbb_platform/core",
    "openbb_platform/providers",
    "openbb_platform/extensions",
]


@nox.session(python=["3.9", "3.10", "3.11"])
def tests(session):
    session.install("poetry", "toml")
    session.run(
        "python",
        "./openbb_platform/dev_install.py",
        "-e",
        "all",
        external=True,
    )
    session.install("pytest")
    session.install("pytest-cov")
    session.run(
        "pytest", *test_locations, "--cov=openbb_platform/", "-m", "not integration"
    )
