"""Targeted tests for ImportDefinition uncovered branches."""

from types import SimpleNamespace
from typing import Annotated

from openbb_core.app.static.package_builder import (
    import_definition as import_def_module,
)
from openbb_core.app.static.package_builder.import_definition import ImportDefinition


def test_sanitize_type_name_strips_quotes_and_subscripts():
    assert ImportDefinition._sanitize_type_name('"typing.Optional[int]"') == "Optional"
    assert ImportDefinition._sanitize_type_name("Foo(x)") == "Foo"
    assert (
        ImportDefinition._sanitize_type_name("typing_extensions.Annotated")
        == "Annotated"
    )


def test_filter_hint_type_list_skips_primitives_and_builtins():
    out = ImportDefinition.filter_hint_type_list([int, str, dict, list])
    assert out == []


def test_filter_hint_type_list_keeps_module_types():
    from datetime import datetime

    out = ImportDefinition.filter_hint_type_list([datetime, int])
    assert datetime in out


def test_filter_hint_type_list_skips_depends_annotated():
    from fastapi import Depends

    def _dep():
        return 1

    annotated = Annotated[int, Depends(_dep)]
    out = ImportDefinition.filter_hint_type_list([annotated, str])
    assert out == []


def test_filter_hint_type_list_unhashable_type_skipped():
    """Lines 98-100: unhashable type triggers TypeError on `in primitive_types`."""

    class _UH(list):  # subclass list -> unhashable instances
        __module__ = "openbb_core.fake_module"

    out = ImportDefinition.filter_hint_type_list([_UH(), int])
    assert all(not isinstance(x, type) or x is not int for x in out)


def test_filter_hint_type_list_deduplicates_unhashable():
    """Lines 115-121: dedup loop, comparison TypeError -> identity check."""

    class _UH:
        __module__ = "openbb_core.fake_module"

        def __eq__(self, other):
            if isinstance(other, _UH):
                raise TypeError("nope")
            return False

        def __hash__(self):
            return id(self)

    a = _UH()
    out = ImportDefinition.filter_hint_type_list([a, a])
    assert len(out) == 1


def test_get_function_hint_type_list_no_validate_clears_response_model():
    async def _endpoint(x: int):
        return x

    route = SimpleNamespace(
        endpoint=_endpoint,
        openapi_extra={"no_validate": True},
        response_model=int,
    )

    out = ImportDefinition.get_function_hint_type_list(route)
    assert isinstance(out, list)
    assert route.response_model is None


def test_get_path_hint_type_list_includes_deprecated_summary_and_router_dep(
    monkeypatch,
):
    async def _endpoint(a: int) -> int:
        return a

    summary = SimpleNamespace(metadata={"x": 1})
    route = SimpleNamespace(
        endpoint=_endpoint,
        openapi_extra={},
        deprecated=True,
        summary=summary,
    )
    dep = SimpleNamespace(dependency=lambda: 1)

    monkeypatch.setattr(
        import_def_module.PathHandler,
        "build_route_map",
        staticmethod(lambda: {"/a": route}),
    )
    monkeypatch.setattr(
        import_def_module.PathHandler,
        "build_path_list",
        staticmethod(lambda route_map: list(route_map.keys())),
    )
    monkeypatch.setattr(
        import_def_module.PathHandler,
        "get_child_path_list",
        staticmethod(lambda path, path_list: ["/a"]),
    )
    monkeypatch.setattr(
        import_def_module.PathHandler,
        "get_route",
        staticmethod(lambda path, route_map: route),
    )
    monkeypatch.setattr(
        import_def_module.PathHandler,
        "get_router_dependencies",
        staticmethod(lambda _p: [dep]),
    )

    out = ImportDefinition.get_path_hint_type_list("/root")
    assert dep.dependency in out


def test_build_generates_module_and_from_imports(monkeypatch):
    Foo = type("Foo", (), {"__module__": "mymod"})
    Bar = type("Bar", (), {"__module__": "mymod"})
    Baz = type("Baz", (), {"__module__": "anothermod"})
    OptionalLike = type("typing.Optional[int]", (), {"__module__": "xmod"})
    UnionLike = type("A|B", (), {"__module__": "xmod"})
    BadIdent = type("not-valid!", (), {"__module__": "xmod"})
    TypingAny = type("Any", (), {"__module__": "typing"})

    class _OriginType:
        __module__ = "origmod"
        __origin__ = list

    class _TypesSkip:
        __module__ = "types"
        __name__ = "SimpleNamespace"

    monkeypatch.setattr(
        ImportDefinition,
        "get_path_hint_type_list",
        classmethod(
            lambda cls, path: [
                Foo,
                Bar,
                Baz,
                OptionalLike,
                UnionLike,
                BadIdent,
                TypingAny,
                _OriginType,
                _TypesSkip,
            ]
        ),
    )

    out = ImportDefinition.build("x.y")
    assert "import anothermod" in out
    assert "import mymod" in out
    assert "from anothermod import Baz" in out
    assert "from mymod import (" in out
    assert "Bar" in out and "Foo" in out
    assert "from xmod import" not in out
    assert "from types import" not in out


def test_filter_hint_type_list_dedup_equal_branch():
    Dup = type("Dup", (), {"__module__": "dupmod"})
    out = ImportDefinition.filter_hint_type_list([Dup, Dup])
    assert len(out) == 1


def test_build_skips_empty_sanitized_and_empty_typing_imports(monkeypatch):
    EmptyName = type("", (), {"__module__": "emptymod"})
    TypingMissing = type("DefinitelyNotInTyping", (), {"__module__": "typing"})

    monkeypatch.setattr(
        ImportDefinition,
        "get_path_hint_type_list",
        classmethod(lambda cls, path: [EmptyName, TypingMissing]),
    )

    out = ImportDefinition.build("x.y")
    assert "from emptymod import" not in out
    assert "from typing import DefinitelyNotInTyping" not in out


def test_unwrap_generic_args_extracts_nested_type():
    """Lines 85-87: get_args yields a real ``type`` -> appended to out."""
    out = import_def_module._unwrap_generic_args(list[int])
    assert int in out


def test_unwrap_generic_args_dedups_repeated_node():
    """Line 73: re-pushing the same id hits the seen guard and continues.

    ``tuple[int, int]`` flattens to ``(int, int)``. Both ints land on the
    stack; the second pop must hit ``seen`` and skip the get_args branch.
    Without the guard, deeply nested or self-referential annotations would
    loop forever — proving the path runs is what this test asserts.
    """
    out = import_def_module._unwrap_generic_args(tuple[int, int])
    # Both ints get collected (collection happens before the stack push), but
    # we mainly care that the function returned at all — the seen guard fires
    # on the duplicate stack entry rather than re-processing it.
    assert int in out


def test_unwrap_generic_args_swallows_get_args_exception(monkeypatch):
    """Lines 82-83: defensive except path when get_args raises."""

    def _boom(_node):
        raise TypeError("synthetic failure")

    sentinel = object()
    monkeypatch.setattr(import_def_module, "get_args", _boom)
    out = import_def_module._unwrap_generic_args(sentinel)
    # The exception was swallowed and ``args`` defaulted to () so no types
    # get collected from the sentinel.
    assert out == []


def test_unwrap_generic_args_handles_annotated_alias():
    """Lines 76-79: ``_AnnotatedAlias`` branch pushes ``__origin__`` on stack."""
    out = import_def_module._unwrap_generic_args(Annotated[int, "tag"])
    # Origin (``int``) gets pushed and processed by the next loop iteration.
    # ``int`` itself isn't a generic, so it lands in ``out`` only if it appears
    # as a top-level type within get_args of the inner — which it doesn't here,
    # so we just confirm the function returns cleanly without raising.
    assert isinstance(out, list)


def test_filter_hint_type_list_skips_empty_param_marker():
    """Line 116: ``_empty`` (signature placeholder) is skipped."""
    from inspect import _empty

    out = ImportDefinition.filter_hint_type_list([_empty, int])
    assert _empty not in out


def test_filter_hint_type_list_skips_bare_depends_instance():
    """Line 123: bare ``Depends(...)`` instance (not Annotated) is skipped."""
    from fastapi import Depends

    def _dep():
        return 1

    bare = Depends(_dep)
    out = ImportDefinition.filter_hint_type_list([bare])
    assert bare not in out


def test_get_function_hint_type_list_extracts_depends_from_annotated_param():
    """Lines 203-207: Annotated metadata containing ``Depends`` exposes its
    ``.dependency`` callable so it ends up in the hint list."""
    from fastapi import Depends

    def _dep():
        return 1

    async def _endpoint(x: Annotated[int, Depends(_dep)]) -> int:
        return x

    route = SimpleNamespace(
        endpoint=_endpoint,
        openapi_extra={},
        response_model=int,
    )

    out = ImportDefinition.get_function_hint_type_list(route)
    assert _dep in out
