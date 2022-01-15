# 1. Gamestonk Terminal : `Unit Testing` - `Fixtures`

In this document we will list custom `pytest fixtures` built in GamestonkTerminal and explain how they works.


## 1.1. What is a `fixture` ?
This part is fully documented so you can take a look directly on `pytest` documentation right here :

https://docs.pytest.org/en/6.2.x/fixture.html

## 1.2. Which `fixtures` are available ?

You can list all the available `pytest fixtures` using the following command :

```
pytest --fixtures
```

This will include the :
- `fixtures` available by default in `pytest`
- `fixtures` defined by installed `pytest plugins`
- custom `fixtures` built specially for this GamestonkTerminal

## 1.3. Which are the custom `fixtures` ?

The fixtures built for GamestonkTerminal are here to : make sure contributors are putting `test data file` in the right location.

Here we call `test data file` the files that you might use to store data.

For instance if you want to test a `function` generating a `Pandas DataFrame`, you might want to :
- store expected `DataFrame` result inside a `csv`
- then compare this expected result with the result of that `function`

Here is a table listing the fixtures specifically built for this library :


|**Fixture**|**Purpose**|
|:-|:-|
|default_csv_path|Builds a default location to store a `csv` file related to a test.|
|default_txt_path|Builds a default location to store a `txt` file related to a test.|
|default_json_path|Builds a default location to store a `json` file related to a test.|
|record_stdout|Capture stdout in a test. And compare it to the last recording.|
|recorder|Allow capturing one or multiple variable(s) in a test. And compare this captured variable(s) to the last recording|

Note that you can't combine `record_stdout` and `recorder` fixtures in the same test.

# 2. Path building `fixtures`
## 2.1. What is the purpose of these `fixtures` ?
These `fixtures` will provide a location to store your `data file`.

The folder to store the `data file` will be generated automatically.

The file will be store :
- inside the same folder than the `test module`
- inside a folder with the data type : for instance `txt` if you are storing text data
- inside a file with the name of the `test function` and with the right extension : `.txt` if its a text file.

Suppose `XXX` is your data type, the generated path will look like this :
- module_path/`XXX`/test_module_name/test_function_name.`XXX`

This mimic the default location for `vcrpy cassettes`.

More on `vcrpy` here :
https://vcrpy.readthedocs.io/en/latest/

## 2.2. How to use `default_csv_path` ?

```python
import pandas as pd
from tested_module import function_generating_a_dataframe

def test_function(default_csv_path):
    result_dataframe = function_generating_a_dataframe()

    result_dataframe.to_csv(default_csv_path)

    expected_dataframe = result_dataframe.read_csv(default_csv_path)
    
    pd.testing.assert_frame_equal(result_dataframe, expected_dataframe)
```

You might want to comment the file saving part after the first run.

Or find a way to conditionally disable it.

## 2.3. How to use `default_txt_path` ?

```python
from tested_module import function_generating_a_str

def test_function(default_txt_path):
    result_txt = function_generating_a_str()

    with open(file=default_txt_path, mode="w", encoding="utf-8") as f:
        f.write(result_txt)

    with open(file=default_txt_path, encoding="utf-8") as f:
        expected_txt = f.read()
    
    assert result_txt == expected_txt
```

## 2.4. How to use `default_json_path` ?

```python
import json
from tested_module import function_generating_a_json

def test_function(default_json_path):
    result_json = function_generating_a_json()

    with open(file=default_txt_path, mode="w", encoding="utf-8") as f:
        json.dump(result_json, f)
    
    with open(file=default_json_path, encoding="utf-8") as f:
        expected_json = json.load(f)
    
    assert result_json == expected_json
```


# 3. Recording fixtures


## 3.1. How to use the `record_stdout fixture` ?

**USAGE**

Example of usage :
```python
import pytest

@pytest.mark.record_stdout
def test_function():
    console.print("Something")
```

This will generate a text file to store the `printed` output.

The content of this file will be compared to the `test_function` output at each execution of the test.

**RECORD ONCE**

You can run this command to generate the text file :

```bash
pytest --record-mode=once
```

This works if :
- the text file was not generated yet
- you remove the text file

**RECORD REWRITE**

You can run this command to regenerate the text file :

```bash
pytest --record-mode=rewrite
```

**REWRITE EXPECTED**

This will force `record_stdout` to rewrite any changed file (`txt`).

This will not rewrite the cassettes.

Example :
```
pytest --rewrite-expected
```

**VCR**

You can combine `record_stdout` and `vcr` fixtures, like this :

```python
import pytest
import requests
from gamestonk_terminal.rich_config import console

@pytest.mark.vcr
@pytest.mark.record_stdout
def test_function():
    response = requests.get('https://api.github.com/user', auth=('user', 'pass'))
    
    console.print(response.status_code)
    console.print(response.text)
```

**ASSERT IN LIST**

You are not forced to save a text file, you can use a list of texts instead like this :

```python
import pytest
from gamestonk_terminal.rich_config import console

@pytest.mark.record_stdout(
    assert_in_list=["Some text", "Another text"],
    save_record=False,
)
def test_function():
    console.print("""
        This text contains :
            - Some text
            - Another text
    """)
```


**STRIP**

If your `test_function` output a random number of blank before or after you can `strip` the captured data.

Example :
```python
import pytest
import random
from gamestonk_terminal.rich_config import console

@pytest.mark.record_stdout(strip=True)
def test_function():
    some_text = "Some text output"
    random_int = random.randint(0,10)

    for _ in range(random_int):
        text += " "

    console.print(some_text)
```

**RECORD MODE**

It is possible to programmatically change the `record_mode` on a `test`.

Example :
```python
import pytest
from gamestonk_terminal.rich_config import console

@pytest.mark.record_stdout(record_mode="rewrite")
def test_function():
    some_text = "Some text output"

    console.print(some_text)
```

## 3.2. How to use the `recorder fixture` ?

**BEWARE**

You can't combine these two fixtures :
 - record_stdout
 - recorder

**USAGE**

Example of usage :
```python
import pytest

@pytest.mark.record_stdout
def test_function(recorder):
    some_dict = {1, 2, 3}
    some_list = [7, 8, 9 ]
    some_tuple = (4, 5, 6)
    some_string = "Some string"

    recorder.capture(some_dict)
    recorder.capture(some_list)
    recorder.capture(some_string)
    recorder.capture(some_tuple)
```

This will generate one or multiple text file(s) to store the `captured` variables.

The content of the file(s) will be compared to the `test_function` output at each execution of the test.



**RECORD ONCE**

You can run this command to generate the text file :

```bash
pytest --record-mode=once
```

This works if :
- the text file was not generated yet
- you remove the text file

**RECORD REWRITE**

You can run this command to regenerate the text file :

```bash
pytest --record-mode=rewrite
```

**REWRITE EXPECTED**

This will force `recorder` to rewrite any changed file (`csv`, `json`, `txt`).

This will not rewrite the cassettes.

Example :
```
pytest --rewrite-expected
```

**VCR**

You can combine `recorder` and `vcr` fixtures, like this :

```python
import requests

@pytest.mark.vcr
@pytest.mark.record_stdout
def test_function():
    response = requests.get('https://api.github.com/user', auth=('user', 'pass'))
    
    recorder.capture(response.status_code)
    recorder.capture(response.text)
```

**STRIP**

If your `test_function` output a random number of blank before or after you can `strip` the captured data.

Example :
```python
import random

def test_function(recorder):
    some_text = "Some text output"
    random_int = random.randint(0,10)

    for _ in range(random_int):
        text += " "

    recorder.capture(some_text, strip=True)
```

**RECORD MODE**

It is possible to programmatically change the `record_mode` on a `test`.

Example :
```python
def test_function(recorder):
    some_text = "Some text output"

    recorder.record_mode = "rewrite"
    recorder.capture(some_text)
```