"""Credentials model and its utilities."""

import json
import os
import traceback
import warnings
from pathlib import Path
from typing import Annotated, ClassVar, Optional

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

    credentials: dict[str, list[str]] = {}
    env = Env()

    @staticmethod
    def _normalize_credential_map(raw: dict | None) -> dict[str, object]:
        """Lower-case keys and drop empty overrides so env values can win."""
        if not raw:
            return {}
        normalized: dict[str, object] = {}
        for key, value in raw.items():
            if not isinstance(key, str):
                normalized[key] = value
                continue
            normalized_key = key.strip().lower()
            if normalized_key in normalized and value in (None, ""):
                continue
            normalized[normalized_key] = value
        return normalized

    def format_credentials(self, additional: dict) -> dict[str, tuple[object, None]]:
        """Prepare credentials map to be used in the Credentials model."""
        formatted: dict[str, tuple[object, None]] = {}
        additional_data = dict(additional)

        for c_origin, c_list in self.credentials.items():
            for c_name in c_list:
                if c_name in formatted:
                    warnings.warn(
                        message=f"Skipping '{c_name}', credential already in use.",
                        category=OpenBBWarning,
                    )
                    continue
                default_value = additional_data.pop(c_name, None)
                formatted[c_name] = (
                    Optional[OBBSecretStr],  # noqa
                    Field(
                        default=default_value,
                        description=c_origin,
                        alias=c_name.upper(),
                    ),
                )

        if additional_data:
            for key, value in additional_data.items():
                if key in formatted:
                    continue
                formatted[key] = (
                    Optional[OBBSecretStr],  # noqa
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
        self.from_providers()
        self.from_obbject()
        path = Path(USER_SETTINGS_PATH)
        additional: dict = {}

        if path.exists():
            with open(USER_SETTINGS_PATH, encoding="utf-8") as f:
                data = json.load(f)
                if "credentials" in data:
                    additional = data["credentials"]

        additional = self._normalize_credential_map(additional)

        all_keys = [
            key
            for keys in ProviderInterface().credentials.values()
            if keys
            for key in keys
        ]

        env_credentials: dict[str, SecretStr] = {}
        for env_key, value in os.environ.items():
            if not value:
                continue
            lower_key = env_key.lower()
            if lower_key in all_keys or env_key.endswith("API_KEY"):
                canonical_key = lower_key if lower_key in all_keys else lower_key
                env_credentials[canonical_key] = SecretStr(value)

        if env_credentials:
            additional.update(env_credentials)

        additional = self._normalize_credential_map(additional)

        env_overrides = {
            key: additional[key]
            for key in env_credentials
            if key in additional and additional[key] not in (None, "")
        }

        model = create_model(
            "Credentials",
            __config__=ConfigDict(validate_assignment=True, populate_by_name=True),
            **self.format_credentials(additional),  # type: ignore
        )
        model._env_defaults = env_overrides  # type: ignore # pylint: disable=W0212
        model.origins = self.credentials

        return model


_Credentials = CredentialsLoader().load()


class Credentials(_Credentials):  # type: ignore
    """Credentials model used to store provider credentials."""

    model_config = ConfigDict(extra="allow")
    _env_defaults: ClassVar[dict[str, object]] = getattr(
        _Credentials, "_env_defaults", {}
    )

    @staticmethod
    def _is_unset(value: object) -> bool:
        if value is None:
            return True
        if isinstance(value, SecretStr):
            return not value.get_secret_value()
        if isinstance(value, str):
            return value == ""
        return False

    def model_post_init(self, __context) -> None:
        """Set unset credentials from environment variables."""
        super().model_post_init(__context)
        for key, secret in self._env_defaults.items():
            if key not in self.model_fields:
                continue
            current = getattr(self, key, None)
            if self._is_unset(current):
                setattr(self, key, secret)

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
