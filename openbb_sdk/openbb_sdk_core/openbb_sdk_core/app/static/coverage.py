from openbb_sdk_core.app.router import CommandMap


class Coverage:
    def __init__(self):
        self.cmap = CommandMap()

    @property
    def provider(self):
        return self.cmap.provider_coverage

    @property
    def command(self):
        return self.cmap.command_coverage
