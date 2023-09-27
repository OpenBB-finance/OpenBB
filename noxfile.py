import nox

test_locations = [
    "openbb_sdk/tests",
    "openbb_sdk/sdk",
    "openbb_sdk/providers",
]


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
def tests(session):
    session.install("poetry", "toml")
    session.run("python", "./openbb_sdk/dev_install.py", external=True)
    session.install("pytest")
    session.install("pytest-cov")
    session.run("pytest", *test_locations, "--cov=openbb_sdk/")
