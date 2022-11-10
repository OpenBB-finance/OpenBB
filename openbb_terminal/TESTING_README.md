# Using OpenBB Integrated Tests

The OpenBB Integrated Tests provide a way for our developers to easily tests the affects of changes
terminal-wide. This document provides an overview of how to use them.

## Running the Tests

To run all unit tests simply run `python testing.py`. This will run every script we have with
default arguments. To send arguments please use the following format `key=value`. For example
to change the ticker value for all items in the terminal use: `python terminal.py ticker=aapl`.
To see a list of possible keys use `python testing.py -h`.

Specific sets of tests can be run. You can do this by adding the paths to folders or tests you
want to run. Note that the base path is `OpenBBTerminal/openbb_terminal/miscellaneous/scripts`.

If there are any test failures a csv will be generated with detailed information on the failures.

## Creating Tests

To create new tests add `.openbb` files to a directory in
`OpenBBTerminal/openbb_terminal/miscellaneous/scripts`. These files can be given dynamic output
with the following syntax `${key=default}`. Please note that both key and default can only contain
letters and numbers with NO special characters. Each dynamic argument MUST contain a key and a
default value.

Once a new key has been added to a script, navigate to `OpenBBTerminal/testing.py` and add the key
to the list `special_arguments`.
