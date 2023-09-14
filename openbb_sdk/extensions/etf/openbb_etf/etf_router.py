"""ETF Router."""

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.query import Query
from openbb_core.app.router import Router

from openbb_etf.etf_definitions import (
    EtfCountries,
    EtfHoldings,
    EtfSearch,
    EtfSectors,
    Results,
)

router = Router(prefix="")


# pylint: disable=unused-argument
@router.command(model="EtfSearch")
def search(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> EtfSearch:
    """Fuzzy search for ETFs. An empty query returns the full list of ETFs from the provider."""

    data = Results(OBBject(results=Query(**locals()).execute()), "EtfSearch")
    results = EtfSearch.parse_obj(data.__dict__)
    results.results = data.results  # type: ignore
    return results


@router.command(model="EtfHoldings")
def holdings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> EtfHoldings:
    """Get the holdings for an individual ETF."""

    data = Results(OBBject(results=Query(**locals()).execute()), "EtfHoldings")
    results = EtfHoldings.parse_obj(data.__dict__)
    results.results = data.results  # type: ignore
    results.fields = sorted(results.to_dataframe().columns.to_list())
    return results


@router.command(model="EtfSectors")
def sectors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> EtfSectors:
    """ETF Sector weighting."""

    data = Results(OBBject(results=Query(**locals()).execute()), "EtfSectors")
    results = EtfSectors.parse_obj(data.__dict__)
    results.results = data.results  # type: ignore

    return results


@router.command(model="EtfCountries")
def countries(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> EtfCountries:
    """ETF Country weighting."""

    data = Results(OBBject(results=Query(**locals()).execute()), "EtfCountries")
    results = EtfCountries.parse_obj(data.__dict__)
    results.results = data.results  # type: ignore

    return results
