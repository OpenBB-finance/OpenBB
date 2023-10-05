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
    EtfInfo,
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
    results = EtfSearch()
    for d in list(data.__dict__.keys()):
        setattr(results, d, data.__dict__[d])
    return EtfSearch.model_validate(results)


@router.command(model="EtfHoldings")
def holdings(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> EtfHoldings:
    """Get the holdings for an individual ETF."""

    # Return data from the Fetcher.  This function operates differently because not all providers return extras.
    _data = Query(**locals()).execute()

    # Determine if the Fetcher returned extras, then conditionally parse through the Results helper class.
    _data_ = _data if isinstance(_data, list) else (_data.holdings_data, _data.extra_info)
    data = Results(OBBject(results=_data_), "EtfHoldings")

    # Set and validate the parsed results object through a model which inherits from OBBject.
    results = EtfHoldings()
    for d in list(data.__dict__.keys()):
        setattr(results, d, data.__dict__[d])

    # Reset the fields using to_df() instead of what was populated by Results, via basemodel_to_df().
    results.fields = list(results.to_df().columns)

    return EtfHoldings.model_validate(results)
    #return _data

@router.command(model="EtfSectors")
def sectors(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> EtfSectors:
    """ETF Sector weighting."""

    data = Results(OBBject(results=Query(**locals()).execute()), "EtfSectors")
    results = EtfSectors()
    for d in list(data.__dict__.keys()):
        setattr(results, d, data.__dict__[d])
    return EtfSectors.model_validate(results)


@router.command(model="EtfCountries")
def countries(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> EtfCountries:
    """ETF Country weighting."""

    data = Results(OBBject(results=Query(**locals()).execute()), "EtfCountries")
    results = EtfCountries()
    for d in list(data.__dict__.keys()):
        setattr(results, d, data.__dict__[d])
    return EtfCountries.model_validate(results)


@router.command(model="EtfInfo")
def info(
    cc: CommandContext,
    provider_choices: ProviderChoices,
    standard_params: StandardParams,
    extra_params: ExtraParams,
) -> EtfInfo:
    """ETF Info."""

    data = Results(OBBject(results=Query(**locals()).execute()), "EtfInfo")
    results = EtfInfo()
    for d in list(data.__dict__.keys()):
        setattr(results, d, data.__dict__[d])
    return EtfInfo.model_validate(results)
