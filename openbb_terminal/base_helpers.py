# This is for helpers that do NOT import any OpenBB Modules
import os
import sys
from typing import Any, Callable, Literal, Union

from rich.console import Console

from openbb_terminal.qt_app.backend import BACKEND

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
# mypy: disable=has-no-attr
class Show:
    """Monkey patch the show method to send the figure to the backend"""

    def show(self, *args, **kwargs) -> Union[str, None]:
        """Show the figure."""
        try:
            # if in terminal pro, we just return the json
            if os.environ.get("TERMINAL_PRO", False):
                return self.to_json()

            if self.layout.template.layout.mapbox.style == "dark":
                self.update_layout(
                    newshape_line_color="gold",
                    modebar=dict(
                        orientation="v",
                        bgcolor="rgba(0,0,0,0)",
                        color="gold",
                        activecolor="#d1030d",
                    ),
                )

            # We send the figure to the backend to be displayed
            BACKEND.send_figure(self)
        except Exception:
            # If the backend fails, we just show the figure normally
            # This is a very rare case, but it's better to have a fallback
            if os.environ.get("DEBUG", False):
                console.print_exception()

            import plotly.io as pio  # pylint: disable=import-outside-toplevel

            kwargs["config"] = {"scrollZoom": True}
            return pio.show(self, *args, **kwargs)

        return None


if not JUPYTER_NOTEBOOK and sys.stdin.isatty():
    # pylint: disable=import-outside-toplevel
    import gc

    from plotly.graph_objs import Figure

    # We need to force a garbage collection to make sure all modules are loaded
    gc.collect()

    for module in list(sys.modules.values()):
        if not hasattr(module, "Figure") or not issubclass(module.Figure, Figure):
            continue
        module.Figure.show = Show.show
