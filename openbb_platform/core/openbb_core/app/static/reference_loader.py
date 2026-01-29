"""用于从文件加载参考数据的 ReferenceLoader 类。"""

import json
from pathlib import Path

from openbb_core.app.model.abstract.singleton import SingletonMeta


class ReferenceLoader(metaclass=SingletonMeta):
    """用于加载 `reference.json` 文件的 ReferenceLoader 类。"""

    def __init__(self, directory: Path | None = None):
        """
        使用特定目录初始化 ReferenceLoader。

        如果未提供目录，则将使用默认目录。

        Attributes
        ----------
        directory : Optional[Path]
            参考文件所在的资产加载目录。
        """

        reference_path = (
            directory.joinpath(
                "reference.json"
                if str(directory).endswith("/assets")
                else "assets/reference.json"
            )
            if directory
            else self._get_default_directory().joinpath("reference.json")
        )
        self.directory = Path(reference_path).parent.resolve()
        self._reference = self._load(reference_path)

    @property
    def reference(self) -> dict[str, dict]:
        """获取参考数据。"""
        return self._reference

    def _get_default_directory(self) -> Path:
        """获取加载参考的默认目录。"""
        default_path = Path(__file__).parents[3].resolve() / "openbb" / "assets"

        return default_path

    def _load(self, file_path: Path):
        """从文件中加载参考数据。"""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        return data
