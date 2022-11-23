from website import generate_sdk_markdown, generate_terminal_markdown


def test_generate_terminal_markdown():
    """Test the terminal markdown generator"""
    assert generate_terminal_markdown.main() is True


def test_generate_sdk_markdown():
    """Test the sdk markdown generator"""
    assert generate_sdk_markdown.main() is True


def mock_func(arg1: str = "Test", arg2: bool = True) -> bool:
    """Stuff here or stuff there, it doesn't matter, it's everywhere.


    Parameters
    ----------
    arg1 : str, optional
        The first argument, by default "Test"
    arg2 : bool, optional
        The second argument, by default True

    Returns
    -------
    bool
        The return value.
    """
    del arg1, arg2
    return True


class MockTrailMap:
    """Mock trail map"""

    def __init__(self):
        self.trailmap = ""
        self.func_attr = {"model": mock_func}
        self.class_attr = {"model": "mock_func"}
        self.lineon = {"model": 69}
        self.full_path = {"model": "test/mock_func.py"}
        self.long_doc = {"model": mock_func.__doc__}
        self.func_def = {"model": "def mock_func():"}
        self.model = "mock_func"
        self.params = {"model": {}}
        for k, p in generate_sdk_markdown.get_signature_parameters(
            mock_func, mock_func.__globals__
        ).items():
            self.params["model"][k] = p


EXPECTED_OUTPUT = """Stuff here or stuff there, it doesn't matter, it's everywhere.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/test/mock_func.py#L69)]

```python
def mock_func():
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| arg1 | str | The first argument, by default "Test" | Test | True |
| arg2 | bool | The second argument, by default True | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| bool | The return value. |
---

"""


def test_docstring_to_markdown():
    """Test the docstring to markdown converter"""
    mock = MockTrailMap()
    func_meta = generate_sdk_markdown.get_function_meta(mock, "model")
    result = generate_sdk_markdown.generate_markdown_section(func_meta)

    assert result == EXPECTED_OUTPUT
