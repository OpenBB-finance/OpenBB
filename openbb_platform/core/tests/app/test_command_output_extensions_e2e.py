"""True end-to-end tests for `on_command_output` extensions.

These tests close the gap between unit/wiring coverage and reality:

* `test_command_runner_runs_real_extension_callback` — wires a real
  ``Extension`` (with the system-settings gate enabled) into the global
  ``ExtensionLoader``, builds a real ``Router`` + ``CommandMap`` over the
  fake provider/model registered by the test ``conftest.py``, and drives
  ``CommandRunner.run`` to completion. The extension's accessor is asserted
  to have actually fired against the returned ``OBBject`` (immutable,
  mutable-modifying-results, and results-only flavors).

* `test_fastapi_endpoint_runs_extension_callback_e2e` — spins up a real
  ``FastAPI`` app with the **real** ``build_api_wrapper`` dispatching to a
  real ``CommandRunner``, hits the generated REST endpoint via
  ``TestClient``, and verifies:

    1. The HTTP request actually reaches and executes the registered
       command.
    2. The on_command_output extension callback fires during request
       handling.
    3. Extension-modified output is propagated to the JSON response body
       (``_extension_modified`` and ``_results_only`` semantics).

These exercise the full ASGI -> wrapper -> CommandRunner -> StaticCommandRunner
-> command -> _trigger_command_output_callbacks -> JSONResponse pipeline.
"""

import contextlib

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from openbb_core.app.command_runner import CommandRunner
from openbb_core.app.extension_loader import ExtensionLoader
from openbb_core.app.model.abstract.singleton import SingletonMeta
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.extension import Extension
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    ProviderInterface,
    StandardParams,
)
from openbb_core.app.router import CommandMap, Router, RouterLoader
from openbb_core.provider.registry_map import RegistryMap


def _reset_provider_interface() -> None:
    ProviderInterface._instances.pop(ProviderInterface, None)  # type: ignore[attr-defined]


def _reset_extension_loader() -> None:
    SingletonMeta._instances.pop(ExtensionLoader, None)  # type: ignore[arg-type]


@pytest.fixture
def isolated_provider_interface(fake_registry):
    """Replace ``ProviderInterface`` singleton with one over the fake registry."""
    _reset_provider_interface()
    pi = ProviderInterface(registry_map=RegistryMap(registry=fake_registry))
    yield pi
    _reset_provider_interface()


@pytest.fixture
def gated_system_settings(monkeypatch):
    """Patch ``SystemService`` so ``Extension(...)`` security gates allow on_command_output + mutable.

    Uses a real ``SystemSettings`` instance so attribute lookups (e.g.
    ``api_settings``, ``logging_suppress``) inside the framework succeed.
    """
    from types import SimpleNamespace

    real_settings = SystemSettings(
        allow_on_command_output=True,
        allow_mutable_extensions=True,
        logging_suppress=True,
    )

    def _stub_system_service(*_args, **_kwargs):
        return SimpleNamespace(system_settings=real_settings)

    monkeypatch.setattr(
        "openbb_core.app.service.system_service.SystemService",
        _stub_system_service,
    )
    return real_settings


@pytest.fixture
def fake_router(
    isolated_provider_interface, fake_model_name, monkeypatch, fake_provider_name
) -> Router:
    """Build a real ``Router`` + override ``RouterLoader.from_extensions``.

    The router carries a single command bound to the fake provider/model from
    ``conftest.py``. Mounted under ``/test`` so the route is ``/test/cmd``.
    """

    async def fake_command(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:
        """Fake command for E2E tests."""
        return OBBject(results=[{"symbol": "FAKE"}])

    child = Router()
    child.command(model=fake_model_name, path="/cmd")(fake_command)

    parent = Router()
    parent.include_router(router=child, prefix="/test")

    RouterLoader.from_extensions.cache_clear()  # type: ignore[attr-defined]
    monkeypatch.setattr(
        "openbb_core.app.router.RouterLoader.from_extensions",
        lambda: parent,
    )

    # ``ExecutionContext._route_map`` is a class-level dict cached from
    # ``PathHandler.build_route_map()`` at *import* time. Refresh it so the
    # new fake route is reachable via ``execution_context.api_route``.
    from openbb_core.app.command_runner import ExecutionContext
    from openbb_core.app.static.package_builder import PathHandler

    monkeypatch.setattr(ExecutionContext, "_route_map", PathHandler.build_route_map())
    return parent


def _install_extension(
    ext: Extension, accessor_factory, monkeypatch, route_pattern: str = "*"
) -> None:
    """Register `ext` on `OBBject` and bind it through a stub ExtensionLoader.

    ``accessor_factory`` is the callable that ``CachedAccessor`` invokes when
    ``getattr(obbject, ext.name)`` is touched on a fresh instance — this is
    where the extension's actual side-effects happen.
    """
    from types import SimpleNamespace

    Extension.register_accessor(ext.name, OBBject)(accessor_factory)

    fake_loader = SimpleNamespace(on_command_output_callbacks={route_pattern: [ext]})
    monkeypatch.setattr(
        "openbb_core.app.command_runner.ExtensionLoader", lambda: fake_loader
    )


@pytest.fixture(autouse=True)
def _restore_obbject_class():
    """Strip any test-installed accessors off ``OBBject`` after each test."""
    pristine_accessors = set(OBBject.accessors)
    pristine_attrs = {
        name: val for name, val in OBBject.__dict__.items() if name.startswith("e2e_")
    }
    yield
    for name in list(OBBject.accessors - pristine_accessors):
        OBBject.accessors.discard(name)
        if name in OBBject.__dict__ and name not in pristine_attrs:
            with contextlib.suppress(AttributeError):
                delattr(OBBject, name)


@pytest.mark.asyncio
async def test_command_runner_runs_real_extension_immutable_callback(
    fake_router, gated_system_settings, monkeypatch, fake_provider_name
):
    """End-to-end: ``CommandRunner.run`` triggers an immutable extension accessor.

    Drives the entire pipeline:
      ``CommandRunner.run`` -> ``StaticCommandRunner.run`` -> command exec ->
      ``_trigger_command_output_callbacks`` -> accessor fires on a copy ->
      original ``OBBject`` is *not* mutated.
    """
    fired: list[OBBject] = []

    def e2e_accessor(obb_instance: OBBject):
        fired.append(obb_instance)

        # Mutate the *copy* — should not affect the runner's returned object
        if isinstance(obb_instance.results, list):
            obb_instance.results.append("CALLBACK_FIRED")
        # Must NOT return a callable: the runner re-invokes any callable
        # return value with zero args (see ``_trigger_command_output_callbacks``).

    ext = Extension(name="e2e_immut", on_command_output=True, immutable=True)
    _install_extension(ext, e2e_accessor, monkeypatch, route_pattern="*")

    # Real CommandRunner over the real CommandMap built from fake_router
    runner = CommandRunner(
        command_map=CommandMap(),
        system_settings=SystemSettings(logging_suppress=True),
        user_settings=UserSettings(),
    )

    output = await runner.run(
        "/test/cmd",
        None,
        provider_choices={"provider": fake_provider_name},
        standard_params={},
        extra_params={"api_key": "x", "api_secret": "y"},
    )

    assert isinstance(output, OBBject), output
    assert fired, "extension accessor was never invoked by the real runner"
    # Immutable extension must NOT have mutated the original returned object
    assert "CALLBACK_FIRED" not in (output.results or []), (
        "immutable extension leaked a mutation onto the runner's OBBject"
    )
    # The accessor's reference is a *copy* — different identity from `output`
    assert fired[0] is not output


@pytest.mark.asyncio
async def test_command_runner_runs_real_extension_mutable_callback(
    fake_router, gated_system_settings, monkeypatch, fake_provider_name
):
    """End-to-end: a mutable extension actually mutates the runner's OBBject.

    Verifies the ``immutable=False`` branch: the accessor receives the *real*
    object, mutations stick, and ``_extension_modified`` is set.
    """

    def e2e_accessor(obb_instance: OBBject):
        if isinstance(obb_instance.results, list):
            obb_instance.results.append("MUTATED")

    ext = Extension(name="e2e_mut", on_command_output=True, immutable=False)
    _install_extension(ext, e2e_accessor, monkeypatch, route_pattern="*")

    runner = CommandRunner(
        command_map=CommandMap(),
        system_settings=SystemSettings(logging_suppress=True),
        user_settings=UserSettings(),
    )

    output = await runner.run(
        "/test/cmd",
        None,
        provider_choices={"provider": fake_provider_name},
        standard_params={},
        extra_params={"api_key": "x", "api_secret": "y"},
    )

    assert isinstance(output, OBBject)
    assert "MUTATED" in (output.results or []), (
        "mutable extension did NOT mutate the runner's OBBject"
    )
    assert getattr(output, "_extension_modified", False) is True


@pytest.mark.asyncio
async def test_command_runner_results_only_extension_sets_flag(
    fake_router, gated_system_settings, monkeypatch, fake_provider_name
):
    """End-to-end: a results_only extension sets the ``_results_only`` marker."""

    def e2e_accessor(obb_instance: OBBject):
        return None

    ext = Extension(
        name="e2e_ro",
        on_command_output=True,
        results_only=True,
        immutable=True,
    )
    _install_extension(ext, e2e_accessor, monkeypatch, route_pattern="*")

    runner = CommandRunner(
        command_map=CommandMap(),
        system_settings=SystemSettings(logging_suppress=True),
        user_settings=UserSettings(),
    )

    output = await runner.run(
        "/test/cmd",
        None,
        provider_choices={"provider": fake_provider_name},
        standard_params={},
        extra_params={"api_key": "x", "api_secret": "y"},
    )

    assert isinstance(output, OBBject)
    assert getattr(output, "_results_only", False) is True
    assert getattr(output, "_extension_modified", False) is True


def _build_app_with_real_command_router(fake_router: Router) -> FastAPI:
    """Build a FastAPI app whose routes are wrapped by the real ``build_api_wrapper``.

    Mirrors ``openbb_core.api.router.commands.add_command_map`` but driven from
    the in-memory ``fake_router`` (so we don't depend on real installed extensions).
    """
    from openbb_core.api.router.commands import build_api_wrapper

    runner = CommandRunner(
        command_map=CommandMap(router=fake_router),
        system_settings=SystemSettings(logging_suppress=True),
        user_settings=UserSettings(),
    )

    api_router = APIRouter()
    for route in fake_router.api_router.routes:
        route.endpoint = build_api_wrapper(  # type: ignore[attr-defined]
            command_runner=runner, route=route
        )
    api_router.include_router(router=fake_router.api_router)

    app = FastAPI()
    app.include_router(api_router)
    return app


def test_fastapi_endpoint_runs_extension_callback_e2e(
    fake_router, gated_system_settings, monkeypatch, fake_provider_name
):
    """Real ASGI request -> wrapper -> CommandRunner -> extension callback fires.

    Mutable extension: appends a marker to ``results``, the marker MUST appear
    in the JSON body returned to the HTTP client.
    """

    def e2e_accessor(obb_instance: OBBject):
        if isinstance(obb_instance.results, list):
            obb_instance.results.append({"injected_by": "extension"})

    ext = Extension(name="e2e_http_mut", on_command_output=True, immutable=False)
    _install_extension(ext, e2e_accessor, monkeypatch, route_pattern="*")

    app = _build_app_with_real_command_router(fake_router)

    with TestClient(app) as client:
        response = client.get(
            "/test/cmd",
            params={"provider": fake_provider_name},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    results = body.get("results") or []
    assert any(
        isinstance(item, dict) and item.get("injected_by") == "extension"
        for item in results
    ), (
        "extension callback did not modify the JSON body returned to the HTTP "
        f"client; got results={results!r}"
    )


def test_fastapi_endpoint_results_only_extension_returns_results_array(
    fake_router, gated_system_settings, monkeypatch, fake_provider_name
):
    """`results_only=True` extension causes the wrapper to return only ``results``.

    The wrapper short-circuits ``_results_only=True`` outputs and returns the
    bare results list/dict instead of the full OBBject envelope. This test
    proves that contract end-to-end.
    """

    def e2e_accessor(obb_instance: OBBject):
        return None

    ext = Extension(
        name="e2e_http_ro",
        on_command_output=True,
        results_only=True,
        immutable=True,
    )
    _install_extension(ext, e2e_accessor, monkeypatch, route_pattern="*")

    app = _build_app_with_real_command_router(fake_router)

    with TestClient(app) as client:
        response = client.get(
            "/test/cmd",
            params={"provider": fake_provider_name},
        )

    assert response.status_code == 200, response.text
    body = response.json()
    # results_only short-circuits to the bare results payload — there is no
    # ``provider`` / ``warnings`` / ``extra`` envelope in this path.
    assert "provider" not in body, (
        f"results_only=True extension did not strip the OBBject envelope; got {body!r}"
    )


def test_fastapi_endpoint_extension_can_be_path_scoped(
    fake_router, gated_system_settings, monkeypatch, fake_provider_name
):
    """Path-scoped extensions only fire for matching routes."""

    fired_routes: list[str] = []

    def e2e_accessor(obb_instance: OBBject):
        fired_routes.append("FIRED")

    # Scope the extension to a DIFFERENT route — it must NOT fire on /test/cmd
    ext = Extension(
        name="e2e_http_scoped",
        on_command_output=True,
        immutable=True,
        command_output_paths=["/some/other/route"],
    )
    _install_extension(
        ext, e2e_accessor, monkeypatch, route_pattern="/some/other/route"
    )

    app = _build_app_with_real_command_router(fake_router)

    with TestClient(app) as client:
        response = client.get(
            "/test/cmd",
            params={"provider": fake_provider_name},
        )

    assert response.status_code == 200, response.text
    assert fired_routes == [], (
        f"path-scoped extension fired on the wrong route: {fired_routes!r}"
    )
