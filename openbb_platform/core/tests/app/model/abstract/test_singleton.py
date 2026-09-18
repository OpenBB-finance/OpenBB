"""Tests for the SingletonMeta metaclass."""

from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from time import sleep

from openbb_core.app.model.abstract.singleton import SingletonMeta


class MyClass(metaclass=SingletonMeta):
    """A simple class."""

    def __init__(self, value):
        """Initialize the class."""
        self.value = value


def test_singleton_instance_creation():
    """Test the SingletonMeta metaclass with instance creation."""
    # Arrange
    instance1 = MyClass(42)
    instance2 = MyClass(100)

    # Act & Assert
    assert instance1 is instance2
    assert instance1.value == instance2.value
    assert instance1.value == 42


def test_singleton_multiple_classes():
    """Test the SingletonMeta metaclass with multiple classes."""

    # Arrange
    class AnotherClass(metaclass=SingletonMeta):
        def __init__(self, data):
            self.data = data

    instance1 = MyClass(42)
    instance2 = AnotherClass("test")

    # Act & Assert
    assert instance1 is not instance2
    assert instance1.value == 42
    assert instance2.data == "test"


def test_singleton_concurrent_creation():
    """Test that racing threads all receive the same, singly-constructed instance."""

    # Arrange
    barrier = Barrier(8)
    constructions = []

    class Racy(metaclass=SingletonMeta):
        def __init__(self):
            constructions.append(self)
            sleep(0.01)  # widen the window between the check and the publish

    def build():
        barrier.wait()
        return Racy()

    # Act
    with ThreadPoolExecutor(max_workers=8) as executor:
        instances = list(executor.map(lambda _: build(), range(8)))

    # Assert
    assert len(constructions) == 1
    assert all(instance is instances[0] for instance in instances)


def test_singleton_nested_creation_does_not_deadlock():
    """Test that building a singleton from inside another's __init__ completes."""

    # Arrange
    class Inner(metaclass=SingletonMeta):
        def __init__(self):
            self.name = "inner"

    class Outer(metaclass=SingletonMeta):
        def __init__(self):
            self.inner = Inner()

    barrier = Barrier(4)

    def build(cls):
        barrier.wait()
        return cls()

    # Act
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(build, cls) for cls in (Outer, Inner, Outer, Inner)]
        results = [future.result(timeout=5) for future in futures]

    # Assert
    assert results[0] is results[2]
    assert results[1] is results[3]
    assert results[0].inner is results[1]
