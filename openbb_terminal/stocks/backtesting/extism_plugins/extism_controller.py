"""Extism Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
from typing import List, Optional

import matplotlib as mpl
import pandas as pd
import pandas_ta as ta

import extism
from extism import Plugin, Function, ValType, host_fn, set_log_file

import json

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_non_negative_float,
    check_positive,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import StockBaseController
from openbb_terminal.rich_config import MenuText, console

# This code below aims to fix an issue with the fnn module, used by bt module
# which forces matplotlib backend to be 'agg' which doesn't allow to plot
# Save current matplotlib backend
default_backend = mpl.get_backend()
# Restore backend matplotlib used

# pylint: disable=wrong-import-position
from openbb_terminal.stocks.backtesting.extism_plugins import extism_view  # noqa: E402

logger = logging.getLogger(__name__)

mpl.use(default_backend)

def ema(data, params):
    #print(data)
    length = params['periods']
    print(length)
    ema = ta.ema(data, length)
    #print(ema)
    return ema

def get_frame(req):
    df = pd.DataFrame({'prices': req['prices']})
    df.index = pd.to_datetime(pd.to_numeric(df.index), unit='ms')
    df['prices'] = pd.to_numeric(df['prices'], errors='coerce')
    return df

def make_response(ema_result):
    # format for returning response to the plugin
    ema_result.name = 'data'
    ema_frame = ema_result.to_frame()
    ema_frame.fillna(0, inplace=True)
    ema_frame.index = ema_frame.index.date
    json_response = ema_frame.to_json()
    return json_response

def handle_request(req):
    # print(req['name'])
    # print(req['prices'])
    # print(req['params'])

    df = get_frame(req)
    print(df)

    params = json.loads(req['params'])
    print(params)

    if req['name'] == 'ema':
        ema_result = ema(df['prices'], params)
        #print(ema_result)
        json_response = make_response(ema_result)
        return json_response

    if req['name'] == 'rsi':
        rsi_result = rsi(df['prices'], params)
        json_response = make_response(rsi_result)
        return json_response

    
    return nil

@host_fn
def get_ta(plugin, input_, output, a_string):
    console.print("Host Function called: get_ta")
    req = json.loads(plugin.input_string(input_[0]))
    rep = handle_request(req)
    console.print(rep)
    plugin.return_string(output[0], rep)

hostfuncs = [
    Function(
        "get_ta",
        [ValType.I64],
        [ValType.I64],
        get_ta,
        None
    ),
]

plugin_manifests = {
    "ema": { "wasm": [{"url": "https://modsurfer.dylibso.workers.dev/api/v1/module/4738fbe83e5a1d2ce3842759722165d79870886e01a9371715807002cb711446.wasm"}]},
}

plugins = {}

# instantiate plugins
for name,manifest in plugin_manifests.items():
    plugins[name] = Plugin(manifest, functions=hostfuncs)
    #console.print(plugins[name])


def no_data_message():
    """Print message when no ticker is loaded"""
    console.print("[red]No data loaded. Use 'load' command to load a symbol[/red]")

# helper function for setting up a plugin command alias
def create_alias(cls, original_name, alias_name, value_add):
    original_method = getattr(cls, original_name)
    def alias_method(self):
        return original_method(self, plugin_name=value_add)

    setattr(cls, alias_name, alias_method)


class ExtismController(StockBaseController):
    """Extism Controller class"""

    CHOICES_COMMANDS = ["load"]
    PATH = "/stocks/bt/extism/"
    CHOICES_GENERATION = True

    def __init__(
        self, ticker: str, stock: pd.DataFrame, queue: Optional[List[str]] = None
    ):
        """Constructor"""
        for name,plugin in plugins.items():
            create_alias(self, 'call_run', 'call_'+name, name)
            self.CHOICES_COMMANDS.append(name)

        super().__init__(queue)

        self.ticker = ticker
        self.stock = stock
        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("stocks/bt/extism/")
        mt.add_raw("")
        mt.add_param("_ticker", self.ticker.upper() or "No Ticker Loaded")
        mt.add_raw("\n")
        mt.add_cmd("load")
        mt.add_raw("\n")

        # add any installed plugins to the menu
        for name in plugins.keys():
            mt.add_cmd(name, self.ticker)

        console.print(text=mt.menu_text, menu="Stocks - Backtesting - Extism")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.ticker:
            return ["stocks", f"load {self.ticker}", "bt", "extism"]
        return []

    def call_run(self, other_args: List[str], plugin_name=""):
        """Call extism"""

        if plugin_name:
            # get the plugin
            plugin = plugins[plugin_name]
            metadata = plugin.call("get_metadata", "")
            metadata = json.loads(metadata)
            description = metadata['description']
        else:
            description = "The base help message for the call_run method"

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="extism",
            description=description,
        )

        # iterate through all of the params and add arg options for each
        params = json.loads(metadata['params'])
        #console.print(params)
        for param in params:
            parser.add_argument(
                param['flag'],
                default=param['default'],
                dest=param["param"],
                help=param['desc'],
            )

        # if other_args and "-" not in other_args[0][0]:
        #     other_args.insert(0, "-n")

        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser and plugin_name:
            if self.stock.empty:
                no_data_message()
                return
            
            args_dict = vars(ns_parser)
            args_dict.pop('help')
            extism_view.display_strategy(plugin=plugin, name=plugin_name, symbol=self.ticker, data=self.stock, **args_dict)


    
