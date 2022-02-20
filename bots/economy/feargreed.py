import datetime
import os

import matplotlib.pyplot as plt

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from gamestonk_terminal.economy import cnn_model, cnn_view


def feargreed_command(indicator=""):
    """CNN Fear and Greed Index [CNN]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("econ-futures")

    # Check for argument
    possible_indicators = ("", "jbd", "mv", "pco", "mm", "sps", "spb", "shd")

    if indicator not in possible_indicators:
        raise Exception(
            f"Select a valid indicator from {', '.join(possible_indicators)}"  # nosec
        )

    # Retrieve data
    fig = plt.figure(figsize=[1, 1], dpi=10)

    report, _ = cnn_model.get_feargreed_report(indicator, fig)
    cnn_view.fear_and_greed_index(indicator=indicator, export="png")
    plt.close("all")

    # Output data
    now = datetime.datetime.now()
    image_path = os.path.join(
        cfg.GST_PATH,
        "exports",
        "economy",
        f"feargreed_{now.strftime('%Y%m%d_%H%M%S')}.png",
    )

    i = 0
    while not os.path.exists(image_path) and i < 10:
        now -= datetime.timedelta(seconds=1)
        image_path = os.path.join(
            cfg.GST_PATH,
            "exports",
            "economy",
            f"feargreed_{now.strftime('%Y%m%d_%H%M%S')}.png",
        )
        i += 1

    return {
        "title": "Economy: [CNN] Fear Geed Index",
        "imagefile": image_path,
        "description": report,
    }
