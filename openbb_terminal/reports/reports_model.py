"""Reports Model Module."""
__docformat__ = "numpy"

import logging

# pylint: disable=R1732, R0912
import os
from pathlib import Path
import webbrowser
from ast import literal_eval
from datetime import datetime
from typing import Any, Dict, List
import papermill as pm

from openbb_terminal import feature_flags as obbff
from openbb_terminal.core.config.paths import USER_EXPORTS_DIRECTORY
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

CURRENT_LOCATION = Path(__file__)
REPORTS_FOLDER = CURRENT_LOCATION.parent / "templates"
OUTPUT_FOLDER = USER_EXPORTS_DIRECTORY / "reports"

REPORT_CHOICES = {
    "etf": {
        "--symbol": {c: None for c in ["SPY"]},
    },
    "forex": {
        "--symbol": {c: None for c in ["EURUSD", "EURAUD"]},
    },
    "portfolio": {
        "--orderbook": {c: None for c in ["example.csv"]},
    },
    "economy": None,
    "equity": {
        "--symbol": {c: None for c in ["TSLA", "GME"]},
    },
    "crypto": {
        "--symbol": {c: None for c in ["BTCUSD"]},
    },
    "forecast": {
        "--symbol": {c: None for c in ["TSLA", "GME"]},
    },
}


def get_reports_available(folder: Path = REPORTS_FOLDER) -> List[str]:
    """Get Jupyter notebook available in folder.

    Parameters
    ----------
    folder: Path
        Path to folder.

    Returns:
        List[str]: List with names of notebooks available.
    """
    available = [
        notebooks[:-6]
        for notebooks in os.listdir(folder)
        if notebooks.endswith(".ipynb")
    ]

    return available


@log_start_end(log=logger)
def extract_parameters(report_name: str) -> Dict[str, str]:
    """Extract required parameters from notebook content.

    Parameters
    ----------
    report_name: str
        Name of report to run.

    """

    notebook_file = REPORTS_FOLDER / report_name
    with open(str(notebook_file) + ".ipynb") as file:
        notebook_content = file.read()

    # Look for the metadata cell to understand if there are parameters required by the report
    metadata_cell = """"metadata": {\n    "tags": [\n     "parameters"\n    ]\n   },\n   "outputs":"""

    # Locate position of the data of interest and get parameters
    metadata = notebook_content[notebook_content.find(metadata_cell) :]  # noqa: E203
    cell_start = 'source": '
    cell_end = "]"
    start_position = metadata.find(cell_start)
    params = metadata[
        start_position : metadata.find(cell_end, start_position) + 1  # noqa: E203
    ]

    # Make sure that the parameters provided are relevant
    if "parameters" in notebook_content:
        parameters_names = [
            param.split("=")[0][:-1]
            for param in literal_eval(params.strip('source": '))
            if param[0] not in ["#", "\n"]
        ]
        parameters_values = [
            param.split("=")[1][2:-1]
            for param in literal_eval(params.strip('source": '))
            if param[0] not in ["#", "\n"]
        ]

    # To ensure default value is correctly selected
    for param in range(len(parameters_values) - 1):
        parameters_values[param] = parameters_values[param][:-1]

    if "report_name" in parameters_names:
        parameters_names.remove("report_name")

    parameters_dict = dict(zip(parameters_names, parameters_values))

    return parameters_dict


@log_start_end(log=logger)
def produce_report(report_name: str, args_dict: Dict[str, str]):
    """Report production end to end.

    Workflow:
        1. Get input path
        2. Update parameters to use in notebook with received arguments
        3. Create output path
        4. Update parameters with output_path
        5. Validate and execute notebook

    Parameters
    ----------
    report_name: str
        Name of report to run.
    args_dict: Dict[str, str]
        Dictionary with received arguments dictionary.

    """

    input_path = get_input_path(report_name)
    parameters_dict = update_parameters(report_name, args_dict)
    output_path = create_output_path(report_name, parameters_dict)
    parameters_dict["report_name"] = output_path

    if parameters_dict:
        try:
            execute_notebook(input_path, output_path, parameters_dict)
        except Exception as e:
            console.print(f"[red]Cannot execute notebook - {e}")


@log_start_end(log=logger)
def get_input_path(report_name: str, folder: Path = REPORTS_FOLDER) -> str:
    """Get path to notebook, thus the input path.

    Parameters
    ----------
    report_name: str
        Name of report to run.
    folder: Path
        Path to folder.

    Returns
    -------
    str
        Path to notebook.

    """

    return str(folder / report_name)


@log_start_end(log=logger)
def update_parameters(report_name: str, args_dict: Dict[str, str]) -> Dict[str, Any]:
    """Update dictionary of parameters to be used in report with received arguments.

    Parameters
    ----------
    report_name: str
        Name of report to run.
    args_dict: Dict[str, str]
        Dictionary with received arguments dictionary.

    Returns
    -------
    Dict[str, Any]
        Dictionary with report parameters.

    """

    parameters_dict = extract_parameters(report_name)
    parameters_dict.update(args_dict)

    return parameters_dict


@log_start_end(log=logger)
def create_output_path(report_name: str, parameters_dict: Dict[str, Any]) -> str:
    """Create path to save rendered report, thus the output path.

    Parameters
    ----------
    report_name: str
        Name of report to run.
    parameters_dict: Dict[str, Any]
        Dictionary with report parameters.

    Returns
    -------
    str
        Path of rendered report.

    """

    param_values = list(parameters_dict.values())
    args_to_output = f"_{'_'.join(param_values)}" if "_".join(param_values) else ""
    report_output_name = (
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        + "_"
        + f"{report_name}{args_to_output}"
    )
    output_path = str(OUTPUT_FOLDER / report_output_name)

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

    if not input_path.endswith(".ipynb"):
        input_path = input_path + ".ipynb"

    result = pm.execute_notebook(
        input_path=input_path,
        output_path=output_path + ".ipynb",
        parameters=parameters,
        kernel_name="python3",
    )

    if not result["metadata"]["papermill"]["exception"]:
        if obbff.OPEN_REPORT_AS_HTML:
            report_output_path = os.path.join(
                os.path.abspath(os.path.join(".")), output_path + ".html"
            )
            console.print(report_output_path)
            webbrowser.open(f"file://{report_output_path}")

        console.print("")
        console.print(
            f"Exported: {report_output_path}",
            "\n",
        )
    else:
        console.print("[red]\nReport couldn't be created.\n[/red]")
