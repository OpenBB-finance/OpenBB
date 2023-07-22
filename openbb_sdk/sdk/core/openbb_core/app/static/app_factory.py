# pylint: disable=W0231:super-init-not-called

from openbb_core.app.command_runner import CommandRunnerSession


def create_app():
    try:
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.static.package.__app__ import App
    except ImportError as e:
        raise Exception(
            "If you are seeing this exception, you should probably be doing: "
            "from openbb_core.app.static.package_builder import PackageBuilder\n"
            "PackageBuilder.build()"
        ) from e

    return App(command_runner_session=CommandRunnerSession())
