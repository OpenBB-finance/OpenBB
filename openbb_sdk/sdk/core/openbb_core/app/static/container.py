from openbb_core.app.command_runner import CommandRunnerSession


class Container:

    def __init__(self, command_runner_session: CommandRunnerSession) -> None:
        self._command_runner_session = command_runner_session
