import sys
import warnings
from multiprocessing import freeze_support

# pylint:disable=wrong-import-position
warnings.filterwarnings("ignore", category=FutureWarning, module="yfinance.*")
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas.*")
import openbb_terminal.config_terminal as cfg  # noqa: E402

# pylint:disable=unused-import,import-outside-toplevel
import openbb_terminal.core.session.current_system as syst  # noqa: F401,E402
from openbb_terminal.terminal_helper import (  # noqa: E402
    hide_splashscreen,
    is_auth_enabled,
    is_installer,
)


def main():
    sent_args = sys.argv[1:]
    cfg.setup_config_terminal()

    if "--streamlit" in sent_args:
        from openbb_terminal.dashboards import streamlit_run

        hide_splashscreen()
        sys.exit(streamlit_run.main())

    if "-t" in sent_args or "--test" in sent_args:
        from openbb_terminal.core.integration_tests import integration_controller

        integration_controller.main()
    else:
        from openbb_terminal.core.session import session_controller

        prompt_login = (
            is_auth_enabled()
            and ("--login" in sys.argv[1:] or is_installer())
            and sys.stdin.isatty()
        )
        dev = "--dev" in sys.argv[1:]

        session_controller.main(prompt=prompt_login, dev=dev)


if __name__ == "__main__":
    freeze_support()
    main()
