"""On-command-output plugin that processes results in a background thread."""

import logging
import threading

from openbb_core.app.model.extension import Extension
from openbb_core.app.model.obbject import OBBject

logger = logging.getLogger(__name__)

nonblocking_plugin = Extension(
    name="nonblocking_plugin",
    description="Hand each /{{ cookiecutter.router_name }}/candles result to a background thread.",
    on_command_output=True,
    command_output_paths=["/{{ cookiecutter.router_name }}/candles"],
    immutable=True,
    results_only=False,
)


def process_in_background(serialized_obbject: dict) -> None:
    """Rebuild the command output and process it off the request path.

    Parameters
    ----------
    serialized_obbject : dict
        The command output dumped with ``model_dump``.
    """
    obbject = OBBject(**serialized_obbject)
    logger.info(
        "Processed %s rows from %s.", len(obbject.results or []), obbject.provider
    )


@nonblocking_plugin.obbject_accessor
def start_background_processing(obbject: OBBject) -> threading.Thread:
    """Start processing the command output without blocking the response.

    Parameters
    ----------
    obbject : OBBject
        The command output.

    Returns
    -------
    threading.Thread
        The started worker thread.
    """
    worker = threading.Thread(
        target=process_in_background,
        args=(obbject.model_dump(),),
        name="nonblocking-plugin",
        daemon=True,
    )
    worker.start()
    return worker
