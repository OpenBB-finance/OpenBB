from openbb_core.app.model.abstract.singleton import SingletonMeta


class MyClass(metaclass=SingletonMeta):
    def __init__(self, value):
        self.value = value


def test_singleton_instance_creation():
    # Arrange
    instance1 = MyClass(42)
    instance2 = MyClass(100)

    # Act & Assert
    assert instance1 is instance2
    assert instance1.value == instance2.value
    assert instance1.value == 42


def test_singleton_multiple_classes():
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
