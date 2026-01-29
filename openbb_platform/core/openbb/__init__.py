"""OpenBB 平台。"""

# flake8: noqa

from pathlib import Path
from typing import List, Optional, Union

from openbb_core.app.static.app_factory import (
    BaseApp as _BaseApp,
    create_app as _create_app,
)
from openbb_core.app.static.package_builder import PackageBuilder as _PackageBuilder
from openbb_core.app.static.reference_loader import ReferenceLoader as _ReferenceLoader

_this_dir = Path(__file__).parent.resolve()


def build(
    modules: Optional[Union[str, List[str]]] = None,
    lint: bool = True,
    verbose: bool = False,
) -> None:
    """构建扩展模块。

    Parameters
    ----------
    modules : Optional[List[str]], optional
        要重建的模块，默认为 None
        例如："/news" 或 ["/news", "/crypto"]
        如果是 None，则重建所有模块。
    lint : bool, optional
        是否对代码进行 lint，默认为 True
    verbose : bool, optional
        启用/禁用详细模式
    """
    _PackageBuilder(_this_dir, lint, verbose).build(modules)


_PackageBuilder(_this_dir).auto_build()
_ReferenceLoader(_this_dir)

try:
    # pylint: disable=import-outside-toplevel
    from openbb.package.__extensions__ import Extensions as _Extensions  # type: ignore

    obb: Union[_BaseApp, _Extensions] = _create_app(_Extensions)  # type: ignore
    sdk = obb
except (ImportError, ModuleNotFoundError):
    print("无法导入扩展。是否已安装任何扩展？")
    obb = sdk = _create_app()  # type: ignore
