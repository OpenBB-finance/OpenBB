import nox

test_locations = [
    "tests",
    "core",
    "providers",
    "extensions",
]


@nox.session(python=["3.9", "3.10", "3.11"])
def tests(session):
    session.install("poetry", "toml")
    session.run(
        "python",
        "dev_install.py",
        "-e",
        "all",
        external=True,
    )
    session.install("pytest")
    session.install("pytest-cov")
    session.run("pytest", *test_locations, "--cov=.", "-m", "not integration")
