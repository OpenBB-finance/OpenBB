from unittest.mock import patch

import pytest

from prediction_techniques.neural_networks import mlp
from gamestonk_terminal import load


@pytest.fixture
def stock():

    def load_stock(name, start='2020-06-04'):
        return load(['-t', name, '-s', start], '', '', '', '')

    return load_stock


@pytest.mark.e2e
def test_mlp(stock):

    with patch('sys.stdout.write') as mock_out:
        tesla = stock('TSLA')
        mlp([], tesla[0], tesla[2], tesla[3])

    mock_out.assert_any_call('Predicted share price:')
