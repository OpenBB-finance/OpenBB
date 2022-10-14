"""Reports Model Module."""
__docformat__ = "numpy"

import logging

# pylint: disable=R1732, R0912
import os
from pathlib import Path
import webbrowser
from ast import literal_eval
from datetime import datetime
from typing import Any, Dict, List, Tuple
import papermill as pm

from openbb_terminal import feature_flags as obbff
from openbb_terminal.core.config.paths import USER_EXPORTS_DIRECTORY
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

CURRENT_LOCATION = Path(__file__)
REPORTS_FOLDER = CURRENT_LOCATION.parent / "templates"
OUTPUT_FOLDER = USER_EXPORTS_DIRECTORY / "reports"


@log_start_end(log=logger)
def extract_parameters(report_name: str) -> Tuple[List[str], List[str]]:
    """Extract required parameters from notebook content.

    Parameters
    ----------
    notebook_content: str
        Text content of Jupyter notebook.

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

    return parameters_names, parameters_values


@log_start_end(log=logger)
def produce_report(report_to_run: str, other_args: List[str] = None):
    """Report production end to end.

    Parameters
    ----------
    known_args: Namespace
        Namespace containing the known arguments received.
        E.g. Namespace(cmd='economy') or Namespace(cmd='4')
    other_args: List[str]
        List containing others args, for example parameters to be used in report.

    """

    input_path = get_input_path(report_to_run)
    output_path = get_output_path(report_to_run, other_args)
    parameters = get_parameters(report_to_run, other_args, output_path)

    if parameters:
        execute_notebook(input_path, output_path, parameters)


@log_start_end(log=logger)
def get_input_path(report_to_run: str) -> str:
    """Get path of specified report to run, thus the input path.

    Parameters
    ----------
    report_to_run: str
        Name of report to run.

    Returns
    -------
    str
        Path of report to be rendered.

    """

    input_path = str(REPORTS_FOLDER / report_to_run)

    return input_path


@log_start_end(log=logger)
def get_output_path(report_to_run: str, other_args: List[str]) -> str:
    """Get path to save rendered report, thus the output path.

    Parameters
    ----------
    report_to_run: str
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
        + f"{report_to_run}{args_to_output}"
    )
    output_path = str(OUTPUT_FOLDER / report_output_name)

    return output_path


@log_start_end(log=logger)
def get_parameters(
    report_to_run: str, other_args: List[str], output_path: str
) -> Dict[str, Any]:
    """Get dictionary of parameters to be used in report.

    Parameters
    ----------
    report_to_run: str
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

    params, _ = extract_parameters(report_to_run)

    if len(other_args) != len(params):
        console.print("Wrong number of arguments provided!")
        if len(params):
            console.print("Provide, in order:")
            for k, v in enumerate(params):
                console.print(f"{k+1}. {v}")
        else:
            console.print("No argument required.")
        console.print("")
        return {}

    report_params = {}
    for idx, args in enumerate(params):
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

    result = pm.execute_notebook(
        input_path=input_path + ".ipynb",
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
