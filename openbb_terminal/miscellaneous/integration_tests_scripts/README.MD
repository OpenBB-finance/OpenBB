# Integration tests

## Table of Contents

- [Integration tests](#integration-tests)
  - [Table of Contents](#table-of-contents)
  - [What is it?](#what-is-it)
  - [OpenBB Terminal integration tests](#openbb-terminal-integration-tests)
    - [How to list the available tests](#how-to-list-the-available-tests)
    - [How to run a test](#how-to-run-a-test)
      - [Run all tests](#run-all-tests)
      - [Run a specific test](#run-a-specific-test)
      - [Custom flags](#custom-flags)

## What is it?

Integration tests are a type of software testing that is used to validate the interactions between different components or modules of an application. Unlike unit tests, which test individual pieces of code in isolation, integration tests verify that the system's different components work together correctly.

The purpose of integration tests is to identify problems that arise when the various parts of an application are integrated. Integration tests help to ensure that the software works as a whole and that different modules can communicate and exchange data correctly.

Integration tests are often used to test the following:

- Integration between different software modules or services
- Integration between an application and external dependencies such as databases, APIs, and other third-party services
- End-to-end functionality of the entire system

Integration tests can be automated or performed manually. They are typically more complex and take longer to run than unit tests, as they require the integration of multiple components. However, integration tests are an essential part of a comprehensive testing strategy and can help to identify issues that may be missed by unit tests.

## OpenBB Terminal integration tests

Those can be found and organized by menu as follows:

- `stocks` menu: `openbb_terminal/miscellaneous/integration_tests_scripts/stocks/`, tests within the folder:
  - `openbb_terminal/miscellaneous/integration_tests_scripts/stocks/test_stocks_ba.openbb`
  - `openbb_terminal/miscellaneous/integration_tests_scripts/stocks/test_stocks_qa.openbb`
  - ...
- `economy` menu: `openbb_terminal/miscellaneous/integration_tests_scripts/economy/`, tests within the folder:
  - `openbb_terminal/miscellaneous/integration_tests_scripts/economy/test_economy.openbb`
- ...

The structure of each test should be a combination of the commands found in the terminal, here is an example you can find [here](openbb_terminal/miscellaneous/integration_tests_scripts/stocks/test_stocks_options_payoff.openbb):

```bash

stocks
options
load aapl
exp 0
payoff
list
pick long
add 20
add 15
add 10 -p
sop
plot
exit

```

Output:

```bash

* Collected 69 script(s)...
* Skipping 0 script(s)...

Available scripts:
0. account/test_account.openbb
1. alternative/test_alt_covid.openbb
2. alternative/test_alt_oss.openbb
3. alternative/test_alt_realestate.openbb
4. cryptocurrency/test_crypto.openbb
5. cryptocurrency/test_crypto_dd.openbb
6. cryptocurrency/test_crypto_defi.openbb
7. cryptocurrency/test_crypto_disc.openbb
8. cryptocurrency/test_crypto_nft.openbb
9. cryptocurrency/test_crypto_onchain.openbb
10. cryptocurrency/test_crypto_ov.openbb
...
```

### How to list the available tests

```bash
python terminal.py -t -l
```

### How to run a test

#### Run all tests

```bash
python terminal.py -t
```

#### Run a specific test

```bash
python terminal.py -t 2
```

> Here the number `2` is the index of the test you want to run, you can find the index by running `python terminal.py -t -l`

#### Custom flags

We can add the following flags to either run all tests or a specific test:

- `subproc` to choose the number of subprocesses to run the tests in parallel.

```bash
python terminal.py -t 2 --subproc 2
```

- `verbose` to print the output of the tests inside the OpenBB Terminal.

```bash
python terminal.py -t 2 --subproc 0 --verbose
```