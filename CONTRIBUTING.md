# CONTRIBUTING

First off, thanks for taking the time to contribute (or at least read the Contributing Guidelines)! 🚀

The following is a set of guidelines for contributing to OpenBB Terminal. These are mostly guidelines, not rules.
Use your best judgment, and feel free to propose changes to this document in a pull request.

- [CONTRIBUTING](#contributing)
- [BASIC](#basic)
  - [Adding a new command](#adding-a-new-command)
    - [Select Feature](#select-feature)
    - [Model](#model)
    - [Data source](#data-source)
    - [View](#view)
    - [Controller](#controller)
    - [Add SDK endpoint](#add-sdk-endpoint)
    - [Add Unit Tests](#add-unit-tests)
    - [Open a Pull Request](#open-a-pull-request)
    - [Review Process](#review-process)
  - [Understand Code Structure](#understand-code-structure)
    - [Backend](#backend)
    - [Frontend](#frontend)
  - [Follow Coding Guidelines](#follow-coding-guidelines)
    - [General Code Requirements](#general-code-requirements)
    - [File Specific Requirements](#file-specific-requirements)
    - [Coding Style](#coding-style)
      - [OpenBB Style Guide](#openbb-style-guide)
      - [Flags](#flags)
      - [Output format](#output-format)
      - [Time-related](#time-related)
      - [Data selection and manipulation](#data-selection-and-manipulation)
      - [Financial instrument characteristics](#financial-instrument-characteristics)
      - [Naming Convention](#naming-convention)
      - [Docstrings](#docstrings)
      - [Linters](#linters)
      - [Command names](#command-names)
      - [UI and UX](#ui-and-ux)
  - [External API Keys](#external-api-keys)
    - [Creating API key](#creating-api-key)
    - [Setting and checking API key](#setting-and-checking-api-key)
- [ADVANCED](#advanced)
  - [Important functions and classes](#important-functions-and-classes)
    - [Base controller class](#base-controller-class)
  - [Default Data Sources](#default-data-sources)
    - [Export Data](#export-data)
    - [Queue and pipeline](#queue-and-pipeline)
    - [Auto Completer](#auto-completer)
    - [Logging](#logging)
    - [Internationalization](#internationalization)
  - [Write Code and Commit](#write-code-and-commit)
    - [Pre Commit Hooks](#pre-commit-hooks)
    - [Coding](#coding)
    - [Git Process](#git-process)
    - [Branch Naming Conventions](#branch-naming-conventions)
  - [Installers](#installers)

# BASIC

## Adding a new command

Before implementing a new command we highly recommend that you go through [Understand Code Structure](#understand-code-structure) and [Follow Coding Guidelines](#follow-coding-guidelines). This will allow you to get your PR merged faster and keep consistency of our code base.

In the next sections we describe the process to add a new command.
We will be adding a function to get price targets from the Financial Modeling Prep API.  Note that there already exists a function to get price targets from the Business Insider website, `stocks/fa/pt`, so we will be adding a new function to get price targets from the Financial Modeling Prep API, and go through adding sources.

### Select Feature

- Pick a feature you want to implement or a bug you want to fix from [our issues](https://github.com/OpenBB-finance/OpenBBTerminal/issues).
- Feel free to discuss what you'll be working on either directly on [the issue](https://github.com/OpenBB-finance/OpenBBTerminal/issues) or on [our Discord](www.openbb.co/discord).
  - This ensures someone from the team can help you and there isn't duplicated work.

Before writing any code, it is good to understand what the data will look like.  In this case, we will be getting the price targets from the Financial Modeling Prep API, and the data will look like this:

```json
[
  {
    "symbol": "AAPL",
    "publishedDate": "2023-02-03T16:19:00.000Z",
    "newsURL": "https://pulse2.com/apple-stock-receives-a-195-price-target-aapl/",
    "newsTitle": "Apple Stock Receives A $195 Price Target (AAPL)",
    "analystName": "Cowen Cowen",
    "priceTarget": 195,
    "adjPriceTarget": 195,
    "priceWhenPosted": 154.5,
    "newsPublisher": "Pulse 2.0",
    "newsBaseURL": "pulse2.com",
    "analystCompany": "Cowen & Co."
  }
```

### Model

1. Create a file with the source of data as the name followed by `_model` if it doesn't exist.  In this case, the file `openbb_terminal/stocks/fundamental_analysis/fmp_model.py` already exists, so we will add the function to that file.
2. Add the documentation header
3. Do the necessary imports to get the data
4. Define a function starting with `get_`
5. In this function:
   1. Use type hinting
   2. Write a descriptive description where at the end the source is specified.
   3. Utilize an official API, get and return the data.

```python
""" Financial Modeling Prep Model """
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helpers import request

logger = logging.getLogger(__name__)

@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_price_targets(cls, symbol: str) -> pd.DataFrame:
    """Get price targets for a company [Source: Financial Modeling Prep]

    Parameters
    ----------
    symbol : str
        Symbol to get data for

    Returns
    -------
    pd.DataFrame
        DataFrame of price targets
    """
    current_user = get_current_user()

    url = f"https://financialmodelingprep.com/api/v4/price-target?symbol={symbol}&apikey={current_user.credentials.API_KEY_FINANCIALMODELINGPREP}"
    response = request(url)

    # Check if response is valid
    if response.status_code != 200 or "Error Message" in response.json():
        message = f"Error, Status Code: {response.status_code}."
        message = (
            message
            if "Error Message" not in response.json()
            else message + "\n" + response.json()["Error Message"] + ".\n"
        )
        console.print(message)
        return pd.DataFrame()

    return pd.DataFrame(response.json())
```

In this function:

- We import the current user object and, consequently, preferences using the `get_current_user` function.  API keys are stored in `current_user.credentials`
- We use the `@log_start_end` decorator to add the function to our logs for debugging purposes.
- We add the `@check_api_key` decorator to confirm the API key is valid.
- We have type hinting and a docstring describing the function.
- We use the openbb_terminal helper function `request`, which is an abstracted version of the requests library, which allows us to add user agents, timeouts, caches, etc. to any HTTP request in the terminal.
- We check for different error messages.  This will depend on the API provider and usually requires some trial and error.  With the FMP API, if there is an invalid symbol, we get a response code of 200, but the json response has an error message field.  Same with an invalid API key.
- When an error is caught, we still return an empty dataframe.
- We return the json response as a pandas dataframe.  Most functions in the terminal should return a datatframe, but if not, make sure that the return type is specified.

Note:

1. If the function is applicable to many asset classes, it is possible that this file needs to be created under `common/` directory rather than `stocks/`, which means the function should be written in a generic way, i.e. not mentioning stocks or a specific context.
2. If the model requires an API key, make sure to handle the error and output relevant message.
3. If the data provider is not yet supported, you'll most likely need to do some extra steps in order to add it to the `keys` menu.  See [this section](#external-api-keys) for more details.

In the example below, you can see that we explicitly handle 4 important error types:

- Invalid API Keys
- API Keys not authorized for Premium feature
- Empty return payload
- Invalid arguments (Optional)

It's not always possible to distinguish error types using status_code. So depending on the API provider, you can use either error messages or exception.

```python
def get_economy_calendar_events() -> pd.DataFrame:
    """Get economic calendar events

    Returns
    -------
    pd.DataFrame
        Get dataframe with economic calendar events
    """
    current_user = get_current_user()
    response = request(
        f"https://finnhub.io/api/v1/calendar/economic?token={current_user.credentials.API_FINNHUB_KEY}"
    )

    df = pd.DataFrame()

    if response.status_code == 200:
        d_data = response.json()
        if "economicCalendar" in d_data:
            df = pd.DataFrame(d_data["economicCalendar"])
        else:
            console.print("No latest economy calendar events found\n")
    elif response.status_code == 401:
        console.print("[red]Invalid API Key[/red]\n")
    elif response.status_code == 403:
        console.print("[red]API Key not authorized for Premium Feature[/red]\n")
    else:
        console.print(f"Error in request: {response.json()['error']}", "\n")

    return df
```

### Data source

Now that we have added the model function getting, we need to specify that this is an available data source.  To do so, we edit the `openbb_terminal/miscellaneous/data_sources_default.json` file.  This file, described below, uses a dictionary structure to identify available sources.  Since we are adding FMP to `stocks/fa/pt`, we find that entry and append it:

```json
    "fa": {
      "pt": ["BusinessInsider", "FinancialModelingPrep"],
```

If you are adding a new function with a new data source, make a new value in the file.

### View

1. Create a file with the source of data as the name followed by `_view` if it doesn't exist, e.g. `fmp_view`
2. Add the documentation header
3. Do the necessary imports to display the data. One of these is the `_model` associated with this `_view`. I.e. from same data source.
4. Define a function starting with `display_`
5. In this function:
   - Use typing hints
   - Write a descriptive description where at the end the source is specified
   - Get the data from the `_model` and parse it to be output in a more meaningful way.
   - Do not degrade the main data dataframe coming from model if there's an export flag. This is so that the export can have all the data rather than the short amount of information we may show to the user. Thus, in order to do so `df_data = df.copy()` can be useful as if you change `df_data`, `df` remains intact.
6. If the source requires an API Key or some sort of tokens, add `check_api_key` decorator on that specific view. This will throw a warning if users forget to set their API Keys
7. Finally, call `export_data` where the variables are export variable, current filename, command name, and dataframe.

```python
@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def display_price_targets(
    symbol: str, limit: int = 10, export: str = "", sheet_name: Optional[str] = None
):
    """Display price targets for a given ticker. [Source: Financial Modeling Prep]

    Parameters
    ----------
    symbol : str
        Symbol
    limit: int
        Number of last days ratings to display
    export: str
        Export dataframe data to csv,json,xlsx file
    sheet_name: str
        Optionally specify the name of the sheet the data is exported to.
    """
    columns_to_show = [
        "publishedDate",
        "analystCompany",
        "adjPriceTarget",
        "priceWhenPosted",
    ]
    price_targets = fmp_model.get_price_targets(symbol)
    if price_targets.empty:
        console.print(f"[red]No price targets found for {symbol}[/red]\n")
        return
    price_targets["publishedDate"] = price_targets["publishedDate"].apply(
        lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%S.%fZ").strftime("%Y-%m-%d %H:%M")
    )
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "pt",
        price_targets,
        sheet_name,
    )

    print_rich_table(
        price_targets[columns_to_show].head(limit),
        headers=["Date", "Company", "Target", "Posted Price"],
        show_index=False,
        title=f"{symbol.upper()} Price Targets",
    )
```

In this function:

- We use the same log and API decorators as in the model.
- We define the columns we want to show to the user.
- We get the data from the fmp_model function
- We check if there is data.  If something went wrong, we don't want to show it, so we print a message and return.  Note that because we have error messages in both the model and view, there will be two print outs.  If you wish to just show one, it is better to handle in the model.
- We do some parsing of the data to make it more readable.  In this case, the output from FMP is not very clear at quick glance, we we put it into something more readable.
- We export the data.  In this function, I decided to export after doing the manipulation.  If we do any removing of columns, we should copy the dataframe before exporting.
- We print the data in table form using our `print_rich_table`.  This provides a nice console print using the rich library.  Note that here I show the top `limit` rows of the dataframe.  Care should be taken to make sure that things are sorted.  If a sort is required, there is a `reverse` argument that can be added to sort in reverse order.

### Controller

Now that we have the model and views, it is time to add to the controller.

1. Import the associated `_view` function to the controller.
2. Add command name to variable `CHOICES_COMMANDS` from `FundamentalAnalysisController` class.
3. Add command and source to `print_help()`.

   ```python
   def print_help(self):
        """Print help"""
        mt = MenuText("stocks/dps/")
        mt.add_cmd("load")
        mt.add_raw("\n")
        mt.add_cmd("shorted")
   ```

4. If there is a condition to display or not the command, this is something that can be leveraged through this `add_cmd` method, e.g. `mt.add_cmd("shorted", self.ticker_is_loaded)`.

5. Add command description to file `i18n/en.yml`. Use the path and command name as key, e.g. `stocks/fa/pt` and the value as description. Please fill in other languages if this is something that you know.

6. Add a method to `FundamentalAnalysisController` class with name: `call_` followed by command name.
   - This method must start defining a parser with arguments `add_help=False` and
     `formatter_class=argparse.ArgumentDefaultsHelpFormatter`. In addition `prog` must have the same name as the command, and `description` should be self-explanatory ending with a mention of the data source.
   - Add parser arguments after defining parser. One important argument to add is the export capability. All commands should be able to export data.
   - If there is a single or even a main argument, a block of code must be used to insert a fake argument on the list of args provided by the user. This makes the terminal usage being faster.

      ```python
      if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
      ```

   - Parse known args from list of arguments and values provided by the user.
   - Call the function contained in a `_view.py` file with the arguments parsed by argparse.

Note that the function self.parse_known_args_and_warn() has some additional options we can add.  If the function is showing a chart, but we want the option to show raw data, we can add the `raw=True` keyword and the resulting namespace will have the `raw` attribute.
Same with limit, we can pass limit=10 to add the `-l` flag with default=10.  Here we also specify the export, and whether it is data only, plots only or anything.  This function also adds the `source` attribute to the namespace.  In our example, this is important because we added an additional source.

Our new function will be:

```python
   @log_start_end(log=logger)
    def call_pt(self, other_args: List[str]):
        """Process pt command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="pt",
            description="""Prints price target from analysts. [Source: Business Insider and Financial Modeling Prep]""",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            dest="ticker",
            help="Ticker to analyze",
            type=str,
            default=None,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, raw=True, limit=10
        )
        if ns_parser:
            if ns_parser.ticker:
                self.ticker = ns_parser.ticker
                self.custom_load_wrapper([self.ticker])

            if ns_parser.source == "BusinessInsider":
                business_insider_view.price_target_from_analysts(
                    symbol=self.ticker,
                    data=self.stock,
                    start_date=self.start,
                    limit=ns_parser.limit,
                    raw=ns_parser.raw,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            elif ns_parser.source == "FinancialModelingPrep":
                fmp_view.display_price_targets(
                    symbol=self.ticker,
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
```

Here, we make the parser, add the arguments, and then parse the arguments.  In order to use the fact that we had a new source, we add the logic to access the correct view function.  In this specific menu, we also allow the user to specify the symbol with -t, which is what the first block is doing.

Note that in the `fa` submenu, we allow the function to be run by specifying a ticker, ie `pt -t AAPL`.  In this submenu we do a `load` behind the scenes with the ticker selected so that other functions can be run without specifying the ticker.

Now from the terminal, this function can be run as desired:

```bash
2023 Mar 03, 11:37 (🦋) /stocks/fa/ $ pt -t aapl --source FinancialModelingPrep

                         AAPL Price Targets
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Date             ┃ Company               ┃ Target ┃ Posted Price ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━┩
│ 2023-02-03 16:19 │ Cowen & Co.           │ 195.00 │ 154.50       │
├──────────────────┼───────────────────────┼────────┼──────────────┤
│ 2023-02-03 09:31 │ D.A. Davidson         │ 173.00 │ 157.09       │
├──────────────────┼───────────────────────┼────────┼──────────────┤
│ 2023-02-03 08:30 │ Rosenblatt Securities │ 173.00 │ 150.82       │
├──────────────────┼───────────────────────┼────────┼──────────────┤
│ 2023-02-03 08:29 │ Wedbush               │ 180.00 │ 150.82       │
├──────────────────┼───────────────────────┼────────┼──────────────┤
│ 2023-02-03 07:21 │ Raymond James         │ 170.00 │ 150.82       │
├──────────────────┼───────────────────────┼────────┼──────────────┤
│ 2023-02-03 07:05 │ Barclays              │ 145.00 │ 150.82       │
├──────────────────┼───────────────────────┼────────┼──────────────┤
│ 2023-02-03 03:08 │ KeyBanc               │ 177.00 │ 150.82       │
├──────────────────┼───────────────────────┼────────┼──────────────┤
│ 2023-02-02 02:08 │ Rosenblatt Securities │ 165.00 │ 145.43       │
├──────────────────┼───────────────────────┼────────┼──────────────┤
│ 2023-02-02 02:08 │ Deutsche Bank         │ 160.00 │ 145.43       │
├──────────────────┼───────────────────────┼────────┼──────────────┤
│ 2023-02-02 02:08 │ J.P. Morgan           │ 180.00 │ 145.43       │
└──────────────────┴───────────────────────┴────────┴──────────────┘
```

When adding a new menu, the code looks like this:

```python
@log_start_end(log=logger)
def call_fa(self, _):
    """Process fa command"""
    from openbb_terminal.stocks.fundamental_analysis.fa_controller import (
        FundamentalAnalysisController,
    )

    self.queue = self.load_class(
        FundamentalAnalysisController, self.ticker, self.start, self.stock, self.queue
    )
```

The **import only occurs inside this menu call**, this is so that the loading time only happens here and not at the terminal startup. This is to avoid slow loading times for users that are not interested in `stocks/fa` menu.

In addition, note the `self.load_class` which allows to not create a new DarkPoolShortsController instance but re-load the previous created one. Unless the arguments `self.ticker, self.start, self.stock` have changed since. The `self.queue` list of commands is passed around as it contains the commands that the terminal must perform.

### Add SDK endpoint

In order to add a command to the SDK, follow these steps:

1. If you've created a new model or view file, add the import with an alias to `openbb_terminal/core/sdk/sdk_init.py` following this structure:

    ```python
    # Stocks - Fundamental Analysis
    from openbb_terminal.stocks.fundamental_analysis import (
        finviz_model as stocks_fa_finviz_model,
        finnhub_model as stocks_fa_finnhub_model,
        finnhub_view as stocks_fa_finnhub_view,
    )
    ```

2. Go to the `trail_map.csv` file located in `openbb_terminal/core/sdk`, which should look like this:

    ```csv
    trail,model,view
    stocks.fa.analyst,stocks_fa_finviz_model.get_analyst_data,
    stocks.fa.rot,stocks_fa_finnhub_model.get_rating_over_time,stocks_fa_finnhub_view.rating_over_time
    ```

    In this file, the trail represents the path to the function to be called. The model represents the import alias we gave to the `_model` file. The view represents the import alias we gave to the `_view` file.

3. Add your new function to this structure.  In our example of the `shorted` function, our trail would be `stocks.dps.shorted`.
The model is the import alias to the `_model` function that was written: `stocks_dps_yahoofinance_model.get_most_shorted`.
The view is the import alias to the `_view` function that was written: `stocks_dps_yahoofinance_view.display_most_shorted`.
The added line of the file should look like this:

    ```csv
    stocks.dps.shorted,stocks_dps_yahoofinance_model.get_most_shorted,stocks_dps_yahoofinance_view.display_most_shorted
    ```

4. Generate the SDK files by running `python generate_sdk.py` from the root of the project. This will automatically generate the SDK `openbb_terminal/sdk.py`, corresponding `openbb_terminal/core/sdk/controllers/` and `openbb_terminal/core/sdk/models/` class files.

    To sort the `trail_map.csv` file and generate the SDK files, run the following command

    ```bash
    python generate_sdk.py sort
    ```

### Add Unit Tests

This is a vital part of the contribution process. We have a set of unit tests that are run on every Pull Request. These tests are located in the `tests` folder.

Unit tests minimize errors in code and quickly find errors when they do arise. Integration tests are standard usage examples, which are also used to identify errors.

A thorough introduction on the usage of unit tests and integration tests in OpenBBTerminal can be found on the following page respectively:

[Unit Test README](tests/README.md)

[Integration Test README](scripts/README.md)

Any new features that do not contain unit tests will not be accepted.

### Open a Pull Request

Once you're happy with what you have, push your branch to remote. E.g. `git push origin feature/AmazingFeature`.

> Note that we follow gitflow naming convention, so your branch name should be prefixed with `feature/` or `hotfix/` depending on the type of work you are doing.

A user may create a **Draft Pull Request** when there is the intention to discuss implementation with the team.

### Review Process

As soon as the Pull Request is opened, our repository has a specific set of github actions that will not only run
linters on the branch just pushed, but also run `pytest` on it. This allows for another layer of safety on the code developed.

In addition, our team is known for performing `diligent` code reviews. This not only allows us to reduce the amount of iterations on that code and have it to be more future proof, but also allows the developer to learn/improve his coding skills.

Often in the past the reviewers have suggested better coding practices, e.g. using `1_000_000` instead of `1000000` for better visibility, or suggesting a speed optimization improvement.

## Understand Code Structure

### Backend

CLI :computer: → `_controller.py` :robot: →&nbsp;`_view.py` :art: &nbsp;&nbsp;&nbsp; → &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`_model.py` :brain:<br />
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  &nbsp;&nbsp;&nbsp;
`chart=True`
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
`chart=False`
<br/>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  &#8593;
  &nbsp;&nbsp;
`sdk.py` :factory:
  &nbsp;
  &#8593;

| **File&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**           | **Role**       | **Description**                                        |
| :------------------------- | :------------- | :----------------------------------------------------- |
| **_controller.py** :robot: | The router/input validator | The controller file should hold the least amount of logic possible. Its role is to be a stupid (no logic) router and redirect the command correctly while checking the input with argparser.   |
| **_view.py** :art:         | The artist     | The view file should only output or visualise the data it gets from the `_model` file! The `_view` can limit the data coming from the `_model`, otherwise the data object should be identical in the `_view` and the `_model` files. |
| **_model.py** 🧠           |The brain       | The model file is where everything fun happens. The data is gathered (external APIs), processed and returned here.                                                                |
| **sdk.py** 🏭              |The SDK Factory | The SDK file is where the callable functions are created for the SDK. There is only one SDK file in the openbb_terminal folder.                                                                                |

### Frontend

| **Item**     | **Description**                                                                                                                                                                                | **Example**                                      |
| :----------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------- |
| **CONTEXT**  | Specific instrument _world_ to analyse.                                                                                                                                                        | `stocks`, `crypto`, `economy`                    |
| **CATEGORY** | Group of similar COMMANDS to do on the instrument <br /> There are the specialized categories, specific to each CONTEXT and there are common categories which are not specific to one CONTEXT. | `due_diligence`, `technical_analysis`, `insider` |
| **COMMAND**  | Operation on one or no instrument that retrieves data in form of string, table or plot.                                                                                                        | `rating`, `supplier`, `sentiment`                |

The following layout is expected: `/<context>/<category>/<command_files>`

If there are sub-categories, the layout will be: `/<context>/<category>/<sub-category>/<command_files>`

**Example:**

```text
openbb_terminal/stocks/stocks_controller.py
                      /stocks_helper.py
                      /due_diligence/dd_controller.py
                                    /marketwatch_view.py
                                    /marketwatch_model.py
                                    /finviz_view.py
                                    /finviz_model.py
                      /technical_analysis/ta_controller.py
                                         /tradingview_view.py
                                         /tradingview_model.py
                /common/technical_analysis/overlap_view.py
                                          /overlap_model.py
                /crypto/crypto_controller.py
                       /crypto_helper.py
                       /due_diligence/dd_controller.py
                                     /binance_view.py
                                     /binance_model.py
                       /technical_analysis/ta_controller.py
```

With:

| **Context** | **Category**          | **File**               | **Description**                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| :---------- | :-------------------- | :--------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `stocks/`   |                       | `stocks_controller.py` | Manages **stocks** _context_ from a user perspective, i.e. routing _commands_ and arguments to output data, or, more importantly, redirecting to the selected _category_.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `stocks/`   |                       | `stocks_helper.py`     | Helper to `stocks` menu. This file is meant to hold generic purpose  `stocks` functionalities.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| `stocks/`   | `due_diligence/`      | `dd_controller.py`     | Manages **due_diligence** _category_ from **stocks** _context_ from a user perspective, i.e. routing _commands_ and arguments to output data.
| `stocks/`   | `due_diligence/`      | `marketwatch_view.py`  | This file contains functions that rely on **Market Watch** data. These functions represent _commands_ that belong to **due_diligence** _category_ from **stocks** _context_. These functions are called by `dd_controller.py` using the arguments given by the user and will output either a string, table or plot.
| `stocks/`   | `due_diligence/`      | `marketwatch_model.py` | This file contains functions that rely on **Market Watch** data. These functions represent _commands_ that belong to **due_diligence** _category_ from **stocks** _context_. These functions are called by `marketwatch_view.py` and will return data to be processed in either a string, dictionary or dataframe format.                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `stocks/`   | `due_diligence/`      | `finviz_view.py`       | This file contains functions that rely on **Finviz** data. These functions represent _commands_ that belong to **due_diligence** _category_ from **stocks** _context_. These functions are called by `dd_controller.py` using the arguments given by the user and will output either a string, table or plot.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `stocks/`   | `due_diligence/`      | `finviz_model.py`      | This file contains functions that rely on **Finviz** data. These functions represent _commands_ that belong to **due_diligence** _category_ from **stocks** _context_. These functions are called by `finviz_view.py` and will return data to be processed in either a string, dictionary or dataframe format.                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| `stocks/`   | `technical_analysis/` | `ta_controller.py`     | Manages **technical_analysis** _category_ from **stocks** _context_ from a user perspective, i.e. routing _commands_ and arguments to output data.
| `stocks/`   | `technical_analysis/` | `tradingview_view.py`  | This file contains functions that rely on **TradingView** data. These functions represent _commands_ that belong to **technical_analysis** _category_ from **stocks** _context_. These functions are called by `ta_controller.py` using the arguments given by the user and will output either a string, table or plot.                                                                                                                                                                                                                                                                                                                                                                                                                               |
| `stocks/`   | `technical_analysis/` | `tradingview_model.py` | This file contains functions that rely on **TradingView** data. These functions represent _commands_ that belong to **technical_analysis** _category_ from **stocks** _context_. These functions are called by `tradingview_view.py` and will return data to be processed in either a string, dictionary or dataframe format.                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `common/`   | `technical_analysis/` | `overlap_view.py`      | This file contains functions that rely on **overlap** data. In this case **overlap** is not a data source, but the type of technical analysis performed. These functions represent _commands_ that belong to **technical_analysis** _category_ from **MULTIPLE** _contexts_. These functions are called by `ta_controller.py`, from **MULTIPLE** _contexts_, using the arguments given by the user and will output either a string, table or plot. Due to the fact that this file is **common** to multiple _contexts_ the functions need to be generic enough to accommodate for this. E.g. if we are providing a dataframe to these functions, we should make sure that `stocks/ta_controller.py` and `crypto/ta_controller` use the same formatting. |
| `common/`   | `technical_analysis/` | `overlap_model.py`     | This file contains functions that rely on **overlap** data. In this case **overlap** is not a data source, but the type of technical analysis performed. These functions represent _commands_ that belong to **technical_analysis** _category_ from **MULTIPLE** _contexts_. These functions are called by `overlap_view.py`, and will return data to be processed in either a string, dictionary or dataframe format. Due to the fact that this file is **common** to multiple _contexts_ the functions need to be generic enough to accommodate for this. E.g. if we are getting the sentiment of an instrument, we should ensure that these functions accept both a "GME" or a "BTC", for `stocks` and `crypto`, respectively.                     |

## Follow Coding Guidelines

### General Code Requirements

1. Each function should have default values for non critical kwargs

    - Why? It increases code readability and acts as an input example for the functions arguments. This increases the ease of use of the functions through the SDK, but also just generally.

    > Watch out, add default values whenever possible, but take care for not adding mutable default arguments! [More info](https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments)

    <br>

    <table>
    <tr>
    <td> Good code :white_check_mark: </td> <td> Bad code :x: </td>
    </tr>
    <tr>
    <td>

    ```python
    def display_last_uni_swaps(
      top: int = 10,
      sortby: str = "timestamp",
      descend: bool = False,
      export: str = "",) -> None:
    ```

    </td>
    <td>

    ```python
    def display_last_uni_swaps(
      top: int,
      sortby: str,
      descend: bool,
      export: str,) -> None:
    ```

    </td>
    </tr>
    </table>

    <br>

2. Simple and understandable input objects; avoid for example weird dictionaries packed with data: {“title”: DataFrame}

    - Why? Ease of use and often these complex formats are clumsy, prone to error and the formatting required for complex parameters is time consuming and unneeded.

    <br>

    <table>
    <tr>
    <td> Good code :white_check_mark: </td> <td> Bad code :x: </td>
    </tr>
    <tr>
    <td>

    ```python
    def get_coins(
      top: int = 250,
      category: str = "") -> pd.DataFrame:
    ```

    </td>
    <td>

    ```python
    def load(
      file: str,
      file_types: list,
      data_files: Dict[Any, Any],
      data_examples: Dict[Any, Any],) -> pd.DataFrame:
    ```

    </td>
    </tr>
    </table>

    <br>

3. Each function needs to have a docstring explaining what it does, its parameters and what it returns.

    - Why? You can use the function without reading its source code. This improves the developing experience and SDK usage. The SDK factory also can’t handle functions with out docstrings.

    <br>

4. Consistent and clear argument naming; not `symbol` in `_view` and then `ticker` in `_file` -> ticker everywhere; the name should be descriptive of what information it holds (see Style Guide section below)

    - Why? You can quickly understand what the input should be; example: tickers and stock names are fundamentally different, but they’re both strings so they should be named accordingly.

    <br>

    <table>
    <tr>
    <td> Good code :white_check_mark: </td> <td> Bad code :x: </td>
    </tr>
    <tr>
    <td>

    ```python
    data: pd.Series, dataset_name: str, y_label: str,
    ```

    </td>
    <td>

    ```python
    data: pd.Series, dataset: str, column: str,
    ```

    </td>
    </tr>
    </table>

    <br>

5. Classes (for example the portfolio class) should hold the relevant data and perform no other calculations, these calculations should be done in an independent function.

    - Why? Two reasons:

    These calculations can then be used outside of the class with custom data; for example via the sdk or for tests.

    ```python
    from openbb_terminal.portfolio.portfolio_helper import get_gaintopain_ratio

    # Direct function access
    get_gaintopain_ratio(historical_trade_data, benchmark_trades, benchmark_returns)
    ```

    The function can be loaded in SDK factory as an endpoint and user can get result by passing the class instance.

    ```python
    from openbb_terminal.sdk import openbb
    from openbb_terminal.sdk import Portfolio

    transactions = Portfolio.read_orderbook("../../portfolio/holdings/example.csv")
    P = Portfolio(transactions)
    P.generate_portfolio_data()
    P.set_benchmark()

    # SDK endpoint access
    openbb.portfolio.gaintopain(P)
    ```

    <table>
    <tr>
    <td> Good code :white_check_mark: </td> <td> Bad code :x: </td>
    </tr>
    <tr>
    <td>

    ```python
    def get_gaintopain_ratio(portfolio: PortfolioEngine) -> pd.DataFrame:

    """..."""

    gtp_period_df = portfolio_helper.get_gaintopain_ratio(
      portfolio.historical_trade_data,
      portfolio.benchmark_trades,
      portfolio.benchmark_returns)

    return gtp_period_df
    ```

    </td>
    <td>

    ```python
    def get_gaintopain_ratio(self) -> pd.DataFrame:

    """..."""

    vals = list()

    for period in portfolio_helper.PERIODS:
           port_rets = portfolio_helper.filter_df_by_period(self.portfolio_returns, period)
           bench_rets =  portfolio_helper.filter_df_by_period(self.benchmark_returns, period)

    ...
    ```

    </td>
    </tr>
    </table>

    <br>

6. Naming among related model and view functions should be obvious; just different prefix if possible

    - Why? Eases SDK factory mapping and keeps code clean.

    <br>

    <table>
    <tr>
    <td> Good code :white_check_mark: </td> <td> Bad code :x: </td>
    </tr>
    <tr>
    <td>

    ```python
    # [fred_view.py]

    def display_yieldcurve(country: str):

          df = fred_model.get_yieldcurve(country)

          …

    # [fred_model.py]

    def get_yieldcurve(country: str) -> pd.Dataframe:

          …
    ```

    </td>
    <td>

    ```python
    # [fred_view.py]

    def display_bondscrv(country: str):

          df = fred_model.get_yieldcurve(country)

          …

    # [fred_model.py]

    def get_yldcurve(country: str) -> pd.Dataframe:

          …
    ```

    </td>
    </tr>
    </table>

    <br>

### File Specific Requirements

1. No data altering in the view file or controller file (view and model with same args)

    - Why? Consistency and good code structure. This also improves the SDK user experience. Thus follows that view and model files will have the same arguments (except for output options like raw, export, external_axes), since no data changes shall be done in the view file.

    <br>

2. Each model (get_) should almost always have its own view function (display_)

    - Why? To respect the principles laid out in Code Structure and the previous bullet point. If your code does not have this `get_` → `display_` map it’s likely that i. and/or ii. fail to hold.

        i. Data is processed in `_model` files and displayed in `_view` files

        ii. `_view` and `_model` files will have the same arguments (except for output options)

    <br>

### Coding Style

When in doubt, follow <https://www.python.org/dev/peps/pep-0008/>.

#### OpenBB Style Guide

The style guide is a reverse dictionary for argument names, where a brief definition is mapped to an OpenBB recommended argument name and type. When helpful a code snippet example is added below. Following this guide will help keep argument naming consistent and improve SDK users experience.

Style guide structure:

```python
<definition> : <argument_name (argument_type)> e.g. <examples>

def func(..., argument_name: argument_type = default, ...):
    ...
```

<br>

#### Flags

Show raw data : `raw` _(bool)_

```python
def display_data(..., raw: bool = False, ...):
    ...
    if raw:
        print_rich_table(...)
```

Sort in ascending order : `ascend` _(bool)_

```python
def display_data(..., sortby: str = "", ascend: bool = False, ...):
    ...
    if sortby:
        data = data.sort_values(by=sortby, ascend=ascend)
```

Show plot : `plot` _(bool)_

```python
def display_data(..., plot: bool = False, ...):
    ...
    if plot:
        ...
        fig.add_scatter(...)
```

<br>

#### Output format

Format to export data : `export` _(str), e.g. csv, json, xlsx_

```python
def display_data(..., export: str = "", ...):
    ...
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "func", data)
```

Whether to display plot or return figure _(False: display, True: return)_ : `external_axes` _(bool)_

```python
def display_data(..., external_axes: bool = False, ...):
    ...
    fig = OpenBBFigure()
    fig.add_scatter(...)
    return fig.show(external=external_axes)
```

Field by which to sort : `sortby` _(str), e.g. "Volume"_

```python
def display_data(..., sortby: str = "col", ...):
    ...
    if sortby:
        data = data.sort_values(by=sortby)
```

Maximum limit number of output items : `limit` _(int)_

```python
def display_data(..., limit = 10, ...):
    ...
    print_rich_table(
        data[:limit],
        ...
    )
```

<br>

#### Time-related

Date from which data is fetched (YYYY-MM-DD) : `start_date` _(str), e.g. 2022-01-01_

Date up to which data is fetched (YYYY-MM-DD) : `end_date` _(str), e.g. 2022-12-31_

Note: We want to accept dates in string because it is easier to deal from user standpoint. Inside the function you can convert it to datetime and check its validity. Please specify date format in docstring.

```python
def get_historical_data(..., start_date: str = "2022-01-01", end_date: str = "2022-12-31",):
    """
    ...
    Parameters
    ----------
    start_date: str
        Date from which data is fetched in format YYYY-MM-DD
    end_date: str
        Date up to which data is fetched in format YYYY-MM-DD
    ...
    """
    data = source_model.get_data(data_name, start_date, end_date, ...)
```

Year from which data is fetched (YYYY) : `start_year` _(str), e.g. 2022_

Year up to which data is fetched (YYYY) : `end_year` _(str), e.g. 2023_

```python
def get_historical_data(..., start_year: str = "2022", end_year str = "2023", ...):
    ...
    data = source_model.get_data(data_name, start_year, end_year, ...)
```

Interval for data observations : `interval` _(str), e.g. 60m, 90m, 1h_

```python
def get_prices(interval: str = "60m", ...):
    ...
    data = source.download(
        ...,
        interval=interval,
        ...
    )
```

Rolling window length : `window` _(int/str), e.g. 252, 252d_

```python
def get_rolling_sum(returns: pd.Series, window: str = "252d"):
    rolling_sum = returns.rolling(window=window).sum()
```

<br>

#### Data selection and manipulation

Search term used to query : `query` (str)

Maximum limit of search items/periods in data source: `limit` _(int)_

Note: please specify limit application in docstring

```python
def get_data_from_source(..., limit: int = 10, ...):
    """
    Parameters
    ----------
    ...
    limit: int
        Number of results to fetch from source
    ...
    """
    data = source.get_data(data_name, n_results=limit, ...)
```

Dictionary of input datasets : `datasets` _(Dict[str, pd.DataFrame])_

Note: Most occurrences are on the econometrics menu and might be refactored in near future

Input dataset : `data` _(pd.DataFrame)_

```python
def process_data(..., data: pd.DataFrame, ...):
    """
    ...
    Parameters
    ----------
    ...
    data : pd.DataFrame
        Dataframe of ...
    ...
    """
    col_data = pd.DataFrame(data["Col"])
```

Dataset name : `dataset_name` _(str)_

Input series : `data` _(pd.Series)_

Dependent variable series : `dependent_series` _(pd.Series)_

Independent variable series : `independent_series` _(pd.Series)_

```python
def get_econometric_test(dependent_series, independent_series, ...):
    ...
    dataset = pd.concat([dependent_series, independent_series], axis=1)
    result = econometric_test(dataset, ...)
```

Country name : `country` _(str), e.g. United States, Portugal_

Country initials or abbreviation : `country_code` _(str) e.g. US, PT, USA, POR_

Currency to convert data : `currency` _(str) e.g. EUR, USD_

<br>

#### Financial instrument characteristics

Instrument ticker, name or currency pair : `symbol` _(str), e.g. AAPL, ethereum, ETH, ETH-USD_

```python
def get_prices(symbol: str = "AAPL", ...):
    ...
    data = source.download(
        tickers=symbol,
        ...
    )
```

Instrument name: `name` _(str)_

Note: If a function has both name and symbol as parameter, we should distinguish them and call it name

List of instrument tickers, names or currency pairs : `symbols` _(List/List[str]), e.g. ["AAPL", "MSFT"]_

Base currency under ***BASE***-QUOTE → ***XXX***-YYY convention : `from_symbol` _(str), e.g. ETH in ETH-USD_

Quote currency under BASE-***QUOTE*** → XXX-***YYY*** convention : `to_symbol` _(str), e.g. USD in ETH-USD_

```python
def get_exchange_rate(from_symbol: str = "", to_symbol: str = "", ...):
    ...
    df = source.get_quotes(from_symbol, to_symbol, ...)
```

Instrument price : `price` _(float)_

Instrument implied volatility : `implied_volatility` _(float)_

Option strike price : `strike_price` _(float)_

Option days until expiration : `time_to_expiration` _(float/str)_

Risk free rate : `risk_free_rate` _(float)_

Options expiry date : `expiry` _(str)_

<br>

#### Naming Convention

- The name of the variables must be descriptive of what they stand for. I.e. `ticker` is descriptive, `aux` is not.
- Single character variables **must** be avoided. Except if they correspond to the iterator of a loop.

#### Docstrings

The docstring format used in **numpy**, an example is shown below:

```python
def command_foo(var1: str, var2: List[int], var3: bool = False) -> Tuple[int, pd.DataFrame]:
"""Small description

[Optional: Longer description]

Parameters
----------
var1 : str
    var1 description
var2 : List[int]
    var2 description
var3 : bool, optional
    var3 description

Returns
-------
foo : int
    returned foo description
pd.DataFrame
    dataframe returned
"""
```

#### Linters

The following linters are used by our codebase:

| Linter       | Description                       |
| ------------ | --------------------------------- |
| bandit       | security analyzer                 |
| black        | code formatter                    |
| codespell    | spelling checker                  |
| ruff         | a fast python linter              |
| mypy         | static typing checker             |
| pylint       | static code analysis              |
| markdownlint | markdown linter                   |

#### Command names

- The command name should be as short as possible.
- The command name should allow the user to know what the command refers to without needing to read description. (e.g. `earn`)

  - If this is not possible, then the command name should be an abbreviation of what the functionality corresponds to (e.g. `ycrv` for `yield curve`)

- The command name **should not** have the data source explicit

#### UI and UX

<img width="1676" alt="Screenshot 2022-10-26 at 12 17 19" src="https://user-images.githubusercontent.com/25267873/198012768-4cfecf7b-e961-4e55-a613-6648c0107b1e.png">

It is important to keep a coherent UI/UX throughout the terminal. These are the rules we must abide:

- There is 1 single empty line between user input and start of the command output.
- There is 1 single empty line between command output and the user input.
- The menu help has 1 empty line above text and 1 empty line below. Both still within the rectangular panel.
- From menu help rectangular panel there's no empty line below - this makes it more clear to the user that they are inside such menu.

## External API Keys

### Creating API key

OpenBB Terminal currently has over 100 different data sources. Most of these require an API key that allows access to some free tier features from the data provider, but also paid ones.

When a new API data source is added to the platform, it must be added through [credentials_model.py](/openbb_terminal/credentials_model.py) under the section that resonates the most with its functionality, from: `Data providers`, `Socials` or `Brokers`.

Example (a section from [credentials_model.py](/openbb_terminal/credentials_model.py)):

```python
# Data providers
API_DATABENTO_KEY = "REPLACE_ME"
API_KEY_ALPHAVANTAGE: str = "REPLACE_ME"
API_KEY_FINANCIALMODELINGPREP: str = "REPLACE_ME"

...

# Socials
API_GITHUB_KEY: str = "REPLACE_ME"
API_REDDIT_CLIENT_ID: str = "REPLACE_ME"
API_REDDIT_CLIENT_SECRET: str = "REPLACE_ME"

...

# Brokers or data providers with brokerage services
RH_USERNAME: str = "REPLACE_ME"
RH_PASSWORD: str = "REPLACE_ME"
DG_USERNAME: str = "REPLACE_ME"

...

```

### Setting and checking API key

One of the first steps once adding a new data source that requires an API key is to add that key to our [keys_controller.py](/openbb_terminal/keys_controller.py). This menu allows the user to set API keys and check their validity.

The following code allows to check the validity of the Polygon API key.

```python

def check_polygon_key(show_output: bool = False) -> str:
    """Check Polygon key

    Parameters
    ----------
    show_output: bool
        Display status string or not. By default, False.

    Returns
    -------
    str
        Status of key set
    """

    current_user = get_current_user()

    if current_user.credentials.API_POLYGON_KEY == "REPLACE_ME":
        logger.info("Polygon key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        r = request(
            "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2020-06-01/2020-06-17"
            f"?apiKey={current_user.credentials.API_POLYGON_KEY}"
        )
        if r.status_code in [403, 401]:
            logger.warning("Polygon key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED
        elif r.status_code == 200:
            logger.info("Polygon key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        else:
            logger.warning("Polygon key defined, test inconclusive")
            status = KeyStatus.DEFINED_TEST_INCONCLUSIVE

    if show_output:
        console.print(status.colorize())

    return str(status)
```

Note that there are usually 3 states:

- **defined, test passed**: The user has set their API key and it is valid.
- **defined, test failed**: The user has set their API key but it is not valid.
- **not defined**: The user has not defined any API key.

Note: Sometimes the user may have the correct API key but still not have access to a feature from that data source, and that may be because such feature required an API key of a higher level.

A function can then be created with the following format to allow the user to change its environment key directly from the terminal.

```python
def call_polygon(self, other_args: List[str]):
    """Process polygon command"""
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="polygon",
        description="Set Polygon API key.",
    )
    parser.add_argument(
        "-k",
        "--key",
        type=str,
        dest="key",
        help="key",
    )
    if not other_args:
        console.print("For your API Key, visit: https://polygon.io")
        return

    if other_args and "-" not in other_args[0][0]:
        other_args.insert(0, "-k")
    ns_parser = self.parse_simple_args(parser, other_args)
    if ns_parser:
        self.status_dict["polygon"] = keys_model.set_polygon_key(
            key=ns_parser.key, persist=True, show_output=True
        )
```

# ADVANCED

## Important functions and classes

### Base controller class

This `BaseController` class is inherited by all controllers on the terminal.

This class contains both important variables and methods that are common across all terminal controllers.

**CHOICES_COMMON**: List of common commands across all controllers

- `cls`: clear screen
- `home`: go back to the main root
- `about`: allows to open our documentation directly on the menu or command
- `h`, `?` and `help`: display the help menu the user is in
- `q`, `quit` and `..`: go back to one menu above
- `exit`: exit the platform
- `r` and `reset`: reset the platform (reading code and settings again but going into the same state)
- `support`: create a support request ticket

All of these variables have a `call_FUNCTION` associated with them.

Worthy methods to mention are:

- `load_class`: Checks for an existing instance of the controller before creating a new one to speed up access to that menu.
- `custom_reset`: Should be used by controllers that rely on a state variable - meant to be overridden. They should add the commands necessary to have the same data loaded.
- `print_help`: Meant to be overridden by each controller
- `parse_input`: Processes the string the user inputs into a list of actionable commands
- `switch`: Acts upon the command action received
- `parse_known_args_and_warn`: Parses the command with the `-` and `--` flags and variables. Some built-in flags are:
  - `export_allowed`: Which can be set to `_NO_EXPORT_`, `_EXPORT_ONLY_RAW_DATA_ALLOWED_`, `_EXPORT_ONLY_FIGURES_ALLOWED_` and `_EXPORT_BOTH_RAW_DATA_AND_FIGURES_`
  - `raw`: Displaying the data raw
  - `limit`: Number of rows to display
- `menu`: Most important method. When a menu is executed, the way to call it is through `stocks_menu.menu()`

## Default Data Sources

The document [data_sources_default.json](/data_sources_default.json) contains all data sources that the terminal has access to and specifies the data source utilized by default for each command.

The convention is as follows:

```python
{
    "stocks": {
        "search": ["FinanceDatabase"],
        "quote": ["YahooFinance"],
        "candle": [],
        "load": [
            "YahooFinance",
            "AlphaVantage",
            "Polygon",
            "EODHD"
        ],
        "options": {
            "unu": ["FDScanner"],
            "calc": [],
            "screen": {
                "view": ["Syncretism"],
                "set": [],
                "scr": ["Syncretism"]
            },
             "load": [
                "YahooFinance",
                "Tradier",
                "Nasdaq"
            ],
            "exp": [
                "YahooFinance",
                "Tradier",
                "Nasdaq"
            ],
            ...
```

The way to interpret this file is by following the path to a data source, e.g.

- `stocks/search` relies on `FinanceDatabase`
- `stocks/candle` does not rely on any data source. This means that it relies on data that has been loaded before.
- `stocks/load` relies on `YahooFinance`, `AlphaVantage`, `Polygon` or `EODHD`.
  - **The order is important as the first data source is the one utilized by default.**
- `stoks/options/unu` relies on `FDScanner`.
- `stocks/options/exp` relies on `YahooFinance` by default but `Tradier` and `Nasdaq` sources are allowed.

### Export Data

In the `_view.py` files it is common having at the end of each function `export_data` being called. This typically looks like:

```python
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "contracts",
        df_contracts,
        figure=fig_contracts,
    )
```

Let's go into each of these arguments:

- `export` corresponds to the type of file we are exporting.
  - If the user doesn't has anything selected, then this function doesn't do anything.
  - The user can export multiple files and even name the files.
  - The allowed type of files `json,csv,xlsx` for raw data and `jpg,pdf,png,svg` for figures depends on the `export_allowed` variable defined in `parse_known_args_and_warn`.
- `os.path.dirname(os.path.abspath(__file__))` corresponds to the directory path
  - This is important when `export folder` selected is the default because the data gets stored based on where it is called.
  - If this is called from a `common` folder, we can use `os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks")` insteaad
- `"contracts"` corresponds to the name of the exported file (+ unique datetime) if the user doesn't provide one
- `df_contracts` corresponds to the dataframe with data.
- `figure=fig_contracts` corresponds to the figure to be exported as an image or pdf.

If `export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES` in `parse_known_args_and_warn`, valid examples are:

- `cmd --export csv`
- `cmd --export csv,png,jpg`
- `cmd --export mydata.csv`
- `cmd --export mydata.txt,alsomydata.csv,alsoalsomydata.png`

Note that these files are saved on a location based on the environment variable: `EXPORT_FOLDER_PATH`. Which can be set in `settings/export`.

The default location is the `exports` folder and the data will be stored with the same organization of the terminal. But, if the user specifies the name of the file, then that will be dropped onto the folder as is with the datetime attached.

### Queue and pipeline

The variable `self.queue` contains a list of all actions to be run on the platform. That is the reason why this variable is always passed as an argument to a new controller class and received back.

```python
  self.queue = self.load_class(
      DarkPoolShortsController, self.ticker, self.start, self.stock, self.queue
  )
```

Example:

If a user is in the root of the terminal and runs:

```shell
stocks/load AAPL/dps/psi -l 90
```

The queue created becomes:
`self.queue = ["stocks", "load AAPL", "dps", "psi -l 90"]`

And the user goes into the `stocks` menu and runs `load AAPL`. Then the queue is updated to
`self.queue = ["dps", "psi -l 90"]`

At that point the user goes into the `dps` menu and runs the command `psi` with the argument `-l 90` therefore displaying price vs short interest of the past 90 days.

### Auto Completer

In order to help users with a powerful autocomplete, we have implemented our own (which can be found [here](/openbb_terminal/custom_prompt_toolkit.py)).

The list of options for each command is automatically generated, if you're interested take a look at its implementation [here](/openbb_terminal/core/completer/choices.py).

To leverage this functionality, you need to add the following line to the top of the desired controller:

```python
CHOICES_GENERATION = True
```

Here's an example of how to use it, on the [`forex` controller](/openbb_terminal/forex/forex_controller.py):

```python
class ForexController(BaseController):
    """Forex Controller class."""

    CHOICES_COMMANDS = [
        "fwd",
        "candle",
        "load",
        "quote",
    ]
    CHOICES_MENUS = [
        "forecast",
        "qa",
        "oanda",
        "ta",
    ]
    RESOLUTION = ["i", "d", "w", "m"]

    PATH = "/forex/"
    FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Construct Data."""
        super().__init__(queue)

        self.fx_pair = ""
        self.from_symbol = ""
        self.to_symbol = ""
        self.source = get_ordered_list_sources(f"{self.PATH}load")[0]
        self.data = pd.DataFrame()

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            choices["load"].update({c: {} for c in FX_TICKERS})

            self.completer = NestedCompleter.from_nested_dict(choices)


    ...
```

In case the user is interested in a **DYNAMIC** list of options which changes based on user's state, then a class method must be defined.

The example below shows the an excerpt from `update_runtime_choices` method in the [`options` controller](/openbb_terminal/stocks/options/options_controller.py).

```python
def update_runtime_choices(self):
        """Update runtime choices"""
        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            if not self.chain.empty:
                strike = set(self.chain["strike"])

                self.choices["hist"]["--strike"] = {str(c): {} for c in strike}
                self.choices["grhist"]["-s"] = "--strike"
                self.choices["grhist"]["--strike"] = {str(c): {} for c in strike}
                self.choices["grhist"]["-s"] = "--strike"
                self.choices["binom"]["--strike"] = {str(c): {} for c in strike}
                self.choices["binom"]["-s"] = "--strike"
```

This method should only be called when the user's state changes leads to the auto-complete not being accurate.

In this case, this method is called as soon as the user successfully loads a new ticker since the options expiry dates vary based on the ticker. Note that the completer is recreated from it.

### Logging

A logging system is used to help tracking errors inside the OpenBBTerminal.

This is storing every logged message inside the following location :

`$HOME/OpenBBUserData/logs`

Where $HOME is the user home directory, for instance:

- `C:\Users\foo` if your are in Windows and your name is foo
- `/home/bar/` if you are is macOS or Linux and your name is bar

The user can override this location using the settings key `OPENBB_USER_DATA_DIRECTORY`.

If you want to log a particular message inside a function you can do like so:

```python
import logging

logger = logging.getLogger(__name__)

def your_function() -> pd.DataFrame:
    logger.info("Some log message with the level INFO")
    logger.warning("Some log message with the level WARNING")
    logger.fatal("Some log message with the level FATAL")
```

You can also use the decorator `@log_start_end` to automatically record a message every time a function starts and ends, like this:

```python
import logging

from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)

@log_start_end(log=logger)
def your_function() -> pd.DataFrame:
    pass
```

> Note: if you don't want your logs to be collected, you can set the `LOG_COLLECT` user preference to `False`.
> Disclaimer: all the user paths, names, IPs, credentials and other sensitive information are anonymized, [take a look at how we do it](/openbb_terminal/core/log/generation/formatter_with_exceptions.py).

### Internationalization

WORK IN PROGRESS - The menu can be internationalised BUT we do not support yet help commands`-h` internationalization.

In order to add support for a new language, the best approach is to:

1. Copy-paste `i18n/en.yml`
2. Rename that file to a short version of language you are translating to, e.g. `i18n/pt.yml` for portuguese
3. Then just update the text on the right. E.g.

```text
  stocks/NEWS: latest news of the company
```

becomes

```text
  stocks/NEWS: mais recentes notícias da empresa
```

Note: To speed up translation, the team developed a [script](/i18n/help_translation.ipynb) that uses Google translator API to help translating the entire `en.yml` document to the language of choice. Then the output still needs to be reviewed, but this can be an useful bootstrap.

This is the convention in use for creating a new key/value pair:

- `stocks/search` - Under `stocks` context, short command `search` description on the `help menu`
- `stocks/SEARCH` - Under `stocks` context, long command `search` description, when `search -h`
- `stocks/SEARCH_query` - Under `stocks` context, `query` description when inquiring about `search` command with `search -h`
- `stocks/_ticker` - Under `stocks` context, `_ticker` is used as a key of a parameter, and the displayed parameter description is given as value
- `crypto/dd/_tokenomics_` - Under `crypto` context and under `dd` menu, `_tokenomics_` is used as a key of an additional information, and the displayed information is given as value

## Write Code and Commit

At this stage it is assumed that you have already forked the project and are ready to start working.

### Pre Commit Hooks

Git hook scripts are useful for identifying simple issues before submission to code review. We run our hooks on every
commit to automatically point out issues in code such as missing semicolons, trailing whitespace, and debug statements.
By pointing these issues out before code review, this allows a code reviewer to focus on the architecture of a change
while not wasting time with trivial style nitpicks.

Install the pre-commit hooks by running: `pre-commit install`.

### Coding

Although the Coding Guidelines section has been already explained, it is worth mentioning that if you want to be faster
at developing a new feature, you may implement it first on a `jupyter notebook` and then carry it across to the
terminal. This is mostly useful when the feature relies on scraping data from a website, or implementing a Neural
Network model.

### Git Process

1. Create your Feature Branch, e.g. `git checkout -b feature/AmazingFeature`
2. Check the files you have touched using `git status`
3. Stage the files you want to commit, e.g.
   `git add openbb_terminal/stocks/stocks_controller.py openbb_terminal/stocks/stocks_helper.py`.
   Note: **DON'T** add `config_terminal.py` or `.env` files with personal information, or even `feature_flags.py` which is user-dependent.
4. Write a concise commit message under 50 characters, e.g. `git commit -m "meaningful commit message"`. If your PR
   solves an issue raised by a user, you may specify such issue by adding #ISSUE_NUMBER to the commit message, so that
   these get linked. Note: If you installed pre-commit hooks and one of the formatters re-formats your code, you'll need
   to go back to step 3 to add these.

### Branch Naming Conventions

The accepted branch naming conventions are:

- `feature/feature-name`
- `hotfix/hotfix-name`
- `release/2.1.0` or `release/2.1.0rc0`.

All `feature/feature-name` related branches can only have PRs pointing to `develop` branch. `hotfix/hotfix-name` and `release/2.1.0` or `release/2.1.0rc0` branches can only have PRs pointing to `main` branch.

## Installers

When implementing a new feature or fixing something within the codebase, it is necessary to ensure that it is working
appropriately on the terminal. However, it is equally as important to ensure that new features or fixes work on the
installer terminal too. This is because a large portion of users utilize the installer to use OpenBB Terminal.
More information on how to build an installer can be found [here](build/README.md).
