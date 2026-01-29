"""
OpenBB 特有的弃用警告。

此实现受到 Pydantic 特定警告的启发，并经过修改以适应 OpenBB 的需求。
"""

from openbb_core.app.version import VERSION, get_major_minor


class DeprecationSummary(str):
    """可用于存储弃用元数据的字符串子类。"""

    def __new__(cls, value: str, metadata: DeprecationWarning):
        """创建该类的新实例。"""
        obj = str.__new__(cls, value)
        setattr(obj, "metadata", metadata)
        return obj


class OpenBBDeprecationWarning(DeprecationWarning):
    """
    OpenBB 特有的弃用警告。

    当在 OpenBB 中使用已弃用的功能时，会引发此警告。它提供了有关引入弃用的时间以及预期删除相应功能的版本的信息。

    Attributes
    ----------
        message: 警告描述。
        since: 引入弃用的版本。
        expected_removal: 预期删除相应功能的版本。
    """

    # 选择使用类变量是基于未来开发中扩展该类的可能性。
    # 示例：发布 Platform V5 并决定创建一个名为 OpenBBDeprecatedSinceV4 的子类，
    # 它继承自 OpenBBDeprecationWarning。在这个子类中，我们将设置 since=4.X 和 expected_removal=5.0。
    # 这些值在类级别定义非常重要，而不仅仅是在实例级别，
    # 以确保我们在整个平台上的弃用警告的一致性和清晰度。

    message: str
    since: tuple[int, int]
    expected_removal: tuple[int, int]

    def __init__(
        self,
        message: str,
        *args: object,
        since: tuple[int, int] | None = None,
        expected_removal: tuple[int, int] | None = None,
    ) -> None:
        """初始化警告。"""
        super().__init__(message, *args)
        self.message = message.rstrip(".")
        self.since = since or get_major_minor(VERSION)
        self.expected_removal = expected_removal or (self.since[0] + 1, 0)
        self.long_message = (
            f"{self.message}. 在 OpenBB Platform V{self.since[0]}.{self.since[1]} 中已弃用"
            f" 并将在 V{self.expected_removal[0]}.{self.expected_removal[1]} 中移除。"
        )

    def __str__(self) -> str:
        """返回警告消息。"""
        return self.long_message
