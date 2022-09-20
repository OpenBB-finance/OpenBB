# IMPORTATION STANDARD

import shutil
import os
from openbb_terminal.core.config.paths import (
    REPO_DIRECTORY,
    CUSTOM_IMPORTS_DIRECTORY,
    USER_STYLES_DIRECTORY,
)


def copy_and_delete_files(from_dir, to_dir):
    """
    Moves default/example files from repo and deletes the folder in the repo
    """
    if os.path.exists(from_dir):
        shutil.copytree(from_dir, to_dir, dirs_exist_ok=True)
        shutil.rmtree(from_dir)


copy_and_delete_files(
    os.path.join(REPO_DIRECTORY, "custom_imports"), CUSTOM_IMPORTS_DIRECTORY
)
copy_and_delete_files(
    os.path.join(REPO_DIRECTORY, "styles", "user"), USER_STYLES_DIRECTORY
)
