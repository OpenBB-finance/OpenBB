"""Pytest configuration and fixtures."""

from __future__ import annotations

import contextlib
import os
import sys
import threading
import time

from pathlib import Path
from typing import TYPE_CHECKING, Any

import pytest


if TYPE_CHECKING:
    from collections.abc import Generator


# Add pywry to path for imports
pywry_path = Path(__file__).parent.parent / "pywry"
if str(pywry_path) not in sys.path:
    sys.path.insert(0, str(pywry_path.parent))


# =============================================================================
# Core Runtime Management - SINGLE SOURCE OF TRUTH
# =============================================================================


@pytest.fixture(autouse=True)
def cleanup_runtime():
    """Ensure runtime is completely fresh for each test.

    This is the SINGLE cleanup fixture used across ALL test files.
    It handles:
    - Stopping the runtime process
    - Clearing callback registry
    - Clearing window lifecycle state
    - Proper timing to avoid race conditions
    """
    from pywry import runtime
    from pywry.callbacks import get_registry
    from pywry.window_manager import get_lifecycle

    # Pre-test cleanup
    runtime.stop()
    time.sleep(0.5)  # Allow subprocess to fully terminate

    registry = get_registry()
    registry.clear()
    get_lifecycle().clear()

    yield

    # Post-test cleanup
    runtime.stop()
    time.sleep(0.3)  # Brief delay before next test
    registry.clear()
    get_lifecycle().clear()


# =============================================================================
# Shared Test Helpers - SINGLE SOURCE OF TRUTH
# =============================================================================


class ReadyWaiter:
    """Helper to wait for window ready event. Must be created BEFORE show()."""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout
        self._ready = threading.Event()

    def on_ready(self, _data: Any, _event_type: str = "", _widget_id: str = "") -> None:
        """Callback for pywry:ready event. Accepts 1-3 args for compatibility."""
        self._ready.set()

    def wait(self) -> bool:
        """Wait for window to be ready. Call AFTER show()."""
        return self._ready.wait(timeout=self.timeout)


def show_and_wait_ready(
    app: Any,
    content: Any,
    timeout: float = 10.0,
    **kwargs: Any,
) -> str:
    """Show content and wait for window to be ready.

    This registers the ready callback BEFORE calling show() to avoid race conditions.

    Parameters
    ----------
    app : PyWry
        The PyWry application instance.
    content : str | HtmlContent
        HTML content to display.
    timeout : float
        Maximum time to wait for window ready.
    **kwargs
        Additional arguments passed to app.show().

    Returns
    -------
    str
        The window label.

    Raises
    ------
    TimeoutError
        If window doesn't become ready within timeout.
    """
    waiter = ReadyWaiter(timeout=timeout)

    # Merge callbacks if provided
    callbacks = kwargs.pop("callbacks", {}) or {}
    callbacks["pywry:ready"] = waiter.on_ready

    widget = app.show(content, callbacks=callbacks, **kwargs)
    label = widget.label if hasattr(widget, "label") else str(widget)

    if not waiter.wait():
        raise TimeoutError(f"Window '{label}' did not become ready within {timeout}s")

    return label


def show_plotly_and_wait_ready(
    app: Any,
    figure: Any,
    timeout: float = 10.0,
    **kwargs: Any,
) -> str:
    """Show Plotly figure and wait for window to be ready."""
    waiter = ReadyWaiter(timeout=timeout)
    callbacks = kwargs.pop("callbacks", {}) or {}
    callbacks["pywry:ready"] = waiter.on_ready

    widget = app.show_plotly(figure, callbacks=callbacks, **kwargs)
    label = widget.label if hasattr(widget, "label") else str(widget)

    if not waiter.wait():
        raise TimeoutError(f"Window '{label}' did not become ready within {timeout}s")

    return label


def show_dataframe_and_wait_ready(
    app: Any,
    data: Any,
    timeout: float = 10.0,
    **kwargs: Any,
) -> str:
    """Show DataFrame and wait for window to be ready."""
    waiter = ReadyWaiter(timeout=timeout)
    callbacks = kwargs.pop("callbacks", {}) or {}
    callbacks["pywry:ready"] = waiter.on_ready

    widget = app.show_dataframe(data, callbacks=callbacks, **kwargs)
    label = widget.label if hasattr(widget, "label") else str(widget)

    if not waiter.wait():
        raise TimeoutError(f"Window '{label}' did not become ready within {timeout}s")

    return label


def wait_for_result(
    label: str,
    script: str,
    timeout: float = 5.0,
    retries: int = 3,
) -> dict[str, Any] | None:
    """Execute JS and wait for pywry.result() callback.

    This is the SINGLE implementation used across all test files.
    Includes retry logic for race conditions (especially on macOS).

    Parameters
    ----------
    label : str
        Window label to execute script in.
    script : str
        JavaScript to execute. Must call pywry.result({...}).
    timeout : float
        Timeout per attempt in seconds.
    retries : int
        Number of retry attempts.

    Returns
    -------
    dict | None
        The result data, or None if timeout/no result.
    """
    from pywry import runtime
    from pywry.callbacks import get_registry

    registry = get_registry()
    result: dict[str, Any] = {"received": False, "data": None}
    event = threading.Event()

    def on_result(data: Any, _event_type: str = "", _widget_id: str = "") -> None:
        """Handle result. Accepts 1-3 args for compatibility."""
        result["received"] = True
        result["data"] = data
        event.set()

    for attempt in range(retries):
        result["received"] = False
        result["data"] = None
        event.clear()

        registry.register(label, "pywry:result", on_result)

        try:
            runtime.eval_js(label, script)

            # Use event.wait() instead of busy loop
            if event.wait(timeout=timeout) and result["data"] is not None:
                return result["data"]
        finally:
            registry.unregister(label, "pywry:result", on_result)

        # Retry after brief delay
        if attempt < retries - 1:
            time.sleep(0.3)

    return result["data"]


# =============================================================================
# Simple Fixtures
# =============================================================================


@pytest.fixture
def temp_css_file(tmp_path):
    """Create a temporary CSS file."""
    css_file = tmp_path / "test.css"
    css_file.write_text("body { color: red; }")
    return css_file


@pytest.fixture
def temp_js_file(tmp_path):
    """Create a temporary JavaScript file."""
    js_file = tmp_path / "test.js"
    js_file.write_text("console.log('test');")
    return js_file


@pytest.fixture
def sample_html_content():
    """Create a sample HtmlContent object."""
    from pywry.models import HtmlContent

    return HtmlContent(
        html="<div id='app'>Hello World</div>",
        json_data={"message": "hello"},
        init_script="console.log('init');",
    )


@pytest.fixture
def sample_window_config():
    """Create a sample WindowConfig object."""
    from pywry.models import ThemeMode, WindowConfig

    return WindowConfig(
        title="Test Window",
        width=1024,
        height=768,
        theme=ThemeMode.DARK,
    )


@pytest.fixture
def default_settings():
    """Create default PyWrySettings."""
    from pywry.config import PyWrySettings

    return PyWrySettings()


@pytest.fixture
def permissive_csp():
    """Create permissive CSP settings."""
    from pywry.config import SecuritySettings

    return SecuritySettings.permissive()


@pytest.fixture
def strict_csp():
    """Create strict CSP settings."""
    from pywry.config import SecuritySettings

    return SecuritySettings.strict()


@pytest.fixture
def asset_loader(tmp_path):
    """Create an AssetLoader with temp directory as base."""
    from pywry.asset_loader import AssetLoader

    return AssetLoader(base_dir=tmp_path)


@pytest.fixture
def callback_registry():
    """Get a clean callback registry."""
    from pywry.callbacks import get_registry

    registry = get_registry()
    registry.clear()
    return registry


# --- Testcontainers Redis Fixture ---


# Redis command-line configuration flags for testing
# These are passed directly to redis-server via with_command()
REDIS_CMD_ARGS = [
    "redis-server",
    "--bind",
    "0.0.0.0",
    "--port",
    "6379",
    "--protected-mode",
    "no",
    "--save",
    "",  # Disable RDB persistence
    "--appendonly",
    "no",  # Disable AOF persistence
    "--maxmemory",
    "128mb",
    "--maxmemory-policy",
    "allkeys-lru",
    "--loglevel",
    "notice",
]

# Redis ACL commands for RBAC testing - executed after container starts
# Note: Using ~* for key patterns to allow any prefix used by tests
REDIS_ACL_COMMANDS = [
    # Admin user - full access to everything
    "ACL SETUSER admin on >admin123 ~* &* +@all",
    # Editor user - can read/write any keys (widgets, sessions, etc.) but not admin commands
    # Needs +@transaction for MULTI/EXEC which widget store uses
    (
        "ACL SETUSER editor on >editor123 ~* &* +@read +@write +@string "
        "+@hash +@set +@list +@connection +@transaction +ping -@admin -@dangerous"
    ),
    # Viewer user - read-only access to any keys
    "ACL SETUSER viewer on >viewer123 ~* &* +@read +@connection +ping -@write -@admin -@dangerous",
    # Blocked user - no access except auth
    "ACL SETUSER blocked on >blocked123 ~* &* -@all +auth",
]


def _configure_testcontainers() -> None:
    """Configure testcontainers settings for the current platform."""
    try:
        from testcontainers.core.config import testcontainers_config

        testcontainers_config.ryuk_disabled = True

        # Ensure images are always pulled (don't rely on local cache check)
        # This fixes issues on some CI environments
        os.environ.setdefault("TC_IMAGE_PULL_POLICY", "always")
    except ImportError:
        pass  # testcontainers not installed


@pytest.fixture(scope="session")
def redis_container() -> Generator[str, None, None]:
    """Spin up a Redis container for integration tests using testcontainers.

    Returns the Redis URL for connecting to the container.
    Testcontainers handles image pulling, port mapping, and lifecycle automatically.
    """
    # If memory backend is explicitly set, skip Redis tests
    if os.environ.get("PYWRY_DEPLOY__STATE_BACKEND", "").lower() == "memory":
        pytest.skip("Memory backend configured - skipping Redis tests")
        return

    # Allow override via environment variable (for external Redis)
    external_url = os.environ.get("PYWRY_DEPLOY__REDIS_URL")
    if external_url:
        yield external_url
        return

    try:
        from testcontainers.redis import RedisContainer
    except ImportError:
        pytest.skip("testcontainers not installed (pip install testcontainers[redis])")
        return

    # Configure testcontainers (disable Ryuk on Windows)
    _configure_testcontainers()

    # Use specific Redis image tag for reliability
    container = RedisContainer("redis:7")
    try:
        container.start()
        host = container.get_container_host_ip()
        port = container.get_exposed_port(container.port)
        redis_url = f"redis://{host}:{port}/0"
        print("\n=== Redis Container Started ===")
        print(f"URL: {redis_url}")
        yield redis_url
    except Exception as e:  # pylint: disable=broad-except
        # On platforms without Docker, this will fail - raise the actual error
        raise RuntimeError(f"Failed to start Redis container: {e}") from e
    finally:
        with contextlib.suppress(Exception):
            container.stop()


@pytest.fixture(scope="session")
def redis_container_with_acl() -> Generator[dict, None, None]:
    """Spin up a Redis container WITH ACL configuration for RBAC testing.

    Configures Redis via command-line, then adds ACL users via commands.

    Returns a dict with:
    - url: Base Redis URL (no auth - default user)
    - admin_url: URL with admin credentials
    - editor_url: URL with editor credentials
    - viewer_url: URL with viewer credentials
    - blocked_url: URL with blocked user credentials
    - users: Dict of user info (username, password, role)
    """
    try:
        from testcontainers.redis import RedisContainer
    except ImportError:
        pytest.skip("testcontainers not installed")
        return

    # Configure testcontainers (disable Ryuk on Windows)
    _configure_testcontainers()

    container = RedisContainer("redis:7")
    try:
        container.start()
        host = container.get_container_host_ip()
        port = container.get_exposed_port(container.port)
        redis_url = f"redis://{host}:{port}/0"

        print("\n=== Redis ACL Container Started ===")
        print(f"URL: {redis_url}")

        # Configure ACL users via Redis commands
        import redis as redis_sync

        client = redis_sync.from_url(redis_url, decode_responses=True)
        try:
            # Configure ACL users
            for acl_cmd in REDIS_ACL_COMMANDS:
                # Parse and execute ACL command
                parts = acl_cmd.split()
                client.execute_command(*parts)

            # Verify users were created
            acl_list = client.execute_command("ACL", "LIST")
            print("=== Redis ACL Users Configured ===")
            for user in acl_list:
                print(f"  {user[:80]}...")
        finally:
            client.close()

        users = {
            "default": {"username": "default", "password": None, "role": "admin"},
            "admin": {"username": "admin", "password": "admin123", "role": "admin"},
            "editor": {"username": "editor", "password": "editor123", "role": "editor"},
            "viewer": {"username": "viewer", "password": "viewer123", "role": "viewer"},
            "blocked": {
                "username": "blocked",
                "password": "blocked123",
                "role": "blocked",
            },
        }

        def make_url(username: str, password: str) -> str:
            return f"redis://{username}:{password}@{host}:{port}/0"

        yield {
            "url": redis_url,
            "host": host,
            "port": port,
            "default_url": redis_url,  # Default user has no password
            "admin_url": make_url("admin", "admin123"),
            "editor_url": make_url("editor", "editor123"),
            "viewer_url": make_url("viewer", "viewer123"),
            "blocked_url": make_url("blocked", "blocked123"),
            "users": users,
        }
    except Exception as e:  # pylint: disable=broad-except
        pytest.skip(f"Docker not available or container failed to start: {e}")
    finally:
        with contextlib.suppress(Exception):
            container.stop()


@pytest.fixture
def session_store_with_fallback(unique_prefix: str = "test:"):
    """Create a session store - Redis if available, else Memory.

    This fixture allows tests to run on platforms without Docker
    by falling back to MemorySessionStore.

    Yields a tuple of (store, store_type) where store_type is 'redis' or 'memory'.
    """
    from pywry.state.memory import MemorySessionStore

    # Check if we should use memory backend (macOS ARM sets this env var)
    use_memory = os.environ.get("PYWRY_DEPLOY__STATE_BACKEND", "").lower() == "memory"

    if use_memory:
        # Use memory backend
        store = MemorySessionStore()
        yield store, "memory"
        return

    # Try to use Redis
    try:
        from testcontainers.redis import RedisContainer

        from pywry.state.redis import RedisSessionStore

        _configure_testcontainers()

        container = RedisContainer("redis:7-alpine")
        container.with_bind_ports(6379, 6397)  # Use different port

        with container as redis:
            host = redis.get_container_host_ip()
            redis_url = f"redis://{host}:6397/0"

            store = RedisSessionStore(
                redis_url=redis_url,
                prefix=unique_prefix,
                default_ttl=60,
            )
            yield store, "redis"
    except Exception:  # pylint: disable=broad-except
        # Fall back to memory
        store = MemorySessionStore()
        yield store, "memory"
