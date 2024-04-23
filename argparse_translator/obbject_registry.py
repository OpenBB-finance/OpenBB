"""Registry for OBBjects."""

import json
from typing import Dict, List

from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.obbject import OBBject


class Registry(metaclass=SingletonMeta):

    obbjects: List[OBBject] = []

    @staticmethod
    def _contains_obbject(uuid: str, obbjects: List[OBBject]) -> bool:
        """Check if obbject with uuid is in the registry."""
        return any(obbject.id == uuid for obbject in obbjects)

    @classmethod
    def register(cls, obbject: OBBject):
        """Designed to add an OBBject instance to the registry."""
        if isinstance(obbject, OBBject) and not cls._contains_obbject(
            obbject.id, cls.obbjects
        ):
            cls.obbjects.append(obbject)

    @classmethod
    def get(cls, idx: int) -> OBBject:
        """Return the obbject at index idx."""
        # the list should work as a stack
        # i.e., the last element needs to be accessed by idx=0 and so on
        reversed_list = list(reversed(cls.obbjects))
        return reversed_list[idx]

    @property
    def all(self) -> Dict[int, Dict]:
        """Return all obbjects in the registry"""

        def _handle_standard_params(obbject: OBBject) -> str:
            """Handle standard params for obbjects"""
            standard_params_json = ""
            std_params = obbject._standard_params  # pylint: disable=protected-access
            if hasattr(std_params, "__dict__"):
                standard_params = {
                    k: str(v)[:30] for k, v in std_params.__dict__.items() if v
                }
                standard_params_json = json.dumps(standard_params)

            return standard_params_json

        def _handle_data_repr(obbject: OBBject) -> str:
            """Handle data representation for obbjects"""
            data_repr = ""
            if hasattr(obbject, "results") and obbject.results:
                data_schema = (
                    obbject.results[0].model_json_schema()
                    if obbject.results and isinstance(obbject.results, list)
                    else ""
                )
                if data_schema and "title" in data_schema:
                    data_repr = f"{data_schema['title']}"
                if data_schema and "description" in data_schema:
                    data_repr += f" - {data_schema['description'].split('.')[0]}"

            return data_repr

        obbjects = {}
        for i, obbject in enumerate(list(reversed(self.obbjects))):
            obbjects[i] = {
                "route": obbject._route,  # pylint: disable=protected-access
                "provider": obbject.provider,
                "standard params": _handle_standard_params(obbject),
                "data": _handle_data_repr(obbject),
            }

        return obbjects
