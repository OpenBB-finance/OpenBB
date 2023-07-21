from pydantic import create_model

from openbb_core.app.provider_interface import get_provider_interface

provider_credentials = get_provider_interface().credentials


class Config:
    validate_assignment = True


def __repr__(self) -> str:
    return (
        self.__class__.__name__
        + "\n\n"
        + "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
    )


Credentials = create_model(  # type: ignore
    "Credentials",
    __config__=Config,
    **provider_credentials,
)


Credentials.__repr__ = __repr__
