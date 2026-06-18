"""Test bootstrap: pre-import openbb-core submodules and bind them as
attributes on their namespace-package parents so ``mock.patch`` resolution
works on Python 3.10."""

import sys

import openbb_core.api
import openbb_core.api.app_loader  # noqa: F401
import openbb_core.api.exception_handlers  # noqa: F401
import openbb_core.app.model
import openbb_core.app.model.credentials  # noqa: F401
import openbb_core.app.service
import openbb_core.app.service.system_service  # noqa: F401
import openbb_core.app.service.user_service  # noqa: F401

for _parent, _children in (
    ("openbb_core.api", ("app_loader", "exception_handlers")),
    ("openbb_core.app.model", ("credentials",)),
    ("openbb_core.app.service", ("system_service", "user_service")),
):
    _pkg = sys.modules[_parent]
    for _child in _children:
        setattr(_pkg, _child, sys.modules[f"{_parent}.{_child}"])
