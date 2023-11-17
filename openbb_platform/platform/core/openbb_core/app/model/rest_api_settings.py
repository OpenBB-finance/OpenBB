"""FastAPI configuration settings model."""
from typing import List

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Cors(BaseModel):
    """Cors model for FastAPI configuration."""

    model_config = ConfigDict(frozen=True)

    allow_origins: List[str] = Field(default_factory=lambda: ["*"])
    allow_methods: List[str] = Field(default_factory=lambda: ["*"])
    allow_headers: List[str] = Field(default_factory=lambda: ["*"])


class Servers(BaseModel):
    """Servers model for FastAPI configuration."""

    model_config = ConfigDict(frozen=True)

    url: str = "http://localhost:8000"
    description: str = "Local OpenBB development server"


class FastAPISettings(BaseModel):
    """Settings model for FastAPI configuration."""

    model_config = ConfigDict(frozen=True)

    version: str = "1"
    prefix: str  # This is set in the model_validator
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

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    @model_validator(mode="before")
    @classmethod
    def update_prefix(cls, values: dict) -> dict:
        """Update prefix based on version."""
        prefix = values.get("prefix")
        if not prefix:
            version = values.get("version", "1")
            values["prefix"] = f"/api/v{version}"
            return values
        return values
