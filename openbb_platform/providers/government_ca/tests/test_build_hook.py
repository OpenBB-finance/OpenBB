"""Government of Canada Hatchling build-hook tests.

``hatch_build.py`` lives at the PACKAGE ROOT (alongside ``pyproject.toml``),
OUTSIDE the importable ``openbb_government_ca`` package and therefore OUTSIDE
the ``--cov=openbb_government_ca`` 100% gate (Clarification 1, mirroring OECD).
These tests are written as good practice; they exercise the build hook's
decision branches without a real Hatch build environment or any live
subprocess / network.
"""

import importlib
import os
import sys
import tempfile
from contextlib import ExitStack, contextmanager
from pathlib import Path
from unittest import mock

import pytest
from hypothesis import (
    given,
    settings,
    strategies as st,
)

# The package root (containing both ``hatch_build.py`` and the
# ``openbb_government_ca`` package) is prepended to ``sys.path`` by pytest, so
# the root-level module resolves with a plain import.
hatch_build = importlib.import_module("hatch_build")

_HOOK = hatch_build.GovernmentCaCacheBuildHook
# Lower-cased values the build hook treats as a truthy force-rebuild flag.
_TRUTHY = {"1", "true", "yes"}
# Minimal valid XZ container magic; the hook only checks file existence.
_XZ_MAGIC = b"\xfd7zXZ\x00\x00"
# Expected POSIX-relative path of the cache asset under the package root.
_REL = "openbb_government_ca/assets/government_ca_cache.json.xz"


class _FakeProc:
    """Stand-in for the generator subprocess returned by ``Popen``."""

    def __init__(self, returncode=0, stdout_lines=("government-ca-cache: ...\n",)):
        self.stdout = list(stdout_lines)
        self._returncode = returncode

    def wait(self):
        """Return the canned exit status, like ``Popen.wait``."""
        return self._returncode


def _build_hook(abort_raises=True):
    """Construct a hook instance with a mock ``app`` and no real Hatch context.

    ``__new__`` bypasses ``BuildHookInterface.__init__`` (which needs a full
    build environment); ``initialize`` only touches ``self.app`` and
    ``type(self)``. ``app`` is a read-only property backed by the name-mangled
    ``_BuildHookInterface__app`` attribute, so the mock is injected there.
    Hatch's real ``app.abort`` raises ``SystemExit``, so the mock mirrors that
    by default.
    """
    hook = _HOOK.__new__(_HOOK)
    app = mock.Mock()
    if abort_raises:
        app.abort.side_effect = SystemExit
    hook._BuildHookInterface__app = app
    return hook


@contextmanager
def _hook_sandbox(*, cache_exists, force_env, returncode=0, popen_creates_cache=True):
    """Run the hook against a throwaway package root with a stubbed subprocess.

    Patches ``_ROOT`` / ``_CACHE_PATH`` / ``_GENERATE_CACHE`` onto a temp tree,
    silences the ``/dev/tty`` writer, stubs ``subprocess.Popen`` (recording each
    invocation and optionally materializing the cache), and sets/clears the
    force-rebuild env var. No real subprocess or network runs.
    """
    with ExitStack() as stack:
        tmp = stack.enter_context(tempfile.TemporaryDirectory())
        root = Path(tmp)
        cache_path = (
            root / "openbb_government_ca" / "assets" / "government_ca_cache.json.xz"
        )
        gen = root / "openbb_government_ca" / "utils" / "generate_cache.py"
        cache_path.parent.mkdir(parents=True)
        gen.parent.mkdir(parents=True)
        gen.write_text("# stub generator\n")
        if cache_exists:
            cache_path.write_bytes(_XZ_MAGIC)

        calls = []

        def _popen(cmd, **kwargs):
            calls.append({"cmd": cmd, "kwargs": kwargs})
            if popen_creates_cache:
                cache_path.write_bytes(_XZ_MAGIC)
            return _FakeProc(returncode=returncode)

        stack.enter_context(mock.patch.object(hatch_build, "_ROOT", root))
        stack.enter_context(mock.patch.object(hatch_build, "_CACHE_PATH", cache_path))
        stack.enter_context(mock.patch.object(hatch_build, "_GENERATE_CACHE", gen))
        stack.enter_context(mock.patch.object(hatch_build, "_open_tty", lambda: None))
        stack.enter_context(mock.patch.object(hatch_build.subprocess, "Popen", _popen))
        stack.enter_context(mock.patch.dict(os.environ, {}, clear=False))

        os.environ.pop(hatch_build._FORCE_ENV, None)
        if force_env is not None:
            os.environ[hatch_build._FORCE_ENV] = force_env

        yield {"root": root, "cache_path": cache_path, "gen": gen, "calls": calls}


@pytest.fixture(autouse=True)
def _reset_session_flag():
    """Reset the class-level per-session flag around every test."""
    _HOOK._generated_this_session = False
    yield
    _HOOK._generated_this_session = False


# ---------------------------------------------------------------------------
# Property 12: Force-rebuild flag truthiness.
# ---------------------------------------------------------------------------

# Mix obviously-relevant literals (varied casing, near-misses) with arbitrary
# text so both the recognized and unrecognized branches are exercised.
_force_values = st.one_of(
    st.sampled_from(
        [
            "1",
            "true",
            "yes",
            "TRUE",
            "Yes",
            "YES",
            "True",
            "tRuE",
            "0",
            "false",
            "no",
            "off",
            "2",
            "y",
            "t",
            "n",
            "",
            " ",
            "1 ",
            "true\n",
            "enabled",
            "on",
        ]
    ),
    # Real environment values are utf-8 encodable with no null byte, so
    # exclude null bytes and unpaired surrogates.
    st.text(
        st.characters(blacklist_characters="\x00", blacklist_categories=("Cs",)),
        max_size=10,
    ),
)


# Feature: government-ca-build-phase-1, Property 12
@settings(max_examples=200, deadline=None)
@given(_force_values)
def test_force_flag_truthiness(value):
    """Property 12: Force-rebuild flag truthiness.

    For any string value of ``OPENBB_GOVERNMENT_CA_FORCE_CACHE_REBUILD``, the
    Build_Hook treats it as truthy if and only if its lower-cased value is one
    of ``"1"``, ``"true"``, or ``"yes"``. Observed through behavior: with the
    cache present and nothing generated yet this session, the hook regenerates
    (invokes the generator subprocess) exactly when the flag is truthy and
    reuses the existing cache otherwise.

    Validates: Requirements 7.4
    """
    _HOOK._generated_this_session = False
    expected_truthy = value.lower() in _TRUTHY

    with _hook_sandbox(cache_exists=True, force_env=value) as ctx:
        hook = _build_hook()
        hook.initialize("1.0.0", {})
        regenerated = len(ctx["calls"]) == 1
        hook.app.abort.assert_not_called()

    assert regenerated == expected_truthy


# ---------------------------------------------------------------------------
# Property 13: Build-hook regenerates at most once per build session.
# ---------------------------------------------------------------------------


# Feature: government-ca-build-phase-1, Property 13
@settings(max_examples=200, deadline=None)
@given(st.integers(min_value=1, max_value=8))
def test_regenerates_at_most_once_per_session(num_calls):
    """Property 13: Build-hook regenerates at most once per build session.

    For any number of ``initialize`` calls within a single build process while
    the force flag is truthy, the generator subprocess is invoked at most once:
    the first target regenerates and sets the class-level
    ``_generated_this_session`` flag, which short-circuits every subsequent
    target into reuse.

    Validates: Requirements 7.8
    """
    _HOOK._generated_this_session = False

    with _hook_sandbox(cache_exists=True, force_env="1") as ctx:
        hook = _build_hook()
        for _ in range(num_calls):
            hook.initialize("1.0.0", {})

        # At most once — and exactly once here since the cache is present and
        # the flag starts truthy, so the first call regenerates.
        assert len(ctx["calls"]) <= 1
        assert len(ctx["calls"]) == 1
        assert _HOOK._generated_this_session is True
        hook.app.abort.assert_not_called()


# ---------------------------------------------------------------------------
# Decision-branch and abort unit tests (task 8.4).
# ---------------------------------------------------------------------------


def test_plugin_name():
    """The hook advertises the expected Hatch plugin name."""
    assert _HOOK.PLUGIN_NAME == "government-ca-cache"


def test_reuse_when_cache_exists_and_no_force():
    """Cache present and force unset → reuse without spawning the generator."""
    hook = _build_hook()
    build_data = {}
    with _hook_sandbox(cache_exists=True, force_env=None) as ctx:
        hook.initialize("1.0.0", build_data)

        assert ctx["calls"] == []
        hook.app.abort.assert_not_called()
        # The asset is still force-included even on the reuse path.
        assert build_data["force_include"] == {str(ctx["cache_path"]): _REL}
        assert build_data["artifacts"] == [_REL]


@pytest.mark.parametrize("force_env", [None, "1"])
def test_regenerate_when_cache_missing_regardless_of_force(force_env):
    """Missing cache → regenerate whether or not the force flag is set."""
    hook = _build_hook()
    with _hook_sandbox(cache_exists=False, force_env=force_env) as ctx:
        hook.initialize("1.0.0", {})

        assert len(ctx["calls"]) == 1
        hook.app.abort.assert_not_called()
        assert _HOOK._generated_this_session is True


def test_regenerate_when_force_truthy_and_not_yet_generated():
    """Force truthy and nothing generated yet → regenerate even if cache exists."""
    hook = _build_hook()
    with _hook_sandbox(cache_exists=True, force_env="true") as ctx:
        hook.initialize("1.0.0", {})

        assert len(ctx["calls"]) == 1
        hook.app.abort.assert_not_called()


def test_subprocess_invoked_by_path():
    """The generator is invoked BY PATH: ``[sys.executable, _GENERATE_CACHE]``."""
    hook = _build_hook()
    with _hook_sandbox(cache_exists=False, force_env=None) as ctx:
        hook.initialize("1.0.0", {})

        call = ctx["calls"][0]
        assert call["cmd"] == [sys.executable, str(ctx["gen"])]
        assert call["kwargs"]["cwd"] == str(ctx["root"])


def test_force_include_and_artifacts_injection_on_success():
    """A successful regeneration injects force_include + artifacts entries."""
    hook = _build_hook()
    build_data = {}
    with _hook_sandbox(cache_exists=False, force_env=None) as ctx:
        hook.initialize("1.0.0", build_data)

        rel = ctx["cache_path"].relative_to(ctx["root"]).as_posix()
        assert rel == _REL
        assert build_data["force_include"] == {str(ctx["cache_path"]): rel}
        assert build_data["artifacts"] == [rel]


def test_abort_on_nonzero_exit():
    """A nonzero generator exit aborts the build and includes no artifact."""
    hook = _build_hook(abort_raises=True)
    build_data = {}
    with _hook_sandbox(cache_exists=True, force_env="1", returncode=1):
        with pytest.raises(SystemExit):
            hook.initialize("1.0.0", build_data)

        hook.app.abort.assert_called_once()
        message = hook.app.abort.call_args.args[0]
        assert "exit code 1" in message
        # No artifact is injected when the build aborts.
        assert "force_include" not in build_data
        assert "artifacts" not in build_data


def test_abort_on_missing_artifact():
    """A missing artifact after a clean exit aborts the build with no artifact."""
    hook = _build_hook(abort_raises=True)
    build_data = {}
    with _hook_sandbox(
        cache_exists=False, force_env=None, returncode=0, popen_creates_cache=False
    ):
        with pytest.raises(SystemExit):
            hook.initialize("1.0.0", build_data)

        hook.app.abort.assert_called_once()
        message = hook.app.abort.call_args.args[0]
        assert "exit code 0" in message
        assert "force_include" not in build_data
        assert "artifacts" not in build_data
