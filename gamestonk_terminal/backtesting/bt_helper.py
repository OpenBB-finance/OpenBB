from datetime import datetime
from typing import Union
import bt


def buy_and_hold(ticker: str, start: Union[str, datetime], name: str):

    prices = bt.get(ticker, start=start)
    bt_strategy = bt.Strategy(
        name,
        [
            bt.algos.RunOnce(),
            bt.algos.SelectAll(),
            bt.algos.WeighEqually(),
            bt.algos.Rebalance(),
        ],
    )
    return bt.Backtest(bt_strategy, prices)
