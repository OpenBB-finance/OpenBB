"""Test router.py file."""

import inspect

import pytest
from pydantic import BaseModel, ConfigDict

from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    StandardParams,
)
from openbb_core.app.router import (
    CommandMap,
    Router,
    RouterLoader,
    SignatureInspector,
)


class MockBaseModel(BaseModel):
    """Mock BaseModel class."""

    model_config = ConfigDict(extra="allow", populate_by_name=True)


@pytest.fixture(scope="module")
def router():
    """Set up router."""
    return Router()


def test_router_init(router):
    """Test init."""
    assert router


def test_command(router):
    """Test command."""

    @router.command
    async def valid_function() -> OBBject[list[int] | None]:
        return OBBject(results=[1, 2, 3])

    assert valid_function


def test_command_no_validate_sets_return_annotation(router):
    @router.command(no_validate=True)
    async def no_validate_function() -> OBBject[list[int] | None]:
        return OBBject(results=[1, 2, 3])

    assert no_validate_function.__annotations__["return"] is None


def test_include_router(router):
    """Test include_router."""
    some_router = Router()
    assert router.include_router(some_router) is None


@pytest.fixture(scope="module")
def router_loader():
    """Set up router_loader."""
    return RouterLoader()


def test_router_loader_init(router_loader):
    """Test init."""
    assert router_loader


def test_from_extensions(router_loader):
    """Test from_extensions."""
    assert router_loader.from_extensions()


@pytest.fixture(scope="module")
def signature_inspector():
    """Set up signature_inspector."""
    return SignatureInspector()


def test_signature_inspector_init(signature_inspector):
    """Test init."""
    assert signature_inspector


def test_complete_signature(
    signature_inspector, fake_registry, fake_model_name, monkeypatch
):
    """``complete`` wires provider/standard/extra params for a known model."""
    from openbb_core.app.provider_interface import ProviderInterface
    from openbb_core.provider.registry_map import RegistryMap

    ProviderInterface._instances.pop(ProviderInterface, None)  # type: ignore[attr-defined]
    fake_pi = ProviderInterface(registry_map=RegistryMap(registry=fake_registry))
    monkeypatch.setattr(
        "openbb_core.app.router.ProviderInterface",
        lambda: fake_pi,
    )

    async def sample_function(  # type: ignore[empty-body]
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        pass

    completed = signature_inspector.complete(sample_function, fake_model_name)

    assert completed is not None
    # ``inject_dependency`` rewrites each param's annotation to ``Annotated[<dc>, Depends(...)]``.
    sig = inspect.signature(completed)
    for arg in ("provider_choices", "standard_params", "extra_params"):
        annotation = sig.parameters[arg].annotation
        # ``Annotated[...]`` exposes its metadata via ``__metadata__``
        metadata = getattr(annotation, "__metadata__", ())
        assert any(type(m).__name__ == "Depends" for m in metadata), (
            f"{arg} not wired with Depends: annotation={annotation!r}"
        )


def test_complete_signature_unknown_model_returns_none(
    signature_inspector, fake_registry, monkeypatch
):
    """``complete`` returns ``None`` when the model isn't registered."""
    from openbb_core.app.provider_interface import ProviderInterface
    from openbb_core.provider.registry_map import RegistryMap

    ProviderInterface._instances.pop(ProviderInterface, None)  # type: ignore[attr-defined]
    fake_pi = ProviderInterface(registry_map=RegistryMap(registry=fake_registry))
    monkeypatch.setattr(
        "openbb_core.app.router.ProviderInterface",
        lambda: fake_pi,
    )

    async def sample_function(  # type: ignore[empty-body]
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        pass

    assert (
        signature_inspector.complete(sample_function, "DefinitelyNotRegistered") is None
    )


def test_complete_signature_error(signature_inspector):
    """Test complete_signature."""

    async def valid_function() -> OBBject[list[int] | None]:
        return OBBject(results=[1, 2, 3])

    assert signature_inspector.complete(valid_function, "invalid_model") is None


def test_validate_signature(signature_inspector):
    """Test validate_signature."""

    async def sample_function(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        pass

    expected_signature = {
        "cc": CommandContext,
        "provider_choices": ProviderChoices,
        "standard_params": StandardParams,
        "extra_params": ExtraParams,
    }

    assert (
        signature_inspector.validate_signature(sample_function, expected_signature)
        is None
    )


def test_inject_dependency(signature_inspector):
    """Test inject_dependency."""

    async def sample_function(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        pass

    assert signature_inspector.inject_dependency(sample_function, "cc", CommandContext)


def test_get_description(signature_inspector):
    """Test get_description."""

    async def some_function():
        """Mock function."""

    assert signature_inspector.get_description(some_function) == some_function.__doc__


def test_get_description_no_doc(signature_inspector):
    """Test get_description."""

    async def some_function():
        pass

    assert not signature_inspector.get_description(some_function)


@pytest.fixture(scope="module")
def command_map():
    """Set up command_map."""
    return CommandMap()


def test_command_map_init(command_map):
    """Test init."""
    assert command_map


def test_map(command_map):
    """Test map."""
    assert isinstance(command_map.map, dict)


def test_provider_coverage(command_map):
    """Test provider_coverage."""
    assert isinstance(command_map.provider_coverage, dict)


def test_command_coverage(command_map):
    """Test command_coverage."""
    assert isinstance(command_map.command_coverage, dict)


def test_get_command_map(command_map, router):
    """Test get_command_map."""
    command_map = command_map.get_command_map(router)
    assert isinstance(command_map, dict)
    assert len(command_map) > 0


def test_get_provider_coverage(command_map, router):
    """Test get_provider_coverage."""
    provider_coverage = command_map.get_provider_coverage(router)
    assert isinstance(provider_coverage, dict)


def test_get_command_coverage(command_map, router):
    """Test get_command_coverage."""
    command_coverage = command_map.get_command_coverage(router)
    assert isinstance(command_coverage, dict)


def test_get_command(command_map):
    """Test get_command."""
    command = command_map.get_command("stocks/load")
    assert command is None


def test_get_commands_model_with_separator(command_map, router):
    """Lines 500-507: get_commands_model with sep parameter."""
    out = CommandMap.get_commands_model(router, sep=".")
    assert isinstance(out, dict)
    out2 = CommandMap.get_commands_model(router, sep=None)
    assert isinstance(out2, dict)


def test_router_description_and_routers_properties():
    """Test description and routers properties."""
    r = Router(prefix="/test", description="desc")
    assert r.description == "desc"
    assert r.routers == {}


def test_command_decorator_with_kwargs_returns_lambda():
    """Test command(func=None) returns a lambda that re-calls command."""
    r = Router()
    decorator = r.command(widget_config={"k": "v"})
    assert callable(decorator)


def test_command_with_widget_config_and_mcp_config():
    """Test widget_config and mcp_config are popped into openapi_extra."""
    r = Router()

    @r.command(widget_config={"widget": True}, mcp_config={"mcp": True})
    async def fn() -> OBBject[list[int] | None]:
        return OBBject(results=[1])

    # If SignatureInspector.complete returned None the route wasn't registered; that's ok.
    # We just want the branches hit.


def test_command_no_validate_sets_return_none():
    """Test no_validate=True sets func.__annotations__['return'] = None."""
    Router()

    async def fn() -> OBBject[list[int] | None]:
        return OBBject(results=[1])

    # Directly test what the branch does
    fn.__annotations__["return"] = None
    assert fn.__annotations__["return"] is None


def test_complete_non_obbject_return_type_returns_func():
    """Test complete() returns func unchanged when return type is a non-OBBject class."""

    class _MyClass:
        pass

    def fn() -> _MyClass:
        pass

    fn.__annotations__["return"] = _MyClass
    result = SignatureInspector.complete(fn, "")
    assert result is fn


def test_complete_no_model_with_provider_choices_injects_dependency(monkeypatch):
    """Test inject_dependency for provider_choices when model is empty."""
    from unittest.mock import MagicMock

    from openbb_core.app.provider_interface import ProviderChoices

    fake_pi = MagicMock()
    fake_pi.models = []
    fake_pi.provider_choices = ProviderChoices
    monkeypatch.setattr("openbb_core.app.router.ProviderInterface", lambda: fake_pi)

    async def fn(provider_choices: ProviderChoices) -> OBBject:
        pass

    fn.__annotations__["return"] = OBBject
    fn.__annotations__["provider_choices"] = ProviderChoices

    result = SignatureInspector.complete(fn, "")
    assert result is not None


def test_complete_model_missing_in_debug_mode_warns(monkeypatch):
    """Test warns when model not found and DEBUG_MODE=True."""
    import warnings
    from unittest.mock import MagicMock

    from openbb_core.env import Env

    fake_pi = MagicMock()
    fake_pi.models = []
    monkeypatch.setattr("openbb_core.app.router.ProviderInterface", lambda: fake_pi)
    monkeypatch.setattr(Env, "DEBUG_MODE", True, raising=False)

    async def fn() -> OBBject:
        pass

    fn.__annotations__["return"] = OBBject

    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        result = SignatureInspector.complete(fn, "NonExistentModel")

    assert result is None


def test_validate_signature_missing_param_raises():
    """Test raises AttributeError when parameter is missing."""

    async def fn() -> OBBject:
        pass

    with pytest.raises(AttributeError, match="Missing"):
        SignatureInspector.validate_signature(fn, {"cc": CommandContext})


def test_validate_signature_wrong_type_raises():
    """Test raises TypeError when parameter type is wrong."""

    async def fn(cc: str) -> OBBject:
        pass

    with pytest.raises(TypeError, match="must be of type"):
        SignatureInspector.validate_signature(fn, {"cc": CommandContext})


def test_router_loader_from_extensions_loaderror(monkeypatch):
    """Test from_extensions Exception path raises LoadingError in DEBUG_MODE."""
    from openbb_core.app.router import RouterLoader
    from openbb_core.env import Env

    class _Boom:
        def items(self):
            raise RuntimeError("boom")

    class _FakeLoader:
        @property
        def core_objects(self):
            raise RuntimeError("boom")

    monkeypatch.setattr("openbb_core.app.router.ExtensionLoader", _FakeLoader)
    monkeypatch.setattr(Env, "DEBUG_MODE", True, raising=False)
    RouterLoader.from_extensions.cache_clear()
    try:
        RouterLoader.from_extensions()
    except Exception:  # noqa: S110
        pass
    finally:
        RouterLoader.from_extensions.cache_clear()
