# 1. OpenBB Terminal : `Unit Testing`

This document is part of the `OpenBB Terminal` library documentation.

It aims to provide necessary information in order to:

- Run `unit tests`
- Build `unit tests`
- Fix failed existing `unit tests`
- Maintain `unit tests`

## 1.1. Why having unit tests ?

`Unit tests` purpose is to allow developers to update without fear.

Writing tests that are easy to run will help the person modifying the code to do so quick and with more confidence. Having tests available also decreases the chances that bugs will make it into production and break other parts of the code.


To do that we need `unit tests` to be :

- fast to write
- fast to run

**FAST TO WRITE**

The `unit tests` is used for testing a single functionality for its correctness of input and the corresponding output. Unit tests are about ensuring that low-level implementation details are rock solid.

**FAST TO RUN**

Tests can be slow at times, due to the need to connect with external services. This can be sending a HTTP request or connecting to a database. We can speed this up by using mocks. In case this is not possible, make sure to `marked` it as `slow`

# 2. Run `unit tests`

In this section we will explain everything you need to run the `unit tests` on `OpenBB Terminal`.

## 2.1. How to install tests dependencies ?

To run the tests you will need first to install the `dev-dependencies`. By default poetry installs the `dev-dependencies` when you run this command :

```bash
poetry install
```

If you do not want to install the `dev-dependencies` you will have to add the option `--no-dev` like this :

```bash
poetry install --no-dev
```

## 2.2. How to run `tests` :
### By `module`

You can run tests on a specific package/module by specifying the path of this package/module, as follows:

```bash
pytest tests/openbb_terminal/some_package
pytest tests/openbb_terminal/some_package/some_module.py
```
### By test `name`

You can run tests by their name with the argument `-k`

```
pytest -k "test_function1"
```

### By `markers`

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

## 2.3. How to skip tests

### Skipping a specific test

You can use the decorator `@pytest.skip` as below:

```python
import pytest

@pytest.skip
def test_some_function(mocker):
    pass

@pytest.skip("This time with a comment")
def test_another_function(mocker):
    pass
```

### Skipping the entire test module

```python
import pytest

pytest.skip(msg="Some optional comment.", allow_module_level=True)

def test_some_function(mocker):
    pass
```

# 3. How to build `unit tests`

When you contribute a new feature to the Terminal, it's important that tests are added for this particular feature. It is a part of the Checklist for the PR to be approved.

All the `unit tests` should be insides the `tests` folder. There should be at most one `test module` for each `module` of `OpenBB Terminal`.

Each `test module` should follow the same path of the `module` that it is `testing`.For instance,
- in order to test the following module `openbb_terminal/stocks/due_diligence/dd_controller.py`
- a `test module` should be added here: `tests/openbb_terminal/stocks/due_diligence/test_dd_controller.py`

Now that you know where to add tests, let's go through 3 types of unit tests that we have:


## 3.1. Model Test

As mentioned in the main repo's README, we are following the MVC pattern. The  `_model.py`'s job to get the required data, e.g. from an external APIs or scraping.

Therefore, in unit tests for `_model.py`, the function output is captured and saved when the test is first run. Then, the next time the test is run, the function's returned value is compared with the captured value in the first run, to ensure parity.

Depending on the data type of function output, we can generate the following files:
- csv : for pandas.DataFrame
- json : for python native data type (list, dict, tuple)
- txt : store str or printed output


Examples:

```
@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_query_parameters": [
            ("token", "MOCK_TOKEN"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.parametrize(
    "ticker",
    [
        ("BTC"),
        ("BTC-USD"),
    ],
)
def test_check_supported_ticker(ticker, recorder):
    df = sentimentinvestor_model.check_supported_ticker(ticker)
    recorder.capture(df)
```


Several things worth noting here:
1. If the model utilizes an API key or token, make sure to filter it insider the `vcr_config` fixture inside your test module, similar to the example. This will hide your actual API key / token for security purposes.
2. Record HTTP requests using the decorator `@pytest.mark.vcr`
   1. When run the first time, the VCR will record the requests to `cassettes/test_*.yml`
   2. Run it again, and VCR will replay the recorded response when the HTTP request is made. This test is now fast (no real HTTP requests are made anymore), deterministic (the test will continue to pass, even if you have no internet connection or that external APIs go down) and accurate (the response will contain the same headers and body you get from a real request).
3. Test out multiple input variables to ensure tests cover multiple edge cases
   1. Use the decorator `@pytest.mark.parametrize`to specify the inputs for your tests.
4. Capture the returned df using `recorder.capture(<return_value>)`
   1. Next time the test run, return output will be compared against the captured file
5. Each fixture / cassette file for a test module should be stored within the same folder. An example with `tests/openbb_terminal/some_package/some_module.py` :
   - `tests/openbb_terminal/some_package`/cassettes/`some_module`/test_function1.yaml
   - `tests/openbb_terminal/some_package`/txt/`some_module`/test_function1.csv
   - `tests/openbb_terminal/some_package`/csv/`some_module`/test_function1.csv
   - `tests/openbb_terminal/some_package`/json/`some_module`/test_function1.json
6. You can choose the `cassette` name using the `@pytest.mark.default_cassette` marker. Here is an example :

```python
@pytest.mark.default_cassette("example.yaml")
@pytest.mark.vcr
def test_default():
    assert requests.get("http://httpbin.org/get").text == '{"get": true}'
```

## 3.2. View Test
Different from the `model.py`, `view.py` module handles how data is displayed, e.g.as a chart or a table.

The `view.py` has no return statement, and simply prints to stdout. Hence, our unit tests will capture stdout values, and compare against the recorded fixture in subsequent runs.

Example:

```
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_historical(mocker):
    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")
    sentimentinvestor_view.display_historical(
        ticker="AAPL", start="2021-12-12", end="2021-12-15", export="", raw=True
    )
```

Important notes to go through:
1. Use `@pytest.mark.record_stdout`to capture `sdtout`.
   1. Recorded stdout is saved as fixtures in a txt file
   2. If your view function only plots a chart, and does not output anything in `sdtout`, you can skip unit testing your `view.py`
   3. Make sure to mock `visualize_output` method.
      1. Inside `visualize_output`, we use `ion` to enable interactive mode. However, under Windows, having `ion` enabled would make tests fail to run. Hence, you should always mock `visualize_output`, and hence `ion`


## 3.3. Controller Test
Unit test for `_controller.py` is the last component you would need to add. Most of the time you won't need to create a `_controller.py` from scratch. Hence, we will only cover how to add tests for a new command to an existing `test_*_controller.py` file


#### Test print help
This test in the `test_*_controller.py` captured the help text printed to stdout.

Example:

```
@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
def test_print_help():
    controller = alt_controller.AlternativeDataController(queue=None)
    controller.print_help()
```

Adding an additional feature to the `controller.py` will alter the help text. Make sure to run the tests with the argument `--rewrite-expected` to re-generate the text file.

Example: `pytest openbb_terminal.cryptocurrency.defi.defi_controller --rewrite-expected`

#### Test call function

This test is to check when `controller.py` calls a command, the corresponding function from a `view.py` will be called with the correct arguments.

Example:

```
@pytest.mark.vcr(record_mode="none")
@pytest.mark.parametrize(
    "tested_func, other_args, mocked_func, called_args, called_kwargs",
    [
        (
            "call_aterra",
            [
                "ust",
                "--address=terra1wg2mlrxdmnnkkykgqg4znky86nyrtc45q336yv",  # pragma: allowlist secret
            ],
            "terraengineer_view.display_terra_asset_history",
            [],
            dict(),
        ),
        (
            "call_newsletter",
            [],
            "substack_view.display_newsletters",
            [],
            dict(),
        ),
    ],
)
def test_call_func(
    tested_func, mocked_func, other_args, called_args, called_kwargs, mocker
):
    path_controller = "openbb_terminal.cryptocurrency.defi.defi_controller"

    if mocked_func:
        mock = mocker.Mock()
        mocker.patch(
            target=f"{path_controller}.{mocked_func}",
            new=mock,
        )

        controller = defi_controller.DefiController(queue=None)
        getattr(controller, tested_func)(other_args)

        if called_args or called_kwargs:
            mock.assert_called_once_with(*called_args, **called_kwargs)
        else:
            mock.assert_called_once()
    else:
        controller = defi_controller.DefiController(queue=None)
        getattr(controller, tested_func)(other_args)
```

When adding a new feature to an existing menu, there should already be a `test_*_controller.py` file with the `test_call_func()` function. You can simply add another tuple under `@pytest.mark.parametrize()`, which contains:
1. `call_<command>` from the controller.py file
2. Arguments you want to pass in the `call_<command>`
3. The corresponding view function, which will be mocked (Here we only want check if the view function is called at least once. We mock it such that the function won't execute.)
4. Arguments you want to pass to the view function. Note that the arguments here need to be the same as arguments in (2). This is to ensure that arguments passed from the controller.py file are passed correctly to function in `view.py`


## 3.4. Fixing existing tests
It is not uncommon that your new feature or bug fixes break the existing code. Understanding a few concepts can help you navigate and fix most common cases.

Before continuing this section, please have a look at our [FIXTURES](FIXTURES.md) documentation.

TL;DR:

You can run unit tests under a few mode:
- `--rewrite-expected` will re-generate the fixtures (csv, json and txt files) if there's detected change.
- `--record-mode` will impact both the cassette (yaml) and fixtures (csv, json, txt files)
    1. `--record-mode=none` : searches for existing cassette / fixtures. If there's none, an exception will be thrown.
    2. `--record-mode=once` : creates new fixtures and cassette if they did not exist. If there are already fixtures or cassette, it will take the existing one.
    3. `--record-mode=rewrite` : this rewrites both the cassette and fixtures, even if they already exist.

### Scenario 1: Update Fixtures
Let's say you just updated the code in `_model.py` file, which then altered the recorded output. You can update the fixture files by running the tests with `--rewrite-expected` argument. This would update the fixtures with latest changes.

Example: `pytest openbb_terminal.cryptocurrency.defi.defi_controller --rewrite-expected`

### Scenario 2: Update both Fixtures and Cassettes
If you want to update existing cassettes and fixtures, use the argument `--record-mode=rewrite` when running tests.

As existing cassettes and fixtures will be overwritten (if there's any), make sure that you check both, and that they yield expected output.

## 3.5. How to `mock` ?

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

## 3.6. Which `helpers` are available ?

You can find the available helpers inside the following package/module :

- `tests/helpers/`
- `tests/conftest.py`

See also the `pytest fixtures` which are autoloaded helpers.

## 3.7. Which `fixtures` are available ?

You can list all the available `pytest fixtures` using the following command :

```
pytest --fixtures
```

More on custom fixtures here :

- [FIXTURES](FIXTURES.md)

## 3.8. Which `markers` are available ?

You can list the available markers using this command :

```
pytest --markers
```

More information on markers location are available in pytest documentation :

- https://docs.pytest.org/en/6.2.x/mark.html#mark

## 3.9. Known `issue` / `solution`

**ION Usage**

As mentioned earlier, if you are testing for a `_view.py` module that uses `ION`, you would need to mock it. With Windows, the charts / graphs are unable to close the graph applications. This would make the tests failed when running with Windows.

You can use the following example below. Once you have mocked the graphs / charts, simply call the display function, which is now a mocked object.

```
@pytest.mark.vcr
@pytest.mark.record_stdout
def test_display_defi_tvl(mocker):
    # MOCK EXPORT_DATA
    mocker.patch(target="openbb_terminal.cryptocurrency.defi.llama_view.export_data")

    # MOCK VISUALIZE_OUTPUT
    mocker.patch(target="openbb_terminal.helper_classes.TerminalStyle.visualize_output")

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

Plus `brotli` is not in `OpenBBTerminal` requirements.

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

## 3.10. List of useful `vscode` tools for `unit tests`

**VSCODE TESTING**

The default testing tool from `vscode` should let you add breakpoints and run debug on a specific `test`.

It's a convenient way to see what's inside your `test` while running.

More information on this tool are available here :

- https://code.visualstudio.com/docs/python/testing

## 3.11. How to handle `dev-dependencies` ?

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
