"""Pred context API."""

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from gamestonk_terminal.common.prediction_techniques.ets_view import (
    display_exponential_smoothing as ets,
)
from gamestonk_terminal.common.prediction_techniques.knn_view import (
    display_k_nearest_neighbors as knn,
)
from gamestonk_terminal.common.prediction_techniques.regression_view import (
    display_regression as regression,
)
from gamestonk_terminal.common.prediction_techniques.arima_view import (
    display_arima as arima,
)
from gamestonk_terminal.common.prediction_techniques.neural_networks_view import (
    display_mlp as mlp,
)
from gamestonk_terminal.common.prediction_techniques.neural_networks_view import (
    display_rnn as rnn,
)
from gamestonk_terminal.common.prediction_techniques.neural_networks_view import (
    display_lstm as lstm,
)
from gamestonk_terminal.common.prediction_techniques.neural_networks_view import (
    display_conv1d as conv1d,
)
from gamestonk_terminal.common.prediction_techniques.mc_view import (
    display_mc_forecast as mc,
)
