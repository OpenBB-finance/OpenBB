from openbb_core.app.router import CommandMap


class Coverage:
    def __init__(self):
        self._command_map = CommandMap(sep=".")

    @property
    def providers(self):
        return self._command_map.provider_coverage

    @property
    def commands(self):
        return self._command_map.command_coverage
