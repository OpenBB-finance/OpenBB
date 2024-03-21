"""Query class."""

from dataclasses import asdict
from typing import Any

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    ProviderInterface,
    StandardParams,
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
        """Initialize Query class."""
        self.cc = cc
        self.provider = str(provider_choices.provider)
        self.standard_params = standard_params
        self.extra_params = extra_params
        self.name = self.standard_params.__class__.__name__
        self.query_executor = ProviderInterface().create_executor()

    async def execute(self) -> Any:
        """Execute the query."""
        return await self.query_executor.execute(
            provider_name=self.provider,
            model_name=self.name,
            params={**asdict(self.standard_params), **asdict(self.extra_params)},
            credentials=self.cc.user_settings.credentials.model_dump(),
            preferences=self.cc.user_settings.preferences.model_dump(),
        )
