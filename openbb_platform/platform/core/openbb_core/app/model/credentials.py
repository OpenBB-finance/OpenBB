from typing import Dict, List, Optional, Tuple

from pydantic import ConfigDict, SecretStr, create_model, field_serializer

from openbb_core.app.provider_interface import ProviderInterface

# Here we create the BaseModel from the provider required credentials.
# This means that if a new provider extension is installed, the required
# credentials will be automatically added to the Credentials model.


def format_map(
    required_credentials: List[str],
) -> Dict[str, Tuple[object, None]]:
    """Format credentials map to be used in the Credentials model"""
    formatted: Dict[str, Tuple[object, None]] = {}
    for c in required_credentials:
        formatted[c] = (Optional[SecretStr], None)

    return formatted


provider_credentials = ProviderInterface().required_credentials

_Credentials = create_model(  # type: ignore
    "Credentials",
    __config__=ConfigDict(validate_assignment=True),
    **format_map(provider_credentials),
)


class Credentials(_Credentials):
    """Credentials model used to store provider credentials"""

    @field_serializer(*provider_credentials, when_used="json-unless-none")
    def _dump_secret(self, v):
        return v.get_secret_value()

    def show(self):
        """Unmask credentials and print them"""
        print(  # noqa: T201
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.model_dump(mode="json").items()])
        )


def __repr__(self: Credentials) -> str:
    return (
        self.__class__.__name__
        + "\n\n"
        + "\n".join([f"{k}: {v}" for k, v in self.model_dump().items()])
    )


Credentials.__repr__ = __repr__
