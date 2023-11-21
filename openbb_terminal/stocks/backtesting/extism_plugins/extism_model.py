"""Backtesting Model"""
__docformat__ = "numpy"

import logging
import warnings

import bt
import pandas as pd
import pandas_ta as ta
import yfinance as yf

import extism
from extism import Plugin, Function, ValType, host_fn, set_log_file
import datetime

import json

# TODO: Remove this later
from openbb_terminal.rich_config import console

from openbb_terminal.common.technical_analysis import ta_helpers
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import is_intraday

logger = logging.getLogger(__name__)

set_log_file('extism.out', level='debug')

# def ema(data, params):
#     #print(data)
#     length = params['periods']
#     print(length)
#     ema = ta.ema(data, length)
#     print(ema)
#     return ema

# def get_frame(req):
#     df = pd.DataFrame({'prices': req['prices']})
#     df.index = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
#     df['prices'] = pd.to_numeric(df['prices'], errors='coerce')
#     return df

# def make_response(ema_result):
#     # format for returning response to the plugin
#     ema_result.name = 'data'
#     ema_frame = ema_result.to_frame()
#     ema_frame.fillna(0, inplace=True)
#     ema_frame.index = ema_frame.index.date
#     json_response = ema_frame.to_json()
#     return json_response

# def handle_request(req):
#     df = get_frame(req)
#     print(df)

#     params = json.loads(req['params'])
#     print(params)

#     if req['name'] == 'ema':
#         ema_result = ema(df['prices'], params)
#         #print(ema_result)
#         json_response = make_response(ema_result)
#         return json_response

#     if req['name'] == 'rsi':
#         rsi_result = rsi(df['prices'], params)
#         json_response = make_response(rsi_result)
#         return json_response

    
#     return nil

# @host_fn
# def get_ta(plugin, input_, output, a_string):
#     print("Host Function called: get_ta")
#     req = json.loads(plugin.input_string(input_[0]))
#     print(req)
#     rep = handle_request(req)
#     print(rep)
#     plugin.return_string(output[0], rep)

# hostfuncs = [
#     Function(
#         "get_ta",
#         [ValType.I64],
#         [ValType.I64],
#         get_ta,
#         None
#     ),
# ]

@log_start_end(log=logger)
def get_data(symbol: str, start_date: str = "2019-01-01") -> pd.DataFrame:
    """Function to replace bt.get, gets Adjusted close of symbol using yfinance.

    Parameters
    ----------
    symbol: str
        Ticker to get data for
    start_date: str
        Start date in YYYY-MM-DD format

    Returns
    -------
    prices: pd.DataFrame
        Dataframe of Adj Close with columns = [ticker]
    """
    data = yf.download(symbol, start=start_date, progress=False, ignore_tz=True)
    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return pd.DataFrame()
    df = pd.DataFrame(data[close_col])
    df.columns = [symbol]

    return df

@log_start_end(log=logger)
def buy_and_hold(symbol: str, start_date: str, name: str = "") -> bt.Backtest:
    """Generates a buy and hold backtest object for the given ticker.

    Parameters
    ----------
    symbol: str
        Stock to test
    start_date: str
        Backtest start date, in YYYY-MM-DD format. Can be either string or datetime
    name: str
        Name of the backtest (for labeling purposes)

    Returns
    -------
    bt.Backtest
        Backtest object for buy and hold strategy
    """
    prices = get_data(symbol, start_date)
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


#(plugin, name: str, symbol: str, data: pd.DataFrame, **kwargs)
@log_start_end(log=logger)
def run_strategy(plugin, name: str, symbol: str, data: pd.DataFrame, **kwargs) -> bt.backtest.Result:
    """Perform backtest for strategies backed by Extism Plugins.

    Parameters
    ----------
    symbol: str
        Stock ticker
    data: pd.DataFrame
        Dataframe of prices

    Returns
    -------
    bt.backtest.Result
        Backtest results
    """

    # console.print(plugin)
    # console.print(kwargs)
    # console.print(data)

    # TODO: Help Wanted!
    # Implement support for backtesting on intraday data
    if is_intraday(data):
        return None

    data.index = pd.to_datetime(data.index.date)
    symbol = symbol.lower()

    start_date = data.index[0]
    close_col = ta_helpers.check_columns(data, high=False, low=False)
    if close_col is None:
        return bt.backtest.Result()

    prices = pd.DataFrame(data[close_col])
    prices.columns = [symbol]

    #console.print(prices)

    json_string = prices.to_json()
    req = json.loads(json_string)

    #console.print(symbol)
    #console.print(req)

    req['prices'] = req.pop(symbol)
    #console.print(req)

    req.update({"params": kwargs})
    #print(req)
    req = json.dumps(req) 
    #console.print(req)

    console.print("Calling Extism plugin")
    # manifest = {"wasm": [{"url": "https://modsurfer.dylibso.workers.dev/api/v1/module/4738fbe83e5a1d2ce3842759722165d79870886e01a9371715807002cb711446.wasm"}]}
    # plugin = Plugin(manifest, functions=hostfuncs)
    rep = plugin.call("call", req)
    #console.print(response)

    signal = json.loads(rep)
    signal = pd.DataFrame(signal)
    signal.index = pd.to_datetime(pd.to_numeric(signal.index), unit='ms').date
    signal.rename(columns={'signal': symbol}, inplace=True)

    console.print(signal)
    console.print(prices)

    merged_data = bt.merge(signal, prices)
    merged_data.columns = ["signal", "price"]

    console.print(merged_data)

    warnings.simplefilter(action="ignore", category=FutureWarning)
    bt_strategy = bt.Strategy(
        "Strategy", [bt.algos.WeighTarget(signal), bt.algos.Rebalance()]
    )
    bt_backtest = bt.Backtest(bt_strategy, prices)
    bt_backtest = bt.Backtest(bt_strategy, prices)
    backtests = [bt_backtest]

    with warnings.catch_warnings():
        stock_bt = buy_and_hold(symbol, start_date, symbol.upper() + " Hold")
        backtests.append(stock_bt)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore")
        res = bt.run(*backtests)

    return res
