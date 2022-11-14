from inspect import getmembers, isfunction
from typing import List, Callable, Tuple
from datetime import datetime
import importlib.util
from pathlib import Path
import pandas as pd

try:
    import darts  # pylint: disable=W0611 # noqa: F401

    # If you just import darts this will pass during pip install, this creates
    # Failures later on, also importing utils ensures that darts is installed correctly
    from darts import utils  # pylint: disable=W0611 # noqa: F401

    FORECASTING = True
except ImportError:
    FORECASTING = False

base_path = Path(__file__).parent / "openbb_terminal"


def load_modules(full_path: Path):
    """Loads a module from a given Path.

    Parameters:
    ----------
    full_path: Path
        The path to the module

    Returns:
    ----------
    The python module
    """
    spec = importlib.util.spec_from_file_location(full_path.stem, full_path)
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

    pattern_list = ["**/*_model.py", "**/*_view.py"]
    module_path_list = []

    for pattern in pattern_list:
        module_path_generator = base_path.glob(pattern)
        module_path_list += list(module_path_generator)

    return module_path_list


def get_sdk(file_path: str = "miscellaneous/library/trail_map.csv") -> pd.DataFrame:
    """Reads the CSV that generates the sdk and converts it to a dataframe

    Parameters:
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
    print(f"Number of duplicate sdk paths: {df_dups}\n")
    views = list(df[["view", "trail"]].itertuples(index=False, name=None))
    models = list(df[["model", "trail"]].itertuples(index=False, name=None))
    combined = views + models
    final_df = pd.DataFrame()
    final_df["name"] = [x[0] for x in combined]
    final_df["trail"] = [x[1] for x in combined]
    final_df = final_df.dropna()
    final_df = final_df.set_index("name")
    return final_df


def format_function(function: Callable) -> Tuple[str, str]:
    """Gives a function a pretty name

    Parameters:
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
    print(f"Number of duplicate functions found: {func_dups}\n")
    func_df = func_df.set_index("name")
    return func_df


def main():
    print(
        "This tool checks all functions in a file with a name including 'view' or 'model'against\n"
        "all functions in the sdk, which is gathered from 'trail_map.csv'. If the generated csv\n"
        "has an entry for 'trail' that means it is in the SDK, and if it has an entry for\n"
        "'docstring' it is in a model or view.\n"
    )
    funcs_df = functions_df()
    sdk_df = get_sdk()

    final_df = funcs_df.merge(sdk_df, how="outer", left_index=True, right_index=True)
    final_df = final_df.sort_values("trail")
    timestamp = datetime.now().timestamp()
    time_str = (str(timestamp)).replace(".", "")
    output_path = f"{time_str}_sdk_audit.csv"
    final_df.to_csv(output_path)
    print(f"File saved to {output_path}")


if __name__ == "__main__":
    main()
