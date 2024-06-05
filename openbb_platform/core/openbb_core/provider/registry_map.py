"""Provider registry map."""

from copy import deepcopy
from inspect import getfile, isclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, get_origin

from pydantic import BaseModel

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.registry import Registry, RegistryLoader

MapType = Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]

STANDARD_MODELS_FOLDER = Path(__file__).parent / "standard_models"
SKIP = {"object", "Representation", "BaseModel", "QueryParams", "Data"}


class RegistryMap:
    """Class to store information about providers in the registry."""

    def __init__(self, registry: Optional[Registry] = None) -> None:
        """Initialize Registry Map."""
        self._registry = registry or RegistryLoader.from_extensions()
        self._credentials = self._get_credentials(self._registry)
        self._available_providers = self._get_available_providers(self._registry)
        self._standard_extra, self._original_models = self._get_maps(self._registry)
        self._models = self._get_models(self._standard_extra)

    @property
    def registry(self) -> Registry:
        """Get the registry."""
        return self._registry

    @property
    def available_providers(self) -> List[str]:
        """Get list of available providers."""
        return self._available_providers

    @property
    def credentials(self) -> Dict[str, List[str]]:
        """Get map of providers to credentials."""
        return self._credentials

    @property
    def standard_extra(self) -> MapType:
        """Get standard extra map."""
        return self._standard_extra

    @property
    def original_models(self) -> MapType:
        """Get original models."""
        return self._original_models

    @property
    def models(self) -> List[str]:
        """Get available models."""
        return self._models

    def _get_credentials(self, registry: Registry) -> Dict[str, List[str]]:
        """Get map of providers to credentials."""
        return {
            name: provider.credentials for name, provider in registry.providers.items()
        }

    def _get_available_providers(self, registry: Registry) -> List[str]:
        """Get list of available providers."""
        return sorted(list(registry.providers.keys()))

    def _get_maps(self, registry: Registry) -> Tuple[MapType, Dict[str, Dict]]:
        """Generate map for the provider package."""
        standard_extra: MapType = {}
        original_models: Dict[str, Dict] = {}

        for p in registry.providers:
            for model_name, fetcher in registry.providers[p].fetcher_dict.items():
                standard_query, extra_query = self._extract_info(
                    fetcher, "query_params"
                )
                standard_data, extra_data = self._extract_info(fetcher, "data")
                if model_name not in standard_extra:
                    standard_extra[model_name] = {}
                    # The deepcopy avoids modifications from one model to affect another
                    standard_extra[model_name]["openbb"] = {
                        "QueryParams": deepcopy(standard_query),
                        "Data": deepcopy(standard_data),
                    }
                standard_extra[model_name][p] = {
                    "QueryParams": extra_query,
                    "Data": extra_data,
                }

                original_models.setdefault(model_name, {}).update(
                    {
                        p: {
                            "query": self._get_model(fetcher, "query_params"),
                            "data": self._get_model(fetcher, "data"),
                            "results_type": self._get_results_type(fetcher),
                        }
                    }
                )

                self._update_json_schema_extra(p, fetcher, standard_extra[model_name])

        return standard_extra, original_models

    def _update_json_schema_extra(
        self,
        provider: str,
        fetcher: Fetcher,
        model_map: dict,
    ):
        """Merge json schema extra for different providers."""
        model: BaseModel = RegistryMap._get_model(fetcher, "query_params")
        standard_fields = model_map["openbb"]["QueryParams"]["fields"]
        extra_fields = model_map[provider]["QueryParams"]["fields"]

        for field, properties in getattr(model, "__json_schema_extra__", {}).items():
            if properties:
                if field in standard_fields:
                    model_field = standard_fields[field]
                elif field in extra_fields:
                    model_field = extra_fields[field]
                else:
                    continue

                if model_field.json_schema_extra is None:
                    model_field.json_schema_extra = {}

                model_field.json_schema_extra[provider] = properties

    def _get_models(self, map_: MapType) -> List[str]:
        """Get available models."""
        return list(map_.keys())

    @staticmethod
    def _get_results_type(fetcher: Fetcher) -> Any:
        """Extract return info from fetcher."""
        return get_origin(getattr(fetcher, "return_type", None))

    @staticmethod
    def _extract_info(
        fetcher: Fetcher, type_: Literal["query_params", "data"]
    ) -> tuple:
        """Extract info (fields and docstring) from fetcher query params or data."""
        model: BaseModel = RegistryMap._get_model(fetcher, type_)
        standard_info: Dict[str, Any] = {"fields": {}, "docstring": None}
        extra_info: Dict[str, Any] = {"fields": {}, "docstring": model.__doc__}
        found_first_standard = False

        family = RegistryMap._get_class_family(model)
        for i, child in enumerate(family):
            if child.__name__ in SKIP:
                continue

            parent = family[i + 1] if family[i + 1] not in SKIP else BaseModel

            fields = {
                name: field
                for name, field in child.model_fields.items()
                # This ensures fields inherited by c are discarded.
                # We need to compare child and parent __annotations__
                # because this attribute is redirected to the parent class
                # when the child simply inherits the parent and does not
                # define any attributes.
                # TLDR: Only fields defined in c are included
                if name in child.__annotations__
                and child.__annotations__ is not parent.__annotations__
            }

            if Path(getfile(child)).parent == STANDARD_MODELS_FOLDER:
                if not found_first_standard:
                    # If standard uses inheritance we just use the first docstring
                    standard_info["docstring"] = child.__doc__
                    found_first_standard = True
                standard_info["fields"].update(fields)
            else:
                extra_info["fields"].update(fields)

        return standard_info, extra_info

    @staticmethod
    def _get_model(
        fetcher: Fetcher, type_: Literal["query_params", "data"]
    ) -> BaseModel:
        """Get model from fetcher."""
        model = getattr(fetcher, f"{type_}_type")
        RegistryMap._validate(model, type_)
        return model

    @staticmethod
    def _validate(model: Any, type_: Literal["query_params", "data"]) -> None:
        """Validate model."""
        parent_model = QueryParams if type_ == "query_params" else Data
        if not isclass(model) or not issubclass(model, parent_model):
            model_str = str(model).replace("<", "<'").replace(">", "'>")
            raise ValueError(
                f"'{model_str}' must be a subclass of '{parent_model.__name__}'.\n"
                "If you are returning a nested type, try specifying"
                f" `{type_}_type = <'your_{type_}_type'>` in the fetcher."
            )

    @staticmethod
    def _get_class_family(class_) -> tuple:
        """Return the class family starting with the class itself until `object`."""
        return getattr(class_, "__mro__", ())
