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

## 3. How integration tests detect bugs ?

When an unhandled exception is raised during a test session, this is considered a bug. The exception is caught and we save its traceback and other details to debug afterwards.

### Script examples

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

- To see the available tests, use `--list` or `-l`:

    ```zsh
    python terminal.py -t -l
    ```

- Run all integration tests:

    ```zsh
    python terminal.py -t
    ```

- Run some integration tests, by number, name or path:

    ```zsh
    python terminal.py -t -p 0 10 22
    ```

    ```zsh
    python terminal.py -t -p stocks cryptocurrency
    ```

    *This specific example runs all of the stocks integration tests. One can use this same format for different tests.*

    ```zsh
    python terminal.py -t openbb_terminal/core/integration_tests/scripts/forex
    ```

- Run one integration test:

    ```zsh
    python terminal.py -t -p alternative/test_alt_covid.openbb
    ```

    *Note that the base path is `OpenBBTerminal/openbb_terminal/core/integration_tests/scripts`.*

- Skip some integration tests:

    ```zsh
    python terminal.py -t -p alternative -s alternative/test_alt_covid.openbb
    ```

- Run integration tests with arguments by adding --key=value:

    ```zsh
    python terminal.py -t --ticker=aapl
    ```

- To see the possible keys, use `--help` or `-h`:

    ```zsh
    python terminal.py -t -h
    ```

- To save time, the tests are run in parallel by default. You can choose the number of subprocesses used with `--subproc`. The default number of subprocesses is the minimum between the number of scripts to run and the number of CPUs of your machine.

    ```zsh
    python terminal.py -t forex --subproc 4
    ```

- To have a more responsive console output we run the tests in parallel and return the
  output of each script as soon as it is ready. This means that test results might not
  be displayed in the same order as they were started. To force displaying tests results
  in the order they start, use the option `--ordered`:

    ```zsh
    python terminal.py -t --ordered
    ```

- To see terminal outputs being printed during the test session, use `--verbose` or `-v`:

    ```zsh
    python terminal.py -t -v
    ```

- To run the tests sequentially (it will be way slower for a large number of scripts),
  use `--subproc 0`:

    ```zsh
    python terminal.py -t --subproc 0
    ```

- Enabling verbose mode and running scripts in several processes will mix the output
  each script in the console. In this case it is advisable to run tests with the option
  `--subproc 0`, this will run the tests sequentially. It will be slower, but the outputs
  of each test will not be mixed up.

    ```zsh
    python terminal.py -t forex --subproc 0 -v
    ```

### Installer Terminal

Integration tests can also be used on installers, which is a packaged version of the conda terminal.
More information on how to build an installer can be found [here](/build/README.md).
To run the tests on installers you can use the same syntax as above, just substitute `python terminal.py` by the full path to OpenBBTerminal executable (not the shortcut!). See the examples below for MacOS.

- Run all integration tests:

    ```zsh
    /Full/Path/To/OpenBB\ Terminal/.OpenBB/OpenBBTerminal -t
    ```

- Run some integration tests:

    ```zsh
    /Full/Path/To/OpenBB\ Terminal/.OpenBB/OpenBBTerminal -t forex stocks
    ```

- Run one integration test:

    ```zsh
    /Full/Path/To/OpenBB\ Terminal/.OpenBB/OpenBBTerminal -t alternative/test_alt_covid.openbb
    ```

- Get integration test coverage:

    ```zsh
    /Full/Path/To/OpenBB\ Terminal/.OpenBB/OpenBBTerminal -t --coverage
    ```

## 4. Test report

The console report has 3 sections: progress, failures and summary.

- Progress
    1. Shows the tests collected and skipped in the current session
    2. Informs if tests are running in parallel or sequentially
    3. Displays the result of tests already finished

- Failures
    1. Traceback
    2. Exception type
    3. Detail with exception message

- Summary
    1. Displays tests failed with the last command called and how long they took to run

- Example

```zsh
(obb) % python terminal.py -t forex
============================ integration test session starts =============================
Collecting scripts from: /Users/username/OpenBBTerminal/openbb_terminal/core/integration_tests/scripts


* Collected 7 script(s)...
* Skipping 0 script(s)...
* Running 7 script(s) in 7 parallel subprocess(es)...

forex/test_forex_av.openbb                                                          [ 14%]
forex/test_forex_base.openbb                                                        [ 29%]
forex/test_forex_load.openbb                                                        [ 43%]
forex/test_forex_oanda.openbb                                                       [ 57%]
forex/test_forex_oanda_base.openbb                                                  [ 71%]
forex/test_forex_qa.openbb                                                          [ 86%]
forex/test_forex_ta.openbb                                                          [100%]

======================================== FAILURES ========================================
------------------------------- forex/test_forex_qa.openbb -------------------------------

Traceback:
  File "/Users/username/OpenBBTerminal/openbb_terminal/core/integration_tests/integration_controller.py", line 299, in run_test
    run_scripts(
  File "/Users/username/OpenBBTerminal/openbb_terminal/core/integration_tests/integration_controller.py", line 272, in run_scripts
    terminal(file_cmds, test_mode=True)
  File "/Users/username/OpenBBTerminal/openbb_terminal/terminal_controller.py", line 905, in terminal
    t_controller.queue = t_controller.switch(an_input)
  File "/Users/username/OpenBBTerminal/openbb_terminal/decorators.py", line 64, in wrapper
    value = func(*args, **kwargs)
  File "/Users/username/OpenBBTerminal/openbb_terminal/parent_classes.py", line 363, in switch
    getattr(
  File "/Users/username/OpenBBTerminal/openbb_terminal/terminal_controller.py", line 401, in call_forex
    self.queue = self.load_class(ForexController, self.queue)
  File "/Users/username/OpenBBTerminal/openbb_terminal/parent_classes.py", line 219, in load_class
    return class_ins(*args, **kwargs).menu()
  File "/Users/username/OpenBBTerminal/openbb_terminal/parent_classes.py", line 934, in menu
    self.queue = self.switch(an_input)
  File "/Users/username/OpenBBTerminal/openbb_terminal/decorators.py", line 64, in wrapper
    value = func(*args, **kwargs)
  File "/Users/username/OpenBBTerminal/openbb_terminal/parent_classes.py", line 363, in switch
    getattr(
  File "/Users/username/OpenBBTerminal/openbb_terminal/decorators.py", line 64, in wrapper
    value = func(*args, **kwargs)
  File "/Users/username/OpenBBTerminal/openbb_terminal/forex/forex_controller.py", line 434, in call_qa
    1 / 0
Exception type: ZeroDivisionError
Detail: division by zero
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

================================ integration test summary ================================
FAILED forex/test_forex_qa.openbb -> command: qa
============================== 1 failed, 6 passed in 8.88s ===============================
```
