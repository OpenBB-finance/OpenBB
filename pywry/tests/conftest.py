"""Pytest configuration and fixtures."""

from __future__ import annotations

import os
import sys

from pathlib import Path
from typing import TYPE_CHECKING

import pytest


if TYPE_CHECKING:
    from collections.abc import Generator


# Add pywry to path for imports
pywry_path = Path(__file__).parent.parent / "pywry"
if str(pywry_path) not in sys.path:
    sys.path.insert(0, str(pywry_path.parent))


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
    "ACL SETUSER editor on >editor123 ~* &* +@read +@write +@string +@hash +@set +@list +@connection +@transaction +ping -@admin -@dangerous",
    # Viewer user - read-only access to any keys
    "ACL SETUSER viewer on >viewer123 ~* &* +@read +@connection +ping -@write -@admin -@dangerous",
    # Blocked user - no access except auth
    "ACL SETUSER blocked on >blocked123 ~* &* -@all +auth",
]


@pytest.fixture(scope="session")
def redis_container() -> Generator[str, None, None]:
    """Spin up a Redis container for integration tests using testcontainers.

    Returns the Redis URL for connecting to the container.
    Uses a fixed port (6399) for predictable debugging.
    Configures Redis via command-line arguments (no config file warning).
    Skips if Docker is not available or testcontainers is not installed.

    If PYWRY_DEPLOY__REDIS_URL is set, uses that instead of starting a container.
    """
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

    # Use fixed port 6399 for predictable testing
    redis_test_port = 6399

    try:
        container = RedisContainer("redis:7-alpine")
        container.with_bind_ports(6379, redis_test_port)
        # Pass configuration via command-line to avoid "no config file" warning
        container.with_command(" ".join(REDIS_CMD_ARGS))

        with container as redis:
            host = redis.get_container_host_ip()
            redis_url = f"redis://{host}:{redis_test_port}/0"
            print("\n=== Redis Container Started ===")
            print(f"URL: {redis_url}")
            print(f"Command: {' '.join(REDIS_CMD_ARGS)}")

            # Verify connection works
            import redis as redis_sync

            client = redis_sync.from_url(redis_url, decode_responses=True)
            try:
                pong = client.ping()
                info = client.info("server")
                print(f"PING: {pong}")
                print(f"Redis version: {info.get('redis_version', 'unknown')}")
            finally:
                client.close()

            yield redis_url
    except Exception as e:  # pylint: disable=broad-except
        pytest.skip(f"Docker not available or container failed to start: {e}")


@pytest.fixture(scope="session")
def redis_container_with_acl() -> Generator[dict, None, None]:
    """Spin up a Redis container WITH ACL configuration for RBAC testing.

    Configures Redis via command-line, then adds ACL users via commands.
    Uses fixed port 6398 for predictable testing.

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

    # Use fixed port 6398 for ACL testing (different from regular redis)
    redis_acl_test_port = 6398

    try:
        container = RedisContainer("redis:7-alpine")
        container.with_bind_ports(6379, redis_acl_test_port)
        # Pass configuration via command-line
        container.with_command(" ".join(REDIS_CMD_ARGS))

        with container as redis:
            host = redis.get_container_host_ip()
            base_url = f"redis://{host}:{redis_acl_test_port}/0"
            print("\n=== Redis ACL Container Started ===")
            print(f"URL: {base_url}")
            print(f"Command: {' '.join(REDIS_CMD_ARGS)}")

            # Configure ACL users via Redis commands
            import redis as redis_sync

            client = redis_sync.from_url(base_url, decode_responses=True)
            try:
                # Verify connection
                pong = client.ping()
                print(f"PING: {pong}")

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
                "blocked": {"username": "blocked", "password": "blocked123", "role": "blocked"},
            }

            def make_url(username: str, password: str) -> str:
                return f"redis://{username}:{password}@{host}:{redis_acl_test_port}/0"

            yield {
                "url": base_url,
                "host": host,
                "port": redis_acl_test_port,
                "default_url": base_url,  # Default user has no password
                "admin_url": make_url("admin", "admin123"),
                "editor_url": make_url("editor", "editor123"),
                "viewer_url": make_url("viewer", "viewer123"),
                "blocked_url": make_url("blocked", "blocked123"),
                "users": users,
            }
    except Exception as e:  # pylint: disable=broad-except
        pytest.skip(f"Docker not available or container failed to start: {e}")
