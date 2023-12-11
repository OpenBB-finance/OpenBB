"""Provider registry map."""

from inspect import getfile, isclass
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional, Tuple, Union, get_origin

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
        self._map, self._return_map = self._get_map(self._registry)
        self._models = self._get_models(self._map)

    @property
    def registry(self) -> Registry:
        """Get the registry."""
        return self._registry

    @property
    def available_providers(self) -> List[str]:
        """Get list of available providers."""
        return self._available_providers

    @property
    def credentials(self) -> List[str]:
        """Get list of required credentials."""
        return self._credentials

    @property
    def map(self) -> MapType:
        """Get provider registry map."""
        return self._map

    @property
    def return_map(self) -> MapType:
        """Get provider registry return map."""
        return self._return_map

    @property
    def models(self) -> List[str]:
        """Get available models."""
        return self._models

    def _get_credentials(self, registry: Registry) -> List[str]:
        """Get list of required credentials."""
        cred_list = []
        for provider in registry.providers.values():
            for c in provider.credentials:
                cred_list.append(c)
        return cred_list

    def _get_available_providers(self, registry: Registry) -> List[str]:
        """Get list of available providers."""
        return sorted(list(registry.providers.keys()))

    def _get_map(self, registry: Registry) -> Tuple[MapType, MapType]:
        """Generate map for the provider package."""
        map_: MapType = {}
        return_map: MapType = {}
        union_return_map: MapType = {}

        for p in registry.providers:
            for model_name, fetcher in registry.providers[p].fetcher_dict.items():
                standard_query, extra_query = self.extract_info(fetcher, "query_params")
                standard_data, extra_data = self.extract_info(fetcher, "data")
                return_type = self.extract_return_type(fetcher)

                if model_name not in map_:
                    map_[model_name] = {}
                    map_[model_name]["openbb"] = {
                        "QueryParams": standard_query,
                        "Data": standard_data,
                    }

                map_[model_name][p] = {
                    "QueryParams": extra_query,
                    "Data": extra_data,
                }

                in_return_map = return_map.get(model_name, return_type)
                if union_return_map.get(model_name, None) is None and get_origin(
                    return_type
                ) != get_origin(in_return_map):
                    union_return_map[model_name] = Union[in_return_map, return_type]  # type: ignore

                return_map[model_name] = return_type

        for model_name, return_type in union_return_map.items():
            return_map[model_name] = return_type

        return map_, return_map

    def _get_models(self, map_: MapType) -> List[str]:
        """Get available models."""
        return list(map_.keys())

    @staticmethod
    def extract_info(fetcher: Fetcher, type_: Literal["query_params", "data"]) -> tuple:
        """Extract info (fields and docstring) from fetcher query params or data."""
        model: BaseModel = RegistryMap._get_model(fetcher, type_)
        all_fields = {}
        alias_dict: Dict[str, List[str]] = {}
        standard_info: Dict[str, Any] = {"fields": {}, "docstring": None}
        found_top_level = False

        for c in RegistryMap._class_hierarchy(model):
            if c.__name__ in SKIP:
                continue
            if (Path(getfile(c)).parent == STANDARD_MODELS_FOLDER) or found_top_level:
                if not found_top_level:
                    # We might update the standard_info more than once to account for
                    # nested standard models, but we only want to update the docstring
                    # once with the __doc__ of the top-level standard model.
                    standard_info["docstring"] = c.__doc__
                    found_top_level = True
                standard_info["fields"].update(c.model_fields)
            else:
                all_fields.update(c.model_fields)
                for name, alias in getattr(c, "__alias_dict__", {}).items():
                    alias_dict.setdefault(name, []).append(alias)

        extra_info: Dict[str, Any] = {
            "fields": {},
            "docstring": model.__doc__,
            "alias_dict": alias_dict,
        }

        # We ignore fields that are already in the standard model
        for name, field in all_fields.items():
            if name not in standard_info["fields"]:
                extra_info["fields"][name] = field

        return standard_info, extra_info

    @staticmethod
    def extract_return_type(fetcher: Fetcher):
        """Extract return info from fetcher."""
        return getattr(fetcher, "return_type", None)

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
    def _class_hierarchy(class_) -> tuple:
        """Return the class hierarchy starting with the class itself until `object`."""
        return getattr(class_, "__mro__", ())
