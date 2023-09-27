import re
import sys
from pathlib import Path

import streamlit.web.bootstrap

from openbb_terminal.core.config.paths import REPOSITORY_DIRECTORY
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.core.session.current_user import set_preference

set_system_variable("LOGGING_SUPPRESS", True)
set_preference("CHART_STYLE", "dark")
set_preference("PLOT_ENABLE_PYWRY", "False")


def main():
    # pylint: disable=E1101,W0212
    parent_path = Path(sys._MEIPASS) if hasattr(sys, "frozen") else REPOSITORY_DIRECTORY  # type: ignore
    filepath = Path(__file__).parent / "stream" / "Forecasting.py"
    file = filepath.relative_to(parent_path).as_posix()

    cmdline = " ".join(sys.argv)
    port = re.findall(r"--port=(\d+)", cmdline)
    port = int(port[0]) if port else 8501

    flag_options = {
        "server.port": port,
        "server.headless": True,
        "global.developmentMode": False,
        "server.enableCORS": False,
        "server.enableXsrfProtection": False,
        "browser.serverAddress": "localhost",
        "theme.base": "dark",
        "browser.gatherUsageStats": False,
    }

    streamlit.web.bootstrap.load_config_options(flag_options=flag_options)
    flag_options["_is_running_with_streamlit"] = True
    streamlit.web.bootstrap.run(
        str(file),
        "streamlit run",
        [],
        flag_options,
    )


if __name__ == "__main__":
    main()
