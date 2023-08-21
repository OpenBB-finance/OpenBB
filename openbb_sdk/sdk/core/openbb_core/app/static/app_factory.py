"""App factory."""
# pylint: disable=W0231:super-init-not-called

from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.static.account import Account
from openbb_core.app.static.coverage import Coverage


def create_app():
    """Create the app."""
    try:
        # pylint: disable=import-outside-toplevel
        from openbb_core.app.static.package.__extensions__ import Extensions
    except ImportError as e:
        raise Exception(
            "If you are seeing this exception, you should probably be doing: "
            "from openbb_core.app.static.package_builder import PackageBuilder\n"
            "PackageBuilder.build()"
        ) from e

    class App(Extensions):
        """Here you can access all the basic utility menus and extensions.

        Basic utility menus:
            - account
            - user
            - system
            - coverage

        Built-in extensions:
            - charting
            - crypto
            - economy
            - fixedincome
            - forex
            - futures
            - news
            - stocks
        """

        def __init__(self, command_runner):
            self._command_runner = command_runner
            self._account = Account(self)
            self._coverage = Coverage()

        @property
        def account(self) -> Account:
            return self._account

        @property
        def user(self) -> UserSettings:
            return self._command_runner.user_settings

        @property
        def system(self) -> SystemSettings:
            return self._command_runner.system_settings

        @property
        def coverage(self) -> Coverage:
            return self._coverage

    return App(command_runner=CommandRunner())
