import pandas as pd

from openbb_terminal.rich_config import console


def merge_brokers_holdings(df: pd.DataFrame) -> pd.DataFrame:
    if set(df.columns) != {"Symbol", "MarketValue", "Quantity", "CostBasis", "Broker"}:
        console.print("Check df generation")
        return None

    df = df.groupby("Symbol").agg(
        {
            "MarketValue": sum,
            "Quantity": sum,
            "CostBasis": sum,
            "Broker": lambda text: "/".join(text),
        }
    )
    return df


def print_brokers_holdings(portfolio):
    console.print(
        "Stonk\t Market Value \t\t Quantity \t\t Cost Basis \t\t All Time % Change \t\t Brokers"
    )

    for row in portfolio.itertuples():
        pct_change = 100 * (row.MarketValue - row.CostBasis) / row.CostBasis
        to_print = (
            f"{row.Index} \t {row.MarketValue:.3f} \t\t "
            f"{row.Quantity:.4f} \t\t {row.CostBasis:.3f} \t\t {pct_change:.4f}"
            f" \t\t\t {row.Broker}"
        )

        if pct_change >= 0:
            console.print(to_print, "green")
        else:
            console.print(to_print, "red")
