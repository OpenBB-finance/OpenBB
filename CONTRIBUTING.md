# CONTRIBUTING

First off, thanks for taking the time to contribute (or at least read the Contributing Guidelines)! 🚀

The following is a set of guidelines for contributing to Gamestonk Terminal. These are mostly guidelines, not rules.
Use your best judgment, and feel free to propose changes to this document in a pull request.

[How Can I Contribute?](#how-can-i-contribute)

* [Community](#community)
* [Retail Trader](#retail-trader)
* [Software Developer](#software-developer)

[Development Process](#development-process)

  1. [Select feature](#select-feature)
  2. [Understand Code Structure](#understand-code-structure)
  3. [Follow Coding Guidelines](#follow-coding-guidelines)
  4. [Remember Coding Style](#remember-coding-style)
  5. [Write Code and Commit](#write-code-and-commit)
  6. [Add a Test](#add-a-test)
  7. [Add Documentation](#add-documentation)
  8. [Open a Pull Request](#open-a-pull-request)
  9. [Review Process](#review-process)

## How Can I Contribute?

### Community

Increase Gamestonk Terminal reach:

* Star the repo.
* Pass the word to your friends/family.
* Create content (e.g. youtube videos) using Gamestonk Terminal.
* Share your terminal graphs and interpretations with other Reddit users ([example](https://www.reddit.com/r/amcstock/comments/of6g83/dark_pool_guy_here_to_kick_off_the_shortened_week/)).
* Join our discord and interact with other users.

### Retail Trader

If you are the typical retail trader that uses the terminal on a daily basis, there are a lot of ways you can con contribute:

* Test Terminal's features.
* Report bugs or even sketch new feature ideas (we have a large dev community since we're open source, hence there's a
lot we can do).
* Improve our documentation or even features by suggesting enhancements.
* Search for more APIs that we can add to our terminal.
* Search websites that we can scrape useful data for free.
* Contact interesting people in our behalf towards partnerships which will provide our user base with more data.
* Reach out to developers/mathematicians/data scientists/finance people to help us build the #1 Retail Trader terminal.

### Software Developer

For a 1h coding session where the (old) architecture of the repo is explained while a new feature is added, check [here](https://www.youtube.com/watch?v=9BMI9cleTTg).

The fact that this is an Open Source project makes the possibilities of contributing pretty much unlimited. In here you
should consider what you want to gain out of this experience of contributing, some examples we've seen since the
repository is live:

* Machine Learning engineers working on our prediction models
* Data Scientists improving our algorithms to make sense out of the data
* Mathematicians exploring our residual analysis menu
* Finance students evaluating a DCF spreadsheet from terminal's data
* DevOps engineers making the repository more robust and ensuring good practices

## Development Process

### Select Feature

* Pick a feature you want to implement or a bug.
* If out are out of ideas, look into our [issues](https://github.com/GamestonkTerminal/GamestonkTerminal/issues) or
search for [`# TODO`](https://www.tickgit.com/browse?repo=github.com/GamestonkTerminal/GamestonkTerminal&branch=main) in
our repository.
* Feel free to discuss what you'll be working on via discord <https://discord.gg/Up2QGbMKHY>, to avoid duplicate work.

## Understand Code Structure

|**Item**|**Description**|**Example**|
|:-|:-|:-|
|**CONTEXT**|Specific instrument *world* to analyse. | `stocks`, `crypto`, `economy` |
|**CATEGORY**|Group of similar COMMANDS to do on the instrument <br /> There are the specialized categories, specific to each CONTEXT and there are common categories which are not specific to one CONTEXT. | `due_diligence`,  `technical_analysis`, `insider` |
|**COMMAND**|Operation on one or no instrument that retrieves data in form of string, table or plot.| `rating`, `supplier`, `sentiment` |

The following layout is expected: `/<context>/<category>/<command_files>`

If there are sub-categories, the layout will be: `/<context>/<category>/<sub-category>/<command_files>`

**Example:**

```text
gamestonk_terminal/stocks/stocks_controller.py
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

|**Context**|**Category**|**File**|**Description**|
|:-|:-|:-|:-|
|`stocks/`|  | `stocks_controller.py` | Manages **stocks** _context_ from a user perspective, i.e. routing _commands_ and arguments to output data, or, more importantly, redirecting to the selected _category_.  |
|`stocks/`|  | `stocks_helper.py` | Helper to `stocks_controller.py`. This file is meant to implement `commands` needed by `stocks_controller.py` |
|`stocks/`| `due_diligence/` | `dd_controller.py` | Manages **due_diligence** _category_ from **stocks** _context_ from a user perspective, i.e. routing _commands_ and arguments to output data. |
|`stocks/`| `due_diligence/` | `marketwatch_view.py` | This file contains functions that rely on **Market Watch** data. These functions represent _commands_ that belong to **due_diligence** _category_ from **stocks** _context_. These functions are called by `dd_controller.py` using the arguments given by the user and will output either a string, table or plot. |
|`stocks/`| `due_diligence/` | `marketwatch_model.py` | This file contains functions that rely on **Market Watch** data. These functions represent _commands_ that belong to **due_diligence** _category_ from **stocks** _context_. These functions are called by `marketwatch_view.py` and will return data to be processed in either a string, dictionary or dataframe format. |
|`stocks/`| `due_diligence/` | `finviz_view.py` | This file contains functions that rely on **Finviz** data. These functions represent _commands_ that belong to **due_diligence** _category_ from **stocks** _context_. These functions are called by `dd_controller.py` using the arguments given by the user and will output either a string, table or plot. |
|`stocks/`| `due_diligence/` | `finviz_model.py` | This file contains functions that rely on **Finviz** data. These functions represent _commands_ that belong to **due_diligence** _category_ from **stocks** _context_. These functions are called by `finviz_view.py` and will return data to be processed in either a string, dictionary or dataframe format. |
|`stocks/`| `technical_analysis/` | `ta_controller.py` | Manages **technical_analysis** _category_ from **stocks** _context_ from a user perspective, i.e. routing _commands_ and arguments to output data. |
|`stocks/`| `technical_analysis/` | `tradingview_view.py` | This file contains functions that rely on **TradingView** data. These functions represent _commands_ that belong to **technical_analysis** _category_ from **stocks** _context_. These functions are called by `ta_controller.py` using the arguments given by the user and will output either a string, table or plot. |
|`stocks/`| `technical_analysis/` | `tradingview_model.py` | This file contains functions that rely on **TradingView** data. These functions represent _commands_ that belong to **technical_analysis** _category_ from **stocks** _context_. These functions are called by `tradingview_view.py` and will return data to be processed in either a string, dictionary or dataframe format. |
|`common/`| `technical_analysis/` | `overlap_view.py` | This file contains functions that rely on **overlap** data. In this case **overlap** is not a data source, but the type of technical analysis performed. These functions represent _commands_ that belong to **technical_analysis** _category_ from **MULTIPLE** _contexts_. These functions are called by `ta_controller.py`, from **MULTIPLE** _contexts_, using the arguments given by the user and will output either a string, table or plot. Due to the fact that this file is **common** to multiple _contexts_ the functions need to be generic enough to accommodate for this. E.g. if we are proving a dataframe to these functions, we should make sure that `stocks/ta_controller.py` and `crypto/ta_controller` use the same formatting. |
|`common/`| `technical_analysis/` | `overlap_model.py` | This file contains functions that rely on **overlap** data. In this case **overlap** is not a data source, but the type of technical analysis performed. These functions represent _commands_ that belong to **technical_analysis** _category_ from **MULTIPLE** _contexts_. These functions are called by `overlap_view.py`, and will return data to be processed in either a string, dictionary or dataframe format. Due to the fact that this file is **common** to multiple _contexts_ the functions need to be generic enough to accommodate for this. E.g. if we are getting the sentiment of an instrument, we  should ensure that these functions accept both a "GME" or a "BTC", for `stocks` and `crypto`, respectively. |

## Follow Coding Guidelines

Process to add a new command. `shorted` command from category `dark_pool_shorts` and context `stocks` will be used as
example. Since this command uses data from Yahoo Finance, a `yahoofinance_view.py` and a `yahoofinance_model.py` files
will be implemented.

### Model

1. Create a file with the source of data as the name followed by `_model` if it doesn't exist, e.g. `yahoofinance_model`
2. Add the documentation header
3. Do the necessary imports to get the data
4. Define a function starting with `get_`
5. In that function:
   1. Use typing hints
   2. Write a descriptive description where at the end the source is specified
   3. Obtain the data and return it. Sometimes the model can contain a more complex logic to it, if the scraping is not
    straightforward. If the data is returned directly by an API, we still want to wrap it around a model function to
    keep consistency across codebase and be more future proof.

```python
""" Yahoo Finance Model """
__docformat__ = "numpy"

import pandas as pd
import requests


def get_most_shorted() -> pd.DataFrame:
    """Get most shorted stock screener [Source: Yahoo Finance]

    Returns
    -------
    pd.DataFrame
        Most Shorted Stocks
    """
    url = "https://finance.yahoo.com/screener/predefined/most_shorted_stocks"

    data = pd.read_html(requests.get(url).text)[0]
    data = data.iloc[:, :-1]
    return data
```

Note: As explained before, it is possible that this file needs to be created under `common/` directory rather than
`stocks/`, which means that when that happens this function should be done in a generic way, i.e. not mentioning stocks
or a specific context.

#### View

1. Create a file with the source of data as the name followed by `_view` if it doesn't exist, e.g. `yahoofinance_view`
2. Add the documentation header
3. Do the necessary imports to display the data. One of these is the `_model` associated with this `_view`. I.e. from
same data source.
4. Define a function starting with `display_`
5. In this function:
   * Use typing hints
   * Write a descriptive description where at the end the source is specified
   * Get the data from the `_model` and parse it to be output in a more meaningful way.
   * Ensure that the data that comes through is reasonable, i.e. at least that we aren't displaying an empty dataframe.
   * Do not degrade the main data dataframe coming from model if there's an export flag. This is so that the export can
    have all the data rather than the short amount of information we may show to the user. Thus, in order to do so
    `df_data = df.copy()` can be useful as if you change `df_data`, `df` remains intact.
   * Always add a new line at the end, this allows for an additional line between 2 commands and makes it easier for the
    user to visualize what is happening.
6. Finally, call `export_data` where the variables are export variable, current filename, command name, and dataframe.

```python
""" Yahoo Finance View """
__docformat__ = "numpy"

import os
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.helper_funcs import export_data, rich_table_from_df
from gamestonk_terminal.stocks.dark_pool_shorts import yahoofinance_model


def display_most_shorted(num_stocks: int, export: str):
    """Display most shorted stocks screener. [Source: Yahoo Finance]

    Parameters
    ----------
    num_stocks: int
        Number of stocks to display
    export : str
        Export dataframe data to csv,json,xlsx file
    """
    df = yahoofinance_model.get_most_shorted()
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    if df.empty:
        console.print("No data found.")
    else:
        rich_table_from_df(
            df.head(num_stocks),
            headers=list(df.columns),
            show_index=False,
            title="Most shorted stocks"
        )
    console.print("")

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
3. Add command name and description to `print_help()`. In addition, an additional line above must contain the Source
of information. E.g.

   ```python
   Yahoo Finance:
       shorted        show most shorted stocks
   ```

4. Add a method to `DarkPoolShortsController` class with name: `call_` followed by command name.
   * This method must start defining a parser with arguments `add_help=False` and
   `formatter_class=argparse.ArgumentDefaultsHelpFormatter`. In addition `prog` must have the same name as the command,
   and `description` should be self-explanatory ending with a mention of the data source.
   * Add parser arguments after defining parser. One important argument to add is the export capability. All commands
   should be able to export data.
   * Initialize a try-catch block. This is so that if there is an issue the terminal doesn't crash and the user can
   keep using it.
   * If there is a single or even a main argument, a block of code must be used to insert a fake argument on the list of
    args provided by the user. This makes the terminal usage being faster.
   * Parse known args from list of arguments and values provided by the user.
   * Call the function contained in a `_view.py` file with the arguments parsed by argparse.

```python
def call_shorted(self, other_args: List[str]):
        """Process shorted command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="shorted",
            description="Print up to 25 top ticker most shorted. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of the most shorted stocks to retrieve.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        yahoofinance_view.display_most_shorted(
            num_stocks=ns_parser.num,
            export=ns_parser.export,
        )

```

## Remember Coding Style

When in doubt, follow <https://www.python.org/dev/peps/pep-0008/>.

### Naming Convention

* The name of the variables must be descriptive of what they stand for. I.e. `ticker` is descriptive, `aux` is not.
* Single character variables **must** be avoided. Except if they correspond to the iterator of a loop.

### Docstrings

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

### Linters

The following linters are used by our codebase:

| Linter | Description |
| --- | --- |
| bandit | security analyzer |
| black | code formatter |
| codespell | spelling checker |
| flake8 | style guide enforcer |
| mypy | static typing checker |
| pyupgrade | upgrade syntax for newer versions |
| safety | checks security vulnerabilities |
| pylint | bug and quality checker |
| markdownlint | markdown linter |

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
`git add gamestonk_terminal/stocks/stocks_controller.py gamestonk_terminal/stocks/stocks_helper.py`.
Note: **DON'T** add `config_terminal.py` or `.env` files with personal information, or even `feature_flags.py` which is user-dependent.
4. Write a concise commit message under 50 characters, e.g. `git commit -m "meaningful commit message"`. If your PR
solves an issue raised by a user, you may specify such issue by adding #ISSUE_NUMBER to the commit message, so that
these get linked. Note: If you installed pre-commit hooks and one of the formatters re-formats your code, you'll need
to go back to step 3 to add these.

## Add a Test

Unit tests minimize errors in code and quickly find errors when they do arise.

### Pytest

Pytest allows users to quickly create unit tests in Python. To use pytest run `pytest tests/`.

### Coverage

Coverage allows users to see how complete unit tests are for Python. To use coverage do the following:

1. `coverage run -m pytest`
2. `coverage html`

To view the tests find the htmlcov folder in the main directory and open the *index.html* file. This will show a detailed
report of testing coverage.

### VCR

VCRPY allows us to save data from request methods to a .YAML file. This increases test integrity and significantly
speeds up the time it takes to run tests. To use VCRPY add **@pytest.mark.vcr** above any function you write.

## Add Documentation

* **High-level documentation**:
  * Add a row to the table on the README of the corresponding context/folder.
  * E.g. if you are adding `pipo` feature to `discovery` menu under `stocks` context, you need to go into the corresponding
  [README](https://github.com/GamestonkTerminal/GamestonkTerminal/blob/main/gamestonk_terminal/stocks/discovery/README.md)
  and add a new row to the table, like:

Command|Description|Source
---|---|---
`pipo`           |past IPOs |[Finnhub](https://finnhub.io)

* **Low-level documentation**:
  * See [Hugo Server instructions](/website/README.md).

## Open a Pull Request

Once you're happy with what you have, push your branch to remote. E.g. `git push origin feature/AmazingFeature`

A user may create a **Draft Pull Request** when he/she wants to discuss implementation with the team.

As reviewers, you should select: @DidierRLopes and @jmaslek.

A label **must** be selected from the following types:

| Label name | Description | Example
| --- | --- | --- |
| `feat XS` | Extra small feature | Add a preset
| `feat S` | Small T-Shirt size Feature | New single command added
| `feat M` | Medium T-Shirt size feature | Multiple commands added from same data source
| `feat L` | Large T-Shirt size Feature | New category added under context
| `feat XL` | Extra Large feature | New context added
| `enhancement` | Enhancement | Add new parameter to existing command
| `bug` | Fix a bug | Fixes terminal crashing or warning message
| `build` | Build-related work | Fix a github action that is breaking the build
| `tests` | Test-related work | Add/improve tests
| `docs` | Improvements on documentation | Add/improve documentation
| `refactor` | Refactor code | Changing argparse location
| `docker` | Docker-related work | Add/improve docker
| `help wanted` | Extra attention is needed | When a contributor needs help
| `do not merge` | Label to prevent pull request merge | When PR is not ready to be merged just yet

## Review Process

As soon as the Pull Request is opened, our repository has a specific set of github actions that will not only run
linters on the branch just pushed, but also run pytest on it. This allows for another layer of safety on the code developed.

In addition, our team is known for performing `diligent` code reviews. This not only allows us to reduce the amount of
iterations on that code and have it to be more future proof, but also allows the developer to learn/improve his coding skills.

Often in the past the reviewers have suggested better coding practices, e.g. using `1_000_000` instead of `1000000` for
better visibility, or suggesting a speed optimization improvement.
