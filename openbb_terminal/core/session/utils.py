import os
import shutil
from pathlib import Path
from typing import Any, Type, TypeVar

from pydantic import ValidationError

from openbb_terminal.core.models import BaseModel

T = TypeVar("T", bound=BaseModel)


def load_dict_to_model(dictionary: dict, model: Type[T]) -> T:
    """Load variables to model.

    Parameters
    ----------
    dictionary : dict
        Variables dictionary.
    model : Type[T]
        Model to load.

    Returns
    -------
    T
        Model with validated data.
    """
    model_name = model.__name__.strip("Model").lower()
    try:
        return model(**dictionary)  # type: ignore
    except ValidationError as error:
        print(f"Error loading {model_name}:")  # noqa: T201
        for err in error.errors():
            loc = err.get("loc", None)
            var_name = str(loc[0]) if loc else ""
            msg = err.get("msg", "")
            var = dictionary.pop(var_name, None)
            fields: dict[str, Any] = model.get_fields()
            if var and var_name in fields:
                default = fields[var_name].default
                print(  # noqa: T201
                    f"    {var_name}: {msg}, using default -> {default}"
                )

        return model(**dictionary)  # type: ignore
    except Exception:
        print(f"Error loading {model_name}, using defaults.")  # noqa: T201
        return model()  # type: ignore


def remove(path: Path) -> bool:
    """Remove path.

    Parameters
    ----------
    path : Path
        The file path.

    Returns
    -------
    bool
        The status of the removal.
    """
    # TODO: Check why module level import leads to circular import.
    from openbb_terminal.rich_config import (
        console,
    )

    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except Exception:
        console.print(
            f"\n[bold red]Failed to remove {path}"
            "\nPlease delete this manually![/bold red]"
        )
        return False
