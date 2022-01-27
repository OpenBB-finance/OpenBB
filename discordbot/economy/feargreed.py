from typing import Any, Dict

import matplotlib.pyplot as plt

from gamestonk_terminal.economy import cnn_model, cnn_view


def feargreed_command(indicator="") -> Dict[str, Any]:
    """CNN Fear and Greed Index [CNN]"""

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
    return {
        "name": "feargreed",
        "title": "Economy: [CNN] Feargreed",
        "report": report,
        "mid_path": "economy",
    }
