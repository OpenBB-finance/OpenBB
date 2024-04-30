"""Platform controller factory to create a platform controller."""

from typing import Dict, List, Union

from openbb_cli.argparse_translator.argparse_class_processor import (
    ArgparseClassProcessor,
)
from openbb_cli.controllers.base_platform_controller import PlatformController


class PlatformControllerFactory:
    """Factory to create a platform controller."""

    def __init__(self, platform_router: type, **kwargs):
        """Create the controller name."""
        self.platform_router = platform_router
        self._translated_target = ArgparseClassProcessor(
            target_class=self.platform_router, reference=kwargs.get("reference", {})
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
        """Create the platform controller."""
        ClassName = self.controller_name
        Parents = (PlatformController,)
        Attributes: Dict[str, Union[bool, List[str]]] = {"CHOICES_GENERATION": True}

        # Menu and Command choices generation
        choices_menus: List[str] = []
        choices_commands: List[str] = []
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
