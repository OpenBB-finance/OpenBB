import nox


@nox.session(python=["3.8", "3.9", "3.10", "3.11"])
def tests(session):
    session.install("./openbb_sdk")
    session.install("pytest")
    session.run("pytest", "openbb_sdk/sdk/core/tests")
