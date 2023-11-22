from typing import Optional

import pytest

try:
    from openbb_terminal.core.sdk.trailmap import get_signature_parameters
    from website import (
        generate_sdk_v3_markdown as gen_sdk,
        generate_terminal_v3_markdown as gen_term,
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
class MockFuncAttrs:
    """Mock function attributes"""

    def __init__(self):
        self.lineon = 69
        self.full_path = "test/mock_func.py"
        self.long_doc = mock_func.__doc__
        self.func_unwrapped = mock_func
        self.func_def = (
            'openbb.mock(arg1: Optional[str] = "Test", arg2: Optional[bool] = True)'
        )
        self.params = {}
        for k, p in get_signature_parameters(mock_func, mock_func.__globals__).items():
            self.params[k] = p


class MockTrailMap:
    """Mock trail map"""

    def __init__(self):
        self.func_attrs = {}
        self.func_attrs["model"] = MockFuncAttrs()
        self.model = mock_func
        self.class_attr = "mock"
        self.location_path = []


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
