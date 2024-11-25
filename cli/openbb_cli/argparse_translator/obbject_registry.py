"""Registry for OBBjects."""

import json
from typing import Dict, List, Optional, Union

from openbb_core.app.model.obbject import OBBject


class Registry:
    """Registry for OBBjects."""

    def __init__(self):
        """Initialize the registry."""
        self._obbjects: List[OBBject] = []

    @staticmethod
    def _contains_obbject(uuid: str, obbjects: List[OBBject]) -> bool:
        """Check if obbject with uuid is in the registry."""
        return any(obbject.id == uuid for obbject in obbjects)

    def register(self, obbject: OBBject) -> bool:
        """Designed to add an OBBject instance to the registry."""
        if (
            isinstance(obbject, OBBject)
            and not self._contains_obbject(obbject.id, self._obbjects)
            and obbject.results
        ):
            self._obbjects.append(obbject)
            return True
        return False

    def get(self, arg: Union[int, str]) -> Optional[OBBject]:
        """Return the obbject with index or key."""
        if isinstance(arg, int):
            return self._get_by_index(arg)
        if isinstance(arg, str):
            return self._get_by_key(arg)

        raise ValueError("Couldn't get the `OBBject` with the provided argument.")

    def _get_by_key(self, key: str) -> Optional[OBBject]:
        """Return the obbject with key."""
        for obbject in self._obbjects:
            if obbject.extra.get("register_key", "") == key:
                return obbject
        return None

    def _get_by_index(self, idx: int) -> Optional[OBBject]:
        """Return the obbject at index idx."""
        # the list should work as a stack
        # i.e., the last element needs to be accessed by idx=0 and so on
        reversed_list = list(reversed(self._obbjects))

        # check if the index is out of bounds
        if idx >= len(reversed_list):
            return None

        return reversed_list[idx]

    def remove(self, idx: int = -1):
        """Remove the obbject at index idx, default is the last element."""
        # the list should work as a stack
        # i.e., the last element needs to be accessed by idx=0 and so on
        reversed_list = list(reversed(self._obbjects))
        del reversed_list[idx]
        self._obbjects = list(reversed(reversed_list))

    @property
    def all(self) -> Dict[int, Dict]:
        """Return all obbjects in the registry."""

        def _handle_standard_params(obbject: OBBject) -> str:
            """Handle standard params for obbjects."""
            standard_params_json = ""
            std_params = getattr(
                obbject, "_standard_params", {}
            )  # pylint: disable=protected-access
            if std_params:
                standard_params = {
                    k: str(v)[:30] for k, v in std_params.items() if v and k != "data"
                }
                standard_params_json = json.dumps(standard_params)

            return standard_params_json

        def _handle_data_repr(obbject: OBBject) -> str:
            """Handle data representation for obbjects."""
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
        for i, obbject in enumerate(list(reversed(self._obbjects))):
            obbjects[i] = {
                "route": obbject._route,  # pylint: disable=protected-access
                "provider": obbject.provider,
                "standard params": _handle_standard_params(obbject),
                "data": _handle_data_repr(obbject),
                "command": obbject.extra.get("command", ""),
                "key": obbject.extra.get("register_key", ""),
            }

        return obbjects

    @property
    def obbjects(self) -> List[OBBject]:
        """Return all obbjects in the registry."""
        return self._obbjects

    @property
    def obbject_keys(self) -> List[str]:
        """Return all obbject keys in the registry."""
        return [
            obbject.extra["register_key"]
            for obbject in self._obbjects
            if "register_key" in obbject.extra
        ]
