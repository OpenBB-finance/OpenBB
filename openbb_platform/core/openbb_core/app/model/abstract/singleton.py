from typing import Dict, Generic, TypeVar

T = TypeVar("T")


class SingletonMeta(type, Generic[T]):
    # TODO : check if we want to update this to be thread safe
    _instances: Dict[T, T] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance

        return cls._instances[cls]
