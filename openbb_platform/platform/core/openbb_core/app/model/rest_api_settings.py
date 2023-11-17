"""FastAPI configuration settings model."""
from typing import List

from pydantic import ConfigDict, Field

from openbb_core.app.model.abstract.tagged import Tagged


class Cors(Tagged):
    """Cors model for FastAPI configuration."""

    model_config = ConfigDict(frozen=True)

    allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    allow_methods: List[str] = Field(default_factory=lambda: ["*"])
    allow_headers: List[str] = Field(default_factory=lambda: ["*"])


class Servers(Tagged):
    """Servers model for FastAPI configuration."""

    model_config = ConfigDict(frozen=True)

    url: str = "http://localhost:8000"
    description: str = "Local OpenBB development server"


class FastAPISettings(Tagged):
    """Settings model for FastAPI configuration."""

    model_config = ConfigDict(frozen=True)

    version: str = "1"
    prefix: str = f"/api/v{version}"
    title: str = "OpenBB Platform API"
    description: str = "This is the OpenBB Platform API."
    terms_of_service: str = "http://example.com/terms/"
    contact_name: str = "OpenBB Team"
    contact_url: str = "https://openbb.co"
    contact_email: str = "hello@openbb.co"
    license_name: str = "MIT"
    license_url: str = (
        "https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/LICENSE"
    )
    servers: List[Servers] = Field(default_factory=lambda: [Servers()])
    cors: Cors = Field(default_factory=Cors)
