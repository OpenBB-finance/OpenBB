"""Reports Model Module."""
__docformat__ = "numpy"

import logging

# pylint: disable=R1732, R0912
import os
from datetime import datetime
from pathlib import Path
from threading import Thread
from typing import Any, Dict, List, Union

import nbformat
import pandas as pd
import papermill as pm
from ipykernel.kernelapp import IPKernelApp

from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
)
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import log_start_end
from openbb_terminal.forex.forex_controller import FX_TICKERS
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

CURRENT_LOCATION = Path(__file__)
REPORTS_FOLDER = CURRENT_LOCATION.parent / "templates"

USER_REPORTS = {
    filepath.name: filepath
    for file_type in ["ipynb"]
    for filepath in get_current_user().preferences.USER_CUSTOM_REPORTS_DIRECTORY.rglob(
        f"*.{file_type}"
    )
}

# TODO: Trim available choices to avoid errors in notebooks.

etf_data_path = CURRENT_LOCATION.parent / "data" / "etf_tickers.csv"
ETF_TICKERS = pd.read_csv(etf_data_path).iloc[:, 0].to_list()

crypto_data_path = CURRENT_LOCATION.parent / "data" / "crypto_tickers.csv"
CRYPTO_TICKERS = pd.read_csv(crypto_data_path).iloc[:, 0].to_list()

stocks_data_path = CURRENT_LOCATION.parent / "data" / "stocks_tickers.csv"
STOCKS_TICKERS = pd.read_csv(stocks_data_path).iloc[:, 0].to_list()

PORTFOLIO_HOLDINGS_FILES = {
    filepath.name: filepath
    for file_type in ["xlsx", "csv"]
    for filepath in (
        get_current_user().preferences.USER_PORTFOLIO_DATA_DIRECTORY / "holdings"
    ).rglob(f"*.{file_type}")
}

PORTFOLIO_HOLDINGS_FILES.update(
    {
        "holdings_example.xlsx": MISCELLANEOUS_DIRECTORY
        / "portfolio"
        / "holdings_example.xlsx"
    }
)

REPORT_CHOICES = {
    "etf": {
        "--symbol": {c: None for c in ETF_TICKERS},
    },
    "forex": {
        "--symbol": {c: None for c in FX_TICKERS},
    },
    "portfolio": {
        "--transactions": {c: None for c in PORTFOLIO_HOLDINGS_FILES},
    },
    "economy": None,
    "equity": {
        "--symbol": {c: None for c in STOCKS_TICKERS},
    },
    "crypto": {
        "--symbol": {c: None for c in CRYPTO_TICKERS},
    },
    "forecast": {
        "--symbol": {c: None for c in STOCKS_TICKERS + ETF_TICKERS},
    },
}
TARGET_TAG = "parameters"


@log_start_end(log=logger)
def get_arg_choices(report_name: str, arg_name: str) -> Union[List[str], None]:
    """Get argument choices from autocompletion for crypto, forex and portfolio.

    Parameters
    ----------
    report_name: str
        Name of report chosen.
    arg_name: str
        Argument to limit choices.

    Returns:
        List[str]: List with argument choices from autocompletion.
    """

    choices = None
    if report_name in ("forex", "portfolio") and "--" + arg_name in REPORT_CHOICES[report_name]:  # type: ignore
        choices = list(REPORT_CHOICES[report_name]["--" + arg_name].keys())  # type: ignore
    return choices


@log_start_end(log=logger)
def get_reports_available(
    folder: Path = REPORTS_FOLDER, warn: bool = True
) -> List[str]:
    """Get Jupyter notebook available in folder.

    Parameters
    ----------
    folder: Path
        Path to folder.

    Returns:
        List[str]: List with names of notebooks available.
    """

    bad_format = []
    available = []

    for notebook in os.listdir(folder):
        if notebook.endswith(".ipynb"):
            if " " in notebook:
                bad_format.append(notebook)
            else:
                available.append(notebook[:-6])

    if bad_format and warn:
        s = ", ".join(bad_format)
        console.print(
            f"[red]Character '_' not allowed in the following names: {s}.[/red]"
        )

    return available


@log_start_end(log=logger)
def extract_parameters(input_path: str) -> Dict[str, str]:
    """Extract required parameters from notebook content.

    Parameters
    ----------
    input_path: str
        Path of report to be rendered.

    Returns:
        Dict[str, str]: Dictionary with parameters names and values.
    """

    input_path = add_ipynb_extension(input_path)

    with open(input_path) as f:
        nb = nbformat.read(f, as_version=nbformat.NO_CONVERT)

    target_tag = TARGET_TAG

    cell_lines = []
    for cell in nb.cells:
        # Filter cells by tag
        if target_tag in cell.metadata.get("tags", []):
            # Split cell source into separate lines
            lines = cell.source.split("\n")
            # Remove empty and commented lines
            lines = [
                line for line in lines if line.strip() and not line.startswith("#")
            ]
            cell_lines.extend(lines)

    parameters_dict = {}
    for line in cell_lines:
        # Extract key and value from each line
        key, value = line.split("=")
        key = key.strip()
        value = value.strip()
        # Add key-value pair to dictionary and remove quotes
        parameters_dict[key] = value.replace('"', "")

    if "report_name" in parameters_dict:
        parameters_dict.pop("report_name")

    return parameters_dict


@log_start_end(log=logger)
def render_report(input_path: str, args_dict: Dict[str, str]):
    """Report rendering end to end.

    Workflow:
        1. Update parameters to use in notebook with received arguments
        2. Create output path
        3. Update parameters with output_path
        4. Validate and execute notebook in a new thread.

    Parameters
    ----------
    input_path: str
        Path of report to be rendered.
    args_dict: Dict[str, str]
        Dictionary with received arguments dictionary.
    """

    try:
        parameters_dict = update_parameters(input_path, args_dict)
        output_path = create_output_path(input_path, parameters_dict)
        parameters_dict["report_name"] = output_path
        if parameters_dict:
            try:
                t = Thread(
                    target=execute_notebook,
                    args=(input_path, parameters_dict, output_path),
                    daemon=True,
                )
                t.start()
                t.join()
            except KeyboardInterrupt:
                console.print("[red]Execution interrupted by user.[/red]")
    except Exception as e:
        console.print(f"[red]Cannot execute notebook - {e}")


@log_start_end(log=logger)
def update_parameters(input_path: str, args_dict: Dict[str, str]) -> Dict[str, Any]:
    """Update dictionary of parameters to be used in report with received arguments.

    Parameters
    ----------
    input_path: str
        Path of report to be rendered.
    args_dict: Dict[str, str]
        Dictionary with received arguments dictionary.

    Returns
    -------
    Dict[str, Any]
        Dictionary with report parameters.
    """

    parameters_dict = extract_parameters(input_path)
    for key, val in args_dict.items():
        if key in parameters_dict:
            parameters_dict[key] = val
        else:
            console.print(f"[red]'{key}' not found in notebook parameters.[/red]")

    return parameters_dict


@log_start_end(log=logger)
def create_output_path(input_path: str, parameters_dict: Dict[str, Any]) -> str:
    """Create path to save rendered report, thus the output path.

    Parameters
    ----------
    input_path: str
        Path of report to be rendered.
    parameters_dict: Dict[str, Any]
        Dictionary with report parameters.

    Returns
    -------
    str
        Path of rendered report.
    """

    report_name = os.path.split(input_path)[-1]
    param_values = list(parameters_dict.values())
    args_to_output = f"_{'_'.join(param_values)}" if "_".join(param_values) else ""
    report_output_name = (
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        + "_"
        + f"{report_name}{args_to_output}"
    )
    report_output_name = report_output_name.replace(".", "_")
    output_path = str(
        get_current_user().preferences.USER_REPORTS_DIRECTORY / report_output_name
    )

    return output_path


@log_start_end(log=logger)
def execute_notebook(input_path, parameters, output_path):
    """Execute the input path's notebook with the parameters provided.
    Then, save it in the output path.

    Parameters
    ----------
    input_path: str
        Path of report to be rendered.
    parameters: Dict[str, Any]
        Dictionary with report parameters.
    output_path: str
        Path of rendered report.
    """

    input_path = add_ipynb_extension(input_path)

    try:
        result = pm.execute_notebook(
            input_path=input_path,
            output_path=output_path + ".ipynb",
            parameters=parameters,
        )

        if not result["metadata"]["papermill"]["exception"]:
            console.print(f"\n[green]Notebook:[/green] {output_path}.ipynb")
            if get_current_user().preferences.OPEN_REPORT_AS_HTML:
                report_output_path = os.path.join(
                    os.path.abspath(os.path.join(".")), output_path + ".html"
                )
                report_output_path = Path(report_output_path)

                plots_backend().send_url(
                    url=f"/{report_output_path.as_uri()}", title="Reports"
                )
                console.print(f"\n[green]Report:[/green] {report_output_path}\n")
            else:
                console.print("\n")
        else:
            console.print("[red]\nReport .html couldn't be created.\n[/red]")

    except pm.PapermillExecutionError as e:
        console.print(
            f"[red]\nAn error was encountered in cell [{e.exec_count}], check the notebook:[/red]\n"
            f"{output_path}.ipynb\n"
        )


@log_start_end(log=logger)
def add_ipynb_extension(path: str) -> str:
    """Add .ipynb extension to path.
    Parameters
    ----------
    path: str
        Path to notebook file.

    Returns
    -------
    str
        Path to .ipynb file.
    """

    if not path.endswith(".ipynb"):
        return path + ".ipynb"
    return path


@log_start_end(log=logger)
def check_ipynb(path: str) -> str:
    """Check if there is .ipynb extension in path.
    This is useful to the controller type check.

    Parameters
    ----------
    path: str
        Path to notebook file.

    Returns
    -------
    bool
        Path if paths endswith .ipynb, else empty string.
    """

    if not path.endswith(".ipynb"):
        console.print("[red]Please provide a .ipynb file.[/red]\n")
        return ""
    return path


def ipykernel_launcher(module_file: str, module_hist_file: str):
    """This function mocks 'ipykernel_launcher.py' launching a Jupyter notebook kernel.

    It is useful when running python commands inside a frozen application like our
    installer distribution, where sys.executable[0] is not the path to python
    interpreter, rather it is the path to the application executable.

    Problem:
        'papermill' was trying to execute the following command on a subprocess:
        $ .../bin/python -m ipykernel_launcher -f ... --HistoryManager.hist_file ...

        'papermill' was using '.../bin/python' because it is looks for the sys.executable[0],
        which most of the time leads to the python interpreter. In our frozen app,
        sys.executable[0] leads to 'OpenBB Terminal/.OpenBB/OpenBBTerminal', which in turn
        executes 'terminal.py.

        This means that the command was being executed in 'terminal.py'. Consequently,
        one gets the following error message:
        $ terminal: error: unrecognized arguments: -m ipykernel_launcher -f ... --HistoryManager.hist_file ...

    Solution:
        Parse 'papermill' command in the 'terminal_controller', which is what follows
        'terminal.py' and here receive the parsed 'papermill' command arguments and
        route them to IPKernelApp as if this is 'ipykernel_launcher' module
        - the kernel is launched.

    Source: https://pyinstaller.org/en/stable/runtime-information.html#using-sys-executable-and-sys-argv-0

    Parameters
    ----------
    module_file: str
        Specified connection file.
    module_hist_file: str
        History manager file.
    """
    # pylint: disable=import-outside-toplevel
    import matplotlib  # noqa

    matplotlib.use("agg")
    IPKernelApp.launch_instance(
        argv=[
            "-f",
            module_file,
            "--HistoryManager.hist_file",
            module_hist_file,
        ]
    )
