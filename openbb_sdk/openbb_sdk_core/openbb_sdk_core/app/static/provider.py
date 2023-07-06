from openbb_sdk_core.app.router import CommandMap


class Provider:
    def __init__(self):
        self.cmap = CommandMap()

    @property
    def coverage(self):
        return self.cmap.provider_coverage
