import traceback
from typing import Any, Dict, Optional, Set, Tuple

from importlib_metadata import entry_points
from pydantic import (
    BaseModel,
    ConfigDict,
    SecretStr,
    create_model,
    model_serializer,
)

from openbb_core.app.model.extension import Extension
from openbb_core.app.provider_interface import ProviderInterface


class LoadingError(Exception):
    """Error loading extension."""


class CredentialsLoader:
    """Here we create the Credentials model from the provider required credentials"""

    credentials: Set[str] = set()

    @staticmethod
    def prepare(
        required_credentials: Set[str],
    ) -> Dict[str, Tuple[object, None]]:
        """Prepare credentials map to be used in the Credentials model"""
        formatted: Dict[str, Tuple[object, None]] = {}
        for c in required_credentials:
            formatted[c] = (Optional[SecretStr], None)

        return formatted

    def from_providers(self) -> None:
        """Load credentials from providers"""
        for c in ProviderInterface().required_credentials:
            self.credentials.add(c)

    def from_extensions(self) -> None:
        """Load credentials from extensions"""
        for entry_point in sorted(entry_points(group="openbb_obbject_extension")):
            try:
                entry = entry_point.load()
                if isinstance(entry, Extension):
                    for c in entry.required_credentials:
                        self.credentials.add(c)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                raise LoadingError(f"Invalid extension '{entry_point.name}'") from e

    def load(self) -> BaseModel:
        """Load credentials from providers"""
        self.from_providers()
        self.from_extensions()
        return create_model(  # type: ignore
            "Credentials",
            __config__=ConfigDict(validate_assignment=True),
            **self.prepare(self.credentials),
        )


_Credentials = CredentialsLoader().load()


class Credentials(_Credentials):  # type: ignore
    """Credentials model used to store provider credentials"""

    @model_serializer(when_used="json-unless-none")
    def _serialize(self) -> Dict[str, Any]:
        """Serialize credentials to a dict"""
        return {
            k: v.get_secret_value() if isinstance(v, SecretStr) else v
            for k, v in self.__dict__.items()
        }

    def __repr__(self) -> str:
        """String representation of the credentials"""
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.__dict__.items()])
        )

    def show(self):
        """Unmask credentials and print them"""
        print(  # noqa: T201
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.model_dump(mode="json").items()])
        )
