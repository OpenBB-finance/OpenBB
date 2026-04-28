"""Test Extension model and its functionalities."""

import sys
import types
from types import SimpleNamespace

import pytest

from openbb_core.app.model.extension import CachedAccessor, Extension


def test_init_raises_if_invalid_configuration():
    # on_command_output False but other flags set -> should raise
    with pytest.raises(ValueError):
        Extension(
            name="bad",
            on_command_output=False,
            command_output_paths=["/some/path"],
        )

    with pytest.raises(ValueError):
        Extension(name="bad2", on_command_output=False, results_only=True)

    with pytest.raises(ValueError):
        Extension(name="bad3", on_command_output=False, immutable=False)


def test_register_accessor_registers_and_warns_on_override():
    class Dummy:
        accessors = set()

    def accessor_factory(obj):
        return SimpleNamespace(called_with=obj)

    # Register new accessor
    decorator = Extension.register_accessor("foo", Dummy)
    returned = decorator(accessor_factory)
    assert returned is accessor_factory  # decorator returns the original accessor
    assert hasattr(Dummy, "foo")
    assert "foo" in Dummy.accessors
    # descriptor instance is stored in the class __dict__; accessing via the
    # class returns the result of descriptor.__get__, so inspect __dict__
    assert isinstance(Dummy.__dict__["foo"], CachedAccessor)

    # If attribute already exists, registration should warn
    Dummy.existing = "I exist"
    with pytest.warns(UserWarning):
        Extension.register_accessor("existing", Dummy)(accessor_factory)

    # Clean up
    if "foo" in Dummy.accessors:
        Dummy.accessors.remove("foo")
    if hasattr(Dummy, "foo"):
        delattr(Dummy, "foo")
    if hasattr(Dummy, "existing"):
        delattr(Dummy, "existing")


def test_cached_accessor_descriptor_behavior_and_caching():
    class Dummy:
        accessors = set()

        def __init__(self, name="n"):
            self.name = name

    def make_accessor(obj):
        # returns an object instance to be cached on the target instance
        return SimpleNamespace(result=f"accessed-{obj.name}")

    Extension.register_accessor("myext", Dummy)(make_accessor)

    inst = Dummy("alice")
    # Accessing on instance should call accessor and cache the result on instance
    returned = inst.myext  # type: ignore
    assert isinstance(returned, SimpleNamespace)
    assert returned.result == "accessed-alice"
    # The attribute should now exist on the instance (cached)
    assert getattr(inst, "myext") is returned

    # The descriptor object itself lives in the class __dict__
    cls_attr = Dummy.__dict__["myext"]
    assert isinstance(cls_attr, CachedAccessor)

    # Clean up
    Dummy.accessors.discard("myext")
    if hasattr(Dummy, "myext"):
        delattr(Dummy, "myext")


def test_obbject_accessor_registers_on_mocked_obbject_module(monkeypatch):
    # Create a fake module to be imported in the property
    mod_name = "openbb_core.app.model.obbject"
    fake_mod = types.ModuleType(mod_name)

    class FakeOBBject:
        accessors = set()

    fake_mod.OBBject = FakeOBBject  # type: ignore

    # Install fake module into sys.modules so import inside property picks it up
    monkeypatch.setitem(sys.modules, mod_name, fake_mod)

    ext = Extension(name="ext_name")
    decorator = (
        ext.obbject_accessor
    )  # should return the register decorator for FakeOBBject

    def sample_accessor(obj):
        return SimpleNamespace(tag=f"ext-{getattr(obj, '_marker', None)}")

    decorator(sample_accessor)

    assert "ext_name" in FakeOBBject.accessors
    assert hasattr(FakeOBBject, "ext_name")
    # descriptor instance must be in the class __dict__
    assert isinstance(FakeOBBject.__dict__["ext_name"], CachedAccessor)

    # cleanup
    FakeOBBject.accessors.discard("ext_name")
    if hasattr(FakeOBBject, "ext_name"):
        delattr(FakeOBBject, "ext_name")
    monkeypatch.delitem(sys.modules, mod_name)


# ----------------- SystemSettings security-gate enforcement -----------------
#
# The Extension constructor enforces two opt-in flags that must be set in
# system_settings.json:
#   * `allow_on_command_output` — must be True to load *any* extension that
#     hooks `on_command_output`.
#   * `allow_mutable_extensions` — must be additionally True to load an
#     extension that mutates the OBBject (`immutable=False`).
#
# These tests drive both gates by patching ``SystemService`` to return
# settings with the desired flags, exactly as ``test_command_runner.py`` does.


def _patch_system_settings(
    monkeypatch, *, allow_on_command_output: bool, allow_mutable_extensions: bool
) -> None:
    """Replace ``SystemService`` with a stub exposing the requested flags."""
    monkeypatch.setattr(
        "openbb_core.app.service.system_service.SystemService",
        lambda: SimpleNamespace(
            system_settings=SimpleNamespace(
                allow_on_command_output=allow_on_command_output,
                allow_mutable_extensions=allow_mutable_extensions,
            )
        ),
    )


def test_on_command_output_blocked_when_setting_disabled(monkeypatch):
    """Loading an `on_command_output` extension without the flag set raises."""
    _patch_system_settings(
        monkeypatch, allow_on_command_output=False, allow_mutable_extensions=False
    )

    with pytest.raises(RuntimeError, match="allow_on_command_output"):
        Extension(name="oco_blocked", on_command_output=True)


def test_on_command_output_allowed_when_setting_enabled(monkeypatch):
    """With the flag set, an immutable on_command_output extension loads cleanly."""
    _patch_system_settings(
        monkeypatch, allow_on_command_output=True, allow_mutable_extensions=False
    )

    ext = Extension(name="oco_ok", on_command_output=True, immutable=True)

    assert ext.on_command_output is True
    assert ext.immutable is True


def test_mutable_extension_blocked_when_setting_disabled(monkeypatch):
    """An `immutable=False` extension is rejected when allow_mutable_extensions is False."""
    _patch_system_settings(
        monkeypatch, allow_on_command_output=True, allow_mutable_extensions=False
    )

    with pytest.raises(RuntimeError, match="allow_mutable_extensions"):
        Extension(name="mut_blocked", on_command_output=True, immutable=False)


def test_mutable_extension_allowed_when_both_settings_enabled(monkeypatch):
    """Both flags True → mutable extension loads."""
    _patch_system_settings(
        monkeypatch, allow_on_command_output=True, allow_mutable_extensions=True
    )

    ext = Extension(name="mut_ok", on_command_output=True, immutable=False)

    assert ext.on_command_output is True
    assert ext.immutable is False


def test_results_only_extension_requires_on_command_output_gate(monkeypatch):
    """`results_only=True` extensions also require the on_command_output gate."""
    _patch_system_settings(
        monkeypatch, allow_on_command_output=False, allow_mutable_extensions=False
    )

    with pytest.raises(RuntimeError, match="allow_on_command_output"):
        Extension(
            name="ro_blocked",
            on_command_output=True,
            results_only=True,
            immutable=True,
        )

    _patch_system_settings(
        monkeypatch, allow_on_command_output=True, allow_mutable_extensions=False
    )
    ext = Extension(
        name="ro_ok",
        on_command_output=True,
        results_only=True,
        immutable=True,
    )
    assert ext.results_only is True


def test_command_output_paths_requires_on_command_output(monkeypatch):
    """`command_output_paths` without `on_command_output=True` is a ValueError, not a gate error."""
    _patch_system_settings(
        monkeypatch, allow_on_command_output=True, allow_mutable_extensions=False
    )

    # ValueError is raised before the gate check — verify ordering.
    with pytest.raises(ValueError, match="on_command_output"):
        Extension(
            name="paths_only",
            on_command_output=False,
            command_output_paths=["/some/path"],
        )

    # With on_command_output=True and the gate enabled, paths-scoped extension loads.
    ext = Extension(
        name="paths_ok",
        on_command_output=True,
        command_output_paths=["/equity/price/historical", "/news/world"],
    )
    assert ext.command_output_paths == [
        "/equity/price/historical",
        "/news/world",
    ]


# --------------- ExtensionLoader callback registration coverage --------------


def test_extension_loader_registers_command_output_callbacks_by_path(monkeypatch):
    """`ExtensionLoader._register_command_output_callbacks` indexes extensions by path.

    Verifies the bridge between ``Extension.command_output_paths`` and
    ``ExtensionLoader.on_command_output_callbacks`` (the dict consumed by
    ``StaticCommandRunner._trigger_command_output_callbacks`` at runtime).
    """
    from openbb_core.app.extension_loader import ExtensionLoader
    from openbb_core.app.model.abstract.singleton import SingletonMeta

    _patch_system_settings(
        monkeypatch, allow_on_command_output=True, allow_mutable_extensions=True
    )

    wildcard = Extension(name="wc_ext", on_command_output=True, immutable=True)
    scoped_a = Extension(
        name="scoped_a_ext",
        on_command_output=True,
        immutable=False,
        command_output_paths=["/equity/price/historical"],
    )
    scoped_b = Extension(
        name="scoped_b_ext",
        on_command_output=True,
        immutable=True,
        command_output_paths=["/equity/price/historical", "/news/world"],
    )

    SingletonMeta._instances.pop(ExtensionLoader, None)  # type: ignore[arg-type]
    loader = ExtensionLoader()
    monkeypatch.setattr(
        type(loader),
        "obbject_objects",
        {
            "wc": wildcard,
            "a": scoped_a,
            "b": scoped_b,
        },
    )
    loader._on_command_output_callbacks = {}
    loader._register_command_output_callbacks()

    callbacks = loader.on_command_output_callbacks

    assert wildcard in callbacks["*"]
    assert scoped_a in callbacks["/equity/price/historical"]
    assert scoped_b in callbacks["/equity/price/historical"]
    assert scoped_b in callbacks["/news/world"]
    assert "/news/world" in callbacks
    # Wildcard is NOT auto-broadcast into specific path buckets:
    assert wildcard not in callbacks["/equity/price/historical"]

    SingletonMeta._instances.pop(ExtensionLoader, None)  # type: ignore[arg-type]
