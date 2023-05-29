"""Obtain the integration test coverage for the OpenBB Terminal."""

# IMPORT STANDARD
import importlib
import json
import os
import re
from pathlib import Path

# IMPORT THIRD-PARTY
import pandas as pd

from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY

# IMPORT INTERNAL
from openbb_terminal.core.integration_tests.utils import (
    SECTION_LENGTH,
    get_submodule_commands,
    map_module_to_calls,
    to_section_title,
    validate_missing_params,
)
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.rich_config import console

INTEGRATION_PATH = os.path.join(MISCELLANEOUS_DIRECTORY, "integration_tests_scripts")
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
    path = os.path.join(".", "openbb_terminal")
    for root, _, files in os.walk(path):
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
        re.sub(r"^\.\\openbb_terminal\\miscellaneous\\integration_tests_scripts", "", i)
        for i in test
    ]
    return test


def create_matching_dict() -> dict:
    """Fill the controller and integration test matches by outlier files."""
    controller_paths = [
        os.path.join(
            ".", "openbb_terminal", "mutual_funds", "mutual_fund_controller.py"
        ),
        os.path.join(
            ".", "openbb_terminal", "stocks", "discovery", "disc_controller.py"
        ),
        os.path.join(
            ".",
            "openbb_terminal",
            "stocks",
            "options",
            "screen",
            "screener_controller.py",
        ),
        os.path.join(".", "openbb_terminal", "terminal_controller.py"),
        os.path.join(
            ".", "openbb_terminal", "stocks", "comparison_analysis", "ca_controller.py"
        ),
    ]
    test_paths = [
        os.path.join("mutual_funds", "test_mutual_fund.openbb"),
        os.path.join("stocks", "test_disc.openbb"),
        os.path.join("stocks", "test_options_screen_ca.openbb"),
        os.path.join("terminal", "test_news.openbb"),
        os.path.join("stocks", "test_ca.openbb"),
    ]
    return dict(zip(controller_paths, test_paths))


def match_controller_with_test(controllers: list, tests: list) -> dict:
    """Match controllers with integration tests."""
    matched = create_matching_dict()

    for key, value in matched.items():
        controllers.remove(key)
        tests = [i for i in tests if value not in i]

    for controller in controllers:
        controller_name = os.path.split(Path(controller))[-1].split("_controller.py")[0]

        for test in tests:
            test_name = os.path.split(Path(test))[-1][5:-7]

            if controller_name == test_name:
                matched[controller] = test
                tests.remove(test)

    for i in tests:
        # Handle edge case as two controllers share the same integration test
        if re.search(r"test_ca.openbb", i):
            tests.remove(i)

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
    commands: list = []
    try:
        module = module()  # type: ignore
    except TypeError:
        commands = get_submodule_commands(module)
        params = map_module_to_calls(module)
        if get_commands and get_params:
            return commands, params
        if get_commands and not get_params:
            return commands
        if not get_commands and get_params:
            return params

    module_data = getattr(module, "choices_default")
    if len(commands) == 0:
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


def calculate_parameter_coverage(
    tested_function: str, module: object
) -> tuple[dict, dict]:
    """Calculate the parameter coverage for controller commands."""
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

    return missing_params, coverage_dict


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

    for controller, integration_test in matched.items():
        if "/" in controller:
            path = controller.replace("/", ".")[2:-3]
        elif "\\" in controller:
            path = controller.replace("\\", ".")[2:-3]
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

        try:
            available_commands = get_commands_and_params(module, get_params=False)
        except TypeError:
            continue

        file_path = os.path.join(INTEGRATION_PATH, integration_test)
        if not os.path.isfile(file_path):
            file_path = os.path.join(INTEGRATION_PATH, integration_test[1:])

        tested_commands = get_tested_commands(file_path)
        command_coverage, untested_commands = calculate_command_coverage(
            tested_commands, available_commands
        )

        missing_params, coverage_dict = calculate_parameter_coverage(
            tested_function=file_path,
            module=module,
        )
        missing_params = validate_missing_params(missing_params, test_file=file_path)

        try:
            average_parameter_coverage = round(
                sum(coverage_dict.values()) / len(coverage_dict), 2
            )
        except ZeroDivisionError:
            average_parameter_coverage = 100

        controller_coverage = calculate_controller_coverage(
            command_coverage=command_coverage,
            average_parameter_coverage=average_parameter_coverage,
        )

        summary[controller] = {
            "Controller coverage": controller_coverage,
            "Command coverage": command_coverage,
            "Parameter coverage": average_parameter_coverage,
        }

        console.print(to_section_title(controller), "\n")
        console.print(
            f"Controller coverage: {controller_coverage}%\n"
            + f"Command coverage: {command_coverage}%\n"
            + f"Parameter coverage: {average_parameter_coverage}%"
        )

        display_uncovered_commands(
            missing_params,
            untested_commands,
            coverage_dict,
            output_table,
        )

        console.print(
            f"* Finished calculating integration test coverage for {controller}\n\n"
        )

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
            summary.items(), key=lambda item: item[1]["Controller coverage"], reverse=False  # type: ignore
        )
    )
    for controller_name, value in summary.items():
        controller_coverage = value["Controller coverage"]
        command_coverage = value["Command coverage"]
        parameter_coverage = value["Parameter coverage"]

        len_res = len(str(controller_coverage)) + len("Controller coverage: %")
        spaces = SECTION_LENGTH - len(controller_name) - len_res

        console.print(
            f"{controller_name}" + spaces * " ",
            f"Controller coverage: {controller_coverage}%",
            f"\n* Command coverage: {command_coverage}%",
            f"\n* Parameter coverage: {parameter_coverage}%",
        )


def display_uncovered_commands(
    missing_params: dict,
    untested_commands: list,
    coverage_dict: dict,
    output_table: bool,
) -> None:
    """Display the uncovered commands."""
    missing_commands = []
    for command in missing_params:
        if command not in untested_commands:
            missing_commands.append(command)

    for command in untested_commands:
        if command not in missing_params:
            missing_commands.append(command)

    if output_table:
        df = pd.DataFrame()
        df["Command"] = missing_commands
        df["Missing params"] = [  # pylint: disable=unsupported-assignment-operation
            "all params missing"
            if command in untested_commands
            else missing_params[command]
            for command in missing_commands
        ]
        df["Coverage"] = [
            0 if command in untested_commands else coverage_dict[command]
            for command in missing_commands
        ]
        df = df.sort_values(by=["Coverage"], ascending=True)
        df["Coverage"].astype(str)
        df["Coverage"] = df[  # pylint: disable=unsupported-assignment-operation
            "Coverage"
        ].apply(lambda x: f"[red]{x}[/red]" if x < 80 else f"[green]{x}[/green]")
        df = df[["Command", "Coverage", "Missing params"]]
        try:
            print_rich_table(df, title="Uncovered commands and parameters")
        except IndexError:
            console.print("\nNo uncovered commands found!")


def calculate_controller_coverage(
    command_coverage: float,
    average_parameter_coverage: float,
) -> float:
    """Calculate the global coverage."""
    controller_coverage = (command_coverage * average_parameter_coverage) / 100

    return round(controller_coverage, 2)


def get_coverage_single_controller(
    controller: str,
    integration_test: str,
    module_name: str = "",
    output_table: bool = True,
) -> None:
    """Get single controller integration test coverage.

    Parameters
    ----------
        controller (str): Controller to test.
        integration_test (str): Integration test to use.
        output_table (bool): Output a table with the detailed results.

    Example:
    --------
        test_single_controller(
            "openbb_terminal.stocks.stocks_controller",
            "/stocks/test_stocks.openbb"
        )

    """
    module = get_module(controller, module_name=module_name)
    available_commands = get_commands_and_params(module, get_params=False)

    file_path = os.path.join(INTEGRATION_PATH, integration_test)
    if not os.path.isfile(file_path):
        file_path = os.path.join(INTEGRATION_PATH, integration_test[1:])

    tested_commands = get_tested_commands(file_path)
    command_coverage, untested_commands = calculate_command_coverage(
        tested_commands, available_commands
    )

    missing_params, coverage_dict = calculate_parameter_coverage(
        tested_function=file_path,
        module=module,
    )
    missing_params = validate_missing_params(missing_params, test_file=file_path)

    try:
        average_parameter_coverage = round(
            sum(coverage_dict.values()) / len(coverage_dict), 2
        )
    except ZeroDivisionError:
        average_parameter_coverage = 100

    controller_coverage = calculate_controller_coverage(
        command_coverage=command_coverage,
        average_parameter_coverage=average_parameter_coverage,
    )

    console.print(to_section_title(controller), "\n")
    console.print(
        f"Controller coverage: {controller_coverage}%\n"
        + f"Command coverage: {command_coverage}%\n"
        + f"Parameter coverage: {round(average_parameter_coverage, 2)}%"
    )

    display_uncovered_commands(
        missing_params,
        untested_commands,
        coverage_dict,
        output_table,
    )


if __name__ == "__main__":
    get_coverage_all_controllers()
