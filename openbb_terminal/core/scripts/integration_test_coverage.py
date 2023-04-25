"""Obtain the integration test coverage for the OpenBB Terminal."""

# IMPORT STANDARD
import importlib
import re

# IMPORT THIRD-PARTY
import pandas as pd

# IMPORT INTERNAL
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console

INTEGRATION_PATH = "./openbb_terminal/miscellaneous/integration_tests_scripts"


def get_module(module_path: str, module_name: str = "") -> object:
    """Obtain a module from a given path."""
    module = importlib.import_module(module_path)
    if module_name == "":
        module_name = re.sub(r".*\.", "", module.__name__)
        module_name = "".join([word.capitalize() for word in module_name.split("_")])
    try:
        module = getattr(module, module_name)
        return module
    except AttributeError:
        raise ModuleNotFoundError  # pylint: disable=raise-missing-from


def get_functions(module: object) -> list:
    """Obtain all functions from a given module."""
    filter_func = [
        "about",
        "cls",
        "home",
        "record",
        "resources",
        "screenshot",
        "stop",
        "support",
        "whoami",
        "wiki",
    ]
    functions = []
    for name in dir(module):
        if name.startswith("call_"):
            functions.append(name[5:])

    functions = [function for function in functions if function not in filter_func]
    return functions


def get_tested_functions(test_file: str) -> list:
    """Obtain all functions that are called in a given test file."""
    tested_functions = []
    with open(test_file) as f:
        for line in f:
            try:
                function = line.split()[0]
            except IndexError:
                continue

            if function != "#":
                tested_functions.append(function)

    tested_functions = list(dict.fromkeys(tested_functions))
    return list(tested_functions)


def calculate_coverage_percentage(
    tested_functions: list, available_functions: list, output_table: bool = False
) -> None:
    """Calculate the integration test coverage."""
    untested_functions = []
    coverage = min(
        100, round(len(tested_functions) / len(available_functions) * 100, 2)
    )
    for function in available_functions:
        if function not in tested_functions:
            untested_functions.append(function)

    if output_table:
        df = pd.DataFrame({"function": available_functions})
        df["tested"] = df["function"].apply(lambda x: x in tested_functions)
        df = df.sort_values(by=["function"])
        df = df.astype({"tested": "str"})
        df["tested"] = df["tested"].apply(
            lambda x: "[red]False[/red]" if x == "False" else "[green]True[/green]"
        )
        print_rich_table(
            df,
            headers=[x.title() for x in df.columns],
            show_index=False,
            title=f"Integration test coverage: {coverage}%",
            automatic_coloring=True,
            columns_to_auto_color=["tested"],
        )
    else:
        console.print(
            f"Integration test coverage: {coverage}%\n"
            f"=============================\n"
            f"[red]Untested functions: {untested_functions}[/red]\n"
            f"[green]Tested functions: {tested_functions}[/green]\n"
            f"=============================\n"
        )


def get_coverage_all_controllers() -> None:
    """Test all controllers."""
    controllers = pd.read_json("controllers.json")

    for controller in controllers:
        if controllers[controller]["integration_test"] == "":
            console.print(
                f"[red]No integration test found for the {controller} controller.[/red]"
            )
        else:
            path = controller.replace("/", ".")
            path = "openbb_terminal" + path
            try:
                module = get_module(path)
            except ModuleNotFoundError:
                try:
                    module = get_module(
                        path, module_name=controllers[controller]["module_name"]
                    )
                except ModuleNotFoundError:
                    console.print(f"Module for {controller} not found.")

            available_functions = get_functions(module)
            tested_functions = get_tested_functions(
                INTEGRATION_PATH + controllers[controller]["integration_test"]
            )
            console.print(f"Calculating coverage for {controller}...")
            calculate_coverage_percentage(
                tested_functions, available_functions, output_table=False
            )


def get_coverage_single_controller(
    controller: str,
    integration_test: str,
    module_name: str = "",
    output_table: bool = False,
) -> None:
    """Test single controller coverage.

    Parameters
    ----------
        controller (str): Controller to test.
        integration_test (str): Integration test to use.
        output_table (bool): Output a table with the results.

    Example:
    --------
        test_single_controller(
            "openbb_terminal.stocks.stocks_controller",
            "/stocks/test_stocks.openbb"
        )

    """
    module = get_module(controller, module_name=module_name)
    functions = get_functions(module)
    tested_functions = get_tested_functions(INTEGRATION_PATH + integration_test)
    calculate_coverage_percentage(tested_functions, functions, output_table)
