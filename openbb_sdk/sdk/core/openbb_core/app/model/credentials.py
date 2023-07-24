from pydantic import create_model

from openbb_core.app.provider_interface import get_provider_interface

# Here we create the BaseModel from the provider required credentials.
# This means that if a new provider extension is installed, the required
# credentials will be automatically added to the Credentials model.


class Config:
    validate_assignment = True


Credentials = create_model(  # type: ignore
    "Credentials",
    __config__=Config,
    **get_provider_interface().required_credentials,
)


def __repr__(self) -> str:
    return (
        self.__class__.__name__
        + "\n\n"
        + "\n".join([f"{k}: {v}" for k, v in self.dict().items()])
    )


Credentials.__repr__ = __repr__
