"""OpenBB SDK."""
# flake8: noqa

from openbb.utils import auto_build as _auto_build, build
from typing import Union
from openbb_core.app.static.app_factory import (
    create_app as _create_app,
    BaseApp as _BaseApp,
)

_auto_build()

try:
    # pylint: disable=import-outside-toplevel
    from openbb.package.__extensions__ import Extensions as _Extensions

    obb: Union[_BaseApp, _Extensions] = _create_app(_Extensions)
    sdk = obb
except (ImportError, ModuleNotFoundError):
    print("Failed to import extensions.")
    obb = sdk = _create_app()
