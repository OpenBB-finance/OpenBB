# OpenBB Terminal : `Integration Testing`

This document is part of the `OpenBB Terminal` library documentation.

It aims to provide necessary information in order to:

- Build `integration tests`
- Run `integration tests`
- Identify errors noted from `integration tests`

## 1.1. Why have integration tests ?

The purpose of integration tests is to provide standard usage examples that can be programmatically run
to make sure that a specific functionality of the terminal and the process to utilize that functionality
is working properly.

## 2. How to build integration tests ?

Integration tests themselves are the same as manually running a certain series of steps. As a result,
writing tests is easy because the integration test script is just the total list of steps necessary to
use a command, command with specific argument, or series of commands.

When you contribute a new feature to the Terminal, it's important that integration tests are added for
this particular feature. It is a part of the Checklist for the PR to be approved.

All the `integration tests` should be insides the `scripts` folder. The naming convention for scripts
should be `test_<menu>_<command>.openbb` if you are testing a specific command or `test_<menu>.openbb`
if you are testing the entire menu. However, it is encouraged to create as specific of integration tests
as possible to identify errors more precisely. Additionally, all tests must end with the `exit` command.

These files can be given dynamic output with the following syntax `${key=default}`. Please note that
both key and default can only contain letters and numbers with NO special characters. Each dynamic
argument MUST contain a key and a default value.

### Examples

Testing a specific command and it's arguments:

```zsh
script: test_alt_covid.openbb
- - - - - - - - - -
alternative
covid
country Australia
reset
slopes
country US
ov
country Russia
deaths
country United Kingdom
cases
country Canada
rates
exit
```

Testing an entire menu

```zsh
test_stocks_options.openbb
- - - - - - - - - -
stocks
options
screen
view
view high_IV
set high_IV
scr
q
unu
calc
load aapl
exp 0
pcr
info
chains
oi
vol
voi
hist 100
grhist 100
plot -x ltd -y iv
parity
binom
load spy
vsurf
exit
```

## 3. How to run integration tests ?

### Conda Terminal

After navigating to the location of the OpenBBTerminal repo, one can run integration tests in a
few different ways using the wildcard expression. Please include a `-t` with `terminal.py` to run
the tests.

- Run all integration tests:

    ```zsh
    python terminal.py -t
    ```

- Run some integration tests:

    ```zsh
    python terminal.py -f stocks cryptocurrency -t
    ```

    *This specific example runs all of the stocks integration tests. One can use this same format for different tests.*

- Run one integration tests:

    ```zsh
    python terminal.py -f alternative/test_alt_covid.openbb -t
    ```

    *Note that the base path is `OpenBBTerminal/openbb_terminal/miscellaneous/scripts`.*

- Run integration tests with arguments by adding --key=value

    ```zsh
    python terminal.py --ticker=aapl -t
    ```

- To see a lot of possible keys, run the following:

    ```zsh
    python terminal.py -h -t
    ```

If there are any test failures a csv will be generated with detailed information on the failures.

### Installer Terminal

Integration tests can also be used on installers, which is a packaged version of the conda terminal.
More information on how to build an installer can be found [here](/build/README.md).

- Run all integration tests:

    ```zsh
    /Full/Path/To/OpenBB\ Terminal/.OpenBB/OpenBBTerminal /Full/Path/To/OpenBBTerminal/OpenBBTerminal/scripts/*.openbb -t
    ```

- Run some integration tests:

    ```zsh
    /Full/Path/To/OpenBB\ Terminal/.OpenBB/OpenBBTerminal /Full/Path/To/OpenBBTerminal/OpenBBTerminal/scripts/test_stocks_*.openbb -t
    ```

- Run one integration tests:

    ```zsh
    /Full/Path/To/OpenBB\ Terminal/.OpenBB/OpenBBTerminal /Full/Path/To/OpenBBTerminal/OpenBBTerminal/scripts/test_alt_covid.openbb -t
    ```

The `-t` argument runs the integration tests in 'test' mode. It is effectively a 'quiet' mode where one
doesn't see the terminal in action. If one were to remove this argument, then the terminal and subsequent
steps will be seen running in real time.

## 4. Errors

If the `-t` argument is given, errors that occur during an integration test are shown after all the
selected tests have run. The specific script that has some type of failure occurring, the reason why
it failed, and a summary of all the integration tests that were run is printed. An example is as followed:

```zsh
/scripts/test_stocks_ba.openbb: Implement enable_gui in a subclass

/scripts/test_stocks_disc.openbb: No tables found

/scripts/test_stocks_dps.openbb: No tables found

/scripts/test_stocks_scr.openbb: 429 Client Error: Too Many Requests for url: https://finviz.com/screener.ashx?v=111&s=ta_toplosers&ft=4&r=101

Summary: Successes: 55 Failures: 4
```

If the `-t` argument is not given, then the reason why a specific failure occurs within an integration
test is printed inline while the test is being run.

If there is an error, one can identify the command and or series of steps that causes it fairly easily.

Output from the integration tests can also be viewed in the `integration_test_output` folder .
