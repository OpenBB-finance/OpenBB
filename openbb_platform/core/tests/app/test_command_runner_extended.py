"""Additional tests targeting uncovered branches in ``command_runner``."""

from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from openbb_core.app.command_runner import (
    CommandRunner,
    ExecutionContext,
    ParametersBuilder,
    StaticCommandRunner,
)
from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.obbject import OBBject

# --- ParametersBuilder.get_polished_func ---


def test_get_polished_func_removes_authenticated_user_settings():
    def f(a: int, __authenticated_user_settings=None) -> int:
        return a

    polished = ParametersBuilder.get_polished_func(f)
    assert "__authenticated_user_settings" not in polished.__annotations__
    assert "__authenticated_user_settings" not in polished.__signature__.parameters  # type: ignore[attr-defined]


# --- ParametersBuilder.merge_args_and_kwargs with **kwargs ---


def test_merge_args_and_kwargs_with_var_keyword():
    def f(a, b, **kwargs):
        return None

    result = ParametersBuilder.merge_args_and_kwargs(
        f, (1,), {"b": 2, "extra": "x", "filter_query": "ignored"}
    )
    assert result["a"] == 1
    assert result["b"] == 2
    assert result["extra"] == "x"
    assert "filter_query" not in result
    assert "kwargs" not in result


def test_merge_args_and_kwargs_default_used_when_missing():
    def f(a, b=99):
        return None

    result = ParametersBuilder.merge_args_and_kwargs(f, (1,), {})
    assert result == {"a": 1, "b": 99}


def test_merge_args_and_kwargs_none_when_missing_required():
    def f(a, b):
        return None

    result = ParametersBuilder.merge_args_and_kwargs(f, (1,), {})
    assert result == {"a": 1, "b": None}


# --- ParametersBuilder._as_dict ---


def test_as_dict_with_dict():
    assert ParametersBuilder._as_dict({"a": 1}) == {"a": 1}


def test_as_dict_with_dataclass():
    @dataclass
    class D:
        a: int = 1
        b: str = "x"

    assert ParametersBuilder._as_dict(D()) == {"a": 1, "b": "x"}


def test_as_dict_with_iterable_of_pairs():
    assert ParametersBuilder._as_dict([("a", 1), ("b", 2)]) == {"a": 1, "b": 2}


def test_as_dict_swallows_exception():
    # Object that can't be coerced to a dict
    assert ParametersBuilder._as_dict(object()) == {}


# --- ParametersBuilder._warn_kwargs chart_params skip branch ---


def test_warn_kwargs_chart_params_key_is_skipped():
    """When extra_params contains a 'chart_params' key, it must NOT trigger a warning."""
    from pydantic import BaseModel, ConfigDict

    from openbb_core.app.provider_interface import ExtraParams

    @dataclass
    class Extras(ExtraParams):
        valid_field: str = ""

    class Model(BaseModel):
        model_config = ConfigDict(arbitrary_types_allowed=True)
        extra_params: Extras

    import warnings

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        ParametersBuilder._warn_kwargs({"chart_params": {}}, Model)
    assert not [w for w in caught if issubclass(w.category, OpenBBWarning)]


# --- StaticCommandRunner._extract_params ---


def test_extract_params_returns_dict_directly():
    out = StaticCommandRunner._extract_params(
        {"standard_params": {"a": 1}}, "standard_params"
    )
    assert out == {"a": 1}


def test_extract_params_with_object_having_dict():
    class P:
        def __init__(self):
            self.symbol = "AAPL"
            self.limit = 5

    out = StaticCommandRunner._extract_params({"extra_params": P()}, "extra_params")
    assert out == {"symbol": "AAPL", "limit": 5}


def test_extract_params_missing_key_returns_default_dict():
    out = StaticCommandRunner._extract_params({}, "standard_params")
    assert out == {}


# --- StaticCommandRunner._chart with chart_params plumbing ---


def test_chart_merges_extra_params_chart_params():
    """``_chart`` should pull ``chart_params`` out of ``obbject._extra_params`` and pass them to ``charting.show``."""
    mock_charting = Mock()
    OBBject.accessors.add("charting")
    try:
        obb = OBBject(results=[{"x": 1}], provider="mock")
        object.__setattr__(obb, "charting", mock_charting)
        object.__setattr__(obb, "_extra_params", {"chart_params": {"title": "Hello"}})

        StaticCommandRunner._chart(obb)

        kwargs = mock_charting.show.call_args.kwargs
        assert kwargs["render"] is False
        assert kwargs["title"] == "Hello"
    finally:
        OBBject.accessors.discard("charting")


def test_chart_merges_top_level_chart_params_kwarg():
    """``chart_params`` passed as a kwarg should be flattened into the call."""
    mock_charting = Mock()
    OBBject.accessors.add("charting")
    try:
        obb = OBBject(results=[{"x": 1}], provider="mock")
        object.__setattr__(obb, "charting", mock_charting)

        StaticCommandRunner._chart(obb, chart_params={"theme": "dark"})

        kwargs = mock_charting.show.call_args.kwargs
        assert kwargs["theme"] == "dark"
    finally:
        OBBject.accessors.discard("charting")


def test_chart_merges_nested_kwargs_chart_params():
    """``kwargs['chart_params']`` (one level deep) should also be flattened."""
    mock_charting = Mock()
    OBBject.accessors.add("charting")
    try:
        obb = OBBject(results=[{"x": 1}], provider="mock")
        object.__setattr__(obb, "charting", mock_charting)

        StaticCommandRunner._chart(obb, kwargs={"chart_params": {"width": 800}})

        kwargs = mock_charting.show.call_args.kwargs
        assert kwargs["width"] == 800
    finally:
        OBBject.accessors.discard("charting")


def test_chart_warns_in_non_debug_mode_on_failure():
    """Without DEBUG_MODE, a chart failure should be downgraded to an OpenBBWarning."""
    obb = OBBject(results=[{"x": 1}], provider="mock")
    with pytest.warns(OpenBBWarning, match="Charting is not installed"):
        StaticCommandRunner._chart(obb)


# --- StaticCommandRunner.run metadata + dependency removal + callback branches ---


import warnings
from unittest.mock import (
    AsyncMock,
    patch as _patch,
)

import pytest as _pytest

from openbb_core.app.model.system_settings import SystemSettings  # noqa: E402
from openbb_core.app.model.user_settings import UserSettings  # noqa: E402
from openbb_core.app.router import CommandMap  # noqa: E402


class _APIRouteWithDep:
    def __init__(self):
        def get_user_id():
            return "u1"

        class Dep:
            dependency = staticmethod(get_user_id)

        self.dependencies = [Dep()]
        self.openapi_extra = {}


class _Ctx(ExecutionContext):
    def __init__(self, user, system, route="mock/route"):
        super().__init__(CommandMap(), route, system, user)
        self._api_route = _APIRouteWithDep()

    @property
    def api_route(self):
        return self._api_route


@_pytest.mark.asyncio
async def test_run_populates_metadata_and_strips_dependencies():
    """Lines 446-475: metadata enabled -> Metadata wrapped, dep keys stripped."""
    user = UserSettings()
    user.preferences.metadata = True
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    obb = OBBject(results=[{"x": 1}], provider="p")
    object.__setattr__(obb, "_extra_params", {"user_id": "abc", "limit": 5})

    async def _fake_execute(**_kwargs):
        return obb

    with (
        _patch.object(
            StaticCommandRunner, "_execute_func", new=AsyncMock(return_value=obb)
        ),
        _patch.object(CommandMap, "get_command", return_value=lambda: None),
    ):
        result = await StaticCommandRunner.run(ctx)

    assert result is obb
    assert "metadata" in result.extra
    # dependency key 'user_id' must be removed from _extra_params
    assert "user_id" not in result._extra_params  # type: ignore


@_pytest.mark.asyncio
async def test_run_callback_strips_callable_arguments():
    """Lines 499-502: callable / falsy values in arguments are removed."""
    user = UserSettings()
    user.preferences.metadata = True
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    obb = OBBject(results=[{"x": 1}], provider="p")
    object.__setattr__(obb, "_extra_params", {})

    async def _fake_execute(**_kwargs):
        return obb

    with (
        _patch.object(
            StaticCommandRunner, "_execute_func", new=AsyncMock(return_value=obb)
        ),
        _patch.object(CommandMap, "get_command", return_value=lambda: None),
    ):
        await StaticCommandRunner.run(ctx, fn=lambda: None, empty="")
    # fn (callable) and empty (falsy) should be stripped from extra_params if metadata exists
    args = obb.extra["metadata"].arguments
    assert "fn" not in args.get("extra_params", {})
    assert "empty" not in args.get("extra_params", {})


@_pytest.mark.asyncio
async def test_run_invalid_route_raises_attribute_error():
    user = UserSettings()
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_, route="does/not/exist")
    with (
        _patch.object(CommandMap, "get_command", return_value=None),
        _pytest.raises(AttributeError, match="Invalid command"),
    ):
        await StaticCommandRunner.run(ctx)


@_pytest.mark.asyncio
async def test_execute_func_merges_inner_kwargs_into_validated_kwargs(monkeypatch):
    user = UserSettings()
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    def my_endpoint(**kwargs):
        return kwargs

    monkeypatch.setattr(
        ParametersBuilder,
        "build",
        staticmethod(lambda **_k: {"a": 1}),
    )

    obb = OBBject(results=[{"x": 1}], provider="p")
    with _patch.object(
        StaticCommandRunner, "_command", new=AsyncMock(return_value=obb)
    ):
        out = await StaticCommandRunner._execute_func(
            route="mock/route",
            args=(),
            execution_context=ctx,
            func=my_endpoint,
            kwargs={"kwargs": {"extra_flag": True}},
        )

    assert out._extra_params.get("extra_flag") is True  # type: ignore[attr-defined]


@_pytest.mark.asyncio
async def test_execute_func_chart_restores_kwargs_into_extra_params(monkeypatch):
    user = UserSettings()
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    def my_endpoint(**kwargs):
        return kwargs

    monkeypatch.setattr(
        ParametersBuilder,
        "build",
        staticmethod(lambda **_k: {"extra_params": {"existing": 1}}),
    )

    obb = OBBject(results=[{"x": 1}], provider="p")
    captured = {}

    def _fake_chart(_obb, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(StaticCommandRunner, "_chart", staticmethod(_fake_chart))

    with _patch.object(
        StaticCommandRunner, "_command", new=AsyncMock(return_value=obb)
    ):
        await StaticCommandRunner._execute_func(
            route="mock/route",
            args=(),
            execution_context=ctx,
            func=my_endpoint,
            kwargs={"chart": True, "outside": "v"},
        )

    assert "chart" not in captured
    assert captured["extra_params"]["outside"] == "v"


@_pytest.mark.asyncio
async def test_execute_func_collects_and_shows_warnings(monkeypatch):
    user = UserSettings()
    user.preferences.show_warnings = True
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    def my_endpoint(**kwargs):
        return kwargs

    monkeypatch.setattr(ParametersBuilder, "build", staticmethod(lambda **_k: {}))

    obb = OBBject(results=[{"x": 1}], provider="p")

    async def _warn_and_return(*_args, **_kwargs):
        warnings.warn("warn-me", OpenBBWarning)
        return obb

    shown = {"count": 0}

    def _fake_showwarning(**_kwargs):
        shown["count"] += 1

    monkeypatch.setattr("openbb_core.app.command_runner.showwarning", _fake_showwarning)

    with _patch.object(StaticCommandRunner, "_command", new=_warn_and_return):
        out = await StaticCommandRunner._execute_func(
            route="mock/route",
            args=(),
            execution_context=ctx,
            func=my_endpoint,
            kwargs={},
        )

    assert out.warnings
    assert shown["count"] >= 1


@_pytest.mark.asyncio
async def test_run_metadata_assignment_failure_warns_when_not_debug(monkeypatch):
    from openbb_core.env import Env

    user = UserSettings()
    user.preferences.metadata = True
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    obb = OBBject(results=[{"x": 1}], provider="p")

    class _BadExtra(dict):
        def __setitem__(self, key, value):  # noqa: ARG002
            raise TypeError("cannot set")

    object.__setattr__(obb, "extra", _BadExtra())

    monkeypatch.setattr(CommandMap, "get_command", lambda *_a, **_k: lambda: None)
    monkeypatch.setattr(
        StaticCommandRunner, "_execute_func", AsyncMock(return_value=obb)
    )
    monkeypatch.setattr(Env, "DEBUG_MODE", False)

    with _pytest.warns(OpenBBWarning):
        out = await StaticCommandRunner.run(ctx)

    assert out is obb


@_pytest.mark.asyncio
async def test_run_populates_metadata_from_nested_kwargs_and_warns_on_callback_error(
    monkeypatch,
):
    user = UserSettings()
    user.preferences.metadata = True
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    obb = OBBject(results=[{"x": 1}], provider="p")
    object.__setattr__(obb, "_extra_params", {})

    monkeypatch.setattr(CommandMap, "get_command", lambda *_a, **_k: lambda: None)
    monkeypatch.setattr(
        StaticCommandRunner, "_execute_func", AsyncMock(return_value=obb)
    )

    def _boom(*_a, **_k):
        raise RuntimeError("cb-boom")

    monkeypatch.setattr(
        StaticCommandRunner, "_trigger_command_output_callbacks", staticmethod(_boom)
    )

    with _pytest.warns(OpenBBWarning):
        out = await StaticCommandRunner.run(ctx, kwargs={"alpha": 1})

    meta = out.extra["metadata"].arguments
    assert meta["extra_params"].get("alpha") == 1


@_pytest.mark.asyncio
async def test_command_runner_run_delegates_to_static_runner(monkeypatch):
    runner = CommandRunner(
        command_map=CommandMap(),
        system_settings=SystemSettings(logging_suppress=True),
        user_settings=UserSettings(),
    )

    expected = OBBject(results=[{"ok": True}], provider="p")

    async def _fake_run(ctx, *args, **kwargs):
        assert ctx.route == "mock/route"
        return expected

    monkeypatch.setattr(StaticCommandRunner, "run", _fake_run)
    out = await runner.run("mock/route")
    assert out is expected


def test_command_runner_sync_run_uses_run_async(monkeypatch):
    runner = CommandRunner(
        command_map=CommandMap(),
        system_settings=SystemSettings(logging_suppress=True),
        user_settings=UserSettings(),
    )

    expected = OBBject(results=[{"ok": True}], provider="p")

    def _fake_run_async(func, route, user_settings, *args, **kwargs):
        assert route == "mock/route"
        return expected

    monkeypatch.setattr("openbb_core.app.command_runner.run_async", _fake_run_async)
    out = runner.sync_run("mock/route")
    assert out is expected


def test_command_runner_init_logging_service(monkeypatch):
    runner = CommandRunner(
        command_map=CommandMap(),
        system_settings=SystemSettings(logging_suppress=True),
        user_settings=UserSettings(),
    )

    called = {"ok": False}

    class _LS:
        def __init__(self, system_settings=None, user_settings=None):
            called["ok"] = system_settings is not None and user_settings is not None

    monkeypatch.setattr("openbb_core.app.logs.logging_service.LoggingService", _LS)
    runner.init_logging_service()
    assert called["ok"] is True


def test_trigger_callbacks_skips_non_cached_accessor(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.model.extension import Extension

    ext = Extension(name="plain_attr_ext", on_command_output=True, immutable=False)
    fake_loader = SimpleNamespace(on_command_output_callbacks={"*": [ext]})
    monkeypatch.setattr(
        "openbb_core.app.command_runner.ExtensionLoader", lambda: fake_loader
    )
    monkeypatch.setattr(
        "openbb_core.app.model.obbject.OBBject.accessors",
        OBBject.accessors | {ext.name},
    )
    monkeypatch.setattr(OBBject, ext.name, object(), raising=False)

    obb = OBBject(results=[1], provider="p")
    StaticCommandRunner._trigger_command_output_callbacks("mock/route", obb)


def test_trigger_callbacks_runs_callable_result(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.model.extension import CachedAccessor, Extension

    ext = Extension(name="callable_result_ext", on_command_output=True, immutable=False)
    fake_loader = SimpleNamespace(on_command_output_callbacks={"*": [ext]})
    monkeypatch.setattr(
        "openbb_core.app.command_runner.ExtensionLoader", lambda: fake_loader
    )
    monkeypatch.setattr(
        "openbb_core.app.model.obbject.OBBject.accessors",
        OBBject.accessors | {ext.name},
    )

    hit = {"called": False}

    def _factory(_obb):
        def _inner():
            hit["called"] = True

        return _inner

    monkeypatch.setattr(
        OBBject, ext.name, CachedAccessor(ext.name, _factory), raising=False
    )

    obb = OBBject(results=[1], provider="p")
    StaticCommandRunner._trigger_command_output_callbacks("mock/route", obb)
    assert hit["called"] is True


def test_command_runner_user_settings_setter():
    runner = CommandRunner(
        command_map=CommandMap(),
        system_settings=SystemSettings(logging_suppress=True),
        user_settings=UserSettings(),
    )
    new_user = UserSettings()
    runner.user_settings = new_user
    assert runner.user_settings is new_user


def test_trigger_callbacks_identifier_and_import_path_key_paths(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.model.extension import Extension

    ext1 = Extension(name="k1", on_command_output=True, immutable=False)
    ext1.identifier = "id-1"
    ext2 = Extension(name="k2", on_command_output=True, immutable=False)
    ext2.import_path = "pkg.mod"
    fake_loader = SimpleNamespace(on_command_output_callbacks={"*": [ext1, ext2]})
    monkeypatch.setattr(
        "openbb_core.app.command_runner.ExtensionLoader", lambda: fake_loader
    )

    obb = OBBject(results=[1], provider="p")
    StaticCommandRunner._trigger_command_output_callbacks("mock/route", obb)


def test_trigger_callbacks_immutable_clone_failure_warns(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.model.extension import CachedAccessor, Extension

    ext = Extension(name="imm_fail_ext", on_command_output=True, immutable=True)
    fake_loader = SimpleNamespace(on_command_output_callbacks={"*": [ext]})
    monkeypatch.setattr(
        "openbb_core.app.command_runner.ExtensionLoader", lambda: fake_loader
    )
    monkeypatch.setattr(
        "openbb_core.app.model.obbject.OBBject.accessors",
        OBBject.accessors | {ext.name},
    )

    def _factory(_obb):
        return None

    monkeypatch.setattr(
        OBBject, ext.name, CachedAccessor(ext.name, _factory), raising=False
    )

    def _boom(*_args, **_kwargs):
        raise ValueError("clone boom")

    monkeypatch.setattr(OBBject, "model_copy", _boom)

    obb = OBBject(results=[1], provider="p")
    with pytest.warns(OpenBBWarning, match="could not be duplicated"):
        StaticCommandRunner._trigger_command_output_callbacks("mock/route", obb)


def test_trigger_callbacks_command_output_paths_skip(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.model.extension import CachedAccessor, Extension

    ext = Extension(name="path_scoped_ext", on_command_output=True, immutable=False)
    ext.command_output_paths = ["other/route"]
    fake_loader = SimpleNamespace(on_command_output_callbacks={"*": [ext]})
    monkeypatch.setattr(
        "openbb_core.app.command_runner.ExtensionLoader", lambda: fake_loader
    )
    monkeypatch.setattr(
        "openbb_core.app.model.obbject.OBBject.accessors",
        OBBject.accessors | {ext.name},
    )

    called = {"ok": False}

    def _factory(_obb):
        called["ok"] = True

    monkeypatch.setattr(
        OBBject, ext.name, CachedAccessor(ext.name, _factory), raising=False
    )

    obb = OBBject(results=[1], provider="p")
    StaticCommandRunner._trigger_command_output_callbacks("mock/route", obb)
    assert called["ok"] is False


def test_trigger_callbacks_async_factory_path(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.model.extension import CachedAccessor, Extension

    ext = Extension(name="async_ext", on_command_output=True, immutable=False)
    fake_loader = SimpleNamespace(on_command_output_callbacks={"*": [ext]})
    monkeypatch.setattr(
        "openbb_core.app.command_runner.ExtensionLoader", lambda: fake_loader
    )
    monkeypatch.setattr(
        "openbb_core.app.model.obbject.OBBject.accessors",
        OBBject.accessors | {ext.name},
    )

    async def _factory(_obb):
        return None

    called = {"ok": False}

    def _fake_run_async(func, arg):
        called["ok"] = True

    monkeypatch.setattr("openbb_core.app.command_runner.run_async", _fake_run_async)
    monkeypatch.setattr(
        OBBject, ext.name, CachedAccessor(ext.name, _factory), raising=False
    )

    obb = OBBject(results=[1], provider="p")
    StaticCommandRunner._trigger_command_output_callbacks("mock/route", obb)
    assert called["ok"] is True


def test_trigger_callbacks_factory_exception_raises_openbb_error(monkeypatch):
    from types import SimpleNamespace

    from openbb_core.app.model.abstract.error import OpenBBError
    from openbb_core.app.model.extension import CachedAccessor, Extension

    ext = Extension(name="boom_ext", on_command_output=True, immutable=False)
    fake_loader = SimpleNamespace(on_command_output_callbacks={"*": [ext]})
    monkeypatch.setattr(
        "openbb_core.app.command_runner.ExtensionLoader", lambda: fake_loader
    )
    monkeypatch.setattr(
        "openbb_core.app.model.obbject.OBBject.accessors",
        OBBject.accessors | {ext.name},
    )

    def _factory(_obb):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        OBBject, ext.name, CachedAccessor(ext.name, _factory), raising=False
    )

    obb = OBBject(results=[1], provider="p")
    with pytest.raises(OpenBBError):
        StaticCommandRunner._trigger_command_output_callbacks("mock/route", obb)


def test_execution_context_api_route_property_access(monkeypatch):
    """Line 57: ExecutionContext.api_route accesses _route_map[self.route]."""
    from unittest.mock import MagicMock

    mock_route = MagicMock()
    route_map = {"/test/path": mock_route}
    monkeypatch.setattr(ExecutionContext, "_route_map", route_map)

    ctx = ExecutionContext(
        command_map=MagicMock(),
        route="/test/path",
        system_settings=MagicMock(),
        user_settings=MagicMock(),
    )
    assert ctx.api_route is mock_route


def test_merge_args_and_kwargs_converts_non_dict_kwargs_field():
    def endpoint(a, **kwargs):
        return None

    merged = ParametersBuilder.merge_args_and_kwargs(
        endpoint,
        args=(),
        kwargs={"a": 1, "kwargs": [("x", 2)], "y": 3},
    )

    assert merged["a"] == 1
    assert merged["x"] == 2
    assert merged["y"] == 3
    assert "kwargs" not in merged


def test_validate_kwargs_skips_var_keyword_parameter():
    def endpoint(a: int, **kwargs):
        return None

    out = ParametersBuilder.validate_kwargs(endpoint, {"a": "5", "extra": 9})

    assert out["a"] == 5
    assert out["extra"] == 9


@_pytest.mark.asyncio
async def test_execute_func_chart_removes_chart_kwarg(monkeypatch):
    user = UserSettings()
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    def my_endpoint(**kwargs):
        return kwargs

    monkeypatch.setattr(ParametersBuilder, "build", staticmethod(lambda **_k: {}))

    obb = OBBject(results=[{"x": 1}], provider="p")
    captured = {}

    def _fake_chart(_obb, **kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(StaticCommandRunner, "_chart", staticmethod(_fake_chart))

    with _patch.object(
        StaticCommandRunner, "_command", new=AsyncMock(return_value=obb)
    ):

        class _NoPopChartDict(dict):
            def pop(self, key, default=None):
                if key == "chart":
                    return self.get(key, default)
                return super().pop(key, default)

        await StaticCommandRunner._execute_func(
            route="mock/route",
            args=(),
            execution_context=ctx,
            func=my_endpoint,
            kwargs=_NoPopChartDict({"chart": True, "outside": "v"}),
        )

    assert captured["chart"] is True
    assert captured["extra_params"]["outside"] == "v"


@_pytest.mark.asyncio
async def test_run_metadata_assignment_failure_raises_when_debug(monkeypatch):
    from openbb_core.app.model.abstract.error import OpenBBError

    user = UserSettings()
    user.preferences.metadata = True
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    obb = OBBject(results=[{"x": 1}], provider="p")

    class _BadExtra(dict):
        def __setitem__(self, key, value):
            raise TypeError("cannot set")

    object.__setattr__(obb, "extra", _BadExtra())

    monkeypatch.setattr(CommandMap, "get_command", lambda *_a, **_k: lambda: None)
    monkeypatch.setattr(
        StaticCommandRunner, "_execute_func", AsyncMock(return_value=obb)
    )
    monkeypatch.setattr(
        "openbb_core.app.command_runner.Env",
        type("E", (), {"DEBUG_MODE": True}),
    )

    with _pytest.raises(OpenBBError):
        await StaticCommandRunner.run(ctx)


@_pytest.mark.asyncio
async def test_run_callback_failure_raises_when_debug(monkeypatch):
    from openbb_core.app.model.abstract.error import OpenBBError

    user = UserSettings()
    user.preferences.metadata = False
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    obb = OBBject(results=[{"x": 1}], provider="p")

    monkeypatch.setattr(CommandMap, "get_command", lambda *_a, **_k: lambda: None)
    monkeypatch.setattr(
        StaticCommandRunner, "_execute_func", AsyncMock(return_value=obb)
    )

    def _boom(*_a, **_k):
        raise RuntimeError("cb-boom")

    monkeypatch.setattr(
        StaticCommandRunner, "_trigger_command_output_callbacks", staticmethod(_boom)
    )
    monkeypatch.setattr(
        "openbb_core.app.command_runner.Env",
        type("E", (), {"DEBUG_MODE": True}),
    )

    with _pytest.raises(OpenBBError):
        await StaticCommandRunner.run(ctx)


@_pytest.mark.asyncio
async def test_run_metadata_cleanup_skips_non_dict_and_removes_unjsonable(monkeypatch):
    from types import SimpleNamespace

    user = UserSettings()
    user.preferences.metadata = False
    sys_ = SystemSettings(logging_suppress=True)
    ctx = _Ctx(user, sys_)

    bad_value = object()
    metadata_obj = SimpleNamespace(
        arguments={
            "standard_params": "not_a_dict",
            "extra_params": {"bad": bad_value, "ok": 1},
            "provider_choices": {},
        }
    )

    obb = OBBject(results=[{"x": 1}], provider="p")
    obb.extra["metadata"] = metadata_obj

    monkeypatch.setattr(CommandMap, "get_command", lambda *_a, **_k: lambda: None)
    monkeypatch.setattr(
        StaticCommandRunner, "_execute_func", AsyncMock(return_value=obb)
    )
    monkeypatch.setattr(
        StaticCommandRunner,
        "_trigger_command_output_callbacks",
        staticmethod(lambda *_a, **_k: None),
    )

    def _fake_jsonable_encoder(value):
        if value is bad_value:
            raise TypeError("nope")
        return value

    monkeypatch.setattr(
        "openbb_core.app.command_runner.jsonable_encoder",
        _fake_jsonable_encoder,
    )

    out = await StaticCommandRunner.run(ctx)
    assert "bad" not in out.extra["metadata"].arguments["extra_params"]
    assert out.extra["metadata"].arguments["extra_params"]["ok"] == 1
