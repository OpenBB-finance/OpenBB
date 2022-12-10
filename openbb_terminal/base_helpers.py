# This is for helpers that do NOT import any OpenBB Modules
import os
import sys
from typing import Any, Callable, Literal, Union

import plotly.graph_objects as go
from rich.console import Console

from plots_backend.helpers import PLOTLY_BACKEND

console = Console()

menus = Literal["", "featflags", "settings"]


def handle_error(name: str, default: Any, menu: menus = ""):
    """Handles the error by returning the default value and printing an
    informative error message.

    Parameters
    ----------
    name: str
        The name of the environment variable
    default: Any
        The value to return if the converter fails
    menu: menus
        If provided, will tell the user where to fix the setting

    Returns
    ----------
    Any
        The default value

    """
    base = f"[red]Invalid variable provided for variable '{name}'."
    if menu:
        base += f" Please change the setting in the `{menu}` menu."
    base += "[/red]\n"
    console.print(base)
    return default


def load_env_vars(
    name: str, converter: Callable, default: Any, menu: menus = ""
) -> Any:
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
    menu: menus
        If provided, will tell the user where to fix the setting

    Returns
    ----------
    Any
        The value or the default
    """
    raw_var = os.getenv(name, str(default))
    try:
        return converter(raw_var)
    except ValueError:
        return handle_error(name, default, menu)
    except AttributeError:
        return handle_error(name, default, menu)
    except TypeError:
        return handle_error(name, default, menu)


def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
    are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
    'val' is anything else.
    """
    val = str(val).lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        output = 1
    elif val in ("n", "no", "f", "false", "off", "0"):
        output = 0
    else:
        raise ValueError(f"invalid truth value {val}")

    return output


try:
    from IPython import get_ipython

    if "IPKernelApp" not in get_ipython().config:
        raise ImportError("console")
    if (
        "parent_header"
        in get_ipython().kernel._parent_ident  # pylint: disable=protected-access
    ):
        raise ImportError("notebook")
except (ImportError, AttributeError):
    JUPYTER_NOTEBOOK = False
else:
    JUPYTER_NOTEBOOK = True


# pylint: disable=no-member
class Show:
    """Monkey patch the show method to send the figure to the backend, or return the json if
    we are in a terminal pro session.
    """

    def show(self) -> Union[str, None]:
        """Show the figure."""
        if os.environ.get("TERMINAL_PRO", False):
            return self.to_json()  # type: ignore
        try:
            # We send the figure to the backend to be displayed
            PLOTLY_BACKEND.send_fig(self)
        except Exception:
            # If the backend fails, we just show the figure normally
            # This is a very rare case, but it's better to have a fallback
            if os.environ.get("DEBUG", False):
                console.print_exception()
            self._show()  # type: ignore

        return None


# If we are not in a notebook, we monkey patch the show method
if not JUPYTER_NOTEBOOK and sys.stdin.isatty():
    setattr(go.Figure, "_show", go.Figure.show)
    go.Figure.show = Show.show
    PLOTLY_BACKEND.start()
