from unittest.mock import patch

import pandas as pd
import pytest

from gamestonk_terminal import load

@pytest.mark.e2e
def test_load_command():

    test_stock = 'TSLA'
    test_start = '2020-06-04'

    with patch('sys.stdout.write') as mock_out:
        result = load(['-t', test_stock, '-s', test_start], '', '', '', '')

    args = mock_out.call_args_list[0][0]

    assert result[0] == test_stock
    assert test_stock in args[0]
    assert test_start in args[0]
