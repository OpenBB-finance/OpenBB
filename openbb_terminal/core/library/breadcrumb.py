from typing import Any, Optional, List
import openbb_terminal.config_terminal as cfg

from openbb_terminal.core.library.metadata import Metadata
from openbb_terminal.core.library.trail_map import TrailMap
from openbb_terminal.core.library.operation import Operation


class MetadataBuilder:
    @staticmethod
    def build_dir_list(trail: str, trail_map: TrailMap) -> List[str]:
        option_list = []
        for key in trail_map.map_dict:
            if trail == "":
                option = key.split(".")[0]
            elif key.startswith(trail):
                option = key[len(trail) + 1 :].split(".")[0]
            else:
                option = None

            if option:
                option_list.append(option)

        return list(set(option_list))

    @staticmethod
    def build_doc_string(trail: str, dir_list: List[str]) -> str:
        if trail == "":
            doc_string = """This is the OpenBB Terminal SDK.
            Use the SDK to get data directly into your jupyter notebook or directly use it in your application.
            For more information see the official documentation at: https://openbb-finance.github.io/OpenBBTerminal/SDK/
            """
        else:
            doc_string = (
                trail.rsplit(".")[-1].upper()
                + " Menu\n\nThe SDK commands of the the menu:"
            )
            for command in dir_list:
                doc_string += f"\n\t<openbb>.{trail}.{command}"

        return doc_string

    @classmethod
    def build(cls, trail: str, trail_map: TrailMap) -> Metadata:
        dir_list = cls.build_dir_list(trail=trail, trail_map=trail_map)
        doc_string = cls.build_doc_string(trail=trail, dir_list=dir_list)
        metadata = Metadata(
            dir_list=dir_list,
            doc_string=doc_string,
        )
        return metadata


class Breadcrumb:
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

        self.__doc__ = metadata.doc_string

        if trail == "":
            BreadcrumbLogger()

    def __dir__(self):
        return self._metadata.dir_list

    def __getattr__(self, name: str) -> Any:
        trail = self._trail
        trail_map = self._trail_map

        if trail == "":
            trail_next = name
        else:
            trail_next = f"{trail}.{name}"

        if Operation.is_valid(trail=trail_next, trail_map=trail_map):
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


# pylint: disable=R0903
class BreadcrumbLogger:
    def __init__(self) -> None:
        self.__check_initialize_logging()

    def __check_initialize_logging(self):
        if not cfg.LOGGING_SUPPRESS:
            self.__initialize_logging()

    @staticmethod
    def __initialize_logging() -> None:
        from openbb_terminal.loggers import setup_logging  # pylint: disable=C0415
        from openbb_terminal.core.log.generation.settings_logger import (  # pylint: disable=C0415
            log_all_settings,
        )

        cfg.LOGGING_SUB_APP = "sdk"
        setup_logging()
        log_all_settings()
