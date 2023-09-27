from typing import Dict, List, Optional, Tuple

from pydantic import ConfigDict, create_model

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
        formatted[c] = (Optional[str], None)

    return formatted


Credentials = create_model(  # type: ignore
    "Credentials",
    __config__=ConfigDict(validate_assignment=True),
    **format_map(ProviderInterface().required_credentials),
)


def __repr__(self: Credentials) -> str:
    return (
        self.__class__.__name__
        + "\n\n"
        + "\n".join([f"{k}: {v}" for k, v in self.model_dump().items()])
    )


Credentials.__repr__ = __repr__
