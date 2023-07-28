from typing import Dict, List, Literal, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.registry import Registry, RegistryLoader


class RegistryMap:
    """Class to store information about providers in the registry."""

    def __init__(self, registry: Optional[Registry] = None) -> None:
        self._registry = registry or RegistryLoader.from_extensions()
        self._required_credentials = self.get_required_credentials()
        self._available_providers = self.get_available_providers()
        self._map = self.get_map()
        self._models = self.get_models(self._map)

    @property
    def registry(self) -> Registry:
        return self._registry

    @property
    def available_providers(self) -> List[str]:
        return self._available_providers

    @property
    def required_credentials(self) -> List[str]:
        return self._required_credentials

    @property
    def map(self) -> Dict[str, List[str]]:
        return self._map

    @property
    def models(self) -> List[str]:
        return self._models

    def get_required_credentials(self) -> List[str]:
        cred_list = []
        for provider in self._registry.providers.values():
            for c in provider.formatted_credentials:
                cred_list.append(c)
        return cred_list

    def get_available_providers(self) -> List[str]:
        return sorted(list(self._registry.providers.keys()))

    def get_map(self) -> Dict:
        map_ = {}

        for p in self._registry.providers:
            for fetcher in self._registry.providers[p].fetcher_dict.values():
                f = fetcher()
                model_name = self.extract_model_name(f)
                standard_query, extra_query = self.extract_info(f, "query_params")
                standard_data, extra_data = self.extract_info(f, "data")

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

        return map_

    def get_models(self, map_: Dict[str, List[str]]) -> List[str]:
        return list(map_.keys())

    @staticmethod
    def extract_model_name(fetcher: Fetcher) -> str:
        # TODO: We should have a better way to extract the model name.
        # This looks fragile, but it's the best we can do for now.
        return fetcher.query_params_type.__name__.replace("QueryParams", "")

    @staticmethod
    def extract_info(fetcher: Fetcher, type_: Literal["query_params", "data"]):

        standard = getattr(fetcher, f"{type_}_type")
        extra = getattr(fetcher, f"provider_{type_}_type")

        standard_info = {"fields": {}, "docstring": standard.__doc__}
        extra_info = {"fields": {}, "docstring": extra.__doc__}

        standard_fields = standard.__fields__
        extra_fields = extra.__fields__

        for name, field in extra_fields.items():
            if name in standard_fields:
                standard_info["fields"][name] = field
            else:
                extra_info["fields"][name] = field

        return standard_info, extra_info
