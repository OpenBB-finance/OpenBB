from typing import Any, List, Optional

import openbb_terminal.config_terminal as cfg
from openbb_terminal import feature_flags as obbff
from openbb_terminal.core.library.metadata import Metadata
from openbb_terminal.core.library.operation import Operation
from openbb_terminal.core.library.trail_map import TrailMap

# pylint: disable=import-outside-toplevel


class MetadataBuilder:
    @staticmethod
    def get_option_list(trail: str, trail_map: TrailMap) -> List[str]:
        option_list = []
        for key in trail_map.map_dict:
            if trail == "":
                option = key.split(".")[0]
            elif key.startswith(trail) and key[len(trail)] == ".":
                option = key[len(trail) + 1 :].split(".")[0]
            else:
                option = None

            if option:
                option_list.append(option)

        return list(set(option_list))

    @classmethod
    def build_dir_list(cls, trail: str, trail_map: TrailMap) -> List[str]:
        option_list = cls.get_option_list(trail=trail, trail_map=trail_map)

        option_list_full = []
        for option in option_list:
            option_list_full.append(option)

            option_view_trail = f"{trail}.{option}_chart"
            if trail_map.get_view_function(trail=option_view_trail):
                option_list_full.append(f"{option}_chart")

        return option_list_full

    @staticmethod
    def build_docstring(trail: str, dir_list: List[str]) -> str:
        if trail == "":
            docstring = """This is the OpenBB Terminal SDK.
            Use the SDK to get data directly into your jupyter notebook or directly use it in your application.
            For more information see the official documentation at: https://openbb-finance.github.io/OpenBBTerminal/SDK/
            """
        else:
            docstring = (
                trail.rsplit(".")[-1].upper()
                + " Menu\n\nThe SDK commands of the the menu:"
            )
            for command in dir_list:
                docstring += f"\n\t<openbb>.{trail}.{command}"

        return docstring

    @classmethod
    def build(cls, trail: str, trail_map: TrailMap) -> Metadata:
        dir_list = cls.build_dir_list(trail=trail, trail_map=trail_map)
        docstring = cls.build_docstring(trail=trail, dir_list=dir_list)
        metadata = Metadata(
            dir_list=dir_list,
            docstring=docstring,
        )
        return metadata


class Breadcrumb:
    __version__ = obbff.VERSION

    def __init__(
        self,
        metadata: Optional[Metadata] = None,
        trail: str = "",
        trail_map: Optional[TrailMap] = None,
    ) -> None:
        """
        Generates a 'trail' that allows accessing OpenBB Terminal SDK methods.

        Example:
            openbb.forex.get_currency_list()
            Breadcrumb(trail="").Breadcrumb(trail="forex").Operation(trail="forex.get_currency_list")()

        Args:
            metadata (Optional[Metadata], optional):
                Object to generate Breadcrumb's metadata (__dir__, __doc__).
                Defaults to None.
            trail (str, optional):
                Current trail of the Breadcrumb.
                Defaults to "".
            trail_map (Optional[TrailMap], optional):
                Mapping with all the trails available and matching models and views.
                Defaults to None.
        """
        trail_map = trail_map or TrailMap()
        metadata = metadata or MetadataBuilder.build(trail=trail, trail_map=trail_map)

        self._metadata = metadata
        self._trail_map = trail_map
        self._trail = trail

        self.__doc__ = metadata.docstring
        if trail == "":
            BreadcrumbLogger()

    def __dir__(self):
        return self._metadata.dir_list

    def __getattr__(self, name: str) -> Any:
        trail = self._trail
        trail_map = self._trail_map

        trail_next = name if trail == "" else f"{trail}.{name}"

        if trail_map.get_model_function(
            trail=trail_next
        ) or trail_map.get_view_function(trail=trail_next):
            next_crumb: Any = Operation(
                trail=trail_next,
                trail_map=trail_map,
            )
        elif name in self._metadata.dir_list:
            next_crumb = Breadcrumb(
                metadata=MetadataBuilder.build(trail=trail_next, trail_map=trail_map),
                trail=trail_next,
                trail_map=trail_map,
            )
        else:
            raise AttributeError(
                f"Module or method '{trail}' has no attribute '{name}'."
            )

        return next_crumb

    def about(self):
        import webbrowser

        trail = self._trail
        url = "https://docs.openbb.co/sdk/reference/"
        url += "/".join(trail.split("."))
        webbrowser.open(url)


# pylint: disable=R0903
class BreadcrumbLogger:
    def __init__(self) -> None:
        self.__check_initialize_logging()

    def __check_initialize_logging(self):
        if not cfg.LOGGING_SUPPRESS:
            self.__initialize_logging()

    @staticmethod
    def __initialize_logging() -> None:
        from openbb_terminal.core.log.generation.settings_logger import (  # pylint: disable=C0415
            log_all_settings,
        )
        from openbb_terminal.loggers import setup_logging  # pylint: disable=C0415

        cfg.LOGGING_SUB_APP = "sdk"
        setup_logging()
        log_all_settings()
