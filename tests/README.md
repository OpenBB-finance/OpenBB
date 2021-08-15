# UNIT TESTS

Unit tests minimize errors in coding and quickly find errors when they do arise. Please note the following tools when creating tests for GamestonkTerminal:

## PYTEST

Pytest allows users to quickly create unittests in Python. To use pytest run `pytest tests/`.

## COVERAGE

Coverage allows users to see how complete unittests are for Python. To use coverage do the following:

1. `coverage run -m pytest`
2. `coverage html`

To view the tests find the htmlcov folder in the main directory and open the index.html file. This will show a detailed report of testing coverage.

## VCRPY

VCRPY allows us to save data from request methods to a .YAML file. This increases test integrity and significantly speeds up the time it takes to run tests. To use VCRPY do the following:

1. `import vcr`
1. add `@vcr.use_cassette("tests/cassettes/{test_folder}/{test_class}/{test_name}.yaml")` as a decorator to the test

**Note:** _If you see an error related to VCRPY add the attribute `record_mode="new_episodes"` to the decorator.

## check_print

GamestonkTerminal relies on print statements to return data to the user. To check whether necessary information was included in a print statement use the check_print decorator as detailed below:

1. `from tests.helpers import check_print`
1. add `@check_print(assert_in="foo")` as a decorator to the test

If you do not want to assert an item but your test still prints output, please add `@check_print()` as a decorator to mute print output.

**Note:** _Ensure `@check_print()` is above `@vcr.use_cassette` when using both.
