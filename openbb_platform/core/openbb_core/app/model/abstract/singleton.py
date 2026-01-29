"""单例元类实现。"""

from typing import Generic, TypeVar

T = TypeVar("T")


class SingletonMeta(type, Generic[T]):
    """单例元类。"""

    # TODO : 检查我们是否想要将其更新为线程安全
    _instances: dict[T, T] = {}

    def __call__(cls: "SingletonMeta", *args, **kwargs):
        """单例模式实现。"""
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance

        return cls._instances[cls]
