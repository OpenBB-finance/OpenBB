from inspect import getmembers, isfunction
from typing import List, Callable
import importlib.util
from pathlib import Path
import os
import pandas as pd

base_path = Path(__file__).parent / "openbb_terminal"


def load_modules(full_path: Path):
    mod_path = str(full_path).split("OpenBBTerminal/")[1].replace("/", ".")
    spec = importlib.util.spec_from_file_location(mod_path, full_path)
    mod = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(mod)
    return mod


def all_view_models() -> List[Path]:
    file_list = []
    all_files = os.walk(base_path)
    for root, _, files in all_files:
        for filename in files:
            if filename.endswith(".py"):
                if "view" in filename or "model" in filename:
                    file_list.append(Path(f"{root}/{filename}"))
    return file_list


def get_sdk(file_path: str = "miscellaneous/library/trail_map.csv"):
    return pd.read_csv(base_path / file_path)


def format_function(function: Callable) -> str:
    mod = str(function.__module__).replace("py", "").replace("/", ".")
    name = function.__name__
    return f"{mod}{name}"


def functions_df() -> pd.DataFrame:
    modules = all_view_models()
    all_formatted = []
    for module in modules:
        loaded = load_modules(module)
        func_list = [x[1] for x in getmembers(loaded, isfunction)]
        formatted_list = [format_function(x) for x in func_list]
        all_formatted.extend(formatted_list)
    func_df = pd.DataFrame()
    func_df["names"] = all_formatted
    func_df = func_df.set_index("names")
    func_df["in_functions"] = 1
    return func_df


def main():
    funcs_df = functions_df()
    sdk_df = get_sdk()

    print(funcs_df)
    print(sdk_df)


if __name__ == "__main__":
    main()
