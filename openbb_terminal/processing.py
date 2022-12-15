from pathlib import Path
from random import random
from multiprocessing.pool import Pool
import sys
from openbb_terminal.integration_tests.integration_controller import run_scripts

from openbb_terminal.terminal_helper import suppress_stdout
import time
import tqdm


# task executed in a worker process
def task(file):

    run_scripts(
        path=file,
        verbose=False,
    )
    return str(file)


# protect the entry point
if __name__ == "__main__":
    # create and configure the process pool

    INPUTS = [
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_av.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_base.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_load.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_oanda.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_qa.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_av.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_base.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_load.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_oanda.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_qa.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_av.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_base.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_load.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_oanda.openbb"
        ),
        Path(
            "/Users/diogosousa/OpenBBTerminal/openbb_terminal/integration_tests/scripts/forex/test_forex_qa.openbb"
        ),
    ]

    if sys.argv[1] == "1":
        start = time.time()
        with Pool() as pool:
            for result in pool.imap(task, INPUTS):
                print(result)

        end = time.time()
        print(f"Multi: {end - start}")
    else:
        start = time.time()
        for file in INPUTS:
            result = task(file)
            print(result)
        end = time.time()
        print(f"Single: {end - start}")
