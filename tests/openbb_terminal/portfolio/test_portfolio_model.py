# IMPORTATION STANDARD

# IMPORTATION THIRDPARTY
from pathlib import Path
import pandas as pd

# IMPORTATION INTERNAL
from openbb_terminal.portfolio import portfolio_model


def build_csv_path(csv_name: str):
    folder_path = Path(__file__).parent

    return folder_path / "csv" / "test_portfolio_model" / csv_name


portfolio_trades = pd.read_csv(build_csv_path("example_portfolio.csv"))

portfolio_returns = pd.read_csv(build_csv_path("portfolio_returns.csv"))

portfolio_returns["Date"] = pd.to_datetime(portfolio_returns["Date"])
portfolio_returns = portfolio_returns.set_index("Date")

benchmark_returns = pd.read_csv(build_csv_path("benchmark_returns.csv"))

benchmark_returns["Date"] = pd.to_datetime(benchmark_returns["Date"])
benchmark_returns = benchmark_returns.set_index("Date")


def test_tracking_error(recorder):
    result_df, _ = portfolio_model.get_tracking_error(
        portfolio_returns, benchmark_returns
    )

    recorder.capture(result_df)


def test_information_ratio(recorder):
    result_df, _ = portfolio_model.get_information_ratio(
        portfolio_returns, benchmark_returns
    )

    recorder.capture(result_df)


def test_tail_ratio(recorder):
    result_df, _, _ = portfolio_model.get_tail_ratio(
        portfolio_returns, benchmark_returns
    )

    recorder.capture(result_df)


def test_common_sense_ratio(recorder):
    result_df = portfolio_model.get_common_sense_ratio(
        portfolio_returns, benchmark_returns
    )

    recorder.capture(result_df)
