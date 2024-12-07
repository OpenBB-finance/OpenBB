"""Command Context."""

from openbb_core.app.model.system_settings import SystemSettings
from openbb_core.app.model.user_settings import UserSettings
from pydantic import BaseModel, Field


class CommandContext(BaseModel):
    """Command Context."""

    user_settings: UserSettings = Field(default_factory=UserSettings)
    system_settings: SystemSettings = Field(default_factory=SystemSettings)
