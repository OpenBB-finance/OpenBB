"""Credentials model and its utilities."""

import json
import os
import traceback
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from openbb_core.app.constants import USER_SETTINGS_PATH
from openbb_core.app.extension_loader import ExtensionLoader
from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.env import Env
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    create_model,
)
from pydantic.functional_serializers import PlainSerializer
from typing_extensions import Annotated


class LoadingError(Exception):
    """Error loading extension."""


# @model_serializer blocks model_dump with pydantic parameters (include, exclude)
OBBSecretStr = Annotated[
    SecretStr,
    PlainSerializer(
        lambda x: x.get_secret_value(), return_type=str, when_used="json-unless-none"
    ),
]


class CredentialsLoader:
    """Here we create the Credentials model."""

    credentials: Dict[str, List[str]] = {}

    def format_credentials(self, additional: dict) -> Dict[str, Tuple[object, None]]:
        """Prepare credentials map to be used in the Credentials model."""
        formatted: Dict[str, Tuple[object, None]] = {}
        for c_origin, c_list in self.credentials.items():
            for c_name in c_list:
                if c_name in formatted:
                    warnings.warn(
                        message=f"Skipping '{c_name}', credential already in use.",
                        category=OpenBBWarning,
                    )
                    continue
                formatted[c_name] = (
                    Optional[OBBSecretStr],
                    Field(default=None, description=c_origin, alias=c_name.upper()),
                )

        if additional:
            for key, value in additional.items():
                if key in formatted:
                    continue
                formatted[key] = (
                    Optional[OBBSecretStr],
                    Field(default=value, description=key, alias=key.upper()),
                )

        return dict(sorted(formatted.items()))

    def from_obbject(self) -> None:
        """Load credentials from OBBject extensions."""
        for ext_name, ext in ExtensionLoader().obbject_objects.items():  # type: ignore[attr-defined]
            try:
                if ext_name in self.credentials:
                    warnings.warn(
                        message=f"Skipping '{ext_name}', name already in user.",
                        category=OpenBBWarning,
                    )
                    continue
                self.credentials[ext_name] = ext.credentials
            except Exception as e:
                msg = f"Error loading extension: {ext_name}\n"
                if Env().DEBUG_MODE:
                    traceback.print_exception(type(e), e, e.__traceback__)
                    raise LoadingError(msg + f"\033[91m{e}\033[0m") from e
                warnings.warn(
                    message=msg,
                    category=OpenBBWarning,
                )

    def from_providers(self) -> None:
        """Load credentials from providers."""
        self.credentials = ProviderInterface().credentials

    def load(self) -> BaseModel:
        """Load credentials from providers."""
        # We load providers first to give them priority choosing credential names
        _ = Env()
        self.from_providers()
        self.from_obbject()
        path = Path(USER_SETTINGS_PATH)
        additional: dict = {}

        if path.exists():
            with open(USER_SETTINGS_PATH, encoding="utf-8") as f:
                data = json.load(f)
                if "credentials" in data:
                    additional = data["credentials"]

        # Collect all keys from providers to match with environment variables
        all_keys = [
            key
            for keys in ProviderInterface().credentials.values()
            if keys
            for key in keys
        ]

        for key in all_keys:
            if key.upper() in os.environ:
                value = os.environ[key.upper()]
                if value:
                    additional[key] = SecretStr(value)

        # Collect all environment variables ending with API_KEY
        environ_keys = [d for d in os.environ if d.endswith("API_KEY")]

        for key in environ_keys:
            value = os.environ[key]
            if value:
                additional[key.lower()] = SecretStr(value)

        model = create_model(
            "Credentials",
            __config__=ConfigDict(validate_assignment=True, populate_by_name=True),
            **self.format_credentials(additional),  # type: ignore
        )
        model.origins = self.credentials
        return model


_Credentials = CredentialsLoader().load()


class Credentials(_Credentials):  # type: ignore
    """Credentials model used to store provider credentials."""

    model_config = ConfigDict(extra="allow")

    def __repr__(self) -> str:
        """Define the string representation of the credentials."""
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in sorted(self.__dict__.items())])
        )

    def show(self):
        """Unmask credentials and print them."""
        print(  # noqa: T201
            self.__class__.__name__
            + "\n\n"
            + "\n".join(
                [f"{k}: {v}" for k, v in sorted(self.model_dump(mode="json").items())]
            )
        )

    def update(self, incoming: "Credentials"):
        """Update current credentials."""
        self.__dict__.update(incoming.model_dump(exclude_none=True))
