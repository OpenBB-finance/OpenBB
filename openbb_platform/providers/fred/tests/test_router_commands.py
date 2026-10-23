"""Tests for the FRED sub-router command bodies."""

import importlib
import importlib.util
import inspect
from importlib import import_module
from importlib.machinery import ModuleSpec
from typing import get_args

import pytest

import openbb_fred

COMMANDS = [
    ("commodity", "spot", "FredCommoditySpotPrices"),
    ("corporate", "commercial_paper", "FredCommercialPaper"),
    ("corporate", "hqm", "FredHighQualityMarketCorporateBond"),
    ("corporate", "spot_rates", "FredSpotRate"),
    ("economy", "balance_of_payments", "FredBalanceOfPayments"),
    ("economy", "cpi", "FredConsumerPriceIndex"),
    ("economy", "calendar", "FredEconomicCalendar"),
    ("economy", "pce", "FredPersonalConsumptionExpenditures"),
    ("economy", "retail_prices", "FredRetailPrices"),
    ("economy", "fred_search", "FredSearch"),
    ("economy", "fred_series", "FredSeries"),
    ("economy", "fred_release_table", "FredReleaseTable"),
    ("economy", "fred_regional", "FredRegional"),
    ("fixedincome", "bond_indices", "FredBondIndices"),
    ("fixedincome", "mortgage_indices", "FredMortgageIndices"),
    ("government", "tips_yields", "FredTipsYields"),
    ("government", "yield_curve", "FredYieldCurve"),
    ("rate", "ameribor", "FredAmeribor"),
    ("rate", "dpcredit", "FredDiscountWindowPrimaryCreditRate"),
    ("rate", "estr", "FredEuroShortTermRate"),
    ("rate", "ecb", "FredEuropeanCentralBankInterestRates"),
    ("rate", "effr", "FredFederalFundsRate"),
    ("rate", "iorb", "FredIORB"),
    ("rate", "overnight_bank_funding", "FredOvernightBankFundingRate"),
    ("rate", "effr_forecast", "FredPROJECTIONS"),
    ("rate", "sofr", "FredSOFR"),
    ("rate", "sonia", "FredSONIA"),
    ("spreads", "treasury_effr", "FredSelectedTreasuryBill"),
    ("spreads", "tcm_effr", "FredSelectedTreasuryConstantMaturity"),
    ("spreads", "tcm", "FredTreasuryConstantMaturity"),
    ("survey", "manufacturing_outlook_ny", "FredManufacturingOutlookNY"),
    ("survey", "manufacturing_outlook_texas", "FredManufacturingOutlookTexas"),
    ("survey", "nonfarm_payrolls", "FredNonFarmPayrolls"),
    ("survey", "sloos", "FredSeniorLoanOfficerSurvey"),
    ("survey", "economic_conditions_chicago", "FredSurveyOfEconomicConditionsChicago"),
    ("survey", "university_of_michigan", "FredUniversityOfMichigan"),
]

NAMESPACE_OWNER = {
    "commodity": "COMMODITY_INSTALLED",
    "corporate": "FIXEDINCOME_INSTALLED",
    "economy": "ECONOMY_INSTALLED",
    "fixedincome": "FIXEDINCOME_INSTALLED",
    "government": "FIXEDINCOME_INSTALLED",
    "rate": "FIXEDINCOME_INSTALLED",
    "spreads": "FIXEDINCOME_INSTALLED",
    "survey": "ECONOMY_INSTALLED",
}

NAMESPACE_PACKAGE = {
    "COMMODITY_INSTALLED": "openbb_commodity",
    "ECONOMY_INSTALLED": "openbb_economy",
    "FIXEDINCOME_INSTALLED": "openbb_fixedincome",
}

INSTALLED = {flag: getattr(openbb_fred, flag) for flag in NAMESPACE_PACKAGE}

SUB_ROUTERS = sorted({module for module, _, _ in COMMANDS})

PROVIDER_OWN_MODELS = {
    "FredReleaseTable",
    "FredSearch",
    "FredSeries",
    "FredRegional",
}

STANDARD_KEYS = {
    model if model in PROVIDER_OWN_MODELS else model.removeprefix("Fred")
    for _, _, model in COMMANDS
}

QUERY_ATTRIBUTES = {
    "cc",
    "provider",
    "standard_params",
    "extra_params",
    "name",
    "provider_interface",
}

ECONOMY_OWN_ENDPOINTS = {
    "/economy/release_table",
    "/economy/release_choices",
    "/economy/element_choices",
    "/economy/frequency_choices",
}

RETAIL_SALES_RELEASE = "9"


def sub_router(module: str):
    """Return one FRED sub-router module."""
    return import_module(f"openbb_fred.routers.{module}")


def command_of(module: str, name: str):
    """Return one sub-router command function."""
    return getattr(sub_router(module), name)


def published_commands(module: str) -> list[str]:
    """Return the declared commands one sub-router currently publishes.

    Parameters
    ----------
    module : str
        The sub-router module name.

    Returns
    -------
    list[str]
        The declared command names the module actually defines.
    """
    published = sub_router(module)

    return [
        name
        for owner, name, _ in COMMANDS
        if owner == module and hasattr(published, name)
    ]


def fetcher_key(module: str, model: str) -> str:
    """Return the key the provider registers one model under.

    Parameters
    ----------
    module : str
        The sub-router the command lives in.
    model : str
        The provider interface model the command declares.

    Returns
    -------
    str
        The FRED alias, or the standard name when the namespace owner is installed.
    """
    if model in PROVIDER_OWN_MODELS or not INSTALLED[NAMESPACE_OWNER[module]]:
        return model

    return model.removeprefix("Fred")


def stands_down(module: str) -> pytest.MarkDecorator:
    """Return the skip mark for a command the namespace owner takes over.

    Parameters
    ----------
    module : str
        The sub-router the command lives in.

    Returns
    -------
    pytest.MarkDecorator
        A skip that fires only when the owning namespace extension is installed.
    """
    flag = NAMESPACE_OWNER[module]

    return pytest.mark.skipif(
        INSTALLED[flag],
        reason=f"{NAMESPACE_PACKAGE[flag]} is installed, so"
        f" openbb_fred.routers.{module} publishes no command",
    )


COMMAND_PARAMS = [
    pytest.param(
        module,
        name,
        model,
        id=f"{module}.{name}",
        marks=stands_down(module),
    )
    for module, name, model in COMMANDS
]

MODULE_PARAMS = [
    pytest.param(module, NAMESPACE_OWNER[module], id=module) for module in SUB_ROUTERS
]


def release_tables(release_id: str) -> list[str]:
    """Return the tables one release publishes, in the packaged map's own order.

    Parameters
    ----------
    release_id : str
        The FRED release id.

    Returns
    -------
    list[str]
        The element id of each table the release publishes.
    """
    from openbb_fred.utils.release_tables import release_map

    release = release_map().get(release_id) or {}

    return [
        element["element_id"]
        for element in release.get("elements") or []
        if element.get("type", "table") == "table"
    ]


def release_name(release_id: str) -> str:
    """Return the name the packaged map carries for one release.

    Parameters
    ----------
    release_id : str
        The FRED release id.

    Returns
    -------
    str
        The release name.
    """
    from openbb_fred.utils.release_tables import release_map

    return release_map()[release_id]["name"]


def _map_ids() -> list[str]:
    """Return every release id the packaged map carries."""
    from openbb_fred.utils.release_tables import release_map

    return list(release_map())


RETAIL_SALES_TABLES = release_tables(RETAIL_SALES_RELEASE)

NO_TABLE_RELEASE = next(rid for rid in _map_ids() if not release_tables(rid))

UNKNOWN_RELEASE = str(max(int(rid) for rid in _map_ids()) + 1)


def arguments_for(model: str) -> dict:
    """Return the dependencies the API injects into one command.

    Parameters
    ----------
    model : str
        The provider interface model the command declares.

    Returns
    -------
    dict
        The four arguments a command is called with.
    """
    from openbb_core.app.model.command_context import CommandContext
    from openbb_core.app.provider_interface import ProviderInterface

    interface = ProviderInterface()

    return {
        "cc": CommandContext(),
        "provider_choices": interface.model_providers[model](provider="fred"),
        "standard_params": interface.params[model]["standard"](),
        "extra_params": interface.params[model]["extra"](),
    }


def reload_provider() -> None:
    """Re-evaluate the provider and every sub-router against the current imports."""
    importlib.reload(openbb_fred)

    for module in SUB_ROUTERS:
        published = sub_router(module)

        for name in published_commands(module):
            delattr(published, name)

        importlib.reload(published)


class StoredCredentials:
    """Stand-in for the credentials the user has stored."""

    def model_dump(self, mode: str = "python") -> dict:
        """Return the stored credentials."""
        return {"fred_api_key": "test-key"}


class StoredSettings:
    """Stand-in for the settings the commands read credentials from."""

    credentials = StoredCredentials()


class StoredUserService:
    """Stand-in for the service holding the default user settings."""

    default_user_settings = StoredSettings()


@pytest.fixture
def handed(monkeypatch):
    """Take the query each command builds, in place of executing it."""
    seen: list = []

    class Served:
        """Stand-in for the object a command hands back."""

        def __init__(self, results):
            self.results = results

        @classmethod
        async def from_query(cls, query):
            """Take the query instead of executing it."""
            seen.append(query)

            return cls([query.name])

    for module in SUB_ROUTERS:
        monkeypatch.setattr(f"openbb_fred.routers.{module}.OBBject", Served)

    return seen


@pytest.fixture
def stored_credentials(monkeypatch):
    """Answer the credential lookup with a known key."""
    monkeypatch.setattr(
        "openbb_core.app.service.user_service.UserService", StoredUserService
    )


@pytest.fixture
def namespace_owners_installed():
    """Re-evaluate the provider with every namespace extension importable.

    Yields
    ------
    module
        The reloaded ``openbb_fred`` package.
    """
    baseline = {module: published_commands(module) for module in SUB_ROUTERS}
    baseline_keys = set(openbb_fred.fred_provider.fetcher_dict)
    genuine = importlib.util.find_spec
    owners = set(NAMESPACE_PACKAGE.values())

    def found(name, package=None):
        return ModuleSpec(name, None) if name in owners else genuine(name, package)

    importlib.util.find_spec = found

    try:
        reload_provider()

        yield openbb_fred
    finally:
        importlib.util.find_spec = genuine
        reload_provider()

    assert {module: published_commands(module) for module in SUB_ROUTERS} == baseline
    assert set(openbb_fred.fred_provider.fetcher_dict) == baseline_keys


class TestCommandInventory:
    """The commands the sub-routers publish, and the models behind them."""

    def test_every_model_the_provider_registers_has_one_command(self):
        """A model with no command is unreachable; two would collide."""
        assert len(COMMANDS) == len({(module, name) for module, name, _ in COMMANDS})
        assert {fetcher_key(module, model) for module, _, model in COMMANDS} == set(
            openbb_fred.fred_provider.fetcher_dict
        )

    @pytest.mark.parametrize(("module", "flag"), MODULE_PARAMS)
    def test_a_sub_router_publishes_its_commands_only_while_it_stands_in(
        self, module, flag
    ):
        """An absent namespace extension is the only reason the commands exist."""
        declared = [name for owner, name, _ in COMMANDS if owner == module]

        assert declared
        assert published_commands(module) == ([] if INSTALLED[flag] else declared)

    def test_the_release_table_endpoints_are_served_either_way(self):
        """They are the provider's own, not a stand-in for economy."""
        from openbb_fred.routers import economy

        served = {route.path for route in economy.router.api_router.routes}

        assert served >= ECONOMY_OWN_ENDPOINTS

    def test_the_choice_endpoints_stay_out_of_the_published_schema(self):
        """They fill the widget's pickers; they are not commands to call."""
        from openbb_fred.routers import economy

        hidden = {
            route.path
            for route in economy.router.api_router.routes
            if not route.include_in_schema
        }

        assert hidden == ECONOMY_OWN_ENDPOINTS - {"/economy/release_table"}

    def test_every_picker_points_at_an_endpoint_that_is_served(self):
        """A picker whose options endpoint is missing opens empty."""
        from openbb_fred.routers import economy

        served = [route.path for route in economy.router.api_router.routes]
        pointed = {
            param["paramName"]: param["optionsEndpoint"]
            for param in economy.PRESENTATION_PARAMS
            if "optionsEndpoint" in param
        }

        assert list(pointed) == ["release_id", "element_id", "frequency"]

        for endpoint in pointed.values():
            assert any(endpoint.endswith(f"/fred{path}") for path in served), endpoint


class TestNamespaceTakeover:
    """What the provider publishes once the namespace extensions are installed."""

    @pytest.mark.parametrize(("module", "flag"), MODULE_PARAMS)
    def test_a_sub_router_stands_down_when_the_namespace_owner_is_installed(
        self, namespace_owners_installed, module, flag
    ):
        """The namespace owner takes the commands over entirely."""
        assert getattr(namespace_owners_installed, flag) is True
        assert [name for owner, name, _ in COMMANDS if owner == module]
        assert published_commands(module) == []

    def test_only_the_release_table_endpoints_outlive_the_takeover(
        self, namespace_owners_installed
    ):
        """They are the provider's own, so no namespace extension replaces them."""
        from openbb_fred.routers import economy

        assert {
            route.path for route in economy.router.api_router.routes
        } == ECONOMY_OWN_ENDPOINTS

    @pytest.mark.parametrize(
        "module", [module for module in SUB_ROUTERS if module != "economy"]
    )
    def test_a_stood_down_sub_router_serves_nothing_at_all(
        self, namespace_owners_installed, module
    ):
        """A stand-in with no command left has no route to publish."""
        assert list(sub_router(module).router.api_router.routes) == []

    def test_the_provider_registers_the_standard_model_names(
        self, namespace_owners_installed
    ):
        """The namespace owner's own model names replace the FRED aliases."""
        registered = set(namespace_owners_installed.fred_provider.fetcher_dict)

        assert "SOFR" in registered
        assert "FredSOFR" not in registered
        assert registered == STANDARD_KEYS

    def test_the_providers_own_models_keep_their_fred_names(
        self, namespace_owners_installed
    ):
        """Nothing owns the release, search, series and regional models but FRED."""
        registered = set(namespace_owners_installed.fred_provider.fetcher_dict)

        assert registered >= PROVIDER_OWN_MODELS

    def test_every_registered_fetcher_survives_the_rename(
        self, namespace_owners_installed
    ):
        """Renaming the keys must not drop or duplicate a fetcher."""
        registered = namespace_owners_installed.fred_provider.fetcher_dict

        assert len(registered) == len(COMMANDS)
        assert len(set(registered.values())) == len(COMMANDS)


class TestCommandRouting:
    """Each model-backed command hands its arguments to the model it declares."""

    @pytest.mark.parametrize(("module", "name", "model"), COMMAND_PARAMS)
    def test_a_command_is_bound_to_the_model_it_declares(self, module, name, model):
        """The decorator injects that model's own parameter classes."""
        from openbb_core.app.provider_interface import ProviderInterface

        interface = ProviderInterface()
        injected = {
            argument: get_args(parameter.annotation)[0]
            for argument, parameter in inspect.signature(
                command_of(module, name)
            ).parameters.items()
            if argument != "cc"
        }

        assert injected == {
            "provider_choices": interface.model_providers[model],
            "standard_params": interface.params[model]["standard"],
            "extra_params": interface.params[model]["extra"],
        }

    @pytest.mark.parametrize(("module", "name", "model"), COMMAND_PARAMS)
    def test_a_command_is_published_under_its_own_name(self, module, name, model):
        """The route path and the declared model both follow the function."""
        module_router = sub_router(module).router
        route = next(
            route
            for route in module_router.api_router.routes
            if route.endpoint is command_of(module, name)
        )

        assert route.path == f"{module_router.api_router.prefix}/{name}"
        assert route.openapi_extra["model"] == model

    @pytest.mark.parametrize(("module", "name", "model"), COMMAND_PARAMS)
    async def test_a_command_hands_the_query_its_arguments_and_nothing_else(
        self, handed, module, name, model
    ):
        """The body holds no other local, so the query carries nothing more."""
        given = arguments_for(model)

        await command_of(module, name)(**given)

        assert len(handed) == 1
        assert set(vars(handed[0])) == QUERY_ATTRIBUTES
        assert handed[0].cc is given["cc"]
        assert handed[0].standard_params is given["standard_params"]
        assert handed[0].extra_params is given["extra_params"]
        assert handed[0].name == model
        assert handed[0].provider == "fred"

    @pytest.mark.parametrize(("module", "name", "model"), COMMAND_PARAMS)
    async def test_a_command_returns_what_the_query_produced(
        self, handed, module, name, model
    ):
        """The command serves the query's result without touching it."""
        result = await command_of(module, name)(**arguments_for(model))

        assert result.results == [model]


class TestReleaseChoices:
    """The release picker behind the release table widget."""

    async def test_every_release_the_map_carries_is_offered(self):
        """A release missing from the picker cannot be reached."""
        from openbb_fred.routers.economy import release_choices
        from openbb_fred.utils.release_tables import release_map

        offered = await release_choices()

        assert {choice["value"] for choice in offered} == set(release_map())

    async def test_a_release_reads_as_its_name_and_its_id(self):
        """The id in brackets tells apart releases that share a name."""
        from openbb_fred.routers.economy import release_choices

        name = release_name(RETAIL_SALES_RELEASE)

        assert {
            "label": f"{name} ({RETAIL_SALES_RELEASE})",
            "value": RETAIL_SALES_RELEASE,
        } in await release_choices()

    async def test_the_releases_are_offered_in_name_order(self):
        """Hundreds of releases in id order make the picker unreadable."""
        from openbb_fred.routers.economy import release_choices

        labels = [choice["label"] for choice in await release_choices()]

        assert len(labels) > 1
        assert labels == sorted(labels)


class TestElementChoices:
    """The table picker, which narrows to the tables of one release."""

    async def test_the_tables_a_release_publishes_are_offered(self):
        """The picker reads the tables in the order the release publishes them."""
        from openbb_fred.routers.economy import element_choices

        offered = await element_choices(RETAIL_SALES_RELEASE)

        assert [choice["value"] for choice in offered] == RETAIL_SALES_TABLES

    async def test_a_release_that_publishes_no_table_offers_all_its_series(self):
        """Without a table the whole release is still readable."""
        from openbb_fred.routers.economy import element_choices

        assert await element_choices(NO_TABLE_RELEASE) == [
            {"label": "All Series", "value": ""}
        ]

    async def test_an_unknown_release_offers_nothing(self):
        """A release the map does not carry has no table to offer."""
        from openbb_fred.routers.economy import element_choices

        assert await element_choices(UNKNOWN_RELEASE) == []

    async def test_the_default_release_opens_on_a_table(self):
        """A default the picker cannot resolve opens the widget empty."""
        from openbb_fred.routers.economy import element_choices

        default = inspect.signature(element_choices).parameters["release_id"].default
        offered = await element_choices()

        assert release_tables(default)
        assert [choice["value"] for choice in offered] == release_tables(default)
        assert all(set(choice) == {"label", "value"} for choice in offered)
        assert all(isinstance(choice["label"], str) for choice in offered)
        assert all(choice["label"] for choice in offered)


class TestFrequencyChoices:
    """The frequency picker, which reads what the chosen table publishes."""

    @pytest.fixture
    def published(self, monkeypatch):
        """Serve one release's series without touching the network."""
        from datetime import date

        today = date.today().isoformat()
        series = {
            "A": {"series_id": "A", "frequency": "Monthly", "observation_end": today},
            "B": {"series_id": "B", "frequency": "Monthly", "observation_end": today},
            "C": {"series_id": "C", "frequency": "Quarterly", "observation_end": today},
        }

        async def observed(release_id, api_key, use_cache=True):
            return {"release_id": release_id}, series

        async def structure(release_id, element_id, api_key, use_cache=True):
            return [
                {"series_id": series_id, "name": series_id, "level": 1, "table": "T"}
                for series_id in series
            ]

        monkeypatch.setattr("openbb_fred.utils.v2.release_observations", observed)
        monkeypatch.setattr("openbb_fred.utils.release_tables.table_lines", structure)

    @pytest.fixture
    def asked(self, monkeypatch):
        """Take the arguments the frequency lookup is called with."""
        calls: list = []

        async def listing(release_id, element_id, credentials):
            calls.append((release_id, element_id, credentials))
            return []

        monkeypatch.setattr(
            "openbb_fred.utils.release_tables.list_frequencies", listing
        )

        return calls

    async def test_the_frequencies_the_table_publishes_are_offered(self, published):
        """Only the intervals the series actually carry reach the picker."""
        from openbb_fred.routers.economy import frequency_choices

        assert await frequency_choices("10") == [
            {"label": "Monthly", "value": "monthly"},
            {"label": "Quarterly", "value": "quarterly"},
        ]

    async def test_a_table_the_release_does_not_publish_is_resolved(self, asked):
        """A picker still holding another release's table would read nothing."""
        from openbb_fred.routers.economy import frequency_choices

        await frequency_choices(RETAIL_SALES_RELEASE, "not-a-table")

        assert [(release, element) for release, element, _ in asked] == [
            (RETAIL_SALES_RELEASE, RETAIL_SALES_TABLES[0])
        ]

    async def test_the_stored_credentials_reach_the_lookup(
        self, asked, stored_credentials
    ):
        """Without the key the lookup reads nothing and the picker opens empty."""
        from openbb_fred.routers.economy import frequency_choices

        await frequency_choices(RETAIL_SALES_RELEASE, RETAIL_SALES_TABLES[1])

        assert asked == [
            (
                RETAIL_SALES_RELEASE,
                RETAIL_SALES_TABLES[1],
                {"fred_api_key": "test-key"},
            )
        ]


class TestReleaseTable:
    """The release table command, which reads one published table directly."""

    @pytest.fixture
    def built(self, monkeypatch, stored_credentials):
        """Take the arguments the table builder is called with."""
        calls: list = []

        async def build(
            release_id, element_id, frequency, limit, api_key, *, use_cache=True
        ):
            calls.append(
                {
                    "release_id": release_id,
                    "element_id": element_id,
                    "frequency": frequency,
                    "limit": limit,
                    "api_key": api_key,
                    "use_cache": use_cache,
                }
            )
            return []

        monkeypatch.setattr(
            "openbb_fred.utils.release_tables.build_release_table", build
        )

        return calls

    async def test_a_table_the_release_does_not_publish_is_resolved(self, built):
        """The widget falls back to the first table the release publishes."""
        from openbb_fred.routers.economy import release_table

        await release_table(RETAIL_SALES_RELEASE, "not-a-table")

        assert built[0]["release_id"] == RETAIL_SALES_RELEASE
        assert built[0]["element_id"] == RETAIL_SALES_TABLES[0]

    async def test_the_table_that_was_asked_for_is_kept(self, built):
        """A table the release does publish is read as asked."""
        from openbb_fred.routers.economy import release_table

        await release_table(RETAIL_SALES_RELEASE, RETAIL_SALES_TABLES[2])

        assert built[0]["element_id"] == RETAIL_SALES_TABLES[2]

    async def test_no_frequency_leaves_the_choice_to_the_table(self, built):
        """An empty frequency asks for whatever the table mostly publishes."""
        from openbb_fred.routers.economy import release_table

        await release_table(RETAIL_SALES_RELEASE, RETAIL_SALES_TABLES[0])

        assert built[0]["frequency"] == ""

    async def test_a_chosen_frequency_is_carried_through(self, built):
        """The picker's interval reaches the builder unchanged."""
        from openbb_fred.routers.economy import release_table

        await release_table(RETAIL_SALES_RELEASE, RETAIL_SALES_TABLES[0], "monthly")

        assert built[0]["frequency"] == "monthly"

    async def test_the_stored_api_key_reaches_the_builder(self, built):
        """Without the key the builder reads nothing and the widget opens empty."""
        from openbb_fred.routers.economy import release_table

        await release_table(RETAIL_SALES_RELEASE, RETAIL_SALES_TABLES[0])

        assert built[0]["api_key"] == "test-key"

    async def test_the_cache_switch_reaches_the_builder(self, built):
        """Turning the cache off must reach the reads the builder makes."""
        from openbb_fred.routers.economy import release_table

        await release_table(
            RETAIL_SALES_RELEASE, RETAIL_SALES_TABLES[0], use_cache=False
        )

        assert built[0]["use_cache"] is False

    async def test_the_carried_symbol_does_not_narrow_the_table(self, built):
        """The table publishes the symbol; reading it would filter the rows."""
        from openbb_fred.routers.economy import release_table

        await release_table(
            RETAIL_SALES_RELEASE, RETAIL_SALES_TABLES[0], "monthly", 4, "RSFHFS"
        )
        await release_table(RETAIL_SALES_RELEASE, RETAIL_SALES_TABLES[0], "monthly", 4)

        assert built[0] == built[1]

    async def test_the_defaults_open_on_eight_periods_of_retail_sales(self, built):
        """The widget opens on a table without the pickers being touched."""
        from openbb_fred.routers.economy import release_table

        await release_table()

        assert built[0] == {
            "release_id": RETAIL_SALES_RELEASE,
            "element_id": RETAIL_SALES_TABLES[0],
            "frequency": "",
            "limit": 8,
            "api_key": "test-key",
            "use_cache": True,
        }

    async def test_the_rows_the_builder_returns_are_served_unchanged(
        self, monkeypatch, stored_credentials
    ):
        """The command presents the builder's rows, it does not reshape them."""
        rows = [{"series": "Total", "symbol": "RSAFS", "2024-01": 1.5}]

        async def build(*args, **kwargs):
            return rows

        monkeypatch.setattr(
            "openbb_fred.utils.release_tables.build_release_table", build
        )

        from openbb_fred.routers.economy import release_table

        assert await release_table(RETAIL_SALES_RELEASE, RETAIL_SALES_TABLES[0]) is rows
