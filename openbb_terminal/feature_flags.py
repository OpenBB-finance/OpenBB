# IMPORTATION STANDARD
import os
import os.path

# IMPORTATION THIRDPARTY
import i18n

# IMPORTATION INTERNAL
from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
)
from openbb_terminal.core.session.current_user import get_current_user

# pylint: disable=no-member,c-extension-no-member

try:
    __import__("git")
except ImportError:
    WITH_GIT = False
else:
    WITH_GIT = True


try:
    if not WITH_GIT:
        import pkg_resources

        version = pkg_resources.get_distribution("OpenBB").version
    else:
        raise Exception("Using git")
except Exception:
    version = "2.5.1"
VERSION = str(os.getenv("OPENBB_VERSION", version))

# # Select the terminal translation language
i18n_dict_location = MISCELLANEOUS_DIRECTORY / "i18n"
i18n.load_path.append(i18n_dict_location)
i18n.set("locale", get_current_user().preferences.USE_LANGUAGE)
i18n.set("filename_format", "{locale}.{format}")
