# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
from pathlib import Path
import pandas as pd
import pytest

# IMPORTATION INTERNAL
from openbb_terminal.portfolio import metrics_model


def build_csv_path(csv_name: str):
    folder_path = Path(__file__).parent

    return folder_path / "csv" / "test_portfolio_model" / csv_name


portfolio_returns = pd.read_csv(build_csv_path("portfolio_returns.csv"))
portfolio_returns["Date"] = pd.to_datetime(portfolio_returns["Date"])
portfolio_returns = portfolio_returns.set_index("Date")

benchmark_returns = pd.read_csv(build_csv_path("benchmark_returns.csv"))
benchmark_returns["Date"] = pd.to_datetime(benchmark_returns["Date"])
benchmark_returns = benchmark_returns.set_index("Date")

benchmark_trades = pd.read_csv(build_csv_path("benchmark_trades.csv"))
benchmark_trades["Date"] = pd.to_datetime(benchmark_trades["Date"])
benchmark_trades = benchmark_trades.set_index("Date")


@pytest.mark.vcr(record_mode="none")
def test_tracking_error(recorder):
    result_df, _ = metrics_model.get_tracking_error(
        portfolio_returns, benchmark_returns
    )

    recorder.capture(result_df)


@pytest.mark.vcr(record_mode="none")
def test_tail_ratio():
    result_df, _, _ = metrics_model.get_tail_ratio(portfolio_returns, benchmark_returns)

    assert isinstance(result_df, pd.DataFrame)
