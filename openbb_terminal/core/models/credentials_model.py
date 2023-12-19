import json
from dataclasses import make_dataclass
from typing import Any, List, Tuple

from pydantic.dataclasses import dataclass as pydanticdataclass

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY
from openbb_terminal.core.models.base_model import BaseModel

with open(MISCELLANEOUS_DIRECTORY / "models" / "hub_credentials.json") as f:
    HUB_CREDENTIALS = json.load(f)

with open(MISCELLANEOUS_DIRECTORY / "models" / "local_credentials.json") as f:
    LOCAL_CREDENTIALS = json.load(f)


fields: List[Tuple[str, type, Any]] = [
    (k, str, "REPLACE_ME") for k in list(HUB_CREDENTIALS) + list(LOCAL_CREDENTIALS)
]

dc = make_dataclass(
    cls_name="CredentialsModel",
    fields=fields,
    bases=(BaseModel,),
)
dc.__repr__ = dc.__base__.__repr__  # type: ignore
CredentialsModel = pydanticdataclass(
    dc, config=dict(validate_assignment=True, frozen=True)
)
