import json
from dataclasses import make_dataclass

from pydantic.dataclasses import dataclass as pydanticdataclass

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY
from openbb_terminal.core.models.base_model import BaseModel

with open(MISCELLANEOUS_DIRECTORY / "models" / "credentials.json") as f:
    credentials_json = json.load(f)

dc = make_dataclass(
    cls_name="CredentialsModel",
    fields=[(k, str, "REPLACE_ME") for k in credentials_json],
    bases=(BaseModel,),
)
dc.__repr__ = dc.__base__.__repr__  # type: ignore
CredentialsModel = pydanticdataclass(
    dc, config=dict(validate_assignment=True, frozen=True)
)
