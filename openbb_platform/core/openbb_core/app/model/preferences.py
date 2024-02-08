"""Preferences for the OpenBB platform."""

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PositiveInt


class Preferences(BaseModel):
    """Preferences for the OpenBB platform."""

    data_directory: str = str(Path.home() / "OpenBBUserData")
    export_directory: str = str(Path.home() / "OpenBBUserData" / "exports")
    user_styles_directory: str = str(Path.home() / "OpenBBUserData" / "styles" / "user")
    cache_directory: str = str(Path.home() / "OpenBBUserData" / "cache")
    charting_extension: Literal["openbb_charting"] = "openbb_charting"
    chart_style: Literal["dark", "light"] = "dark"
    plot_enable_pywry: bool = True
    plot_pywry_width: PositiveInt = 1400
    plot_pywry_height: PositiveInt = 762
    plot_open_export: bool = (
        False  # Whether to open plot image exports after they are created
    )
    table_style: Literal["dark", "light"] = "dark"
    request_timeout: PositiveInt = 15
    metadata: bool = True
    output_type: Literal["OBBject", "dataframe", "polars", "numpy", "dict", "chart"] = (
        Field(default="OBBject", description="Python default output type.")
    )
    show_warnings: bool = True

    model_config = ConfigDict(validate_assignment=True)

    def __repr__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.__class__.__name__}\n\n" + "\n".join(
            f"{k}: {v}" for k, v in self.model_dump().items()
        )
