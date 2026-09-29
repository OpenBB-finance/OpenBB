"""Package Builder Class.

This package was split from the original ``package_builder.py`` module into
smaller submodules. The public API is preserved: every name that was importable
from ``openbb_core.app.static.package_builder`` continues to be importable from
this package.
"""

# Re-export module-level helpers and singletons so that callers that patch via
# dotted paths (e.g. ``monkeypatch.setattr("openbb_core.app.static.package_builder.X", ...)``)
# continue to work unchanged.
# Re-export common symbols from the original module-level namespace so that
# downstream code (and tests) which used to import them via
# ``openbb_core.app.static.package_builder.X`` continues to work.
from inspect import Parameter, _empty, isclass, signature  # noqa: E402, F401
from typing import (  # noqa: E402, F401
    TYPE_CHECKING,
    Annotated,
    Any,
    Literal,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from typing_extensions import _AnnotatedAlias  # noqa: E402, F401

from openbb_core.app.static.package_builder.builder import (  # noqa: E402, F401
    CHARTING_INSTALLED,
    CORE_VERSION,
    VERSION,
    Console,
    DataProcessingSupportedTypes,
    Env,
    ExtensionLoader,
    Linters,
    OpenBBGroups,
    PackageBuilder,
    contextlib,
    dumps,
    entry_points,
    load,
    os,
    shutil,
    signal,
    sys,
    traceback,
)
from openbb_core.app.static.package_builder.class_definition import ClassDefinition
from openbb_core.app.static.package_builder.docstring_generator import (  # noqa: E402, F401
    DocstringGenerator,
    SystemService,
)
from openbb_core.app.static.package_builder.file_lock import FileLock
from openbb_core.app.static.package_builder.import_definition import ImportDefinition
from openbb_core.app.static.package_builder.method_definition import MethodDefinition
from openbb_core.app.static.package_builder.module_builder import ModuleBuilder

# Module-level constants / aliases that were defined in the original file.
from openbb_core.app.static.package_builder.path_handler import (  # noqa: E402
    TAB,
    PathHandler,
    RouterLoader,
    create_indent,
)
from openbb_core.app.static.package_builder.reference_generator import (
    ReferenceGenerator,
)

__all__ = [
    "CHARTING_INSTALLED",
    "CORE_VERSION",
    "ClassDefinition",
    "Console",
    "DocstringGenerator",
    "Env",
    "ExtensionLoader",
    "FileLock",
    "ImportDefinition",
    "Linters",
    "MethodDefinition",
    "ModuleBuilder",
    "OpenBBGroups",
    "PackageBuilder",
    "Parameter",
    "PathHandler",
    "ReferenceGenerator",
    "RouterLoader",
    "SystemService",
    "TAB",
    "VERSION",
    "create_indent",
]
