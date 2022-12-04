# CONTRIBUTING

First off, thanks for taking the time to contribute (or at least read the Contributing Guidelines)! 🚀

The following is a set of guidelines for contributing to OpenBB Terminal. These are mostly guidelines, not rules.
Use your best judgment, and feel free to propose changes to this document in a pull request.

- [CONTRIBUTING](#contributing)
- [BASIC](#basic)
  - [Adding a new command](#adding-a-new-command)
    - [Select Feature](#select-feature)
    - [Model](#model)
    - [View](#view)
    - [Controller](#controller)
    - [Add SDK endpoint](#add-sdk-endpoint)
    - [Add Documentation](#add-documentation)
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
  - [Add a Test](#add-a-test)
  - [Installers](#installers)

# BASIC

## Adding a new command

Before implementing a new command we highly recommend that you go through [Understand Code Structure](#understand-code-structure) and [Follow Coding Guidelines](#follow-coding-guidelines). This will allow you to get your PR merged faster and keep consistency of our code base.

In the next sections we describe the process to add a new command. `shorted` command from category `dark_pool_shorts` and context `stocks` will be used as
example. Since this command uses data from Yahoo Finance, a `yahoofinance_view.py` and a `yahoofinance_model.py` files
will be implemented.

### Select Feature

- Pick a feature you want to implement or a bug you want to fix from [our issues](https://github.com/OpenBB-finance/OpenBBTerminal/issues).
- Feel free to discuss what you'll be working on either directly on [the issue](https://github.com/OpenBB-finance/OpenBBTerminal/issues) or on [our Discord](www.openbb.co/discord).
  - This ensures someone from the team can help you and there isn't duplicated work.

### Model

1. Create a file with the source of data as the name followed by `_model` if it doesn't exist, e.g. `yahoofinance_model`
2. Add the documentation header
3. Do the necessary imports to get the data
4. Define a function starting with `get_`
5. In that function:
   1. Use typing hints
   2. Write a descriptive description where at the end the source is specified
   3. Utilizing a third party API, get and return the data.

```python
""" Yahoo Finance Model """
__docformat__ = "numpy"

import logging

import pandas as pd
import requests

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)

@log_start_end(log=logger)
def get_most_shorted() -> pd.DataFrame:
    """Get most shorted stock screener [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most Shorted Stocks
    """
    url = "https://finance.yahoo.com/screener/predefined/most_shorted_stocks"

    data = pd.read_html(
        requests.get(url, headers={"User-Agent": get_user_agent()}).text
    )[0]
    data = data.iloc[:, :-1]
    return data
```

Note:

1. As explained before, it is possible that this file needs to be created under `common/` directory rather than
   `stocks/`, which means that when that happens this function should be done in a generic way, i.e. not mentioning stocks
   or a specific context.
2. If the model require an API key, make sure to handle the error and output relevant message.

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
    response = requests.get(
        f"https://finnhub.io/api/v1/calendar/economic?token={cfg.API_FINNHUB_KEY}"
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

### View

1. Create a file with the source of data as the name followed by `_view` if it doesn't exist, e.g. `yahoofinance_view`
2. Add the documentation header
3. Do the necessary imports to display the data. One of these is the `_model` associated with this `_view`. I.e. from same data source.
4. Define a function starting with `display_`
5. In this function:
   - Use typing hints
   - Write a descriptive description where at the end the source is specified
   - Get the data from the `_model` and parse it to be output in a more meaningful way.
   - Ensure that the data that comes through is reasonable, i.e. at least that we aren't displaying an empty dataframe.
   - Do not degrade the main data dataframe coming from model if there's an export flag. This is so that the export can
     have all the data rather than the short amount of information we may show to the user. Thus, in order to do so
     `df_data = df.copy()` can be useful as if you change `df_data`, `df` remains intact.
6. If the source requires an API Key or some sort of tokens, add `check_api_key` decorator on that specific view. This will throw a warning if users forget to set their API Keys
7. Finally, call `export_data` where the variables are export variable, current filename, command name, and dataframe.

```python
""" Yahoo Finance View """
__docformat__ = "numpy"

import logging
import os

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import export_data, print_rich_table
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.dark_pool_shorts import yahoofinance_model

logger = logging.getLogger(__name__)

@log_start_end(log=logger)
def display_most_shorted(limit: int = 10, export: str = ""):
    """Display most shorted stocks screener. [Source: Yahoo Finance]

    Parameters
    ----------
    limit: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = yahoofinance_model.get_most_shorted().head(limit)
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    else:
        print_rich_table(
            df, headers=list(df.columns), show_index=False, title="Most Shorted Stocks"
        )

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "shorted",
        df,
    )

```

Note: As explained before, it is possible that this file needs to be created under `common/` directory rather than
`stocks/`, which means that when that happens this function should be done in a generic way, i.e. not mentioning stocks
or a specific context. The arguments will need to be parsed by `stocks_controller,py` and the other controller this
function shares the data output with.

### Controller

1. Import `_view` associated with command we want to allow user to select.
2. Add command name to variable `CHOICES` from `DarkPoolShortsController` class.
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

5. Add command description to file `i18n/en.yml`. Use the path and command name as key, e.g. `stocks/dps/shorted` and the value as description. Please fill in other languages if this is something that you know.

6. Add a method to `DarkPoolShortsController` class with name: `call_` followed by command name.
   - This method must start defining a parser with arguments `add_help=False` and
     `formatter_class=argparse.ArgumentDefaultsHelpFormatter`. In addition `prog` must have the same name as the command,
     and `description` should be self-explanatory ending with a mention of the data source.
   - Add parser arguments after defining parser. One important argument to add is the export capability. All commands should be able to export data.
   - If there is a single or even a main argument, a block of code must be used to insert a fake argument on the list of
     args provided by the user. This makes the terminal usage being faster.

      ```python
      if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
      ```

   - Parse known args from list of arguments and values provided by the user.
   - Call the function contained in a `_view.py` file with the arguments parsed by argparse.

```python
def call_shorted(self, other_args: List[str]):
        """Process shorted command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="shorted",
            description="Print up to 25 top ticker most shorted. [Source: Yahoo Finance]",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser,
            other_args,
            limit=10,
            export=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
          yahoofinance_view.display_most_shorted(
              num_stocks=ns_parser.num,
              export=ns_parser.export,
          )
```

If a new menu is being added the code looks like this:

```python
@log_start_end(log=logger)
def call_dps(self, _):
    """Process dps command"""
    from openbb_terminal.stocks.dark_pool_shorts.dps_controller import (
        DarkPoolShortsController,
    )

    self.queue = self.load_class(
        DarkPoolShortsController, self.ticker, self.start, self.stock, self.queue
    )
```

The **import only occurs inside this menu call**, this is so that the loading time only happens here and not at the terminal startup. This is to avoid slow loading times for users that are not interested in `stocks/dps` menu.

In addition, note the `self.load_class` which allows to not create a new DarkPoolShortsController instance but re-load the previous created one. Unless the arguments `self.ticker, self.start, self.stock` have changed since. The `self.queue` list of commands is passed around as it contains the commands that the terminal must perform.

### Add SDK endpoint

In order to add a command to the SDK, follow these steps:

1. Go to the `sdk.py` file and scroll to the `functions` dictionary, it should look like this:

    ```python
    functions = {
        "stocks.get_news": {
            "model": "openbb_terminal.common.newsapi_model.get_news",
        },
        "stocks.load": {
            "model": "openbb_terminal.stocks.stocks_helper.load",
        },
        "stocks.candle": {
            "model": "openbb_terminal.stocks.stocks_helper.load",
            "view": "openbb_terminal.stocks.stocks_helper.display_candle",
        },

    ...
    ```

2. Add a new key to the dictionary, which corresponds to the way the added command shall be accessed from the sdk.
This is called the `virtual path`. In this case it should be `stocks.dps.shorted`.
3. Now it is time to add the value to the key. This key shall be another dictionary with a `model` key and possibly a
`view` key.
   1. The model keys value should be the path from project root to the new commands model function as a string. This
   case it is `openbb_terminal.stocks.dark_pool_shorts.yahoofinance_model.get_most_shorted`.
   2. If and **only if** the view function of the command **displays a chart**, then the `view` key and its value is
   the view functions path from the project root as a string. In this example the view function of the only prints a
   table and thus this step can be ignored.
4. Done!!! The final new dictionary looks like this after the added example:

    ```python
    functions = {
        ...

        "stocks.dps.shorted": {
            "model": "openbb_terminal.stocks.dark_pool_shorts.yahoofinance_model.get_most_shorted",
        },

        ...
    ```

### Add Documentation

To check whether documentation is added correctly follow [Hugo Server instructions](/website/README.md).

This is the structure that the documentation follows:

```txt
website/content/_index.md
               /stocks/_index.md
                      /load/_index.md
                      /candle/_index.md
                      /discovery/_index.md
                                /ipo/_index.md
                                    /...
                                /...
                      /...
               /cryptocurrency/_index.md
                              /chart/_index.md
                              /defi/_index.md
                                   /borrow/_index.md
                                   /...
                              /...
               /...
               /common/_index.md
                      /technical_analysis/_index.md
                                         /ema/_index.md
                                         /...
                      /...
```

Note that the `common` folder holds features that are common across contexts, e.g. `technical analysis` can be performed on both `stocks` or `crytpo`.

To add a new command, there are two main actions that need to be done:

1. Create a directory with the name of the command and a `_index.md` file within. Examples:

   - When adding `ipo`, since this command belongs to context `stocks` and category `discovery`, we added a `ipo` folder with a `_index.md` file within to `website/content/stocks/discovery`.

   - When adding `candle`, since this command belongs to context `stocks`, we added a `candle` folder with a `_index.md` file within to `website/content/stocks/`.

2. The `_index.md` file should have the output of the `command -h` followed by a screenshot example of what the user can expect. Note that you can now drag and drop the images while editing the readme file on the remote web version of your PR branch. Github will create a link for it with format (<https://user-images.githubusercontent.com/***/***.file_format>).

    Example:

    ---

    ```shell
    usage: ipo [--past PAST_DAYS] [--future FUTURE_DAYS]
    ```

    Past and future IPOs. [Source: <https://finnhub.io>]

    - --past : Number of past days to look for IPOs. Default 0.
    - --future : Number of future days to look for IPOs. Default 10.

    <IMAGE HERE - Use drag and drop hint mentioned above>

    ---

3. Update the Navigation bar to match the content you've added. This is done by adding 2 lines of code to `website/data/menu/`, i.e. a `name` and a `ref`. Example:

    ```python
    ---
    main:
      - name: stocks
        ref: "/stocks"
        sub:
          - name: load
            ref: "/stocks/load"
          - name: candle
            ref: "/stocks/candle"
          - name: discovery
            ref: "/stocks/discovery"
            sub:
              - name: ipo
                ref: "/stocks/discovery/ipo"
              - name: map
                ref: "/stocks/discovery/map"
    ```

### Open a Pull Request

Once you're happy with what you have, push your branch to remote. E.g. `git push origin feature/AmazingFeature`
A user may create a **Draft Pull Request** when he/she wants to discuss implementation with the team.

The team will then assign your PR one of the following labels:

| Label name     | Description                         | Example                                        |
| -------------- | ----------------------------------- | ---------------------------------------------- |
| `feat XS`      | Extra small feature                 | Add a preset                                   |
| `feat S`       | Small T-Shirt size Feature          | New single command added                       |
| `feat M`       | Medium T-Shirt size feature         | Multiple commands added from same data source  |
| `feat L`       | Large T-Shirt size Feature          | New category added under context               |
| `feat XL`      | Extra Large feature                 | New context added                              |
| `enhancement`  | Enhancement                         | Add new parameter to existing command          |
| `bug`          | Fix a bug                           | Fixes terminal crashing or warning message     |
| `build`        | Build-related work                  | Fix a github action that is breaking the build |
| `tests`        | Test-related work                   | Add/improve tests                              |
| `docs`         | Improvements on documentation       | Add/improve documentation                      |
| `refactor`     | Refactor code                       | Changing argparse location                     |
| `docker`       | Docker-related work                 | Add/improve docker                             |
| `help wanted`  | Extra attention is needed           | When a contributor needs help                  |
| `do not merge` | Label to prevent pull request merge | When PR is not ready to be merged just yet     |

### Review Process

As soon as the Pull Request is opened, our repository has a specific set of github actions that will not only run
linters on the branch just pushed, but also run pytest on it. This allows for another layer of safety on the code developed.

In addition, our team is known for performing `diligent` code reviews. This not only allows us to reduce the amount of
iterations on that code and have it to be more future proof, but also allows the developer to learn/improve his coding skills.

Often in the past the reviewers have suggested better coding practices, e.g. using `1_000_000` instead of `1000000` for
better visibility, or suggesting a speed optimization improvement.

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

4. Consistent and clear argument naming; not `symbol` in _view and then `ticker` in `_file` -> ticker everywhere; the name should be descriptive of what information it hold (see Style Guide section below)

    - Why? You can quickly understand what the input it should be; example: tickers and stock names are fundamentally different, but they’re both strings so they should be named accordingly.

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
           port_rets = portfolio_helper.filter_df_by_period(self.returns, period)
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

        i. Data is processed in _model files and displayed in `_view` files

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

Show raw data : `raw` *(bool)*

```python
def display_data(..., raw: bool = False, ...):
    ...
    if raw:
        print_rich_table(...)
```

Sort in ascending order : `ascend` *(bool)*

```python
def display_data(..., sortby: str = "", ascend: bool = False, ...):
    ...
    if sortby:
        data = data.sort_values(by=sortby, ascend=ascend)
```

Show plot : `plot` *(bool)*

```python
def display_data(..., plot: bool = False, ...):
    ...
    if plot:
        ...
        ax.plot(...)
```

<br>

#### Output format

Format to export data : `export` *(str), e.g. csv, json, xlsx*

```python
def display_data(..., export: str = "", ...):
    ...
    export_data(export, os.path.dirname(os.path.abspath(__file__)), "func", data)
```

List of external axes to include in a plot : `external_axes` *(Optional[List[plt.Axes]])*

```python
def display_data(..., external_axes: Optional[List[plt.Axes]] = None, ...):
    ...
    if external_axes is None:
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        ax = external_axes[0]
    ax.plot(...)
```

Field by which to sort : `sortby` *(str), e.g. "Volume"*

```python
def display_data(..., sortby: str = "col", ...):
    ...
    if sortby:
        data = data.sort_values(by=sortby)
```

Maximum limit number of output items : `limit` *(int)*

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

Date from which data is fetched (YYYY-MM-DD) : `start_date` *(str), e.g. 2022-01-01*

Date up to which data is fetched (YYYY-MM-DD) : `end_date` *(str), e.g. 2022-12-31*

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

Year from which data is fetched (YYYY) : `start_year` *(str), e.g. 2022*

Year up to which data is fetched (YYYY) : `end_year` *(str), e.g. 2023*

```python
def get_historical_data(..., start_year: str = "2022", end_year str = "2023", ...):
    ...
    data = source_model.get_data(data_name, start_year, end_year, ...)
```

Interval for data observations : `interval` *(str), e.g. 60m, 90m, 1h*

```python
def get_prices(interval: str = "60m", ...):
    ...
    data = source.download(
        ...,
        interval=interval,
        ...
    )
```

Rolling window length : `window` *(int/str), e.g. 252, 252d*

```python
def get_rolling_sum(returns: pd.Series, window: str = "252d"):
    rolling_sum = returns.rolling(window=window).sum()
```

<br>

#### Data selection and manipulation

Search term used to query : `query` (str)

Maximum limit of search items/periods in data source: `limit` *(int)*

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

Dictionary of input datasets : `datasets` *(Dict[str, pd.DataFrame])*

Note: Most occurrences are on the econometrics menu and might be refactored in near future

Input dataset : `data` *(pd.DataFrame)*

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

Dataset name : `dataset_name` *(str)*

Input series : `data` *(pd.Series)*

Dependent variable series : `dependent_series` *(pd.Series)*

Independent variable series : `independent_series` *(pd.Series)*

```python
def get_econometric_test(dependent_series, independent_series, ...):
    ...
    dataset = pd.concat([dependent_series, independent_series], axis=1)
    result = econometric_test(dataset, ...)
```

Country name : `country` *(str), e.g. United States, Portugal*

Country initials or abbreviation : `country_code` *(str) e.g. US, PT, USA, POR*

Currency to convert data : `currency` *(str) e.g. EUR, USD*

<br>

#### Financial instrument characteristics

Instrument ticker, name or currency pair : `symbol` *(str), e.g. AAPL, ethereum, ETH, ETH-USD*

```python
def get_prices(symbol: str = "AAPL", ...):
    ...
    data = source.download(
        tickers=symbol,
        ...
    )
```

Instrument name: `name` *(str)*

Note: If a function has both name and symbol as parameter, we should distinguish them and call it name

List of instrument tickers, names or currency pairs : `symbols` *(List/List[str]), e.g. ["AAPL", "MSFT"]*

Base currency under ***BASE***-QUOTE → ***XXX***-YYY convention : `from_symbol` *(str), e.g. ETH in ETH-USD*

Quote currency under BASE-***QUOTE*** → XXX-***YYY*** convention : `to_symbol` *(str), e.g. USD in ETH-USD*

```python
def get_exchange_rate(from_symbol: str = "", to_symbol: str = "", ...):
    ...
    df = source.get_quotes(from_symbol, to_symbol, ...)
```

Instrument price : `price` *(float)*

Instrument implied volatility : `implied_volatility` *(float)*

Option strike price : `strike_price` *(float)*

Option days until expiration : `time_to_expiration` *(float/str)*

Risk free rate : `risk_free_rate` *(float)*

Options expiry date : `expiry` *(str)*

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
| flake8       | style guide enforcer              |
| mypy         | static typing checker             |
| pyupgrade    | upgrade syntax for newer versions |
| safety       | checks security vulnerabilities   |
| pylint       | bug and quality checker           |
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

When a new API data source is added to the platform, it must be added through [config_terminal.py](/openbb_terminal/config_terminal.py). E.g.

```python
# https://messari.io/
API_MESSARI_KEY = os.getenv("OPENBB_API_MESSARI_KEY") or "REPLACE_ME"
```

Note that a `OPENBB_` is added so that the user knows that that environment variable is used by our terminal.

### Setting and checking API key

One of the first steps once adding a new data source that requires an API key is to add that key to our [keys_controller.py](/openbb_terminal/keys_controller.py). This menu allows the user to set API keys and check their validity.

The following code allows to check the validity of the IEX Cloud API key.

```python
def check_iex_key(show_output: bool = False) -> str:
    """Check IEX Cloud key

    Parameters
    ----------
        show_output: bool
            Display status string or not.

    Returns
    -------
    status: str

    """

    if cfg.API_IEX_TOKEN == "REPLACE_ME":  # nosec
        logger.info("IEX Cloud key not defined")
        status = KeyStatus.NOT_DEFINED
    else:
        try:
            pyEX.Client(api_token=cfg.API_IEX_TOKEN, version="v1").quote(symbol="AAPL")
            logger.info("IEX Cloud key defined, test passed")
            status = KeyStatus.DEFINED_TEST_PASSED
        except Exception as _:  # noqa: F841
            logger.warning("IEX Cloud key defined, test failed")
            status = KeyStatus.DEFINED_TEST_FAILED

    if show_output:
        console.print(status.colorize() + "\n")

    return status
```

Note that there are usually 3 states:

- **defined, test passed**: The user has set their API key and it is valid.
- **defined, test failed**: The user has set their API key but it is not valid.
- **not defined**: The user has not defined any API key.

Note: Sometimes the user may have the correct API key but still not have access to a feature from that data source, and that may be because such feature required an API key of a higher level.

A function can then be created with the following format to allow the user to change its environment key directly from the terminal.

```python
@log_start_end(log=logger)
def call_iex(self, other_args: List[str]):
    """Process iex command"""
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="iex",
        description="Set IEX Cloud API key.",
    )
    parser.add_argument(
        "-k",
        "--key",
        type=str,
        dest="key",
        help="key",
    )
    if not other_args:
        console.print("For your API Key, visit: https://iexcloud.io\n")
        return
    if other_args and "-" not in other_args[0][0]:
        other_args.insert(0, "-k")
    ns_parser = parse_simple_args(parser, other_args)
    if ns_parser:
        self.status_dict["iex"] = keys_model.set_iex_key(
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
            "IEXCloud",
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
- `stocks/load` relies on `YahooFinance`, `IEXCloud`, `AlphaVantage`, `Polygon` or `EODHD`.
  - **The order is important as the first data source is the one utilized by default.**
- `stoks/options/unu` relies on `FDScanner`.
- `stocks/options/exp` relies on `YahooFinance` by default but `Tradier` and `Nasdaq` sources are allowed.

### Export Data

In the `_view.py` files it is common having at the end of each function `export_data` being called. This tipycally looks like:

```python
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "contracts",
        df_contracts
    )
```

Let's go into each of these arguments:

- `export` corresponds to the type of file we are exporting.
  - If the user doesn't has anything selected, then this function doesn't do anything.
  - The user can export multiple files and even name the files.
  - The allowed type of files `json,csv,xlsx` for raw data and `jpg,png,svg` for figures depends on the `export_allowed` variable defined in `parse_known_args_and_warn`.
- `os.path.dirname(os.path.abspath(__file__))` corresponds to the directory path
  - This is important when `export folder` selected is the default because the data gets stored based on where it is called.
  - If this is called from a `common` folder, we can use `os.path.dirname(os.path.abspath(__file__)).replace("common", "stocks")` insteaad
- `"contracts"` corresponds to the name of the exported file (+ unique datetime) if the user doesn't provide one
- `df_contracts` corresponds to the dataframe with data. Although we don't call this function with the figure reference, because it is open, we can use `plt.savefig` to achieve that.

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

This **STATIC** list of options is meant to be defined on the `__init__` method of a class as follows.

```python
if session and obbff.USE_PROMPT_TOOLKIT:
  self.choices: dict = {c: {} for c in self.controller_choices}
  self.choices["overview"] = {
     "--type": {c: None for c in self.overview_options},
     "-t": "--type",
  }
  self.choices["futures"] = {
     "--commodity": {c: None for c in self.futures_commodities},
     "-c": "--commodity",
     "--sortby": {c: None for c in self.wsj_sortby_cols_dict.keys()},
     "-s": "--sortby",
     "--reverse": {},
     "-r": "--reverse",
  }
  self.choices["map"] = {
     "--period": {c: None for c in self.map_period_list},
     "-p": "--period",
     "--type": {c: None for c in self.map_filter_list},
     "-t": "--type",
  }
  self.completer = NestedCompleter.from_nested_dict(self.choices)
```

Important things to note:

- `self.choices: dict = {c: {} for c in self.controller_choices}`: this allows users to have autocomplete on the command that they are allowed to select in each menu
- `self.choices["overview"]`: this corresponds to the list of choices that the user is allowed to select after specifying `$ overview`
- `"--commodity": {c: None for c in self.futures_commodities}`: this allows the user to select several commodity values after `--commodity` flag
- `"-c": "--commodity"`: this is interpreted as `-c` having the same effect as `--commodity`
- `"--reverse": {}`: corresponds to a boolean flag (does not expect any value after)
- `"--start": None`: corresponds to a flag where the values allowed are not easily discrete due to vast range
- `self.completer = NestedCompleter.from_nested_dict(self.choices)`: from the choices create our custom completer

In case the user is interested in a **DYNAMIC** list of options which changes based on user's state, then a class method must be defined.

The example below shows the `update_runtime_choices` method being defined in the options controller.

```python
def update_runtime_choices(self):
    """Update runtime choices"""
    if self.expiry_dates and session and obbff.USE_PROMPT_TOOLKIT:
        self.choices["exp"] = {str(c): {} for c in range(len(self.expiry_dates))}
        self.choices["exp"]["-d"] = {c: {} for c in self.expiry_dates + [""]}

        self.completer = NestedCompleter.from_nested_dict(self.choices)
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

Although the Coding Guidelines section has been already explained. It is worth mentioning that if you want to be faster
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

## Add a Test

Unit tests minimize errors in code and quickly find errors when they do arise. Integration tests are standard usage examples, which are also used to identify errors.

A thorough introduction on the usage of unit tests and integration tests in OpenBBTerminal can be found on the following page respectively:

[Unit Test README](tests/README.md)

[Integration Test README](scripts/README.md)

In short:

- Pytest: is the tool we are using to run our tests, with the command: `pytest tests/`
- Coverage: can be checked like running `coverage run -m pytest` or `coverage html`

## Installers

When implementing a new feature or fixing something within the codebase, it is necessary to ensure that it is working
appropriately on the terminal. However, it is equally as important to ensure that new features or fixes work on the
installer terminal too. This is because a large portion of users utilize the installer to use OpenBB Terminal.
More information on how to build an installer can be found [here](build/README.md).
