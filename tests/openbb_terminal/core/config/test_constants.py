import os
from pathlib import Path
from openbb_terminal.core.config import constants


def test_user_data_dir():
    assert os.path.exists(constants.USER_DATA_DIR)


def test_env_file_dir():
    assert os.path.exists(constants.ENV_FILE_DIR)


def test_env_file_default():
    assert constants.ENV_FILE_DEFAULT.is_file()


def test_folder_paths():
    for v in constants.folder_paths.values():
        assert os.path.exists(v)


def test_copying_internal_paths():
    for int_path_dif in constants.internal_paths:
        internal_routines = constants.REPO_DIR / os.path.join(
            *int_path_dif[0].split("/")
        )
        for file in os.listdir(internal_routines):
            new_path = os.path.join(constants.folder_paths[int_path_dif[1]], file)
            if not Path(new_path).is_file():
                assert False
