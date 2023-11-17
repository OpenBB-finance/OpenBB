"""FastAPI configuration settings model."""
from functools import partial
from typing import List

from pydantic import Field

from openbb_core.app.model.abstract.tagged import Tagged

FrozenField = partial(Field, frozen=True)


class Cors(Tagged):
    """Cors model for FastAPI configuration."""

    allow_origins: List[str] = FrozenField(default_factory=lambda: ["*"])
    allow_methods: List[str] = FrozenField(default_factory=lambda: ["*"])
    allow_headers: List[str] = FrozenField(default_factory=lambda: ["*"])


class Servers(Tagged):
    """Servers model for FastAPI configuration."""

    url: str = FrozenField(default="http://localhost:8000")
    description: str = FrozenField(default="Local OpenBB development server")


class FastAPISettings(Tagged):
    """Settings model for FastAPI configuration."""

    title: str = FrozenField(default="OpenBB Platform API")
    description: str = FrozenField(default="This is the OpenBB Platform API.")
    terms_of_service: str = FrozenField(default="http://example.com/terms/")
    contact_name: str = FrozenField(default="OpenBB Team")
    contact_url: str = FrozenField(default="https://openbb.co")
    contact_email: str = FrozenField(default="hello@openbb.co")
    license_name: str = FrozenField(default="MIT")
    license_url: str = FrozenField(
        default="https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/LICENSE"
    )
    servers: List[Servers] = FrozenField(default_factory=lambda: [Servers()])
    cors: Cors = FrozenField(default_factory=Cors)
