import nox

test_locations = ["openbb_sdk/sdk/core/tests", "openbb_sdk/providers/tests"]


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
def tests(session):
    session.install("-e ./openbb_sdk[all]")
    session.install("pytest")
    session.install("pytest-cov")
    session.run("pytest", *test_locations, "--cov=openbb_sdk/")
