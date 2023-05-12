# IMPORT STANDARD
import inspect
import re

# IMPORT THIRD PARTY

# IMPORT INTERNAL

SECTION_LENGTH = 90
STYLES = [
    "[bold]",
    "[/bold]",
    "[red]",
    "[/red]",
    "[green]",
    "[/green]",
    "[bold red]",
    "[/bold red]",
]


def to_section_title(title: str, char: str = "=") -> str:
    """Format title for test mode.

    Parameters
    ----------
    title: str
        The title to format

    Returns
    -------
    str
        The formatted title
    """
    title = " " + title + " "

    len_styles = 0
    for style in STYLES:
        if style in title:
            len_styles += len(style)

    n = int((SECTION_LENGTH - len(title) + len_styles) / 2)
    formatted_title = char * n + title + char * n
    formatted_title = formatted_title + char * (
        SECTION_LENGTH - len(formatted_title) + len_styles
    )

    return formatted_title


def get_submodule_commands(module: object) -> list:
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
        "ad",
    ]
    functions = []
    for name in dir(module):
        if name.startswith("call_"):
            functions.append(name[5:])

    functions = [function for function in functions if function not in filter_func]
    return functions


def find_all_calls(module) -> list:
    """Find all function calls in a module."""
    calls = []
    module_dict = module.__dict__
    for key, _ in module_dict.items():
        if "call_" in key:
            calls.append(key)
    return calls


def parse_args(module, func) -> list:
    """Parse the arguments of a given module function."""
    filters = [
        "-ape",
        "-yacht",
        "-club",
        "-h",
        "-to",
        "-seeking",
        "-sloping",
        "-neutral",
        "-known",
        "-yields",
        "-level",
        "-rating",
        "-traded",
        "-frens",
        "-ad",
        "-sheet",
        "-flow",
        "-weighted",
        "-curve",
        "-year",
    ]
    source = inspect.getsource(module.__dict__[func])
    params = re.findall(r"-\w+", source)
    params = [param for param in params if not param[1:].isupper()]
    params = [param for param in params if not param[1:].isdigit()]
    params = [param for param in params if not param[1].isupper()]
    params = [param for param in params if param not in filters]
    params = list(dict.fromkeys(params))
    return params


def map_module_to_calls(module) -> dict:
    """Map module to its function calls and parameters."""
    calls = find_all_calls(module)
    calls_dict = {}
    for call in calls:
        calls_dict[call] = parse_args(module, call)

    calls_dict = {k[5:]: v for k, v in calls_dict.items()}
    return calls_dict


def validate_missing_params(missing_params: dict, test_file: str) -> dict:
    """Validate missing parameters."""
    with open(test_file) as f:
        lines = f.readlines()
        for key, values in missing_params.items():
            for line in lines:
                for value in values:
                    if key in line and value in line:
                        missing_params[key].remove(value)

    missing_params = {k: v for k, v in missing_params.items() if v}
    return missing_params
