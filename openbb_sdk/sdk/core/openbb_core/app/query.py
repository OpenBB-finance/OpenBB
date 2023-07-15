"""Helper functions for the builtin extensions."""

import warnings
from dataclasses import asdict
from typing import Any, Dict

from pydantic import BaseModel

from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
    get_provider_interface,
)


class Query:
    def __init__(
        self,
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> None:
        self.cc = cc
        self.provider = str(provider_choices.provider)
        self.standard_params = standard_params
        self.extra_params = extra_params
        self.name = self.standard_params.__class__.__name__

    @staticmethod
    def filter_extra_params(
        extra_params: ExtraParams,
        provider_name: str,
    ) -> Dict[str, Any]:
        """Filter extra params based on the provider and warn if not supported."""
        original = asdict(extra_params)
        filtered = {}

        provider_interface = get_provider_interface()
        query = extra_params.__class__.__name__
        fields = asdict(provider_interface.params[query]["extra"]())  # type: ignore

        for k, v in original.items():
            f = fields[k]
            providers = f.description.replace("Available for providers: ", "").split(
                ", "
            )
            if v != f.default:
                if provider_name in providers:
                    filtered[k] = v
                else:
                    available = ", ".join(providers)
                    warnings.warn(
                        message=f"Parameter '{k}' is not supported by {provider_name}. Available for: {available}.",
                        category=OpenBBWarning,
                    )

        return filtered

    def to_query_params(self, standard_params: StandardParams) -> StandardParams:
        """Convert standard params to query params.
        This is essentially adding a suffix to the query name and assign it to __name__.
        """
        standard_params.__name__ = self.name + "QueryParams"  # type: ignore
        return standard_params

    def execute(self) -> BaseModel:
        """Execute the query."""

        registry = get_provider_interface().create_registry()
        creds = self.cc.user_settings.credentials
        registry.api_keys[self.provider] = getattr(creds, self.provider + "_api_key")  # type: ignore

        query_params = self.to_query_params(self.standard_params)

        filtered = (
            self.filter_extra_params(self.extra_params, self.provider)
            if self.extra_params
            else None
        )

        return registry.fetch(
            provider_name=self.provider,  # type: ignore
            # TODO: provider_name should accept a general object, otherwise we need to import from provider.
            query=query_params,  # type: ignore
            # TODO: query should accept a general object, otherwise we need to import from provider.
            extra_params=filtered,
        )
