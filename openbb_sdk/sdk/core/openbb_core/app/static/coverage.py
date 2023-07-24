from openbb_core.app.router import CommandMap


class Coverage:
    def __init__(self):
        self.__command_map = CommandMap()

    @property
    def providers(self):
        return self.__command_map.provider_coverage

    @property
    def commands(self):
        return self.__command_map.command_coverage
