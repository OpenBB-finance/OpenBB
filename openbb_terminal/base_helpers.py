# This is for helpers that do NOT import any OpenBB Modules
from typing import Callable, Any
import os

from rich.console import Console

console = Console()


def load_env_vars(name: str, converter: Callable, default: Any) -> Any:
    """Loads an environment variable and attempts to convert it to the correct data type.
    Will return the provided default if it fails

    Parameters
    ----------
    name: str
        The name of the environment variable
    converter: Callable
        The function to convert the env variable to the desired format
    default: Any
        The value to return if the converter fails

    Returns
    ----------
    Any
        The value or the default
    """
    raw_var = os.getenv(name)
    try:
        return converter(raw_var)
    except ValueError:
        console.print(f"[red]Invalid type provided for variable '{name}'.[/red]\n")
        return default
    except AttributeError:
        console.print(f"[red]Invalid type provided for variable '{name}'.[/red]\n")
        return default
    except TypeError:
        console.print(f"[red]Invalid type provided for variable '{name}'.[/red]\n")
        return default
