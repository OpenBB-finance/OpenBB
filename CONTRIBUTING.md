# CONTRIBUTING

First off, thanks for taking the time to contribute (or at least read the Contributing Guidelines)! 🚀

The following is a set of guidelines for contributing to Gamestonk Terminal. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

[How Can I Contribute?](#how-can-i-contribute)
  * [Community/Marketing](#Community/Marketing)
  * [Retail Trader/QA](#retail-trader/qa)
  * [Programmer](#programmer)

[Code Architecture](#code-architecture)
  * [Conventions](#conventions)
  * [Folder Organization](#folder-organization)
  * [MVC Design](#mvc-design)
  * [Tests](#tests)
  * [Documentation](#Documentation)

[Coding Guidelines](#coding-guidelines)
  * [Naming Convention](naming-convention)
  * [Docstrings](#docstrings)
  * [Linters](#linters)

[Github Guidelines](#github-guidelines)
  * [Git Commit Messages](#git-commit-messages)
  * [Pull Requests](#pull-requests)


## How Can I Contribute?

When contributing to this repository, feel free to discuss the change you wish to make via discord https://discord.gg/Up2QGbMKHY!

#### Community/Marketing

Increase Gamestonk Terminal reach:

  * Star the repo.
  * Pass the word to your friends/family.
  * Create content (e.g. youtube videos) using Gamestonk Terminal.
  * Share your terminal graphs and interpretations with other Reddit users ([example](https://www.reddit.com/r/amcstock/comments/of6g83/dark_pool_guy_here_to_kick_off_the_shortened_week/)).
  * Join our discord and interact with other users.

#### Retail Trader/QA

If you are the typical retail trader that uses the terminal on a daily basis, there are a lot of ways you can con contribute:

  * Test Terminal's features.
  * Report bugs or even sketch new feature ideas (we have a large dev community since we're open source, hence there's a lot we can do).
  * Improve our documentation or even features by suggesting enhancements.
  * Search for more APIs that we can add to our terminal.
  * Search websites that we can scrape useful data for free.
  * Contact interesting people in our behalf towards partnerships which will provide our user base with more data.
  * Reach out to developers/mathematicians/data scientists/finance people to help us build the #1 Retail Trader terminal.

#### Programmers

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

T.B.D.

#### Folder Organization

T.B.D.

#### MVC Design

T.B.D.

#### Tests

##### UNIT TESTS

Unit tests minimize errors in code and quickly find errors when they do arise. Please note the following tools when creating tests for GamestonkTerminal:

###### PYTEST

Pytest allows users to quickly create unittests in Python. To use pytest run `pytest tests/`.

###### COVERAGE

Coverage allows users to see how complete unittests are for Python. To use coverage do the following:

1. `coverage run -m pytest`
2. `coverage html`

To view the tests find the htmlcov folder in the main directory and open the index.html file. This will show a detailed report of testing coverage.

###### VCRPY

VCRPY allows us to save data from request methods to a .YAML file. This increases test integrity and significantly speeds up the time it takes to run tests. To use VCRPY do the following:

1. `import vcr`
1. add `@vcr.use_cassette("tests/cassettes/{test_folder}/{test_class}/{test_name}.yaml")` as a decorator to the test

**Note:** If you see an error related to VCRPY add the attribute `record_mode="new_episodes"` to the decorator.

###### check_print

GamestonkTerminal relies on print statements to return data to the user. To check whether necessary information was included in a print statement use the check_print decorator as detailed below:

1. `from tests.helpers import check_print`
1. add `@check_print(assert_in="foo")` as a decorator to the test

If you do not want to assert an item but your test still prints output, please add `@check_print()` as a decorator to mute print output.

**Note:** Ensure `@check_print()` is above `@vcr.use_cassette` when using both.

#### Documentation

T.B.D.

## Coding Guidelines

#### Naming Convention

T.B.D.

#### Docstrings

The docstring format used in `numpy`, an example is shown below:
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

T.B.D.

## Github Guidelines

T.B.D.

#### Git Commit Messages

Attempt to write a concise message under 50 characters to represent what each commit is about. This makes it easier for the team to review the Pull Request.

#### Pull Requests

**Labels**

| Label name | Description | Example
| --- | --- | --- |
| `size:XS` | Extra small feature | Add a preset
| `size:S` | Small T-Shirt size Feature | New single command added
| `size:M` | Medium T-Shirt size feature | Multiple commands added from same data source
| `size:L` | Large T-Shirt size Feature | New category added under context
| `size:XL` | Extra Large feature | New context added

| Label name | Description |
| --- | --- |
| `enhancement` | Enhance existing code
| `bug` | Fix a bug
| `docs` | Improvements on documentation
| `refactor` | Refactor code to follow our convention
| `tests` | Work on pytests
| `build` | Fix a github action that is breaking the build
