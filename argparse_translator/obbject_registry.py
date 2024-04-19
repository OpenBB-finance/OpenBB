import json
from typing import Dict, List

from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.obbject import OBBject


class Registry(metaclass=SingletonMeta):

    obbject_instances: List[OBBject] = []
    ids: List[str] = []

    @classmethod
    def register(cls, obbject: OBBject):
        if isinstance(obbject, OBBject):
            for obbject_ in cls.obbject_instances:
                if obbject_.id == obbject.id:
                    return
            cls.obbject_instances.append(obbject)
            cls.ids.append(obbject.id)

    @classmethod
    def remove(cls, id_: str):
        for obbject in cls.obbject_instances:
            if obbject.id == id_:
                cls.obbject_instances.remove(obbject)
                cls.ids.remove(id_)

    @classmethod
    def get(cls, id_: str) -> OBBject:
        for obbject in cls.obbject_instances:
            if obbject.id == id_:
                return obbject
        raise ValueError(f"OBBject with id {id_} not found")

    @classmethod
    def pop(cls, id_: str) -> OBBject:
        for obbject in cls.obbject_instances:
            if obbject.id == id_:
                cls.obbject_instances.remove(obbject)
                cls.ids.remove(id_)
                return obbject
        raise ValueError(f"OBBject with id {id_} not found")

    @property
    def all(self) -> Dict[str, Dict]:
        """Return all obbjects in the registry"""

        def _handle_standard_params(obbject: OBBject) -> str:
            """Handle standard params for obbjects"""
            standard_params_json = ""
            std_params = obbject._standard_params  # pylint: disable=protected-access
            if hasattr(std_params, "__dict__"):
                standard_params = {k: v for k, v in std_params.__dict__.items() if v}
                standard_params_json = json.dumps(standard_params)

            return standard_params_json

        obbjects = {}
        for obbject in self.obbject_instances:
            obbjects[obbject.id] = {
                "route": obbject._route,  # pylint: disable=protected-access
                "provider": obbject.provider,
            }

            data_schema = (
                obbject.results[0].model_json_schema()
                if obbject.results and isinstance(obbject.results, list)
                else ""
            )
            data_repr = (
                f"{data_schema['title']} - {data_schema['description'].split('.')[0]}"
            )
            obbjects[obbject.id]["standard params"] = _handle_standard_params(obbject)
            obbjects[obbject.id]["data"] = data_repr

        return obbjects
