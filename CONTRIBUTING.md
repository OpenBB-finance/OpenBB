# CONTRIBUTING

First off, thanks for taking the time to contribute (or at least read the Contributing Guidelines)! 🚀

The following is a set of guidelines for contributing to Gamestonk Terminal. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

[How Can I Contribute?](#how-can-i-contribute)
  * [Community - Marketing](#community---marketing)
  * [Retail Trader - Quality Assurance](#retail-trader---quality-assurance)
  * [Programmer - Data Scientist](#programmer---data-scientist)

[Code Architecture](#code-architecture)
  * [Conventions](#conventions)
  * [Model-View-Controller](#model---view---controller)

[Tests](#tests)
  * [Pytest](#pytest)
  * [Coverage](#coverage)
  * [VCR](#vcr)
  * [check_print](#check_print)

[Documentation](#Documentation)

[Coding Guidelines](#coding-guidelines)
  * [Naming Convention](naming-convention)
  * [Docstrings](#docstrings)
  * [Linters](#linters)

[Github Guidelines](#github-guidelines)
  * [Pre Commit Hooks](#pre-commit-hooks)
  * [Git Commit Messages](#git-commit-messages)
  * [Pull Requests](#pull-requests)


## How Can I Contribute?

When contributing to this repository, feel free to discuss the change you wish to make via discord https://discord.gg/Up2QGbMKHY!

#### Community - Marketing

Increase Gamestonk Terminal reach:

  * Star the repo.
  * Pass the word to your friends/family.
  * Create content (e.g. youtube videos) using Gamestonk Terminal.
  * Share your terminal graphs and interpretations with other Reddit users ([example](https://www.reddit.com/r/amcstock/comments/of6g83/dark_pool_guy_here_to_kick_off_the_shortened_week/)).
  * Join our discord and interact with other users.

#### Retail Trader - Quality Assurance

If you are the typical retail trader that uses the terminal on a daily basis, there are a lot of ways you can con contribute:

  * Test Terminal's features.
  * Report bugs or even sketch new feature ideas (we have a large dev community since we're open source, hence there's a lot we can do).
  * Improve our documentation or even features by suggesting enhancements.
  * Search for more APIs that we can add to our terminal.
  * Search websites that we can scrape useful data for free.
  * Contact interesting people in our behalf towards partnerships which will provide our user base with more data.
  * Reach out to developers/mathematicians/data scientists/finance people to help us build the #1 Retail Trader terminal.

#### Programmer - Data Scientist

For a 1h coding session where the (old) architecture of the repo is explained while a new feature is added, check https://www.youtube.com/watch?v=9BMI9cleTTg.

The fact that this is an Open Source project makes the possibilities of contributing pretty much unlimited. In here you should consider what do you want to gain out of this experience of contributing, some examples we've seen since the repository is live:

  * Machine Learning engineers working on our prediction models
  * Data Scientists improving our algorithms to make sense out of the data
  * Mathematicians exploring our residual analysis menu
  * Finance students evaluating a DCF spreadsheet from terminal's data
  * DevOps engineers making the repository more robust and ensuring good practices

Throughout the code we're leaving `# TODO` flags behind for tasks that aren't high priority, but still a good-to-have. So if you would be happy to work on anything, you can search for these on the project and let us know you'll be tackling it.

The steps to contribute are:
1. Fork the Project
2. Create your Feature Branch (git checkout -b feature/AmazingFeature)
3. Commit your Changes (git commit -m 'Add some AmazingFeature')
4. Install the pre-commit hooks by running: pre-commit install. Any time you commit a change, linters will be run automatically. On changes, you will have to re-commit.
5. Push to your Branch (git push origin feature/AmazingFeature)
6. Open a Pull Request


## Code Architecture

#### Conventions

|**Item**|**Description**|**Example**|
|:-|:-|:-|
|**CONTEXT**|Specific instrument *world* to analyse. | `stocks`, `crypto`, `economy` |
|**CATEGORY**|Group of similar COMMANDS to do on the instrument <br /> There are the specialized categories, specific to each CONTEXT and there are common categories which are not specific to one CONTEXT. | `due_diligence`,  `technical_analysis`, `insider` |
|**COMMAND**|Operation on one or no instrument that retrieves data in form of string, table or plot.| `rating`, `supplier`, `sentiment` |


#### Model-View-Controller

The following layout is expected: `/<context>/<category>/<command_files>`

If there are sub-categories, the layout will be: `/<context>/<category>/<sub-category>/<command_files>`
    
**Example:**
```
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
|`common/`| `technical_analysis/` | `overlap_view.py` | This file contains functions that rely on **overlap** data. In this case **overlap** is not a data source, but the type of technical analysis performed. These functions represent _commands_ that belong to **technical_analysis** _category_ from **MULTIPLE** _contexts_. These functions are called by `ta_controller.py`, from **MULTIPLE** _contexts_, using the arguments given by the user and will output either a string, table or plot. Due to the fact that this file is **common** to multiple _contexts_ the functions need to be generic enough to accomodate for this. E.g. if we are proving a dataframe to these functions, we should make sure that `stocks/ta_controller.py` and `crypto/ta_controller` use the same formatting. | 
|`common/`| `technical_analysis/` | `overlap_model.py` | This file contains functions that rely on **overlap** data. In this case **overlap** is not a data source, but the type of technical analysis performed. These functions represent _commands_ that belong to **technical_analysis** _category_ from **MULTIPLE** _contexts_. These functions are called by `overlap_view.py`, and will return data to be processed in either a string, dictionary or dataframe format. Due to the fact that this file is **common** to multiple _contexts_ the functions need to be generic enough to accomodate for this. E.g. if we are getting the sentiment of an instrument, we  should ensure that these functions accept both a "GME" or a "BTC", for `stocks` and `crypto`, respectively. | 


## Tests

Unit tests minimize errors in code and quickly find errors when they do arise.

##### Pytest

Pytest allows users to quickly create unittests in Python. To use pytest run `pytest tests/`.

##### Coverage

Coverage allows users to see how complete unittests are for Python. To use coverage do the following:

1. `coverage run -m pytest`
2. `coverage html`

To view the tests find the htmlcov folder in the main directory and open the *index.html* file. This will show a detailed report of testing coverage.

##### VCR

VCRPY allows us to save data from request methods to a .YAML file. This increases test integrity and significantly speeds up the time it takes to run tests. To use VCRPY do the following:

1. `import vcr`
1. add `@vcr.use_cassette("tests/cassettes/{test_folder}/{test_class}/{test_name}.yaml")` as a decorator to the test

**Note:** If you see an error related to VCRPY add the attribute `record_mode="new_episodes"` to the decorator.

##### check_print

GamestonkTerminal relies on print statements to return data to the user. To check whether necessary information was included in a print statement use the check_print decorator as detailed below:

* `from tests.helpers import check_print`
* Add `@check_print(assert_in="foo")` as a decorator to the test

If you do not want to assert an item but your test still prints output, please add `@check_print()` as a decorator to mute print output.

**Note:** Ensure `@check_print()` is above `@vcr.use_cassette` when using both.

## Documentation

T.B.D.

## Coding Guidelines

When in doubt, follow https://www.python.org/dev/peps/pep-0008/.

#### Naming Convention

* The name of the variables must be descriptive of what they stand for. I.e. `ticker` is descriptive, `aux` is not.
* Single character variables **must** be avoided. Except if they correspond to the iterator of a loop.

#### Docstrings

The docstring format used in **numpy**, an example is shown below:
```
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

## Github Guidelines

#### Pre Commit Hooks

Git hook scripts are useful for identifying simple issues before submission to code review. We run our hooks on every commit to automatically point out issues in code such as missing semicolons, trailing whitespace, and debug statements. By pointing these issues out before code review, this allows a code reviewer to focus on the architecture of a change while not wasting time with trivial style nitpicks.

Install the pre-commit hooks by running: `pre-commit install`.

#### Git Commit Messages

Attempt to write a concise message under 50 characters to represent what each commit is about. This makes it easier for the team to review the Pull Request.

If your PR solves an issue raised by a user, you may specify such issue by adding #ISSUE_NUMBER to the commit message, so that these get linked.

#### Pull Requests

A user may create a **Draft Pull Request** when he/she wants to discuss implementation with the team.

As a reviewers, you should select: @DidierRLopes and @jmaslek.

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
