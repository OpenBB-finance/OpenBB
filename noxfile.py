import nox

test_locations = ["openbb_sdk/sdk/core/tests", "openbb_sdk/providers"]


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
def tests(session):
    session.install("poetry")
    # run a shell command
    session.run("ls", "-la")
    # session.run("sh", "./openbb_sdk/install_all.sh")
    # session.install("pytest")
    # session.install("pytest-cov")
    # session.run("pytest", *test_locations, "--cov=openbb_sdk/")
