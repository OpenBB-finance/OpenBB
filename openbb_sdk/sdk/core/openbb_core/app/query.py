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
    """Query class."""

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
            providers = f.title.replace("Available for providers: ", "").split(", ")
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
        """Convert standard params to QueryParams like class."""
        standard_params.__name__ = self.name + "QueryParams"  # type: ignore
        return standard_params

    def execute(self) -> BaseModel:
        """Execute the query."""

        # TODO: Understand if we really need to create the registry in every call
        registry = get_provider_interface().build_registry()
        creds = self.cc.user_settings.credentials.dict()
        query_params = self.to_query_params(self.standard_params)

        filtered = (
            self.filter_extra_params(self.extra_params, self.provider)
            if self.extra_params
            else None
        )

        return registry.fetch(
            provider_name=self.provider,
            query_params=query_params,
            extra_params=filtered,
            credentials=creds,
        )
