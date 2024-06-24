import io

import pytest
from openbb_cli.cli import main


@pytest.mark.parametrize(
    "input_values",
    [
        "/equity/price/historical --symbol aapl --provider fmp",
        "/equity/price/historical --symbol msft --provider fmp",
        "/equity/price/historical --symbol goog --provider fmp",
    ],
)
@pytest.mark.integration
def test_launch_with_cli_input(monkeypatch, input_values):
    """Test launching the CLI and providing input via stdin with multiple parameters."""
    stdin = io.StringIO(input_values)
    monkeypatch.setattr("sys.stdin", stdin)

    try:
        main()
    except Exception as e:
        pytest.fail(f"Main function raised an exception: {e}")
