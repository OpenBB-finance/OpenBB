"""Coverage for the dependency-injection rules in ``package_builder``.

These tests close the gaps in coverage around how the static package
builder discovers and wires FastAPI ``Depends(...)`` dependencies into
generated client methods. They cover three layers:

1. ``ImportDefinition.filter_hint_type_list`` — must skip both bare
   ``Depends`` instances and ``Annotated[X, Depends(...)]`` so they don't
   leak into the import block.

2. ``ImportDefinition.get_function_hint_type_list`` — must extract the
   ``meta.dependency`` callable out of ``Annotated[..., Depends(...)]``
   and add it to the import list (so generated code can call it).

3. Router-level dependencies discovered via
   ``PathHandler.get_router_dependencies`` and rendered through
   ``MethodDefinition._dependency_identifier`` and ``_build_func_params``
   into the generated method body — i.e. ``kwargs['x'] = get_x()``.

End-to-end builder runs are exercised in
``test_package_builder_generated.py``; this module focuses on the
DI-specific units that file does not cover.
"""

# flake8: noqa: E402

from inspect import _empty, signature
from typing import Annotated
from unittest.mock import patch

import pytest

pandas = pytest.importorskip("pandas")

from fastapi import APIRouter, Depends, Request

pytestmark = pytest.mark.requires_pandas

from openbb_core.app.router import Router
from openbb_core.app.static.package_builder import (
    ImportDefinition,
    MethodDefinition,
    PathHandler,
)

# ---------------------------------------------------------------------------
# Test helpers / sample dependencies
# ---------------------------------------------------------------------------


class MockDep:
    """Plain return type used by the safe sample dependency."""

    def __init__(self):
        self.value = "real"


def get_mock_dep() -> MockDep:
    """Safe DI factory — no Request, non-None return."""
    return MockDep()


def get_unsafe_dep(request: Request):
    """Unsafe DI factory — takes a Request and must be filtered out."""
    return request


def make_param(annotation):
    """Tiny helper: make a single-parameter signature carrying ``annotation``."""

    async def _fn(x: annotation = None):  # type: ignore[valid-type]
        return None

    return signature(_fn).parameters["x"]


# ---------------------------------------------------------------------------
# 1. filter_hint_type_list — skips Depends instances and Annotated[Depends]
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def import_def() -> ImportDefinition:
    """Module-scoped ``ImportDefinition`` for the filter tests."""
    return ImportDefinition()


def test_filter_hint_type_list_skips_bare_depends_instance(import_def):
    """A bare ``Depends(...)`` instance must not be emitted as an import."""
    dep_instance = Depends(get_mock_dep)
    output = import_def.filter_hint_type_list(
        hint_type_list=[dep_instance, MockDep, int, str, _empty]
    )
    assert dep_instance not in output, (
        "filter_hint_type_list leaked a bare Depends instance into imports"
    )
    # `MockDep` should pass through as a real type to import.
    assert MockDep in output, "real dependency return type should be importable"


def test_filter_hint_type_list_skips_annotated_with_depends(import_def):
    """``Annotated[X, Depends(...)]`` must be skipped to avoid bogus imports."""
    annotated_with_depends = Annotated[MockDep, Depends(get_mock_dep)]
    plain_annotated = Annotated[int, "metadata-only"]
    output = import_def.filter_hint_type_list(
        hint_type_list=[annotated_with_depends, plain_annotated, MockDep]
    )
    assert annotated_with_depends not in output, (
        "Annotated[X, Depends(...)] leaked into the import list"
    )


def test_filter_hint_type_list_keeps_annotated_without_depends(import_def):
    """An ``Annotated[X, ...]`` *without* ``Depends`` must NOT be filtered out.

    Guards against a regression where the Depends-detection accidentally
    swallowed every ``Annotated`` type.
    """

    class _SomeMeta:
        pass

    annotated_without_depends = Annotated[MockDep, _SomeMeta()]
    output = import_def.filter_hint_type_list(
        hint_type_list=[annotated_without_depends]
    )
    assert annotated_without_depends in output


# ---------------------------------------------------------------------------
# 2. get_function_hint_type_list — extracts meta.dependency for the import list
# ---------------------------------------------------------------------------


def test_get_function_hint_type_list_extracts_param_dependency(import_def):
    """Param-level ``Depends(get_mock_dep)`` must surface ``get_mock_dep`` for import."""

    async def endpoint(
        dep: Annotated[MockDep, Depends(get_mock_dep)],
    ) -> MockDep:
        return dep

    router = APIRouter()
    router.add_api_route("/x", endpoint, methods=["GET"], response_model=None)
    route = router.routes[0]

    hints = ImportDefinition.get_function_hint_type_list(route)

    assert get_mock_dep in hints, (
        "param-level Depends(get_mock_dep) must add the dep callable to the "
        f"import list; got {hints!r}"
    )


# ---------------------------------------------------------------------------
# 3. Router-level dependencies — discovery + rendering
# ---------------------------------------------------------------------------


@pytest.fixture
def router_with_router_level_dep(monkeypatch, fake_router):
    """Stamp a router-level ``Depends(get_mock_dep)`` onto the test sub-router.

    ``fake_router`` from ``conftest.py`` returns the *parent* Router; the
    real fake command lives on its ``/test`` child. We attach the
    dependency directly to the sub-router's APIRouter so
    ``PathHandler.get_router_dependencies("/test/...")`` finds it.
    """
    test_subrouter: Router = fake_router.routers["test"]
    test_subrouter.api_router.dependencies.append(Depends(get_mock_dep))
    return fake_router


def _resolve_test_path(router: Router) -> str:
    """Return the single registered sub-route path under ``/test``."""
    routes = router.routers["test"].api_router.routes
    assert routes, "fake_router has no sub-routes"
    return f"/test{routes[0].path}"


def test_get_router_dependencies_discovers_router_level_dep(
    router_with_router_level_dep,
):
    """``PathHandler.get_router_dependencies`` finds router-level Depends.

    Walks the path segments, asks each parent for ``api_router.dependencies``,
    and collects them dedup'd. We previously had zero tests for this.
    """
    path = _resolve_test_path(router_with_router_level_dep)

    deps = PathHandler.get_router_dependencies(path)

    funcs = [getattr(d, "dependency", None) for d in deps]
    assert get_mock_dep in funcs, (
        f"router-level Depends(get_mock_dep) was not discovered for {path!r}; "
        f"found deps={funcs!r}"
    )


def test_get_router_dependencies_dedupes_same_callable(
    router_with_router_level_dep,
):
    """Duplicate router-level Depends with the *same* callable collapse to one."""
    test_subrouter = router_with_router_level_dep.routers["test"]
    # Append a second Depends wrapping the SAME callable
    test_subrouter.api_router.dependencies.append(Depends(get_mock_dep))

    path = _resolve_test_path(router_with_router_level_dep)
    deps = PathHandler.get_router_dependencies(path)

    funcs = [getattr(d, "dependency", None) for d in deps]
    assert funcs.count(get_mock_dep) == 1, (
        f"router-level deps must be dedup'd by callable; got {funcs!r}"
    )


def test_get_path_hint_type_list_includes_router_level_dep(
    router_with_router_level_dep,
):
    """Router-level dep callable must also flow into the import list for the path."""
    path = _resolve_test_path(router_with_router_level_dep)

    hints = ImportDefinition.get_path_hint_type_list(path=path)

    assert get_mock_dep in hints, (
        f"router-level Depends callable should be importable; got {hints!r}"
    )


def test_dependency_identifier_uses_return_class_name():
    """`_dependency_identifier` derives the kwarg name from the return class."""

    def get_my_thing() -> MockDep:
        return MockDep()

    assert MethodDefinition._dependency_identifier(get_my_thing) == "mock_dep"


def test_dependency_identifier_strips_get_prefix_when_no_return_annotation():
    """No return annotation → strip ``get_`` prefix from the function name."""

    def get_widget():  # no return annotation
        return None

    assert MethodDefinition._dependency_identifier(get_widget) == "widget"


def test_dependency_identifier_uses_class_name_when_callable_is_class():
    """A class used as a dependency is identified by its (snake-cased) name."""

    class FancyService:
        pass

    assert MethodDefinition._dependency_identifier(FancyService) == "fancy_service"


def test_dependency_identifier_handles_string_return_annotation():
    """Forward-ref / string return annotations get their tail segment used."""

    def get_obj() -> "some.module.Thing":  # type: ignore[name-defined]  # noqa: F722, F821
        return None  # type: ignore[return-value]

    assert MethodDefinition._dependency_identifier(get_obj) == "thing"


def test_build_func_params_renders_router_level_dependency(
    router_with_router_level_dep,
):
    """End-to-end render: router-level Depends produces the kwargs wiring lines.

    This is the actual emitted-code contract: a router-level ``Depends(get_mock_dep)``
    must produce ``mock_dep = get_mock_dep()`` and ``kwargs['mock_dep'] = mock_dep``
    in the generated method body.
    """

    async def fake_func():
        return None

    path = _resolve_test_path(router_with_router_level_dep)

    code = MethodDefinition.build_command_method_body(path=path, func=fake_func)

    assert "mock_dep = get_mock_dep()" in code, code
    assert "kwargs['mock_dep'] = mock_dep" in code, code


def test_build_func_params_drops_unsafe_router_level_dependency(
    monkeypatch, fake_router
):
    """`_is_safe_dependency` gate: a router-level Request-bound Depends must NOT render."""
    test_subrouter = fake_router.routers["test"]
    test_subrouter.api_router.dependencies.append(Depends(get_unsafe_dep))

    async def fake_func():
        return None

    path = _resolve_test_path(fake_router)

    code = MethodDefinition.build_command_method_body(path=path, func=fake_func)

    assert "get_unsafe_dep" not in code, (
        f"unsafe (Request-bound) router-level dep must be filtered out, got:\n{code}"
    )


def test_build_func_params_renders_param_level_dependency(fake_router):
    """Param-level ``Depends(get_mock_dep)`` renders ``dep = get_mock_dep()`` in the body."""

    async def fake_func(dep: Annotated[MockDep, Depends(get_mock_dep)]):
        return dep

    path = _resolve_test_path(fake_router)

    # No router-level deps on this path — only the param-level dep should render.
    with patch.object(PathHandler, "get_router_dependencies", return_value=[]):
        code = MethodDefinition.build_command_method_body(path=path, func=fake_func)

    assert "dep = get_mock_dep()" in code, code
