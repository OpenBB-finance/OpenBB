"""Test the package_builder.py file."""

import signal
from dataclasses import dataclass
from inspect import _empty
from pathlib import Path
from typing import Annotated, Any
from unittest.mock import PropertyMock, mock_open, patch

import pytest

pandas = pytest.importorskip("pandas")

from fastapi import Depends, Request  # noqa: E402
from importlib_metadata import EntryPoint, EntryPoints  # noqa: E402

pytestmark = pytest.mark.requires_pandas

from pydantic import BaseModel, Field

from openbb_core.app.static.package_builder import (
    ClassDefinition,
    DocstringGenerator,
    ImportDefinition,
    MethodDefinition,
    ModuleBuilder,
    PackageBuilder,
    Parameter,
    PathHandler,
)
from openbb_core.env import Env


@pytest.fixture(scope="module")
def tmp_openbb_dir(tmp_path_factory):
    """Return a temporary openbb directory."""
    return tmp_path_factory.mktemp("openbb")


@pytest.fixture(scope="module")
def package_builder(tmp_openbb_dir):
    """Return package builder."""
    return PackageBuilder(tmp_openbb_dir)


def test_package_builder_init(package_builder):
    """Test package builder init."""
    assert package_builder


def test_package_builder_build(tmp_openbb_dir):
    """Test package builder build."""
    builder = PackageBuilder(tmp_openbb_dir)

    # Mock the _save_reference_file method to avoid sys.modules iteration
    with patch.object(builder, "_save_reference_file"):
        builder.build()


def test_save_modules(package_builder):
    """Test save module."""
    package_builder._save_modules()


def test_save_modules_empty_path_list(tmp_openbb_dir):
    """Test that ``_save_modules`` short-circuits when there is nothing to write."""
    builder = PackageBuilder(tmp_openbb_dir)
    builder.path_list = []
    # Should return early without raising; nothing to write.
    builder._save_modules()


def test_save_package(package_builder):
    """Test save package."""
    package_builder._save_package()


def test_run_linters(package_builder):
    """Test run linters."""
    package_builder._run_linters()


def test_write(package_builder):
    """Test save to package."""
    package_builder._write(code="", name="test", extension="json")


def test_clean_unlinks_requested_modules(tmp_openbb_dir):
    builder = PackageBuilder(tmp_openbb_dir)
    package_dir = tmp_openbb_dir / "package"
    package_dir.mkdir(parents=True, exist_ok=True)
    target = package_dir / "equity.py"
    target.write_text("x", encoding="utf-8")

    builder._clean(modules=["equity"])

    assert not target.exists()


def test_build_raises_runtime_error_when_lock_is_held(tmp_openbb_dir):
    builder = PackageBuilder(tmp_openbb_dir)

    class _HeldLock:
        def __init__(self, _f):
            return None

        def acquire(self, blocking=False):
            raise BlockingIOError

        def release(self):
            return None

    with (
        patch("openbb_core.app.static.package_builder.builder.FileLock", _HeldLock),
        pytest.raises(RuntimeError, match="Another build process is running"),
    ):
        builder.build()


def test_build_sigterm_handler_cleans_and_exits(tmp_openbb_dir):
    builder = PackageBuilder(tmp_openbb_dir, lint=False)
    calls = {"clean": 0}
    captured = {}

    class _FreeLock:
        def __init__(self, _f):
            return None

        def acquire(self, blocking=False):
            return None

        def release(self):
            return None

    def _clean(modules=None):
        calls["clean"] += 1

    def _signal(_sig, handler):
        if callable(handler):
            captured["handler"] = handler

    def _save_modules(_modules=None, _ext_map=None):
        captured["handler"](signal.SIGTERM, None)

    builder._clean = _clean
    builder._get_extension_map = lambda: {}
    builder._save_modules = _save_modules
    builder._save_reference_file = lambda _ext_map=None: None
    builder._save_package = lambda: None

    with (
        patch("openbb_core.app.static.package_builder.builder.FileLock", _FreeLock),
        patch(
            "openbb_core.app.static.package_builder.builder.signal.getsignal",
            lambda _s: None,
        ),
        patch("openbb_core.app.static.package_builder.builder.signal.signal", _signal),
        pytest.raises(SystemExit),
    ):
        builder.build()

    assert calls["clean"] >= 1


@pytest.fixture(scope="module")
def module_builder():
    """Return module builder."""
    return ModuleBuilder()


def test_module_builder_init(module_builder):
    """Test module builder init."""
    assert module_builder


@pytest.fixture(scope="module")
def class_definition():
    """Return class definition."""
    return ClassDefinition()


def test_class_definition_init(class_definition):
    """Test class definition init."""
    assert class_definition


def test_build(class_definition):
    """Test build."""
    code = class_definition.build("openbb_core.app.static.container.Container")
    assert code


def test_class_definition_skips_root_command_routes(monkeypatch):
    class _Route:
        name = "cmd"
        path = "/root/cmd"
        methods = {"GET"}
        openapi_extra = {"model": "M", "examples": ["e"]}

        @staticmethod
        def endpoint():
            return None

    monkeypatch.setattr(
        PathHandler, "build_module_class", staticmethod(lambda path: "C")
    )
    monkeypatch.setattr(
        PathHandler, "build_route_map", staticmethod(lambda: {"root/cmd": _Route()})
    )
    monkeypatch.setattr(
        PathHandler, "build_path_list", staticmethod(lambda _rm: ["root/cmd"])
    )
    monkeypatch.setattr(
        PathHandler, "get_child_path_list", staticmethod(lambda _p, _pl: ["root/cmd"])
    )
    monkeypatch.setattr(
        PathHandler, "get_route", staticmethod(lambda _c, _rm: _Route())
    )

    called = {"command": 0}
    monkeypatch.setattr(
        MethodDefinition,
        "build_command_method",
        staticmethod(
            lambda **_k: called.__setitem__("command", called["command"] + 1) or ""
        ),
    )

    out = ClassDefinition.build("", None)
    assert "Routers:" in out
    assert called["command"] == 0


def test_class_definition_adds_subroute_loader_for_non_command_route(monkeypatch):
    class _Route:
        name = "parent"
        path = "/a/parent"
        methods = None
        openapi_extra = None
        endpoint = None

    route_map = {"a/parent": _Route(), "a/parent/child": object()}

    monkeypatch.setattr(
        PathHandler, "build_module_class", staticmethod(lambda path: "C")
    )
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: route_map))
    monkeypatch.setattr(
        PathHandler, "build_path_list", staticmethod(lambda _rm: list(route_map.keys()))
    )
    monkeypatch.setattr(
        PathHandler, "get_child_path_list", staticmethod(lambda _p, _pl: ["a/parent"])
    )
    monkeypatch.setattr(
        PathHandler, "get_route", staticmethod(lambda _c, _rm: _Route())
    )

    monkeypatch.setattr(
        MethodDefinition,
        "build_class_loader_method",
        staticmethod(
            lambda path: (
                f"\n    def load_{path.replace('/', '_')}(self):\n        pass\n"
            )
        ),
    )
    monkeypatch.setattr(
        MethodDefinition,
        "build_command_method",
        staticmethod(lambda **_k: ""),
    )

    out = ClassDefinition.build("a", None)
    assert "/parent" in out
    assert "load_a_parent" in out


def test_class_definition_includes_extensions_for_root(monkeypatch):
    monkeypatch.setattr(
        PathHandler, "build_module_class", staticmethod(lambda path: "C")
    )
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: {}))
    monkeypatch.setattr(PathHandler, "build_path_list", staticmethod(lambda _rm: []))
    monkeypatch.setattr(
        PathHandler, "get_child_path_list", staticmethod(lambda _p, _pl: [])
    )

    out = ClassDefinition.build(
        "",
        {
            "openbb_core_extension": ["core_ext"],
            "openbb_provider_extension": ["prov_ext"],
        },
    )
    assert "Extensions:" in out
    assert "core_ext" in out
    assert "prov_ext" in out


def test_class_definition_builds_command_method_for_non_root_path(monkeypatch):
    class _Route:
        name = "quote"
        path = "/equity/quote"
        methods = {"GET"}
        openapi_extra = {"model": "Quote", "examples": ["ex1"]}

        @staticmethod
        def endpoint():
            return None

    monkeypatch.setattr(
        PathHandler, "build_module_class", staticmethod(lambda path: "C")
    )
    monkeypatch.setattr(
        PathHandler, "build_route_map", staticmethod(lambda: {"equity/quote": _Route()})
    )
    monkeypatch.setattr(
        PathHandler, "build_path_list", staticmethod(lambda _rm: ["equity/quote"])
    )
    monkeypatch.setattr(
        PathHandler,
        "get_child_path_list",
        staticmethod(lambda _p, _pl: ["equity/quote"]),
    )
    monkeypatch.setattr(
        PathHandler, "get_route", staticmethod(lambda _c, _rm: _Route())
    )

    called = {"args": None}
    monkeypatch.setattr(
        MethodDefinition,
        "build_command_method",
        staticmethod(
            lambda **kwargs: (
                called.__setitem__("args", kwargs)
                or "\n    def quote(self):\n        pass\n"
            )
        ),
    )

    out = ClassDefinition.build("equity", None)
    assert "quote" in out
    assert called["args"]["model_name"] == "Quote"
    assert called["args"]["examples"] == ["ex1"]


def test_class_definition_missing_route_with_subroutes_builds_loader(monkeypatch):
    route_map = {"fx/rates": object(), "fx/rates/intraday": object()}

    monkeypatch.setattr(
        PathHandler, "build_module_class", staticmethod(lambda path: "C")
    )
    monkeypatch.setattr(PathHandler, "build_route_map", staticmethod(lambda: route_map))
    monkeypatch.setattr(
        PathHandler, "build_path_list", staticmethod(lambda _rm: list(route_map.keys()))
    )
    monkeypatch.setattr(
        PathHandler, "get_child_path_list", staticmethod(lambda _p, _pl: ["fx/rates"])
    )
    monkeypatch.setattr(PathHandler, "get_route", staticmethod(lambda _c, _rm: None))
    monkeypatch.setattr(
        MethodDefinition,
        "build_class_loader_method",
        staticmethod(
            lambda path: (
                f"\n    def load_{path.replace('/', '_')}(self):\n        pass\n"
            )
        ),
    )

    out = ClassDefinition.build("fx", None)
    assert "/rates" in out
    assert "load_fx_rates" in out


def test_module_builder_build(monkeypatch):
    monkeypatch.setattr(
        ImportDefinition, "build", staticmethod(lambda path: "import x\n")
    )
    monkeypatch.setattr(
        ClassDefinition,
        "build",
        staticmethod(lambda path, ext_map=None: "class C:\n    pass\n"),
    )

    out = ModuleBuilder.build("equity.quote", {"openbb_core_extension": []})
    assert "Autogenerated OpenBB equity.quote Module" in out
    assert "THIS FILE IS AUTO-GENERATED" in out
    assert "import x" in out
    assert "class C" in out


@pytest.fixture(scope="module")
def method_definition():
    """Return method definition."""
    return MethodDefinition()


def test_method_definition_init(method_definition):
    """Test method definition init."""
    assert method_definition


def test_build_class_loader_method(method_definition):
    """Test build class loader method."""
    code = method_definition.build_class_loader_method(
        "openbb_core.app.static.container.Container"
    )
    assert code


def test_get_type(method_definition):
    """Test get type."""
    type_ = method_definition.get_type(field=Parameter.empty)
    assert type_
    assert isinstance(type_, type)


def test_get_type_hint(method_definition):
    """Test get type hint."""

    class TestField:
        annotation = int

    field = TestField()
    result = method_definition.get_type(field)
    assert result is int


def test_field_with_type_attribute_missing_type(method_definition):
    """Test field with type attribute missing type."""

    class TestField:
        annotation = Parameter.empty

    field = TestField()
    result = method_definition.get_type(field)
    assert result is _empty


def test_get_default(method_definition):
    """Test get default."""

    class TestField:
        default = Field(default=42)

    field = TestField()
    result = method_definition.get_default(field)
    assert result == 42


def test_get_default_none(method_definition):
    """Test get default."""

    class TestField:
        default = None

    field = TestField()
    result = method_definition.get_default(field)
    assert result is None


def test_get_default_default_value(method_definition):
    """Test get default default value."""

    class TestField:
        default = type(Ellipsis)()

    field = TestField()
    result = method_definition.get_default(field)
    assert result is None


def test_get_default_no_default(method_definition):
    """Test get default no default."""

    class TestField:
        pass

    field = TestField()
    result = method_definition.get_default(field)
    assert result == _empty


def test_is_annotated_dc(method_definition):
    """Test is annotated dc."""
    result = method_definition.is_annotated_dc(annotation=Parameter.empty)
    assert not result


def test_is_annotated_dc_annotated(method_definition):
    """Test is annotated dc annotated."""

    @dataclass
    class TestAnnotatedDataClass:
        """Test annotated data class."""

        value: int

    annotated_dataclass = Annotated[TestAnnotatedDataClass, "test_annotation"]
    result = method_definition.is_annotated_dc(annotation=annotated_dataclass)
    assert result


@pytest.mark.parametrize(
    "params, var_kw, expected",
    [
        (
            {
                "provider": Parameter.empty,
                "extra_params": Parameter.empty,
                "param1": Parameter.empty,
                "param2": Parameter.empty,
            },
            None,
            ["extra_params", "param1", "param2", "provider"],
        ),
        (
            {
                "param1": Parameter.empty,
                "provider": Parameter.empty,
                "extra_params": Parameter.empty,
                "param2": Parameter.empty,
            },
            ["extra_params"],
            ["param1", "param2", "provider", "extra_params"],
        ),
        (
            {
                "param2": Parameter.empty,
                "any_kwargs": Parameter.empty,
                "provider": Parameter.empty,
                "param1": Parameter.empty,
            },
            ["any_kwargs"],
            ["param2", "param1", "provider", "any_kwargs"],
        ),
        (
            {
                "any_kwargs": Parameter.empty,
                "extra_params": Parameter.empty,
                "provider": Parameter.empty,
                "param1": Parameter.empty,
                "param2": Parameter.empty,
            },
            ["any_kwargs", "extra_params"],
            ["param1", "param2", "provider", "any_kwargs", "extra_params"],
        ),
    ],
)
def test_reorder_params(method_definition, params, var_kw, expected):
    """Test reorder params, ensure var_kw are last after 'provider'."""
    result = method_definition.reorder_params(params, var_kw)
    assert result
    assert list(result.keys()) == expected


def test_build_func_params(method_definition):
    """Test build func params."""
    param_map = {
        "param1": Parameter(
            name="param1", kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=type(None)
        ),
        "param2": Parameter(
            "param2", kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=int
        ),
        "param3": Parameter(
            "param3",
            kind=Parameter.POSITIONAL_OR_KEYWORD,
            annotation=dict[str, Any] | pandas.DataFrame,
        ),
    }

    expected_output = "param1: None,\n        param2: int,\n        param3: dict[str, Any] | pandas.DataFrame"
    output = method_definition.build_func_params(param_map)

    assert output == expected_output


@pytest.mark.parametrize(
    "return_type, expected_output",
    [
        (_empty, "Any"),
        (int, "int"),
    ],
)
def test_build_func_returns(method_definition, return_type, expected_output):
    """Test build func returns."""
    output = method_definition.build_func_returns(return_type=return_type)
    assert output == expected_output


@patch("openbb_core.app.static.package_builder.method_definition.MethodDefinition")
def test_build_command_method_signature(mock_method_definitions, method_definition):
    """Test build command method signature."""
    mock_method_definitions.is_deprecated_function.return_value = False
    formatted_params = {
        "param1": Parameter("NoneType", kind=Parameter.POSITIONAL_OR_KEYWORD),
        "param2": Parameter("int", kind=Parameter.POSITIONAL_OR_KEYWORD),
    }
    return_type = int
    output = method_definition.build_command_method_signature(
        func_name="test_func",
        formatted_params=formatted_params,
        return_type=return_type,
        path="test_path",
    )
    assert output


@patch("openbb_core.app.static.package_builder.method_definition.MethodDefinition")
def test_build_command_method_signature_deprecated(
    mock_method_definitions, method_definition
):
    """Test build command method signature."""
    mock_method_definitions.is_deprecated_function.return_value = True
    formatted_params = {
        "param1": Parameter("NoneType", kind=Parameter.POSITIONAL_OR_KEYWORD),
        "param2": Parameter("int", kind=Parameter.POSITIONAL_OR_KEYWORD),
    }
    return_type = int
    output = method_definition.build_command_method_signature(
        func_name="test_func",
        formatted_params=formatted_params,
        return_type=return_type,
        path="test_path",
    )
    assert "@deprecated" in output


def test_build_command_method_doc(method_definition):
    """Test build command method doc."""

    def some_func():
        """Do some func doc."""

    formatted_params = {
        "param1": Parameter("NoneType", kind=Parameter.POSITIONAL_OR_KEYWORD),
        "param2": Parameter("int", kind=Parameter.POSITIONAL_OR_KEYWORD),
    }

    output = method_definition.build_command_method_doc(
        path="/menu/submenu/command", func=some_func, formatted_params=formatted_params
    )
    assert output
    assert isinstance(output, str)


def test_build_command_method_body(method_definition):
    """Test build command method body."""

    def some_func():
        """Do some func doc."""
        return 42

    with (
        patch(
            "openbb_core.app.static.package_builder.MethodDefinition.is_data_processing_function",
            return_value=False,
        ),
        patch(
            "openbb_core.app.static.package_builder.MethodDefinition.is_deprecated_function",
            return_value=False,
        ),
    ):
        output = method_definition.build_command_method_body(
            path="openbb_core.app.static.container.Container", func=some_func
        )

    assert output
    assert isinstance(output, str)


def test_build_command_method(method_definition):
    """Test build command method."""

    def some_func():
        """Do some func doc."""
        return 42

    with (
        patch(
            "openbb_core.app.static.package_builder.MethodDefinition.is_data_processing_function",
            return_value=False,
        ),
        patch(
            "openbb_core.app.static.package_builder.MethodDefinition.is_deprecated_function",
            return_value=False,
        ),
    ):
        output = method_definition.build_command_method(
            path="openbb_core.app.static.container.Container",
            func=some_func,
            model_name=None,
        )

    assert output
    assert isinstance(output, str)


class MyPostBody(BaseModel):
    """My post body model."""

    field1: str = Field(description="A string field.")
    field2: int = Field(default=10, description="An integer field.")


def mock_get_endpoint(
    param1: str,
    param2: int | None = None,
):
    """This is a mock GET endpoint."""


def mock_post_endpoint(
    body: MyPostBody,
):
    """This is a mock POST endpoint."""


class MockDep:
    """Mock dependency class."""

    def __init__(self):
        self.value = "real_dependency_value"


def get_mock_dep():
    """This is a real mock dependency."""
    return MockDep()


def mock_endpoint_with_real_dependency(
    dep: MockDep = Depends(get_mock_dep),
):
    """This is a mock endpoint with a real dependency."""


def test_build_command_method_get_endpoint(method_definition):
    """Test build_command_method with a GET endpoint."""
    with (
        patch(
            "openbb_core.app.static.package_builder.MethodDefinition.is_data_processing_function",
            return_value=False,
        ),
        patch(
            "openbb_core.app.static.package_builder.MethodDefinition.is_deprecated_function",
            return_value=False,
        ),
    ):
        output = method_definition.build_command_method(
            path="/test/get",
            func=mock_get_endpoint,
            model_name=None,
        )

    assert "def get(" in output
    assert "param1: Annotated[\n            str" in output
    assert "Annotated[\n            int | None,\n" in output
    assert "This is a mock GET endpoint." in output
    assert "return self._run(" in output
    assert '"/test/get",' in output
    assert "param1=param1," in output
    assert "param2=param2," in output


def test_build_command_method_post_endpoint(method_definition):
    """Test build_command_method with a POST endpoint."""
    with (
        patch(
            "openbb_core.app.static.package_builder.MethodDefinition.is_data_processing_function",
            return_value=False,
        ),
        patch(
            "openbb_core.app.static.package_builder.MethodDefinition.is_deprecated_function",
            return_value=False,
        ),
    ):
        output = method_definition.build_command_method(
            path="/test/mock_post_endpoint",
            func=mock_post_endpoint,
            model_name=None,
        )

    assert "def mock_post_endpoint(" in output
    assert "body: Annotated[\n            MyPostBody," in output
    assert "This is a mock POST endpoint." in output
    assert "return self._run(" in output
    assert '"/test/mock_post_endpoint",' in output
    assert "body=body," in output


def test_build_command_method_with_dependency(method_definition):
    """Test build_command_method with a dependency."""
    with (
        patch(
            "openbb_core.app.static.package_builder.MethodDefinition.is_data_processing_function",
            return_value=False,
        ),
        patch(
            "openbb_core.app.static.package_builder.MethodDefinition.is_deprecated_function",
            return_value=False,
        ),
    ):
        output = method_definition.build_command_method(
            path="/test/dependency",
            func=mock_endpoint_with_real_dependency,
            model_name=None,
        )

    assert "def dependency(" in output
    assert "dep: Annotated[" in output
    assert "MockDep" in output
    assert "get_mock_dep" in output
    assert "dep=dep," in output


@pytest.fixture(scope="module")
def import_definition():
    """Return import definition."""
    return ImportDefinition()


def test_import_definition_init(import_definition):
    """Test import definition init."""
    assert import_definition


def test_filter_hint_type_list(import_definition):
    """Test filter type hint list."""
    output = import_definition.filter_hint_type_list(
        hint_type_list=[int, str, float, bool, _empty, _empty, _empty, _empty]
    )
    assert output == []


def test_import_definition_get_path_hint_type_list(import_definition):
    """Test import definition get path hint type list."""
    hint_type_list = import_definition.get_path_hint_type_list(
        path="openbb_core.app.static.container.Container"
    )
    assert hint_type_list == []


def test_import_definition_build(import_definition):
    """Test import definition build."""
    code = import_definition.build(path="openbb_core.app.static.container.Container")
    assert code


@pytest.fixture(scope="module")
def path_handler():
    """Return path handler."""
    return PathHandler()


def test_path_handler_init(path_handler):
    """Test path handler init."""
    assert path_handler


@pytest.fixture
def route_map(path_handler, fake_router):
    """Return route map."""
    return path_handler.build_route_map()


def test_build_route_map(route_map):
    """Test build route map."""
    assert route_map
    assert isinstance(route_map, dict)


@pytest.fixture
def path_list(path_handler, route_map):
    """Return path list."""
    return path_handler.build_path_list(route_map=route_map)


def test_build_path_list(path_list):
    """Test build path list."""
    assert path_list
    assert isinstance(path_list, list)


def test_get_route(path_handler, route_map):
    """Test get route."""
    path = next(iter(route_map))
    route = path_handler.get_route(route_map=route_map, path=path)

    assert route


def test_get_child_path_list(path_handler, path_list):
    """Test get child path list."""
    child_path_list = path_handler.get_child_path_list(
        path="/test", path_list=path_list
    )

    assert child_path_list
    assert isinstance(child_path_list, list)


def test_clean_path(path_handler):
    """Test clean path."""
    path = "/equity/price/historical"
    result = path_handler.clean_path(path=path)
    assert result == "equity_price_historical"


def test_build_module_name(path_handler):
    """Test build module name."""
    module_name = path_handler.build_module_name(path="")
    assert module_name == "__extensions__"

    module_name = path_handler.build_module_name(path="/equity/price/historical")
    assert module_name == "equity_price_historical"


def test_build_module_class(path_handler):
    """Test build module class."""
    module_class = path_handler.build_module_class(path="")
    assert module_class == "Extensions"

    module_class = path_handler.build_module_class(path="/equity/price/historical")
    assert module_class == "ROUTER_equity_price_historical"


@pytest.fixture
def docstring_generator(isolated_provider_interface):
    """Return docstring generator bound to the isolated fake provider interface."""
    original = DocstringGenerator.provider_interface
    DocstringGenerator.provider_interface = isolated_provider_interface
    try:
        yield DocstringGenerator()
    finally:
        DocstringGenerator.provider_interface = original


def test_docstring_generator_init(docstring_generator):
    """Test docstring generator init."""
    assert docstring_generator


def test_get_OBBject_description(docstring_generator):
    """Test build docstring."""
    docstring = docstring_generator.get_OBBject_description(
        "SomeModel", "some_provider"
    )
    assert docstring


def test_generate_model_docstring(docstring_generator, fake_model_name):
    """Test generate model docstring."""
    docstring = ""
    model_name = fake_model_name
    summary = "This is a summary."
    sections = ["description", "parameters", "returns", "examples"]

    pi = docstring_generator.provider_interface
    kwarg_params = pi.params[model_name]["extra"].__dataclass_fields__
    return_schema = pi.return_schema[model_name]
    returns = (
        return_schema if isinstance(return_schema, type) else type(return_schema)
    ).model_fields

    formatted_params = {
        "param1": Parameter("NoneType", kind=Parameter.POSITIONAL_OR_KEYWORD),
        "param2": Parameter("int", kind=Parameter.POSITIONAL_OR_KEYWORD),
    }
    explicit_dict = dict(formatted_params)

    docstring = docstring_generator.generate_model_docstring(
        model_name=model_name,
        summary=summary,
        explicit_params=explicit_dict,
        kwarg_params=kwarg_params,
        returns=returns,
        results_type=f"list[{model_name}]",
        sections=sections,
    )

    assert docstring
    assert summary in docstring
    assert "Parameters" in docstring
    assert "Returns" in docstring
    assert model_name in docstring


@pytest.mark.parametrize(
    "type_, expected",
    [
        (Any, []),
        (list[str], ["list"]),
        (dict[str, str], ["dict"]),
        (tuple[str], ["tuple"]),
        (list[str] | dict[str, str] | tuple[str], ["list", "dict", "tuple"]),
    ],
)
def test__get_generic_types(docstring_generator, type_, expected):
    """Test get generic types."""
    output = docstring_generator._get_generic_types(type_, [])
    assert output == expected


@pytest.mark.parametrize(
    "items, model, expected",
    [
        ([], "test_model", "test_model"),
        (["list"], "test_model", "list[test_model]"),
        (["dict"], "test_model", "dict[str, test_model]"),
        (["tuple"], "test_model", "tuple[test_model]"),
        (
            ["list", "dict", "tuple"],
            "test_model",
            "list[test_model] | dict[str, test_model] | tuple[test_model]",
        ),
    ],
)
def test__get_repr(docstring_generator, items, model, expected):
    output = docstring_generator._get_repr(items, model)
    assert output == expected


def test_generate(docstring_generator, fake_model_name):
    """Test generate docstring."""

    def some_func():
        """Define Some func docstring."""

    formatted_params = {
        "param1": Parameter("NoneType", kind=Parameter.POSITIONAL_OR_KEYWORD),
        "param2": Parameter("int", kind=Parameter.POSITIONAL_OR_KEYWORD),
    }

    doc = docstring_generator.generate(
        path="/menu/submenu/command",
        func=some_func,
        formatted_params=formatted_params,
        model_name=fake_model_name,
    )
    assert doc
    assert "Parameters" in doc
    assert "Returns" in doc


def test__read(package_builder, tmp_openbb_dir):
    """Test read."""

    PATH = "openbb_core.app.static.package_builder.builder."
    open_mock = mock_open()
    with patch(PATH + "open", open_mock), patch(PATH + "load") as mock_load:
        package_builder._read(Path(tmp_openbb_dir / "assets" / "reference.json"))
        open_mock.assert_called_once_with(
            Path(tmp_openbb_dir / "assets" / "reference.json")
        )
        mock_load.assert_called_once()


@pytest.mark.parametrize(
    "ext_built, ext_installed, ext_inst_version, expected_add, expected_remove",
    [
        (
            {
                "openbb_core_extension": [
                    "ext_1@0.0.0",
                    "ext_2@0.0.0",
                ],
                "openbb_provider_extension": [
                    "prov_1@0.0.0",
                    "prov_2@1.1.1",
                ],
            },
            EntryPoints(
                (
                    EntryPoint(
                        name="ext_2", value="...", group="openbb_core_extension"
                    ),
                    EntryPoint(
                        name="prov_2", value="...", group="openbb_provider_extension"
                    ),
                )
            ),
            "0.0.0",
            {"prov_2@0.0.0"},
            {"ext_1@0.0.0", "prov_1@0.0.0", "prov_2@1.1.1"},
        ),
        (
            {
                "openbb_core_extension": ["ext_1@9.9.9"],
                "openbb_provider_extension": ["prov_2@0.0.0"],
            },
            EntryPoints(
                (
                    EntryPoint(
                        name="ext_2", value="...", group="openbb_core_extension"
                    ),
                    EntryPoint(
                        name="prov_1", value="...", group="openbb_provider_extension"
                    ),
                )
            ),
            "5.5.5",
            {"ext_2@5.5.5", "prov_1@5.5.5"},
            {"ext_1@9.9.9", "prov_2@0.0.0"},
        ),
    ],
)
def test_package_diff(
    package_builder,
    ext_built,
    ext_installed,
    ext_inst_version,
    expected_add,
    expected_remove,
):
    """Test package differences."""

    def mock_entry_points(group):
        """Mock entry points."""
        return ext_installed.select(**{"group": group})

    PATH = "openbb_core.app.static.package_builder.builder."
    with (
        patch(PATH + "entry_points", mock_entry_points),
        patch.object(EntryPoint, "dist", new_callable=PropertyMock) as mock_obj,
    ):

        class MockPathDistribution:
            version = ext_inst_version

        mock_obj.return_value = MockPathDistribution()

        add, remove = package_builder._diff(ext_built)

        # We add whatever is not built, but is installed
        assert add == expected_add
        # We remove whatever is built, but is not installed
        assert remove == expected_remove


@pytest.mark.parametrize(
    "add, remove, openbb_auto_build",
    [
        (set(), set(), True),
        ({"this"}, set(), True),
        (set(), {"that"}, True),
        ({"this"}, {"that"}, True),
        ({"this"}, {"that"}, False),
    ],
)
def test_auto_build(package_builder, add, remove, openbb_auto_build):
    """Test auto build."""

    with (
        patch.object(PackageBuilder, "_diff") as mock_assets_diff,
        patch.object(PackageBuilder, "build") as mock_build,
        patch.object(Env, "AUTO_BUILD", openbb_auto_build),
    ):
        mock_assets_diff.return_value = add, remove

        package_builder.auto_build()

    if openbb_auto_build:
        if add or remove:
            mock_build.assert_called_once()
    else:
        mock_assets_diff.assert_not_called()
        mock_build.assert_not_called()


def test_is_safe_dependency(method_definition):
    """Test dependency safety detection."""

    class MockDep:
        """Mock dependency."""

    def safe_dependency(optional: str = "value") -> int:
        return 1

    def unsafe_dependency(request: Request):
        return request

    def optional_request_dependency(optional: Request | None = None) -> MockDep:
        return MockDep()

    def none_return_dependency(optional: str = "value") -> None:
        return None

    def optional_return_dependency(optional: str = "value") -> MockDep | None:
        return MockDep()

    assert method_definition._is_safe_dependency(safe_dependency)
    assert not method_definition._is_safe_dependency(unsafe_dependency)
    assert not method_definition._is_safe_dependency(optional_request_dependency)
    assert not method_definition._is_safe_dependency(none_return_dependency)
    assert method_definition._is_safe_dependency(optional_return_dependency)


def test_build_func_params_unwraps_forward_ref(method_definition):
    """Test that ForwardRef annotations are unwrapped in generated function params.

    Regression test: when extensions use `from __future__ import annotations`
    with `no_validate=True`, annotations remain as strings at runtime.
    Annotated["int", ...] auto-wraps "int" into ForwardRef("int").
    The builder must unwrap these to plain type strings.
    """
    from collections import OrderedDict
    from typing import ForwardRef

    from openbb_core.app.model.field import OpenBBField

    param_map = OrderedDict(
        {
            "symbol": Parameter(
                name="symbol",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[ForwardRef("str"), OpenBBField(description="")],
            ),
            "days": Parameter(
                name="days",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[ForwardRef("int"), OpenBBField(description="")],
                default=7,
            ),
            "asset_type": Parameter(
                name="asset_type",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=Annotated[
                    ForwardRef("Literal['stock', 'etf', 'all'] | None"),
                    OpenBBField(description=""),
                ],
                default=None,
            ),
        }
    )

    output = method_definition.build_func_params(param_map)

    assert "ForwardRef" not in output, (
        f"ForwardRef should be unwrapped in generated params, got:\n{output}"
    )
    assert "str," in output
    assert "int," in output
    assert "Literal['stock', 'etf', 'all']" in output


def test_build_func_returns_string_annotation(method_definition):
    """Test that string return types are emitted directly, not wrapped in ForwardRef.

    Regression test: `from __future__ import annotations` causes return annotations
    to be strings. The builder should emit the string directly (e.g., "OBBject")
    rather than wrapping it as ForwardRef('OBBject').
    """
    output = method_definition.build_func_returns(return_type="OBBject")
    assert output == "OBBject"
    assert "ForwardRef" not in output

    output2 = method_definition.build_func_returns(return_type="Any")
    assert output2 == "Any"
    assert "ForwardRef" not in output2


def test_get_field_type_unwraps_forward_ref(docstring_generator):
    """Test that ForwardRef is unwrapped in docstring type formatting.

    Regression test: ForwardRef('int') should render as 'int' in docstrings,
    not as the literal string "ForwardRef('int')".
    """
    from typing import ForwardRef

    result = docstring_generator.get_field_type(ForwardRef("int"), is_required=True)
    assert "ForwardRef" not in result, (
        f"ForwardRef should be unwrapped in docstring types, got: {result}"
    )
    assert "int" in result

    result2 = docstring_generator.get_field_type(
        ForwardRef("Literal['stock', 'etf', 'all'] | None"), is_required=False
    )
    assert "ForwardRef" not in result2, (
        f"ForwardRef should be unwrapped in docstring types, got: {result2}"
    )


def test_build_purges_on_failure(tmp_openbb_dir):
    """Test that build purges incomplete assets on failure."""
    builder = PackageBuilder(tmp_openbb_dir)

    # Mocking _save_modules to fail
    with (
        patch.object(builder, "_clean") as mock_clean,
        patch.object(builder.console, "error") as mock_error,
        patch.object(builder, "_get_extension_map"),
        patch.object(
            builder, "_save_modules", side_effect=Exception("Generation failed")
        ),
    ):
        with pytest.raises(Exception, match="Generation failed"):
            builder.build()

        # _clean should be called twice: once at the start, once after failure
        assert mock_clean.call_count == 2
        # console.error should be called for error message, traceback and instruction
        assert mock_error.call_count >= 3
        mock_error.assert_any_call("\nBuild failed!")
        assert any(
            "Generation failed" in str(call) for call in mock_error.call_args_list
        )


def test_build_purges_on_keyboard_interrupt(tmp_openbb_dir):
    """Test that build purges incomplete assets on KeyboardInterrupt."""
    builder = PackageBuilder(tmp_openbb_dir)

    # Mocking _save_modules to raise KeyboardInterrupt
    with (
        patch.object(builder, "_clean") as mock_clean,
        patch.object(builder.console, "error") as mock_error,
        patch.object(builder, "_get_extension_map"),
        patch.object(builder, "_save_modules", side_effect=KeyboardInterrupt()),
    ):
        with pytest.raises(KeyboardInterrupt):
            builder.build()

        # _clean should be called twice: once at the start, once after interruption
        assert mock_clean.call_count == 2
        # console.error should NOT be called for KeyboardInterrupt
        mock_error.assert_not_called()
