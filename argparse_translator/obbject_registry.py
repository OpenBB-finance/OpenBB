import json
from typing import Dict, List

from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.obbject import OBBject


class Registry(metaclass=SingletonMeta):

    obbject_instances: List[OBBject] = []

    @classmethod
    def register(cls, obbject: OBBject):
        if isinstance(obbject, OBBject):
            for obbject_ in cls.obbject_instances:
                if obbject_.id == obbject.id:
                    return
            cls.obbject_instances.append(obbject)

    @classmethod
    def remove(cls, id_: str):
        for obbject in cls.obbject_instances:
            if obbject.id == id_:
                cls.obbject_instances.remove(obbject)

    @classmethod
    def get(cls, id_: str):
        for obbject in cls.obbject_instances:
            if obbject.id == id_:
                return obbject
        raise ValueError(f"OBBject with id {id_} not found")

    @classmethod
    def pop(cls, id_: str):
        for obbject in cls.obbject_instances:
            if obbject.id == id_:
                cls.obbject_instances.remove(obbject)
                return obbject
        raise ValueError(f"OBBject with id {id_} not found")

    @property
    def all(self) -> Dict[str, Dict]:
        obbjects = {}
        for obbject in self.obbject_instances:
            obbjects[obbject.id] = {
                "route": obbject._route,  # pylint: disable=protected-access
                "provider": obbject.provider,
            }
            standard_params = (
                obbject._standard_params.__dict__  # pylint: disable=protected-access
            )
            standard_params = {k: v for k, v in standard_params.items() if v}
            standard_params_json = json.dumps(standard_params)
            data_schema = (
                obbject.results[0].model_json_schema() if obbject.results else ""
            )
            data_repr = f"{data_schema['title']} - {data_schema['description']}"
            obbjects[obbject.id]["standard params"] = standard_params_json
            obbjects[obbject.id]["data"] = data_repr

        return obbjects
