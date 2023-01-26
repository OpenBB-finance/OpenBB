from typing import Optional
import pytest

try:
    from website import (
        generate_sdk_markdown as gen_sdk,
        generate_terminal_markdown as gen_term,
    )
except ImportError:
    pytest.skip(allow_module_level=True)


def test_generate_terminal_markdown():
    """Test the terminal markdown generator"""
    assert gen_term.main() is True


def test_generate_sdk_markdown():
    """Test the sdk markdown generator"""
    assert gen_sdk.main() is True


def mock_func(arg1: Optional[str] = "Test", arg2: Optional[bool] = True) -> bool:
    """Stuff here or stuff there, it doesn't matter, it's everywhere.


    Parameters
    ----------
    arg1 : Optional[str]
        The first argument, by default "Test"
    arg2 : Optional[bool]
        The second argument, by default True

    Returns
    -------
    bool
        The return value.
    """
    del arg1, arg2
    return True


# pylint:disable=too-few-public-methods
class MockTrailMap:
    """Mock trail map"""

    def __init__(self):
        self.trailmap = ""
        self.func_attr = {"model": mock_func}
        self.class_attr = {"model": "mock"}
        self.lineon = {"model": 69}
        self.full_path = {"model": "test/mock_func.py"}
        self.model = "mock_func"
        self.long_doc = {"model": mock_func.__doc__}
        self.func_def = {
            "model": 'openbb.mock(arg1: Optional[str] = "Test", arg2: Optional[bool] = True)'
        }
        self.params = {"model": {}}
        for k, p in gen_sdk.get_signature_parameters(
            mock_func, mock_func.__globals__
        ).items():
            self.params["model"][k] = p


EXPECTED_OUTPUT = """Stuff here or stuff there, it doesn't matter, it's everywhere.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/test/mock_func.py#L69)]

```python wordwrap
openbb.mock(arg1: Optional[str] = "Test", arg2: Optional[bool] = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| arg1 | Optional[str] | The first argument, by default "Test" | Test | True |
| arg2 | Optional[bool] | The second argument, by default True | True | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| bool | The return value. |
---

"""


def test_sdk_docstring_to_markdown():
    """Test the docstring to markdown converter"""
    mock = MockTrailMap()
    func_meta = gen_sdk.get_function_meta(mock, "model")
    result = gen_sdk.generate_markdown_section(func_meta)

    assert result == EXPECTED_OUTPUT
