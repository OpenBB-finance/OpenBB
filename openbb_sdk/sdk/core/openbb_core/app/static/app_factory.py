# pylint: disable=W0231:super-init-not-called

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Callable


def run_async(func: Callable, *args, **kwargs):
    try:
        asyncio.get_running_loop()
        with ThreadPoolExecutor(1) as pool:
            result = pool.submit(lambda: asyncio.run(func(*args, **kwargs))).result()
    except RuntimeError:
        result = asyncio.run(func(*args, **kwargs))

    return result


def create_app():
    return App(command_runner_session=CommandRunnerSession())


try:
    from openbb_core.api.dependency.system import get_system_settings
    from openbb_core.app.command_runner import CommandRunnerSession
    from openbb_core.app.model.system_settings import SystemSettings
    from openbb_core.app.model.user_settings import UserSettings
    from openbb_core.app.static.account import Account
    from openbb_core.app.static.coverage import Coverage
    from openbb_core.app.static.package.MODULE_ import CLASS_
except ImportError:
    app = None
else:

    class App(CLASS_):
        """App class."""

        def __init__(self, command_runner_session):
            self._command_runner_session = command_runner_session
            self._account = Account(self)
            self._coverage = Coverage()

        @property
        def account(self) -> Account:
            return self._account

        @property
        def settings(self) -> UserSettings:
            return self._command_runner_session.user_settings

        @property
        def system(self) -> SystemSettings:
            return run_async(get_system_settings)

        @property
        def coverage(self) -> Coverage:
            return self._coverage

    app = create_app()
