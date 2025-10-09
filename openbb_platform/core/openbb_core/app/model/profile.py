"""Profile model."""

from openbb_core.app.model.hub.hub_session import HubSession
from pydantic import BaseModel, ConfigDict, Field


class Profile(BaseModel):
    """Profile."""

    hub_session: HubSession | None = Field(default=None)
    model_config = ConfigDict(validate_assignment=True)

    def __repr__(self) -> str:
        """Return string representation."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )
