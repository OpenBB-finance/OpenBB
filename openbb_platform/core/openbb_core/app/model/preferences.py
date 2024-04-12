"""Preferences for the OpenBB platform."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator

from openbb_core.env import Env


class Preferences(BaseModel):
    """Preferences for the OpenBB platform."""

    cache_directory: str = str(Path.home() / "OpenBBUserData" / "cache")
    chart_style: Literal["dark", "light"] = "dark"
    data_directory: str = str(Path.home() / "OpenBBUserData")
    export_directory: str = str(Path.home() / "OpenBBUserData" / "exports")
    metadata: bool = True
    model_config = ConfigDict(validate_assignment=True)
    output_type: Literal[
        "OBBject", "dataframe", "polars", "numpy", "dict", "chart", "llm"
    ] = Field(default="OBBject", description="Python default output type.")
    plot_enable_pywry: bool = True
    plot_open_export: bool = (
        False  # Whether to open plot image exports after they are created
    )
    plot_pywry_height: PositiveInt = 762
    plot_pywry_width: PositiveInt = 1400
    request_timeout: PositiveInt = 15
    show_warnings: bool = True
    table_style: Literal["dark", "light"] = "dark"
    user_styles_directory: str = str(Path.home() / "OpenBBUserData" / "styles" / "user")

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )

    @field_validator("output_type")
    @classmethod
    def llm_mode(cls, value: str) -> str:  # pylint: disable=no-self-argument
        """Set LLM mode."""
        if Env().LLM_MODE:
            return "llm"
        return value
