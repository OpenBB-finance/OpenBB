from argparse_translator.argparse_class_processor import ArgparseClassProcessor
from openbb_terminal.base_platform_controller import PlatformController


class PlatformControllerFactory:
    def __init__(self, platform_router: type):
        self.platform_router = platform_router
        self._translated_target = ArgparseClassProcessor(
            target_class=self.platform_router
        )
        self.router_name = (
            str(type(self.platform_router))
            .rsplit(".", maxsplit=1)[-1]
            .replace("'>", "")
            .replace("ROUTER_", "")
            .lower()
        )
        self.controller_name = f"{self.router_name.capitalize()}Controller"

    def create(self) -> type:
        ClassName = self.controller_name
        Parents = (PlatformController,)
        Attributes = {"CHOICES_GENERATION": True}

        # Menu and Command choices generation
        choices_menus = []
        choices_commands = []
        translators = self._translated_target.translators
        paths = self._translated_target.paths
        # menus
        for key, value in paths.items():
            if value == "path":
                continue
            choices_menus.append(key)
        # commands
        for name, _ in translators.items():
            if any(f"{self.router_name}_{path}" in name for path in paths):
                continue
            new_name = name.replace(f"{self.router_name}_", "")
            choices_commands.append(new_name)

        Attributes["CHOICES_MENUS"] = choices_menus
        Attributes["CHOICES_COMMANDS"] = choices_commands

        # Use type to create the class
        DynamicClass = type(ClassName, Parents, Attributes)

        return DynamicClass
