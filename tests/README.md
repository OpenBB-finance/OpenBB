# 1. OpenBB Terminal : `Unit Testing`

This document is part of the `OpenBB Terminal` library documentation.

It aims to provide necessary information in order :

- Run `unit tests`
- Build `unit tests`
- Maintain `unit tests`

## 1.1. Why having unit tests ?

Here `Unit tests` purpose is to allow : update without fear.

Insuring with enough confidence that : addition, removal or update of a `module/function` won't break other parts of the code.

To do that we need `unit tests` to be :

- fast to write
- fast to run

**FAST TO WRITE**

The `unit tests` will only tests the most common cases.

**FAST TO RUN**

Slow part of the code like `network` or `database` access should be either `mocked` or `marked` as `slow`.

# 2. Run `unit tests`

In this section we will explain everything you need to run the `unit tests` on `OpenBB Terminal`.

## 2.1. How to install tests dependencies ?

To run the tests you will need the `dev-dependencies`.

By default poetry installs the `dev-dependencies` when you run this command :

```bash
poetry install
```

If you dont want to install the `dev-dependencies` you will have to add the option `--no-dev` like this :

```bash
poetry install --no-dev
```

## 2.2. How to run `tests` : by `module` ?

You can run tests on a specific package/module by specifying the path of this package/module, like this :

```bash
pytest tests/openbb_terminal/some_package
pytest tests/openbb_terminal/some_package/some_module.py
```

## 2.3. How to run `tests` : by `name` ?

You can run tests by their name :

```
pytest -k "test_function1"
```

## 2.4. How to run `tests` : by `markers` ?

You can run tests only on specific markers, like this :

```
pytest -m slow
pytest -k "not slow"
pytest -k "not slow and not network"
```

You can list the available markers using this command :

```
pytest --markers
```

## 2.5. How to skip tests function ?

```python
import pytest

@pytest.skip
def test_some_function(mocker):
    pass

@pytest.skip("This time with a comment")
def test_another_function(mocker):
    pass
```

## 2.6. How to skip tests modules ?

```python
import pytest

pytest.skip(msg="Some optional comment.", allow_module_level=True)

def test_some_function(mocker):
    pass
```

# 3. Build `unit tests`

## 3.1. Where to add my `test module` ?

All the `unit tests` should be insides the `tests` folder.

There should be at most one `test module` for each `module` of `OpenBB Terminal`.

Each `test module` should follow the same path than the `module` it is `testing`.

For instance to `test` the following module :

- `openbb_terminal/stocks/due_diligence/dd_controller.py`

A `test module` should be added here :

- `tests/openbb_terminal/stocks/due_diligence/test_dd_controller.py`

## 3.2. How to record network ?

Network exchange can be recording inside a `test function` using the `@pytest.mark.vcr` `marker`.

Here is an example :

```python
@pytest.mark.vcr
def test_single():
    assert requests.get("http://httpbin.org/get").text == '{"get": true}'
```

You can choose the `cassette` name using the `@pytest.mark.default_cassette` marker.
Here is an example :

```python
@pytest.mark.default_cassette("example.yaml")
@pytest.mark.vcr
def test_default():
    assert requests.get("http://httpbin.org/get").text == '{"get": true}'
```

## 3.2. Where to put data files ?

Each data file should be related exactly to one `test module`.

The purpose is to have each `test module` as self-contained as possible.

Data related to a `test module` should be stored within the same folder than this `test module`.

Example with `tests/openbb_terminal/some_package/some_module.py` :

- `tests/openbb_terminal/some_package`/cassettes/`some_module`/test_function1.yaml
- `tests/openbb_terminal/some_package`/txt/`some_module`/test_function1.csv
- `tests/openbb_terminal/some_package`/csv/`some_module`/test_function1.csv
- `tests/openbb_terminal/some_package`/json/`some_module`/test_function1.json

## 3.3. How to filter `api keys` on `cassettes` ?

The filtering of `api keys` from a `cassette` should be done directly inside the `test module` using this `cassette`.

The purpose is to have each `test module` as self-contained as possible.

To filter `api keys` from a `cassettes` you can define a `vcr_config` fixture inside your `test module`.

Here is an example of filtering :

```python
@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ]
    }
```

More information about `vcr_config` fixture in the documentation of `pytest-recording` :

- https://github.com/kiwicom/pytest-recording

## 3.4. How to `mock` ?

**PYTEST-MOCK**

A `mocker` fixture is available through the package `pytest-mock`.

Here is an example on how to `mocker` fixture can be used :

```python
def test_something(mocker):
    mocker.patch("some_package.some_module")
```

More information about `pytest-mock` are available here :

- https://pypi.org/project/pytest-mock/

**MOCKEYPATCH**

There is also a `monkeypatch` fixture available by default inside `pytest`.

```python
def test_double(monkeypatch):
    monkeypatch.setattr("some_package.some_module", "Some value")
```

More information about `monkeypatch` are available here :

- https://docs.pytest.org/en/6.2.x/monkeypatch.html

## 3.5. Which `helpers` are available ?

You can find the available helpers inside the following package/module :

- `tests/helpers/`
- `tests/conftest.py`

See also the `pytest fixtures` which are autoloaded helpers.

## 3.6. Which `fixtures` are available ?

You can list all the available `pytest fixtures` using the following command :

```
pytest --fixtures
```

More on custom fixtures here :

- [FIXTURES](FIXTURES.md)

## 3.7. Which `markers` are available ?

You can list the available markers using this command :

```
pytest --markers
```

More information on markers location are available in pytest documentation :

- https://docs.pytest.org/en/6.2.x/mark.html#mark

## 3.8. Known `issue` / `solution`

**ION Usage**

If you are testing for a `_view.py` module that uses `ION`, you would need to mock it. With Windows, the charts / graphs are unable to close the graph applications. This would make the tests failed when running with Windows.

You can use the following example below. Once you have mocked the graphs / charts, simply call the display function, which is now a mocked object.

```
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_defi_tvl(mocker):
    # MOCK CHARTS
    mocker.patch.object(target=llama_view.obbff, attribute="USE_ION", new=True)
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.plt.ion")
    mocker.patch(target="openbb_terminal.stocks.options.yfinance_view.plt.show")
    llama_view.display_defi_tvl(20)
```

**YFINANCE**

If a method is using the `yfinance` library but do not let you pick the `start/end` dates it will pick the current date each time.

So your test might fail the next days.

To solve that you can filter the `start/end` date like this :

```python
@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ],
    }
```

You can also refactor this method to let access to `stard/end` dates.

**USER-AGENT**

Some function uses a random `User-Agent` on the `HTTP HEADER` when fetching data from an `API`.

Here is how to filter this random `User-Agent`.

```python
@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
    }
```

**YFINANCE**

If you do something like this with `yfinance` library.

```python
import yfinance as yf

yf.download(tickers="VCYT QSI")
```

Chances are you requests will be multi-threaded.

Issues : as for now `vcrpy` seems to be incompatible with multi-threading.

The library `vcrpy` is used to record `cassettes` (`network` calls into `yaml` files).

Here is a solution to still combine `yfinance` and `vcrpy` :

```python
import pytest
import yfinance

yf_download = yf.download
def mock_yf_download(*args, **kwargs):
    kwargs["threads"] = False
    return yf_download(*args, **kwargs)

@pytest.mark.vcr
def test_ark_orders_view(kwargs_dict, mocker, use_color):
    mocker.patch("yfinance.download", side_effect=mock_yf_download)

    yf.download(tickers="VCYT QSI")
```

**BROTLI**

The library `requests` doesn't support : `brotli` comnpression.

Unless `brotli` library is installed in the environment.

Plus `brotli` is not in `GamestonkTerminal` requirements.

So if both of these conditions are fulfilled :

- one generates a cassette with `brotli` installed in his/her environment
- the server choose to send `brotli` compressed data

Then the `test` might work in local but crash during `PullRequest`.

**BEFORE_RECORD_RESPONSE**

The library `vcrpy` has a `before_record_response` which accept a filtering function that can be used to filter your cassette content :

```python
import pytest

def my_custom_filter(response):
    return response

@pytest.mark.vcr(before_record_response=my_custom_filter)
def test_simple(recorder):
    pass
```

For instance this can be used to reduce the size of a `cassette` if it's too heavy.

Or to filter sensitive data in the response.

The issue with this `before_record_response` : it isn't launched at the first run of the test.

More on this here : https://github.com/kevin1024/vcrpy/pull/594

A solution for now is to run this command while initializing the `cassettes` :

```bash
# THE SAME COMMAND NEEDS TO BE RUN TWICE
pytest tests/.../test_some_test_module.py --record-mode=once --rewrite-expected
pytest tests/.../test_some_test_module.py --record-mode=once --rewrite-expected
```

## 3.9. List of useful `vscode` tools for `unit tests`

**VSCODE TESTING**

The default testing tool from `vscode` should let you add breakpoints and run debug on a specific `test`.

It's a convenient way to see what's inside your `test` while running.

More information on this tool are available here :

- https://code.visualstudio.com/docs/python/testing

## 3.10. How to handle `dev-dependencies` ?

**UPDATE PYPROJECT**

If a library need to be added or removed from `dev-dependencies` this can be done directly in the `pyproject.toml` file.

All the `dev-dependencies` should be under the `tool.poetry.dev-dependencies` section, like in this example :

```toml
[tool.poetry.dev-dependencies]
pytest = "^6.2.2"
pylint = "^2.7.2"
flake8 = "^3.9.0"
...
```

**EXPORT REQUIREMENTS**

After updating the `pyproject.toml` you will have to export the `requirements` files using the following commands :

```bash
poetry export -f requirements.txt  -o requirements.txt --without-hashes --dev
poetry export -f requirements.txt  -o requirements-full.txt --extras prediction --without-hashes --dev
poetry export -f requirements.txt  -o bots/requirements.txt --extras bots --without-hashes --dev
```

# 4. Maintain `unit tests`

## 4.1. What is the PR process ? (in progress)

Here are the steps to write proper tests for Gamestonk :

    A. Find right place
    B. Verify coverage is above 90%
    C. Set the right markers

**A. Find right place**

Put the code following the same module and package structure than `openbb_terminal` package.

**B. Verify coverage is above 90%**

Once you made your `PullRequest` an automation will let you know whether or not you have the proper amount of tests coverage.

You can also run the following command to check your coverage manually :

- `pytest --cov --cov-fail-under=90`

**C. Set the right markers**

If parts of your have specificities like :

- being `slow`
- requiring `network` connectivity
- requiring `authentication` to `APIs`

Then the proper markers should be sent on each test.

The rests of this document is there to provide a deeper comprehension of this steps.

A tests update might be asked whenever the answer to one of the following question is `yes` :

    A. Is this PR fixing bug which was not detected by the current tests ?
    B. Is this PR reducing code coverage ?
    C. Is this PR adding features ?
    D. Is this PR updating features ?

## 4.2. Which automations are available ?

**PULL REQUEST**

A `github action` should comment every `Pull Request` with the code `coverage`.

This automation will not enforce any rules regarding `tests`.

## 4.3. How to check code coverage ?

**PULL REQUEST AUTOMATION**

You should be able to see the code coverage on comment of your `Pull Requests`.

**MANUALLY**

This is how to manually check code coverage.

```bash
pytest --cov=openbb_terminal --cov=terminal --cov-report term-missing
```

You can also select a specific package/module with the option `--cov`.

Here is an example where we select only the package `stocks\due_diligence` :

```bash
pytest --cov=openbb_terminal\stocks\due_diligence --cov-report term-missing
```

**PRE-COMMIT**

Code `coverage` and `unit tests` are not run on `pre-commit` hooks since it will slow down each commit.
