import pandas as pd
from termcolor import colored

def alpaca_positions_to_df(positions):

    df = pd.DataFrame(columns=["Symbol", "MarketValue", "Quantity", "CostBasis"])
    sym = []
    mv = []
    qty = []
    cb = []

    for pos in positions:
        sym.append(pos.symbol)
        mv.append(float(pos.market_value))
        qty.append(float(pos.qty))
        cb.append(float(pos.cost_basis))

    df["Symbol"] = sym
    df["MarketValue"] = mv
    df["Quantity"] = qty
    df["CostBasis"] = cb
    df["Broker"] = "alp"

    return df


def ally_positions_to_df(df):
    names = {
        "costbasis": "CostBasis",
        "marketvalue": "MarketValue",
        "sym": "Symbol",
        "qty": "Quantity",
    }

    df = df.loc[:, ["costbasis", "marketvalue", "qty", "sym"]]
    df[["costbasis", "marketvalue", "qty"]] = df[
        ["costbasis", "marketvalue", "qty"]
    ].astype(float)
    df = df.rename(columns=names)
    df["Broker"] = "ally"
    return df


def rh_positions_to_df(holds: dict):

    df = pd.DataFrame(columns=["Symbol", "MarketValue", "Quantity", "CostBasis"])
    sym = []
    mv = []
    qty = []
    cb = []
    for stonk, data in holds.items():
        sym.append(stonk)
        qty.append(float(data["quantity"]))
        mv.append(float(data["equity"]))
        cb.append(float(data["quantity"]) * float(data["average_buy_price"]))
    df["Symbol"] = sym
    df["MarketValue"] = mv
    df["Quantity"] = qty
    df["CostBasis"] = cb
    df["Broker"] = "rh"

    return df


def merge_portfolios(df: pd.DataFrame) -> pd.DataFrame:
    if set(df.columns) != {
        "Symbol", "MarketValue", "Quantity", "CostBasis", "Broker"
    }:
        print("Check df generation")
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


def print_portfolio(portfolio):
    print(
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
            print(colored(to_print, "green"))
        else:
            print(colored(to_print, "red"))
    print("")
