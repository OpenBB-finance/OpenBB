"""Inference API."""
import os
from openbb_terminal.helper_classes import ModelsNamespace as _models
from openbb_terminal.common import prediction_techniques

# flake8: noqa
# pylint: disable=unused-import

# Menu commands
from openbb_terminal.common.prediction_techniques.ets_view import (
    display_exponential_smoothing as ets,
)
from openbb_terminal.common.prediction_techniques.knn_view import (
    display_k_nearest_neighbors as knn,
)
from openbb_terminal.common.prediction_techniques.regression_view import (
    display_regression as regression,
)
from openbb_terminal.common.prediction_techniques.arima_view import (
    display_arima as arima,
)
from openbb_terminal.common.prediction_techniques.neural_networks_view import (
    display_mlp as mlp,
)
from openbb_terminal.common.prediction_techniques.neural_networks_view import (
    display_rnn as rnn,
)
from openbb_terminal.common.prediction_techniques.neural_networks_view import (
    display_lstm as lstm,
)
from openbb_terminal.common.prediction_techniques.neural_networks_view import (
    display_conv1d as conv1d,
)
from openbb_terminal.common.prediction_techniques.mc_view import (
    display_mc_forecast as mc,
)

# Models
models = _models(os.path.abspath(os.path.dirname(prediction_techniques.__file__)))
