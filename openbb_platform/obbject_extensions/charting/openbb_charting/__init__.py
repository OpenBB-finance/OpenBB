"""OpenBB OBBject extension for charting."""

import warnings

from openbb_core.app.model.extension import Extension

from openbb_charting.charting import Charting as _Charting

warnings.filterwarnings(
    "ignore", category=UserWarning, module="openbb_core.app.model.extension", lineno=47
)

ext = Extension(name="charting", description="Create custom charts from OBBject data.")
Charting = ext.obbject_accessor(_Charting)
