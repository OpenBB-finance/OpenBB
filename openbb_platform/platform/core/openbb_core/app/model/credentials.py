from typing import Any, Dict, List, Optional, Tuple

from pydantic import (
    ConfigDict,
    SecretStr,
    create_model,
    model_serializer,
)
from pydantic.fields import FieldInfo

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

    def model_dump(self, *args, **kwargs) -> Dict[str, Any]:
        """Override model_dump to include new fields added with `_add_fields`"""
        instance_fields = super().model_dump(*args, **kwargs)
        class_fields = self.model_fields
        for f_name, f_info in class_fields.items():
            instance_fields.setdefault(f_name, f_info.default)

        return instance_fields

    @model_serializer(when_used="json-unless-none")
    def _serialize(self) -> Dict[str, Any]:
        return {
            k: v.get_secret_value() if isinstance(v, SecretStr) else v
            for k, v in self.model_dump().items()
        }

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.model_dump().items()])
        )

    @classmethod
    def _add_fields(cls, **field_definitions: Any) -> None:
        """Add new fields to the Credentials model"""
        new_fields: Dict[str, FieldInfo] = {}
        new_annotations: Dict[str, Optional[type]] = {}

        for f_name, f_def in field_definitions.items():
            if isinstance(f_def, tuple):
                try:
                    f_annotation, f_value = f_def
                except ValueError as e:
                    raise Exception(
                        "field definitions should either be a tuple of (<type>, <default>) or just a "
                        "default value, unfortunately this means tuples as "
                        "default values are not allowed"
                    ) from e
            else:
                f_annotation, f_value = None, f_def

            if f_annotation:
                new_annotations[f_name] = f_annotation
            new_fields[f_name] = FieldInfo.from_annotated_attribute(
                annotation=f_annotation, default=f_value
            )

            if hasattr(cls, f_name):
                raise ValueError(f"Attribute '{f_name}' is already defined.")
            setattr(cls, f_name, None)

        cls.model_fields.update(new_fields)
        cls.__annotations__.update(new_annotations)
        cls.model_rebuild(force=True)

    def show(self):
        """Unmask credentials and print them"""
        print(  # noqa: T201
            self.__class__.__name__
            + "\n\n"
            + "\n".join([f"{k}: {v}" for k, v in self.model_dump(mode="json").items()])
        )
