"""Obtain the integration test coverage for the OpenBB Terminal."""

# IMPORT STANDARD
import importlib
import json
import os
import re
from pathlib import Path

# IMPORT THIRD-PARTY
import pandas as pd

from openbb_terminal.core.integration_tests.utils import (
    SECTION_LENGTH,
    to_section_title,
)

# IMPORT INTERNAL
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console

INTEGRATION_PATH = "./openbb_terminal/miscellaneous/integration_tests_scripts"
COMMAND_FILTERS = [
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
    "h",
    "e",
    "q",
    "r",
    "?",
]


def find_controllers() -> list:
    """Find all controllers in the OpenBB Terminal."""
    controllers = []

    for root, _, files in os.walk("./openbb_terminal"):
        for file in files:
            if file.endswith("_controller.py") and "sdk" not in root:
                controllers.append(os.path.join(root, file))

    return controllers


def find_integration_tests() -> list:
    """Find all integration tests in the OpenBB Terminal."""
    test = []
    for root, _, files in os.walk(INTEGRATION_PATH):
        for file in files:
            if file.endswith(".openbb"):
                test.append(os.path.join(root, file))

    test = [
        re.sub(r"^\./openbb_terminal/miscellaneous/integration_tests_scripts", "", i)
        for i in test
    ]
    return test


def create_matching_dict() -> dict:
    """Fill the controller and integration test matches by outlier files."""
    return {
        "./openbb_terminal/mutual_funds/mutual_fund_controller.py": "/mutual_funds/test_mutual_fund.openbb",
        "./openbb_terminal/stocks/options/screen/screener_controller.py": "/stocks/test_screen.openbb",
        "./openbb_terminal/stocks/discovery/disc_controller.py": "/stocks/test_disc.openbb",
    }


def match_controller_with_test(controllers: list, tests: list) -> dict:
    """Match controllers with integration tests."""
    matched = create_matching_dict()

    for key, value in matched.items():
        controllers.remove(key)
        tests.remove(value)

    for controller in controllers:
        try:
            controller_name = re.search(  # type: ignore
                r"(?<=/)[a-zA-Z]+(?=_controller)", controller
            ).group(0)
        except AttributeError:
            controller_name = "mutual_fund"

        for test in tests:
            try:
                test_name = re.search(r"(?<=/test_)[a-zA-Z]+(?=.openbb)", test).group(0)  # type: ignore
            except AttributeError:
                test_name = "mutual_fund"

            if controller_name == test_name:
                if controller_name in ["ta", "qa"]:
                    controller_path = re.search(  # type: ignore
                        r"(?<=openbb_terminal/)[a-zA-Z/]+(?=/)", controller
                    ).group(0)
                    if controller_path in test:
                        matched[controller] = test
                        tests.remove(test)
                else:
                    matched[controller] = test
                    tests.remove(test)

    if len(tests) > 0:
        console.print(f"[red]Unmatched tests: {tests}[/red]")

    return matched


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


def get_commands_and_params(
    module: object, get_commands: bool = True, get_params: bool = True
):
    """Get all commands from a given module."""
    params: dict = {}

    module = module()  # type: ignore
    module_data = getattr(module, "choices_default")
    commands = list(module_data.keys())
    commands = [command for command in commands if command not in COMMAND_FILTERS]

    for command in commands:
        params[command] = []
        try:
            params[command] = list(module_data[command].keys())
        except AttributeError:
            pass
    if get_commands and get_params:
        return commands, params
    if get_commands and not get_params:
        return commands
    if not get_commands and get_params:
        return params

    return None


def get_tested_commands(test_file: str) -> list:
    """Obtain all functions that are called in a given test file."""
    tested_commands = []
    with open(test_file) as f:
        for line in f:
            try:
                function = line.split()[0]
            except IndexError:
                continue

            if function != "#":
                tested_commands.append(function)

    tested_commands = list(dict.fromkeys(tested_commands))
    return list(tested_commands)


def get_tested_command_params(test_file: str) -> list:
    """Obtain all function parameters that are called in a given test file."""
    tested_commands = []
    with open(test_file) as f:
        for line in f:
            try:
                function = line.split()[0]
            except IndexError:
                continue

            params = re.findall(r"-\w+", line)
            tested_commands.append((function, params))
    return tested_commands


def get_missing_params(
    tested_command_params: list, controller: str, module_dict: dict
) -> dict:
    """Get missing parameters for a given function."""
    missing_params = {}
    for function, params in tested_command_params:
        if function != controller:
            try:
                all_params = module_dict[function]
                all_params = [param.replace("--", "-") for param in all_params]
            except KeyError:
                # this catches the (sub)menu
                continue

            if set(params).issubset(set(all_params)):
                all_params = [param for param in all_params if param not in params]
                for param in params:
                    if param in all_params:
                        all_params.remove(param)
            else:
                unpacked_params = []
                used_unabbreviated_params = []
                for param in params:
                    unpacked_params.append(param)

                for param in unpacked_params:
                    for unabbreviated_param in all_params:
                        if unabbreviated_param.startswith(param):
                            used_unabbreviated_params.append(unabbreviated_param)

                missing_params[function] = [
                    param for param in all_params if param not in params
                ]

                for param in all_params:
                    for param2 in used_unabbreviated_params:
                        if param2.startswith(param):
                            try:
                                missing_params[function].remove(param)
                                missing_params[function].remove(param2)
                            except ValueError:
                                pass

                missing_params[function] = [
                    param
                    for param in missing_params[function]
                    if param not in used_unabbreviated_params
                ]

            try:
                missing_params[function] = list(dict.fromkeys(missing_params[function]))
            except KeyError:
                # this catches the (sub)menu
                continue

    for key, value in missing_params.items():
        missing_params[key] = list(value)
        for param in value:
            for param2 in value:
                if param != param2 and param2.startswith(param):
                    try:
                        missing_params[key].remove(param)
                    except ValueError:
                        pass

    missing_params = {k: v for k, v in missing_params.items() if v}

    return missing_params


def display_parameter_coverage(
    coverage_dict: dict, missing_params: dict, limit: int = 5, output_table: bool = True
) -> None:
    if output_table:
        df = pd.DataFrame(
            coverage_dict.items(),
            columns=["Command", "Coverage %"],
        ).sort_values(by=["Coverage %"], ascending=True)
        average_coverage = round(df["Coverage %"].mean(), 2)
        df["Coverage %"] = df[  # pylint: disable=unsupported-assignment-operation
            "Coverage %"
        ].apply(lambda x: f"[green]{x}[/green]" if x >= 80 else f"[red]{x}[/red]")
        df["Missing params"] = (  # pylint: disable=unsupported-assignment-operation
            df["Command"].map(missing_params).fillna("")
        )
        print_rich_table(
            df,
            headers=[
                "Command",
                "Coverage",
                "Missing params",
            ],
            limit=limit,
            title=f"* Integration test parameter coverage {average_coverage}%",
        )


def calculate_parameter_coverage(
    tested_function: str,
    module: object,
    limit: int = 5,
    output_table: bool = True,
) -> dict:
    """Compare tested functions with module."""
    module_dict = get_commands_and_params(module, get_commands=False)

    tested_command_params = get_tested_command_params(tested_function)
    for key, value in dict(tested_command_params).items():
        dict(tested_command_params)[key] = list(set(value))
    tested_command_params = list(dict(tested_command_params).items())

    try:
        controller = str(module).split(".")[3].split("_")[0]
    except IndexError:
        controller = str(module).split(".")[2].split("_")[0]

    missing_params = get_missing_params(tested_command_params, controller, module_dict)

    coverage_dict = {}
    for key, value in missing_params.items():
        try:
            coverage_dict[key] = round(
                (len(module_dict[key]) - len(value)) / len(module_dict[key]) * 100, 2
            )
        except ZeroDivisionError:
            coverage_dict[key] = 100

    for key, value in module_dict.items():
        if key not in coverage_dict:
            coverage_dict[key] = 100

    if output_table:
        display_parameter_coverage(coverage_dict, missing_params, limit, output_table)

    if len(missing_params) > 0:
        console.print(f"[red]Missing params: {missing_params}[/red]")

    return missing_params


def display_command_coverage(
    available_commands: list,
    tested_commands: list,
    untested_commands: list,
    coverage: float,
    output_table: bool = False,
    limit: int = 10,
) -> None:
    """Display coverage."""
    if output_table:
        df = pd.DataFrame({"function": available_commands})
        df["tested"] = df["function"].apply(lambda x: x in tested_commands)
        df = df.sort_values(by=["function"])
        df = df.astype({"tested": "str"})
        df["tested"] = df["tested"].apply(
            lambda x: "[red]False[/red]" if x == "False" else "[green]True[/green]"
        )
        # sort df by Tested columns so that the first ones are False
        df = df.sort_values(by=["tested"], ascending=False)
        print_rich_table(
            df,
            headers=[x.title() for x in df.columns],
            show_index=False,
            title=f"* Integration test command coverage: {coverage}%",
            automatic_coloring=True,
            columns_to_auto_color=["tested"],
            limit=limit,
        )
    else:
        console.print(f"* Integration test command coverage: {coverage}%\n")
        console.print(f"[red]Untested commands: {untested_commands}[/red]")
        console.print(f"[green]Tested commands: {tested_commands}[/green]\n")


def calculate_command_coverage(
    tested_commands: list, available_commands: list
) -> tuple[float, list]:
    """Calculate the integration test coverage."""
    untested_commands = []
    for function in available_commands:
        if function not in tested_commands:
            untested_commands.append(function)

    try:
        coverage = round(
            (len(available_commands) - len(untested_commands))
            / len(available_commands)
            * 100,
            2,
        )
    except ZeroDivisionError:
        coverage = 100

    return coverage, untested_commands


def get_coverage_all_controllers(output_table: bool = True) -> None:
    """Get integration test coverage for all controllers."""
    summary = {}

    parent_dir = os.path.join(Path(__file__).parent)
    with open(os.path.join(parent_dir, "controllers.json")) as f:
        controller_name_mapping = json.load(f)

    controllers = find_controllers()
    tests = find_integration_tests()
    matched = match_controller_with_test(controllers, tests)

    for controller, test in matched.items():
        path = controller.replace("/", ".")[2:-3]
        try:
            module = get_module(path)
        except ModuleNotFoundError:
            module_name = controller_name_mapping.get(path, "")
            try:
                module = get_module(path, module_name=module_name)
            except ModuleNotFoundError:
                console.print(f"Module {module_name} not found!")
                continue
        except OSError as e:
            console.print(e)
            continue

        available_commands = get_commands_and_params(module, get_params=False)
        tested_commands = get_tested_commands(INTEGRATION_PATH + test)

        console.print(to_section_title(controller), "\n")
        coverage, untested_commands = calculate_command_coverage(
            tested_commands, available_commands
        )
        display_command_coverage(
            available_commands,
            tested_commands,
            untested_commands,
            coverage,
            output_table,
        )
        missing_params = calculate_parameter_coverage(
            tested_function=INTEGRATION_PATH + test, module=module
        )

        console.print(f"* Finished calculating coverage for {controller}\n\n")

        summary[controller] = {
            "Coverage": coverage,
            "Untested commands": untested_commands,
            "Missing params": missing_params,
        }

    display_coverage_summary(summary)


def display_coverage_summary(summary: dict) -> None:
    """Display the coverage summary.

    Parameters
    ----------
    summary: dict
        Summary of the integration test coverage.
    """

    console.print(to_section_title("Integration Coverage Summary"))
    summary = dict(
        sorted(
            summary.items(), key=lambda item: item[1]["Coverage"], reverse=False  # type: ignore
        )
    )
    for controller_name, value in summary.items():
        coverage = value["Coverage"] / 100
        coverage_percentage = f"{coverage:.0%}"

        untested = value.get("Untested commands", [])
        len_untested = len(untested)
        missing = value.get("Missing params", {})
        len_missing = len(missing)

        len_res = len(coverage_percentage) + len_untested
        spaces = SECTION_LENGTH - len(controller_name) - len_res

        console.print(
            f"{controller_name}"
            + spaces * " "
            + f"{coverage_percentage}, {len_untested}"
            + f"missing params: {len_missing}"
        )


def get_coverage_single_controller(
    controller: str,
    integration_test: str,
    module_name: str = "",
    output_table: bool = False,
) -> None:
    """Get single controller integration test coverage.

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
    available_commands = get_commands_and_params(module, get_params=False)
    tested_commands = get_tested_commands(INTEGRATION_PATH + integration_test)
    coverage, untested_commands = calculate_command_coverage(
        tested_commands, available_commands
    )
    display_command_coverage(
        available_commands, tested_commands, untested_commands, coverage, output_table
    )
    calculate_parameter_coverage(
        tested_function=INTEGRATION_PATH + integration_test,
        module=module,
        output_table=output_table,
    )


# get_coverage_single_controller(
#     "openbb_terminal.economy.economy_controller",
#     "/economy/test_economy.openbb",
#     output_table=False,
# )
