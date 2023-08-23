import importlib.util
import os
from datetime import datetime
from inspect import getmembers, isfunction
from pathlib import Path
from typing import Callable, List, Tuple

import pandas as pd

from openbb_terminal.core.config.paths import MAP_PATH
from openbb_terminal.rich_config import console

try:
    import darts  # pylint: disable=W0611 # noqa: F401

    # If you just import darts this will pass during pip install, this creates
    # Failures later on, also importing utils ensures that darts is installed correctly
    from darts import utils  # pylint: disable=W0611 # noqa: F401

    FORECASTING = True
except ImportError:
    FORECASTING = False

base_path = Path(__file__).parent.parent.parent.parent / "openbb_terminal"


def load_modules(full_path: Path):
    """Loads a module from a given Path.

    Parameter:
    ----------
    full_path: Path
        The path to the module

    Returns:
    ----------
    The python module
    """
    mod_path = str(full_path).split("OpenBBTerminal" + os.sep)[1].replace(os.sep, ".")
    spec = importlib.util.spec_from_file_location(mod_path, full_path)
    if not spec:
        raise ValueError(f"Could not import path: {full_path}")
    mod = importlib.util.module_from_spec(spec)
    if not mod:
        raise ValueError(f"Could not import path: {full_path}")
    if not spec.loader:
        raise ValueError(f"Could not import path: {full_path}")
    spec.loader.exec_module(mod)
    return mod


def all_view_models() -> List[Path]:
    """Geta all files with 'view' or 'model' in the name.

    Returns:
    ----------
    List[Path]
        All paths in openbb_terminal with 'view' or 'model' in the name
    """

    file_list = []
    all_files = os.walk(base_path)
    for root, _, files in all_files:
        for filename in files:
            if filename.endswith(".py") and ("view" in filename or "model" in filename):
                file_list.append(f"{root}/{filename}")
    clean_list = set(file_list)
    return [Path(x) for x in clean_list]


def get_sdk(file_path: Path = MAP_PATH) -> pd.DataFrame:
    """Reads the CSV that generates the sdk and converts it to a dataframe

    Parameters
    ----------
    file_path: str
        The path to the sdk csv

    Returns:
    ----------
    pd.DataFrame
        A dataframe with columns for sdk endpoint functiom and trail. Trails will be duplicated
        because there is a model and view function
    """
    df = pd.read_csv(base_path / file_path)
    df_dups = len(df["trail"]) - len(df["trail"].drop_duplicates())
    if df_dups > 0:
        console.print(f"Number of duplicate sdk paths: {df_dups}")
        console.print(
            "This indicates that the same SDK trail is being used multiple times\n"
        )
    views = list(df[["view", "trail"]].itertuples(index=False, name=None))
    models = list(df[["model", "trail"]].itertuples(index=False, name=None))
    # Add in whether it is a view or a model in pandas
    combined = [x + ("view",) for x in views] + [x + ("model",) for x in models]
    final_df = pd.DataFrame()
    final_df["name"] = [x[0] for x in combined]
    final_df["trail"] = [x[1] for x in combined]
    final_df["type"] = [x[2] for x in combined]
    final_df = final_df.dropna()
    final_df = final_df.set_index("name")
    return final_df


def format_function(function: Callable) -> Tuple[str, str]:
    """Gives a function a pretty name

    Parameters
    ----------
    function: Callable
        The function to get a pretty string for

    Returns:
    ----------
    Tuple[str, str]
        The functions pretty name and docstring
    """
    mod = str(function.__module__)[:-2].replace("/", ".")
    name = function.__name__
    if mod[-1] != ".":
        mod = f"{mod}."
    return f"{mod}{name}", str(function.__doc__)


def functions_df() -> pd.DataFrame:
    """Creates a dataframe for all functions in 'models' and 'views'.

    Returns:
    ----------
    pd.DataFrame
        Information for all view and model functions
    """
    modules = all_view_models()
    all_formatted = []
    for module in modules:
        if not FORECASTING and "forecast" in str(module):
            continue
        loaded = load_modules(module)
        # Gets all of a module's functions, but ignores imported functions
        func_list = [
            x[1]
            for x in getmembers(loaded, isfunction)
            if x[1].__module__ == loaded.__name__
        ]
        formatted_list = [format_function(x) for x in func_list]
        all_formatted.extend(formatted_list)
    func_df = pd.DataFrame()
    func_df["name"] = [x[0] for x in all_formatted]
    func_df["docstring"] = [x[1] for x in all_formatted]
    func_dups = len(func_df["name"]) - len(func_df["name"].drop_duplicates())
    if func_dups > 0:
        console.print(f"Number of duplicate functions found: {func_dups}")
        console.print(
            "This may indicate that functions are defined several times in the terminal.\n"
        )
    func_df = func_df.set_index("name")
    return func_df


def save_df(data: pd.DataFrame) -> None:
    timestamp = datetime.now().timestamp()
    time_str = (str(timestamp)).replace(".", "")
    output_path = f"{time_str}_sdk_audit.csv"
    data.to_csv(output_path)
    console.print(f"File saved to {output_path}")


def get_nonconforming_functions(data: pd.DataFrame) -> pd.DataFrame:
    """When we first check all functions we only look in model and view files. This means that any
    function in the helpers will be ignored. This function checks any helper funcs in the sdk
    treemap, so that we can get a clearer picture of whether or not functions exist

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe of all values, this will be searched

    Returns
    ----------
    pd.DataFrame
        The dataframe with any functions that could not be found
    """
    df = data[data["docstring"].isnull()]
    names = df.index.tolist()
    for name in names:
        path_list = name.split(".")
        file = "/".join(path_list[:-1])
        mod_path = Path(__file__).parent.parent.parent.parent / f"{file}.py"
        module = load_modules(mod_path)
        command = path_list[-1]
        function = getattr(module, command)
        if function:
            data.loc[name, "docstring"] = function.__doc__
    return data


def main():
    console.print(
        "This tool checks all functions in a file with a name including 'view' or 'model'against\n"
        "all functions in the sdk, which is gathered from 'trail_map.csv'. If the generated csv\n"
        "has an entry for 'trail' that means it is in the SDK, and if it has an entry for\n"
        "'docstring' it is in a model or view.\n"
    )
    funcs_df = functions_df()
    sdk_df = get_sdk()

    final_df = funcs_df.merge(sdk_df, how="outer", left_index=True, right_index=True)
    final_df = final_df.sort_values("name")
    final_df = get_nonconforming_functions(final_df)
    # Do this so that the duplicated method also checks the name column
    final_df = final_df.reset_index()
    # Get further stats on bad data
    no_doc_count = len(final_df[final_df["docstring"].isnull()].index)
    if no_doc_count > 0:
        console.print(f"The number of rows with blank docstrings is: {no_doc_count}")
        console.print(
            "This indicates a matching function does not exist, is not in a 'model' or 'view'\n"
            "file, or that the trailmap does not import it from the place it is defined.\n"
        )
    dup_name_count = len(final_df[final_df.duplicated(keep=False)].index)
    if dup_name_count > 0:
        console.print(
            f"The number of duplicate functions after merge is: {dup_name_count}"
        )
        console.print(
            "This most likely indicates that the same function is being used at "
            "different SDK endpoints.\n"
        )
    save_df(final_df)


if __name__ == "__main__":
    main()
