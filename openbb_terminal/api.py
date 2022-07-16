"""OpenBB Terminal API."""

import types
import functools
from degiro_connector.core.helpers.lazy_loader import LazyLoader

"""
THIS IS SOME EXAMPLE OF USAGE

shortcuts = {
    "stocks.get_news": {
        "model": "openbb_terminal.common.newsapi_model.get_news",
    },
    "economy.bigmac": {
        "model": "openbb_terminal.economy.nasdaq_model.get_big_mac_index",
        "view": "openbb_terminal.economy.nasdaq_view.display_big_mac_index",
    },
}


api = APILoader(shortcuts=shortcuts)
api.stocks.get_news()
api.economy.bigmac(chart=True)
api.economy.bigmac(chart=False)
"""


def copy_func(f):
    """Based on https://stackoverflow.com/a/13503277"""
    g = types.FunctionType(
        f.__code__,
        f.__globals__,
        name=f.__name__,
        argdefs=f.__defaults__,
        closure=f.__closure__,
    )
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g


class API_Factory:
    def __init__(self, model, view):
        self.model_only = False
        if view is None:
            self.model_only = True
            self.model = copy_func(model)
            # print(self.model.__doc__)
        else:
            # Get attributes from functions
            self.model = copy_func(model)
            self.view = copy_func(view)

    def __call__(self, *args, **kwargs):
        if "chart" not in kwargs:
            kwargs["chart"] = False
        if kwargs["chart"] and (not self.model_only):
            kwargs.pop("chart")
            return self.view(*args, **kwargs)
        else:
            kwargs.pop("chart")
            return self.model(*args, **kwargs)


def get_function(function_path: str):
    module_path, function_name = function_path.rsplit(sep=".", maxsplit=1)
    module = LazyLoader.load_module(module_path=module_path)

    return getattr(module, function_name)


class Item:
    def __init__(self, function):
        self.__function = function

    def __call__(self, *args, **kwargs):
        self.__function(*args, **kwargs)


class APILoader:
    def __init__(self, shortcuts: dict):
        self.__mapping = self.build_mapping(shortcuts=shortcuts)
        self.load_items()

    def load_items(self):
        mapping = self.__mapping
        for shorcut, function in mapping.items():
            shortcut_split = shorcut.split(".")
            last_shortcurt = shortcut_split[-1]

            previous = self
            for item in shortcut_split[:-1]:
                next_item = Item(function=item)
                previous.__setattr__(item, next_item)
                previous = next_item

            previous.__setattr__(last_shortcurt, function)

    @staticmethod
    def build_mapping(shortcuts: dict):
        mapping = {}

        for shortcut in shortcuts.keys():
            model_path = shortcuts[shortcut].get("model")
            view_path = shortcuts[shortcut].get("view")

            if model_path:
                model_function = get_function(function_path=model_path)
            else:
                model_function = None

            if view_path:
                view_function = get_function(function_path=view_path)
            else:
                view_function = None

            mapping[shortcut] = API_Factory(model=model_function, view=view_function)

        return mapping
