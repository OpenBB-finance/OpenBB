# IMPORTATION STANDARD
import os
from paths import ENV_FILE_DIR, USER_DATA_DIR, ENV_FILE_DEFAULT, ENV_FILE_REPO

if not os.path.exists(ENV_FILE_DIR):
    os.mkdir(ENV_FILE_DIR)

if not ENV_FILE_DEFAULT.is_file():
    with open(str(ENV_FILE_DEFAULT), "w"):
        pass

if not ENV_FILE_REPO.is_file():
    with open(str(ENV_FILE_REPO), "w"):
        pass

if not os.path.exists(USER_DATA_DIR):
    os.mkdir(USER_DATA_DIR)
