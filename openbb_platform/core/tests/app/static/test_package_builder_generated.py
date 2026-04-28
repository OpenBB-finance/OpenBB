"""End-to-end tests for the static package generator.

These tests exercise the *full* code-generation pipeline and verify the
output is real, valid Python that can be imported and invoked. Unlike
``test_package_builder.py``, which tests individual emitter methods by
string equality on rendered fragments, this module:

1. Builds a synthetic ``Router`` containing one or more fake commands
   tied to the fake provider/model registered in ``conftest.py``.
2. Runs ``PackageBuilder.build()`` against a temp directory **with the
   same ``ruff --fix`` lint pass production uses** — without that pass,
   the generated package is not importable (see comment at
   ``ImportDefinition.build`` in ``package_builder.py`` ~line 560).
3. Parses every emitted ``.py`` file with ``ast.parse`` and ``compile``
   to prove the output is syntactically valid Python.
4. Imports each generated module via ``importlib`` and verifies the
   container class, method signatures, decorators, docstrings, and
   property accessors match the documented contract.
5. Invokes generated command methods against a stub ``CommandRunner``
   and asserts they dispatch to ``Container._run`` with the correct
   route path, ``provider_choices`` payload, and forwarded kwargs.
"""

import ast
import importlib.util
import shutil
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from openbb_core.app.deprecation import OpenBBDeprecationWarning
from openbb_core.app.model.command_context import CommandContext
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.provider_interface import (
    ExtraParams,
    ProviderChoices,
    ProviderInterface,
    StandardParams,
)
from openbb_core.app.router import Router, RouterLoader
from openbb_core.app.static.package_builder import PackageBuilder
from openbb_core.provider.registry_map import RegistryMap

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _reset_provider_interface() -> None:
    """Drop the ``ProviderInterface`` singleton so the next call rebuilds it."""
    ProviderInterface._instances.pop(ProviderInterface, None)  # type: ignore[attr-defined]


@pytest.fixture
def isolated_provider_interface(fake_registry):
    """Replace the ``ProviderInterface`` singleton with one over the primary fake registry."""
    _reset_provider_interface()
    pi = ProviderInterface(registry_map=RegistryMap(registry=fake_registry))
    yield pi
    _reset_provider_interface()


@pytest.fixture
def isolated_multi_provider_interface(multi_provider_registry):
    """Replace the singleton with a ``ProviderInterface`` over the multi-provider registry."""
    _reset_provider_interface()
    pi = ProviderInterface(registry_map=RegistryMap(registry=multi_provider_registry))
    yield pi
    _reset_provider_interface()


def _make_fake_command():
    """Return a fresh async fake command with the four model-driven dependencies.

    The function is freshly defined per call because ``Router.command`` mutates
    ``func.__annotations__`` in-place via ``inject_dependency`` /
    ``inject_return_annotation`` — sharing one function across routers would
    cross-contaminate state.
    """

    async def fake_command(
        cc: CommandContext,
        provider_choices: ProviderChoices,
        standard_params: StandardParams,
        extra_params: ExtraParams,
    ) -> OBBject:  # type: ignore[empty-body]
        """Fake command for generator testing."""

    return fake_command


@pytest.fixture
def install_router(monkeypatch):
    """Factory that mounts a built ``Router`` as the global ``RouterLoader.from_extensions`` result."""

    def _install(child: Router, prefix: str = "/test") -> Router:
        parent = Router()
        parent.include_router(router=child, prefix=prefix)
        RouterLoader.from_extensions.cache_clear()  # type: ignore[attr-defined]
        monkeypatch.setattr(
            "openbb_core.app.router.RouterLoader.from_extensions",
            lambda: parent,
        )
        return parent

    return _install


@pytest.fixture
def fake_router(isolated_provider_interface, fake_model_name, install_router) -> Router:
    """Construct a ``Router`` with one fake command using the primary fake provider."""
    child = Router()
    child.command(model=fake_model_name)(_make_fake_command())
    return install_router(child, prefix="/test")


@pytest.fixture
def multi_provider_router(
    isolated_multi_provider_interface, fake_model_name, install_router
) -> Router:
    """Construct a ``Router`` whose single command is backed by both fake providers."""
    child = Router()
    child.command(model=fake_model_name)(_make_fake_command())
    return install_router(child, prefix="/test")


def _build(tmp_path: Path) -> Path:
    """Run ``PackageBuilder.build()`` with production-equivalent lint."""
    if not shutil.which("ruff") or not shutil.which("black"):
        pytest.skip("ruff and black are required to lint the generated package")
    builder = PackageBuilder(directory=tmp_path, lint=True, verbose=False)
    with patch.object(builder, "_save_reference_file"):
        builder.build()
    return tmp_path


@pytest.fixture
def built_package_dir(tmp_path: Path, fake_router: Router) -> Path:
    """Build the package against a tmp dir using the single-provider fixture."""
    return _build(tmp_path)


@pytest.fixture
def built_multi_provider_dir(tmp_path: Path, multi_provider_router: Router) -> Path:
    """Build the package using the multi-provider fixture."""
    return _build(tmp_path)


# ---------------------------------------------------------------------------
# 1. Generated files are valid Python
# ---------------------------------------------------------------------------


def _emitted_py_files(package_dir: Path) -> list[Path]:
    return sorted((package_dir / "package").glob("*.py"))


def test_build_emits_at_least_one_generated_module(built_package_dir):
    """The generator must produce at least one ``.py`` file under ``package/``."""
    files = _emitted_py_files(built_package_dir)
    assert files, f"No .py files emitted under {built_package_dir / 'package'}"


def test_generated_modules_are_syntactically_valid_python(built_package_dir):
    """Every emitted ``.py`` file must ``ast.parse`` cleanly.

    This is the core smoke test for the generator: it catches all the
    classic codegen failures — unbalanced parens, missing colons, bad
    indentation, malformed type expressions — that the existing
    string-equality tests cannot detect.
    """
    files = _emitted_py_files(built_package_dir)
    for path in files:
        source = path.read_text(encoding="utf-8")
        try:
            ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            pytest.fail(
                f"Generated module {path} is not valid Python: {exc}\n\n--- source ---\n{source}\n--- end ---"
            )


def test_generated_modules_compile_to_bytecode(built_package_dir):
    """Generated modules must compile to bytecode (catches name-binding bugs ``ast.parse`` misses).

    ``compile`` runs the full parser+compiler pipeline, including checks
    like duplicate keyword arguments and assignments to literals.
    """
    files = _emitted_py_files(built_package_dir)
    for path in files:
        source = path.read_text(encoding="utf-8")
        try:
            compile(source, str(path), "exec")
        except (SyntaxError, ValueError) as exc:
            pytest.fail(f"Generated module {path} did not compile: {exc}")


def test_init_module_is_emitted(built_package_dir):
    """``__init__.py`` is written into the package dir."""
    init = built_package_dir / "package" / "__init__.py"
    assert init.exists()
    assert "AUTO-GENERATED" in init.read_text()


# ---------------------------------------------------------------------------
# 2. Generated package imports and exposes the expected API
# ---------------------------------------------------------------------------


def _import_module_from_path(name: str, path: Path) -> Any:
    """Import a generated module file as a top-level module."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return module


def test_generated_command_method_imports_and_has_expected_signature(
    built_package_dir,
):
    """Generated module imports cleanly and exposes the fake command method.

    The generator deliberately emits a superset of imports (``import
    pandas``, ``import numpy``, ``from openbb_core.app.provider_interface
    import OBBject_<Model>``, etc.) and relies on ``ruff --fix --unsafe-fixes``
    in ``_run_linters`` to strip those that are unused by the rendered
    method body — see the comment at ``ImportDefinition.build``
    (package_builder.py ~line 560). With ``lint=True`` the generated
    module imports cleanly without pandas/numpy installed because the
    fake command's signature does not reference any of those types.
    """
    files = _emitted_py_files(built_package_dir)
    # Find the module that contains the fake_command — exclude __init__
    candidates = [p for p in files if p.name != "__init__.py"]
    assert candidates, "No non-__init__ modules emitted"

    found_command = False
    for path in candidates:
        try:
            mod = _import_module_from_path(f"_gen_{path.stem}", path)
        except Exception as exc:  # pragma: no cover - aids debugging
            pytest.fail(
                f"Generated module {path} failed to import: {exc}\n\n--- source ---\n{path.read_text()}\n--- end ---"
            )

        # Each generated module exports a single class (per ``ClassDefinition``).
        cls_names = [
            name
            for name in dir(mod)
            if isinstance(getattr(mod, name), type)
            and getattr(mod, name).__module__ == mod.__name__
        ]
        for cls_name in cls_names:
            cls = getattr(mod, cls_name)
            if hasattr(cls, "fake_command"):
                method = cls.fake_command
                assert callable(method)
                found_command = True
                break
        if found_command:
            break

    assert found_command, (
        "fake_command method not found on any generated container class"
    )


def test_generated_command_dispatches_to_container_run(
    built_package_dir, fake_model_name
):
    """Calling the generated method dispatches through ``Container._run`` with the correct path.

    This is the contract that matters most: the static package is a
    typed shim that calls into the dynamic command runner. If the
    generator emits the wrong path string, every consumer of the static
    package silently calls the wrong route.
    """
    target_class = _locate_container_class(built_package_dir, "fake_command")
    assert target_class is not None, "Could not locate generated container class"

    instance, captured = _instantiate_with_capturing_run(target_class)
    sentinel = OBBject(results=[{"symbol": "FAKE"}])
    captured["return_value"] = sentinel

    result = instance.fake_command(provider="fake")

    assert result is sentinel
    assert captured["args"], "Container._run called without a path"
    route_path = captured["args"][0]
    assert route_path == "/test/fake_command", (
        f"Expected route path '/test/fake_command', got {route_path!r}"
    )


# ---------------------------------------------------------------------------
# 3. Behavioral contract: provider routing, dispatch payload, sub-routers
# ---------------------------------------------------------------------------


def _locate_container_class(package_dir: Path, method_name: str):
    """Import every generated module and return the container class exposing ``method_name``."""
    for path in [p for p in _emitted_py_files(package_dir) if p.name != "__init__.py"]:
        mod = _import_module_from_path(f"_load_{path.stem}_{method_name}", path)
        for name in dir(mod):
            obj = getattr(mod, name)
            if (
                isinstance(obj, type)
                and obj.__module__ == mod.__name__
                and hasattr(obj, method_name)
            ):
                return obj
    return None


def _instantiate_with_capturing_run(container_cls):
    """Build a container instance whose ``_run`` records args/kwargs into a dict."""
    runner = MagicMock()
    runner.user_settings = MagicMock(defaults=MagicMock(commands={}))
    runner.system_settings = MagicMock()
    instance = container_cls(command_runner=runner)

    captured: dict = {"return_value": None}

    def fake_run(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return captured["return_value"]

    instance._run = fake_run  # type: ignore[method-assign]
    return instance, captured


def _command_module_source(package_dir: Path, method_name: str) -> tuple[Path, str]:
    """Return ``(path, source)`` for the generated module that defines ``method_name``."""
    for path in [p for p in _emitted_py_files(package_dir) if p.name != "__init__.py"]:
        source = path.read_text()
        if f"def {method_name}(" in source:
            return path, source
    pytest.fail(f"No emitted module defines '{method_name}'")


def _find_method_def(source: str, method_name: str) -> ast.FunctionDef:
    """Locate the ``ast.FunctionDef`` for ``method_name`` in ``source``."""
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            return node
    pytest.fail(f"AST: no FunctionDef named '{method_name}' in source")


def test_extensions_module_emitted_with_root_class(built_package_dir):
    """Root path emits ``__extensions__.py`` exposing an ``Extensions`` container subclass."""
    ext_path = built_package_dir / "package" / "__extensions__.py"
    assert ext_path.exists(), "Expected __extensions__.py at the package root"

    mod = _import_module_from_path("_ext_root", ext_path)
    assert hasattr(mod, "Extensions"), "Extensions class missing on __extensions__"
    from openbb_core.app.static.container import Container

    assert issubclass(mod.Extensions, Container)


def test_router_module_class_name_matches_path_handler_contract(built_package_dir):
    """The container class name must follow ``ROUTER_<clean_path>`` from PathHandler."""
    from openbb_core.app.static.package_builder import PathHandler

    expected = PathHandler.build_module_class("/test")
    target_class = _locate_container_class(built_package_dir, "fake_command")
    assert target_class is not None
    assert target_class.__name__ == expected, (
        f"Expected class {expected!r}, got {target_class.__name__!r}"
    )


def test_root_extensions_class_exposes_test_property(built_package_dir):
    """Root ``Extensions`` class exposes a ``test`` property that returns a ``ROUTER_test``.

    The generated ``Extensions.test`` body does ``from . import test`` to lazily
    load the sibling module — which only works when the module is imported as
    part of a real package. Add ``built_package_dir`` to ``sys.path`` and import
    ``package`` so the relative import resolves.
    """
    sys.path.insert(0, str(built_package_dir))
    try:
        # Drop any cached references so we get a fresh import of the generated tree
        for name in list(sys.modules):
            if name == "package" or name.startswith("package."):
                sys.modules.pop(name, None)

        import package  # type: ignore  # noqa: F401
        from package import __extensions__ as ext_mod  # type: ignore

        assert isinstance(getattr(ext_mod.Extensions, "test", None), property), (
            "Expected 'test' to be a property on Extensions"
        )

        runner = MagicMock()
        runner.user_settings = MagicMock(defaults=MagicMock(commands={}))
        runner.system_settings = MagicMock()
        container = ext_mod.Extensions(command_runner=runner)

        child = container.test
        assert child.__class__.__name__ == "ROUTER_test"
        assert hasattr(child, "fake_command")
    finally:
        sys.path.remove(str(built_package_dir))
        for name in list(sys.modules):
            if name == "package" or name.startswith("package."):
                sys.modules.pop(name, None)


def test_provider_literal_in_signature_lists_only_registered_provider(
    built_package_dir,
):
    """Single-provider router emits ``Literal['fake']`` (and only that) on the ``provider`` param."""
    _path, source = _command_module_source(built_package_dir, "fake_command")
    func = _find_method_def(source, "fake_command")

    provider_param = next((a for a in func.args.args if a.arg == "provider"), None)
    assert provider_param is not None, "Generated method has no 'provider' parameter"
    annotation = ast.unparse(provider_param.annotation)
    assert "'fake'" in annotation, (
        f"Expected provider Literal to include 'fake', got: {annotation}"
    )
    assert "'fake_two'" not in annotation, (
        f"Single-provider build leaked 'fake_two' into Literal: {annotation}"
    )


def test_multi_provider_literal_in_signature_lists_all_providers(
    built_multi_provider_dir,
):
    """Multi-provider router emits a ``Literal`` containing every registered provider name."""
    _path, source = _command_module_source(built_multi_provider_dir, "fake_command")
    func = _find_method_def(source, "fake_command")

    provider_param = next((a for a in func.args.args if a.arg == "provider"), None)
    assert provider_param is not None
    annotation = ast.unparse(provider_param.annotation)
    assert "'fake'" in annotation and "'fake_two'" in annotation, (
        f"Multi-provider Literal missing one or both providers: {annotation}"
    )


def test_dispatch_payload_includes_provider_choices(built_package_dir):
    """``_run`` is invoked with ``provider_choices={'provider': <choice>}`` from ``filter_inputs``."""
    target_class = _locate_container_class(built_package_dir, "fake_command")
    instance, captured = _instantiate_with_capturing_run(target_class)
    captured["return_value"] = OBBject(results=[{"symbol": "X"}])

    instance.fake_command(provider="fake")

    pc = captured["kwargs"].get("provider_choices")
    assert pc == {"provider": "fake"}, (
        f"Expected provider_choices={{'provider': 'fake'}}, got {pc!r}"
    )


def test_dispatch_payload_with_multi_provider_routes_each_choice(
    built_multi_provider_dir,
):
    """Both registered providers are accepted as ``provider=`` and propagate to ``_run``."""
    target_class = _locate_container_class(built_multi_provider_dir, "fake_command")

    for provider_name in ("fake", "fake_two"):
        instance, captured = _instantiate_with_capturing_run(target_class)
        captured["return_value"] = OBBject(results=[{"symbol": "X"}])
        instance.fake_command(provider=provider_name)
        assert captured["kwargs"]["provider_choices"] == {"provider": provider_name}


def test_extra_kwargs_are_forwarded_via_extra_params(built_package_dir):
    """Arbitrary ``**kwargs`` to the generated method land in ``extra_params`` after ``filter_inputs``."""
    target_class = _locate_container_class(built_package_dir, "fake_command")
    instance, captured = _instantiate_with_capturing_run(target_class)
    captured["return_value"] = OBBject(results=[{"symbol": "X"}])

    instance.fake_command(provider="fake", custom_extra="banana")

    extra = captured["kwargs"].get("extra_params")
    assert isinstance(extra, dict), f"Expected extra_params dict, got {extra!r}"
    assert extra.get("custom_extra") == "banana", (
        f"Expected extra_params['custom_extra']='banana', got {extra!r}"
    )


def test_command_docstring_preserved_in_generated_source(built_package_dir):
    """The user-supplied docstring summary is preserved in the rendered method body."""
    _path, source = _command_module_source(built_package_dir, "fake_command")
    assert "Fake command for generator testing." in source, (
        "Expected user docstring summary to appear in generated source"
    )


def test_build_is_deterministic(tmp_path: Path, fake_router: Router):
    """Running ``PackageBuilder.build()`` twice over the same input must produce byte-identical output."""
    if not shutil.which("ruff") or not shutil.which("black"):
        pytest.skip("ruff and black are required to lint the generated package")

    out_a = tmp_path / "a"
    out_b = tmp_path / "b"

    for target in (out_a, out_b):
        target.mkdir(parents=True, exist_ok=True)
        builder = PackageBuilder(directory=target, lint=True, verbose=False)
        with patch.object(builder, "_save_reference_file"):
            builder.build()

    files_a = {
        p.relative_to(out_a): p.read_bytes() for p in (out_a / "package").glob("*.py")
    }
    files_b = {
        p.relative_to(out_b): p.read_bytes() for p in (out_b / "package").glob("*.py")
    }

    assert files_a.keys() == files_b.keys(), (
        f"File set differs across builds: {files_a.keys()} vs {files_b.keys()}"
    )
    for rel_path, content_a in files_a.items():
        assert content_a == files_b[rel_path], (
            f"Non-deterministic output: {rel_path} differs between builds"
        )


# ---------------------------------------------------------------------------
# 4. Special command shapes: multiple commands per router, deprecation, raw
# ---------------------------------------------------------------------------


def test_router_with_two_commands_emits_both_methods(
    isolated_provider_interface, fake_model_name, install_router, tmp_path: Path
):
    """A router with two commands emits both methods on the same container class."""
    child = Router()

    fc1 = _make_fake_command()
    fc1.__name__ = "command_one"
    child.command(model=fake_model_name)(fc1)

    fc2 = _make_fake_command()
    fc2.__name__ = "command_two"
    child.command(model=fake_model_name)(fc2)

    install_router(child, prefix="/two")
    package_dir = _build(tmp_path)

    target = _locate_container_class(package_dir, "command_one")
    assert target is not None
    assert hasattr(target, "command_one") and hasattr(target, "command_two"), (
        f"Expected both methods on {target}, got dir={dir(target)}"
    )


def test_deprecated_command_emits_deprecated_decorator(
    isolated_provider_interface, fake_model_name, install_router, tmp_path: Path
):
    """A deprecated command renders an ``@deprecated(...)`` decorator above the method."""
    child = Router()
    deprecation = OpenBBDeprecationWarning(
        message="will be removed in 2.0",
        since=(1, 6),
        expected_removal=(2, 0),
    )

    fc = _make_fake_command()
    fc.__name__ = "soon_gone"
    child.command(
        model=fake_model_name,
        deprecated=True,
        deprecation=deprecation,
    )(fc)

    install_router(child, prefix="/legacy")
    package_dir = _build(tmp_path)

    _path, source = _command_module_source(package_dir, "soon_gone")
    func = _find_method_def(source, "soon_gone")
    deco_names = [
        (
            getattr(d.func, "id", None)
            if isinstance(d, ast.Call)
            else getattr(d, "id", None)
        )
        for d in func.decorator_list
    ]
    assert "deprecated" in deco_names, (
        f"Expected @deprecated decorator on soon_gone, got {deco_names}"
    )


def test_command_without_model_emits_user_signature(
    isolated_provider_interface, install_router, tmp_path: Path
):
    """A command without ``model=`` keeps the user-defined parameters in the rendered signature."""
    child = Router()

    @child.command
    def echo(payload: str) -> OBBject:  # type: ignore[empty-body]
        """Echo the payload back unchanged."""

    install_router(child, prefix="/raw")
    package_dir = _build(tmp_path)

    _path, source = _command_module_source(package_dir, "echo")
    func = _find_method_def(source, "echo")
    arg_names = [a.arg for a in func.args.args]
    # ``self`` is always first; ``payload`` must appear; no ``provider`` is injected
    assert arg_names[0] == "self"
    assert "payload" in arg_names, f"Expected 'payload' in {arg_names}"
    assert "provider" not in arg_names, (
        f"Raw command should not gain a 'provider' kwarg; got {arg_names}"
    )


# ---------------------------------------------------------------------------
# 6. End-to-end: dependency injection wires through the generated module
# ---------------------------------------------------------------------------
#
# These tests build the *real* package against a router that carries both
# router-level and param-level FastAPI ``Depends(...)``, then read the
# emitted ``.py`` file off disk and assert the DI wiring shows up in the
# rendered method body. They also import the generated module to confirm
# the dependency callable resolves from the emitted ``from <mod> import
# get_di_mock_dep`` import line.
#
# These functions live at module scope (not inside a fixture) so their
# ``__module__`` resolves to ``test_package_builder_generated`` — the same
# module pytest already inserted into ``sys.modules`` — guaranteeing the
# generator's emitted import line resolves at runtime.


class DIMockDep:
    """Return type for the DI test's safe dependency."""

    def __init__(self) -> None:
        self.value = "real"


def get_di_mock_dep() -> DIMockDep:
    """Safe FastAPI dependency factory used by the generated-output DI tests."""
    return DIMockDep()


@pytest.fixture
def router_with_dependencies(
    isolated_provider_interface, install_router, fake_model_name
) -> Router:
    """A ``Router`` whose ``/test`` sub-router has a router-level ``Depends``."""
    from fastapi import Depends

    child = Router()
    child.command(model=fake_model_name)(_make_fake_command())
    # Stamp a router-level dependency onto the sub-router itself so
    # ``PathHandler.get_router_dependencies('/test/...')`` walks into it.
    child.api_router.dependencies.append(Depends(get_di_mock_dep))
    return install_router(child, prefix="/test")


@pytest.fixture
def built_di_package_dir(tmp_path: Path, router_with_dependencies: Router) -> Path:
    """Build the package against a router that carries router-level DI."""
    return _build(tmp_path)


def test_generated_module_renders_router_level_dependency_wiring(
    built_di_package_dir,
):
    """End-to-end: the on-disk emitted ``.py`` contains the DI wiring lines.

    Asserts the rendered method body has both halves of the contract:

      * the dep instantiation: ``mock_dep = get_di_mock_dep()``
      * the kwargs hand-off:   ``kwargs['mock_dep'] = mock_dep``

    plus the import line that makes ``get_di_mock_dep`` resolvable in the
    generated module.
    """
    _path, source = _command_module_source(built_di_package_dir, "fake_command")

    assert "di_mock_dep = get_di_mock_dep()" in source, (
        "router-level Depends did not render the dep instantiation line in the "
        f"emitted module:\n--- source ---\n{source}\n--- end ---"
    )
    assert 'kwargs["di_mock_dep"] = di_mock_dep' in source, (
        "router-level Depends did not render the kwargs hand-off line in the "
        f"emitted module:\n--- source ---\n{source}\n--- end ---"
    )
    # The generator must also import the dep callable so the line above resolves.
    assert "get_di_mock_dep" in source, (
        "emitted module is missing the import for get_di_mock_dep:"
        f"\n--- source ---\n{source}\n--- end ---"
    )


def test_generated_module_with_dependency_imports_and_dispatches_with_kwarg(
    built_di_package_dir,
):
    """The emitted module imports cleanly and the rendered method passes the dep into ``_run``.

    Drives the full pipeline:
      1. Import the generated module from disk.
      2. Locate the container class.
      3. Replace ``_run`` with a capturing stub.
      4. Call the generated method.
      5. Assert ``kwargs['mock_dep']`` made it through and is a ``DIMockDep``
         instance produced by the actual ``get_di_mock_dep()`` factory.
    """
    target_class = _locate_container_class(built_di_package_dir, "fake_command")
    assert target_class is not None, "Could not locate generated container class"

    instance, captured = _instantiate_with_capturing_run(target_class)
    captured["return_value"] = OBBject(results=[{"symbol": "FAKE"}])

    instance.fake_command(provider="fake")

    run_kwargs = captured.get("kwargs", {})
    # The generator routes the router-level dep through ``extra_params``,
    # tagged by the snake-cased return-class identifier.
    extra = run_kwargs.get("extra_params", {})
    assert "di_mock_dep" in extra, (
        "router-level dep was not forwarded into extra_params on Container._run; "
        f"got kwargs={run_kwargs!r}"
    )
    assert isinstance(extra["di_mock_dep"], DIMockDep), (
        "extra_params['di_mock_dep'] is not the real DIMockDep instance produced "
        f"by get_di_mock_dep(); got {extra['di_mock_dep']!r}"
    )


def test_generated_module_with_param_level_dependency_renders_wiring(
    isolated_provider_interface, install_router, tmp_path: Path
):
    """Param-level ``Annotated[X, Depends(...)]`` also renders into the emitted module."""
    from typing import Annotated

    from fastapi import Depends

    child = Router()

    @child.command
    def with_dep(
        payload: str,
        dep: Annotated[DIMockDep, Depends(get_di_mock_dep)],
    ) -> OBBject:  # type: ignore[empty-body]
        """Command whose user signature carries a param-level Depends."""

    install_router(child, prefix="/raw")
    package_dir = _build(tmp_path)

    _path, source = _command_module_source(package_dir, "with_dep")

    assert "dep = get_di_mock_dep()" in source, (
        "param-level Depends did not render the dep instantiation in the emitted module:"
        f"\n--- source ---\n{source}\n--- end ---"
    )
    # The import of the dep callable must be present — verified by the fact
    # the line above resolves at runtime; the explicit string check guards
    # against accidental refactors that drop the import-discovery hook.
    assert "get_di_mock_dep" in source


def test_generated_module_filters_unsafe_router_level_dependency(
    isolated_provider_interface, install_router, fake_model_name, tmp_path: Path
):
    """Unsafe (Request-bound) router-level deps must NOT appear in the emitted module.

    Defends the ``_is_safe_dependency`` gate end-to-end: even if such a dep is
    attached to the sub-router, the generator must drop it during emission.
    """
    from fastapi import Depends, Request

    def get_unsafe_dep(request: Request):
        return request

    child = Router()
    child.command(model=fake_model_name)(_make_fake_command())
    child.api_router.dependencies.append(Depends(get_unsafe_dep))
    install_router(child, prefix="/test")

    package_dir = _build(tmp_path)

    _path, source = _command_module_source(package_dir, "fake_command")

    assert "get_unsafe_dep" not in source, (
        "Unsafe (Request-bound) router-level dep leaked into the emitted "
        f"module:\n--- source ---\n{source}\n--- end ---"
    )
