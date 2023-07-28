"""Helper functions for the builtin extensions."""

import warnings
from dataclasses import asdict
from typing import Any, Dict, Optional

from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
    get_provider_interface,
)
from openbb_provider.query_executor import QueryExecutor


class Query:
    """Query class."""

    def __init__(
        self,
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
        query_executor: Optional[QueryExecutor] = None,
    ) -> None:
        self.cc = cc
        self.provider = str(provider_choices.provider)
        self.standard_params = standard_params
        self.extra_params = extra_params
        self.name = self.standard_params.__class__.__name__
        self.query_executor = query_executor or QueryExecutor()

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

    def execute(self) -> Any:
        """Execute the query."""
        standard_dict = asdict(self.standard_params)
        extra_dict = (
            self.filter_extra_params(self.extra_params, self.provider)
            if self.extra_params
            else {}
        )

        return self.query_executor.execute(
            provider_name=self.provider,
            model_name=self.name,
            params={**standard_dict, **extra_dict},
            credentials=self.cc.user_settings.credentials.dict(),
        )
