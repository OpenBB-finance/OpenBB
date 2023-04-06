import atexit
import json
import os
from pathlib import Path

from pydantic.json import pydantic_encoder

from openbb_terminal.core.config.paths import (
    SETTINGS_DIRECTORY,
)
from openbb_terminal.core.models import SystemModel
from openbb_terminal.core.session.env_handler import load_env_to_model, reading_env

SYSTEM_FILE_PATH = SETTINGS_DIRECTORY / "system.json"


def handle_system(file_path: Path = SYSTEM_FILE_PATH) -> SystemModel:
    """
    Handle the system.

    Reads system data from file if it exists, else reads environment variable data.
    Returns a system model built from the loaded data.

    Parameters
    ----------
    file_path (Path): The file path.

    Returns
    -------
        SystemModel: The system model.
    """

    try:
        if os.path.isfile(file_path):
            system_data = {}
            with open(file_path) as f:
                system_data = json.load(f)
            if system_data:
                return load_env_to_model(system_data, SystemModel)
    except Exception:
        pass

    __env_dict = reading_env()
    system = load_env_to_model(__env_dict, SystemModel)
    save_system(system=system, file_path=file_path)
    subscribe_delete_system_on_exit(file_path=file_path)
    return system


def save_system(system: SystemModel, file_path: Path = SYSTEM_FILE_PATH):
    """
    Write system to file.

    Parameters
    ----------
    system (SystemModel): The system model.
    file_path (Path): The file path.

    Returns
    -------
        system (SystemModel): The system model.
    """

    try:
        with open(file_path, "w") as f:
            json_content = json.dumps(system, default=pydantic_encoder)
            f.write(json_content)
    except Exception:
        pass


def subscribe_delete_system_on_exit(file_path: Path):
    """
    Deletes the system file on exiting the application.

    Parameters
    ----------
    file_path (Path): The file path.
    """

    def delete_file(file_path: Path):
        if os.path.isfile(file_path):
            os.remove(file_path)

    atexit.register(delete_file, file_path=file_path)
