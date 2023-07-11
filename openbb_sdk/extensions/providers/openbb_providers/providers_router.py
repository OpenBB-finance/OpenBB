"""OpenBB Provider command Coverage Router."""
from openbb_provider.provider.abstract.provider import ProviderName
from openbb_sdk_core.app.model.command_output import CommandOutput
from openbb_sdk_core.app.router import CommandMap, Router

router = Router()


def __create_command_coverage(provider_name: ProviderName):
    """Create a command coverage function for a specific provider."""

    def command_coverage() -> CommandOutput[list]:
        """Get command coverage for a specific provider."""
        provider_coverage = CommandMap().provider_coverage
        return CommandOutput(results=provider_coverage[provider_name])

    command_coverage.__name__ = provider_name
    return command_coverage


def create_command_coverage_routers():
    """Create a router for each provider."""
    meta_router = Router()
    for provider_name in ProviderName.__args__:
        data_router = Router()
        data_router.command(
            func=__create_command_coverage(provider_name),
        )
        meta_router.include_router(router=data_router)

    return meta_router


router.include_router(router=create_command_coverage_routers())
