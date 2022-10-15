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
    # WHAT'S THE PURPOSE OF THIS BELOW?
    for param in range(len(parameters_values) - 1):
        parameters_values[param] = parameters_values[param][:-1]

    if "report_name" in parameters_names:
        parameters_names.remove("report_name")

    parameters_dict = dict(zip(parameters_names, parameters_values))

    return parameters_dict


@log_start_end(log=logger)
def produce_report(report_name: str, other_args: List[str] = None):
    """Report production end to end.

    Parameters
    ----------
    report_name: str
        Name of report to run.
    other_args: List[str]
        List containing others args, for example parameters to be used in report.

    """

    input_path = str(REPORTS_FOLDER / report_name)
    output_path = get_output_path(report_name, other_args)
    parameters = get_parameters(report_name, other_args, output_path)

    if parameters:
        try:
            execute_notebook(input_path, output_path, parameters)
        except Exception as e:
            console.print(f"[red]Cannot execute notebook - {e}")


@log_start_end(log=logger)
def get_output_path(report_name: str, other_args: List[str]) -> str:
    """Get path to save rendered report, thus the output path.

    Parameters
    ----------
    report_name: str
        Name of report to run.
    other_args: List[str]
        List containing others args, for example parameters to be used in report.

    Returns
    -------
    str
        Path of rendered report.

    """

    args_to_output = f"_{'_'.join(other_args)}" if "_".join(other_args) else ""
    report_output_name = (
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        + "_"
        + f"{report_name}{args_to_output}"
    )
    output_path = str(OUTPUT_FOLDER / report_output_name)

    return output_path


@log_start_end(log=logger)
def get_parameters(
    report_name: str, other_args: List[str], output_path: str
) -> Dict[str, Any]:
    """Get dictionary of parameters to be used in report.

    Parameters
    ----------
    report_name: str
        Name of report to run.
    other_args: List[str]
        List containing others args, for example parameters to be used in report.
    output_path: str
        Path of rendered report.

    Returns
    -------
    Dict[str, Any]
        Dictionary with report parameters.

    """

    parameters_dict = extract_parameters(report_name)
    parameters_names = list(parameters_dict.keys())

    if len(other_args) != len(parameters_names):
        console.print("Wrong number of arguments provided!")
        if len(parameters_names):
            console.print("Provide, in order:")
            for k, v in enumerate(parameters_names):
                console.print(f"{k+1}. {v}")
        else:
            console.print("No argument required.")
        console.print("")
        return {}

    report_params = {}
    for idx, args in enumerate(parameters_names):
        report_params[args] = other_args[idx]

    report_params["report_name"] = output_path

    return report_params


@log_start_end(log=logger)
def execute_notebook(input_path, output_path, parameters):
    """Execute the input path's notebook with the parameters provided.
    Then, save it in the output path.

    Parameters
    ----------
    input_path: str
        Path of report to be rendered.
    output_path: str
        Path of rendered report.
    parameters: Dict[str, Any]
        Dictionary with report parameters.

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
