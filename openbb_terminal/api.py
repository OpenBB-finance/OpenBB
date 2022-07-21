"""OpenBB Terminal API."""
from inspect import signature, Parameter
import types
import functools
import importlib
from typing import Optional, Callable

"""
THIS IS SOME EXAMPLE OF USAGE FOR USING IT DIRECTLY IN JUPYTER NOTEBOOK
"""
functions = {
    "stocks.get_news": {
        "model": "openbb_terminal.common.newsapi_model.get_news",
    },
    "stocks.load": {
        "model": "openbb_terminal.stocks.stocks_helper.load",
    },
    "stocks.candle": {
        "model": "openbb_terminal.stocks.stocks_helper.load",
        "view": "openbb_terminal.stocks.stocks_helper.display_candle",
    },
    "stocks.fa.info": {
        "model": "openbb_terminal.stocks.fundamental_analysis.yahoo_finance_model.get_info"
    },
    "stocks.fa.income": {
        "model": "openbb_terminal.stocks.fundamental_analysis.av_model.get_income_statements"
    },
    "economy.bigmac": {
        "model": "openbb_terminal.economy.nasdaq_model.get_big_mac_index",
        "view": "openbb_terminal.economy.nasdaq_view.display_big_mac_index",
    },
}
"""
api = Loader(functions=functions)
api.stocks.get_news()
api.economy.bigmac(chart=True)
api.economy.bigmac(chart=False)


TO USE THE API DIRECTLY JUST IMPORT IT:
from openbb_terminal.api import openbb (or: from openbb_terminal.api import openbb as api)
"""


def copy_func(f: Callable) -> Callable:
    """Copies the contents and attributes of the entered function. Based on https://stackoverflow.com/a/13503277

    Parameters
    ----------
    f: Callable
        Function to be copied

    Returns
    -------
    g: Callable
        New function
    """
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


def change_docstring(api_callable, model: Callable, view: Callable = None):
    if view is None:
        api_callable.__doc__ = model.__doc__
        api_callable.__name__ = model.__name__
        api_callable.__signature__ = signature(model)
    else:
        index = view.__doc__.find("Parameters")
        all_parameters = (
            "\nAPI function, use the chart kwarg for getting the view model and it's plot. "
            "See every parmater below:\n\n\t"
            + view.__doc__[index:]
            + """chart: bool
    If the view and its chart shall be used"""
        )
        api_callable.__doc__ = (
            all_parameters
            + "\n\nModel doc:\n"
            + model.__doc__
            + "\n\nView doc:\n"
            + view.__doc__
        )
        api_callable.__name__ = model.__name__.replace("get_", "")
        parameters = [param for param in signature(view).parameters.values()]
        chart_parameter = [
            Parameter(
                "chart", Parameter.POSITIONAL_OR_KEYWORD, annotation=bool, default=False
            )
        ]
        api_callable.__signature__ = signature(view).replace(
            parameters=parameters + chart_parameter
        )

    return api_callable


class FunctionFactory:
    """The API Function Factory, which creates the callable instance"""

    def __init__(self, model: Callable, view: Callable = None):
        """Initialises the FunctionFactory instance

        Parameters
        ----------
        model: Callable
            The original model function from the terminal
        view: Callable
            The original view function from the terminal, this shall be set to None if the function has no charting
        """
        self.model_only = False
        if view is None:
            self.model_only = True
            self.model = copy_func(model)
        else:
            self.model = copy_func(model)
            self.view = copy_func(view)

    def api_callable(self, *args, **kwargs):
        """This returns the result of the command from the view or the model function based on the chart parameter

        Parameters
        ----------
        args
        kwargs

        Returns
        -------
        Result from the view or model
        """
        if "chart" not in kwargs:
            kwargs["chart"] = False
        if kwargs["chart"] and (not self.model_only):
            kwargs.pop("chart")
            return self.view(*args, **kwargs)
        else:
            kwargs.pop("chart")
            return self.model(*args, **kwargs)


class MenuFiller:
    """Creates a filler callable for the menus"""

    def __init__(self, function: Callable):
        self.__function = function

    def __call__(self, *args, **kwargs):
        print(self.__function(*args, **kwargs))

    def __repr__(self):
        return self.__function()


class Loader:
    """The Loader class"""

    def __init__(self, functions: dict):
        self.__function_map = self.build_function_map(functions=functions)
        self.load_menus()

    def __call__(self):
        """Prints help message"""
        print(self.__repr__())

    def __repr__(self):
        return """This is the API of the OpenBB Terminal.

        Use the API to get data directly into your jupyter notebook or directly use it in your application.

        ...

        For more information see the official documentation at: https://openbb-finance.github.io/OpenBBTerminal/api/
        """

    # TODO: Add settings
    def settings(self):
        pass

    def load_menus(self):
        """Creates the API structure (see openbb.stocks.command) by setting attributes and saving the functions"""

        def menu_message(menu: str, function_map: dict):
            """Creates a callable function, which prints a menus help message

            Parameters
            ----------
            menu: str
                Menu for which the help message is generated
            function_map: dict
                Dictionary with the functions and their shortcuts

            Returns
            -------
            Callable:
                Function which prints help message
            """
            filtered_dict = {k: v for (k, v) in function_map.items() if menu in k}

            def f():
                string = menu.upper() + " Menu\n\nThe api commands of the the menu:"
                for command in filtered_dict:
                    string += "\n\t<openbb>." + command
                return string

            return f

        function_map = self.__function_map
        for shortcut, function in function_map.items():
            shortcut_split = shortcut.split(".")
            last_shortcut = shortcut_split[-1]

            previous_menu = self
            for menu in shortcut_split[:-1]:
                if not hasattr(previous_menu, menu):
                    next_menu = MenuFiller(function=menu_message(menu, function_map))
                    previous_menu.__setattr__(menu, next_menu)
                    previous_menu = previous_menu.__getattribute__(menu)
                else:
                    previous_menu = previous_menu.__getattribute__(menu)
            previous_menu.__setattr__(last_shortcut, function)

    @staticmethod
    def load_module(module_path: str) -> Optional[types.ModuleType]:
        """Load a module from a path.

        Parameters
        ----------
        module_path: str
            Module"s path.

        Returns
        -------
        Optional[ModuleType]:
            Loaded module or None.
        """

        try:
            spec = importlib.util.find_spec(module_path)
        except ModuleNotFoundError:
            spec = None

        if spec is None:
            return None
        else:
            module = importlib.import_module(module_path)

            return module

    @classmethod
    def get_function(cls, function_path: str) -> Callable:
        """Get function from string path

        Parameters
        ----------
        cls
            Class
        function_path: str
            Function path from repository base root

        Returns
        -------
        Callable
            Function
        """
        module_path, function_name = function_path.rsplit(sep=".", maxsplit=1)
        module = cls.load_module(module_path=module_path)

        return getattr(module, function_name)

    @classmethod
    def build_function_map(cls, functions: dict) -> dict:
        """Builds dictionary with FunctionFactory instances as items

        Parameters
        ----------
        functions: dict
            Dictionary which has string path of view and model functions as keys. The items is dictionary with
            the view and model function as items of the respectivee "view" and "model" keys

        Returns
        -------
        dict
            Dictionary with FunctionFactory instances as items and string path as keys
        """
        function_map = {}

        for shortcut in functions.keys():
            model_path = functions[shortcut].get("model")
            view_path = functions[shortcut].get("view")

            if model_path:
                model_function = cls.get_function(function_path=model_path)
            else:
                model_function = None

            if view_path:
                view_function = cls.get_function(function_path=view_path)
            else:
                view_function = None

            function_factory = FunctionFactory(model=model_function, view=view_function)
            function_with_doc = change_docstring(
                types.FunctionType(function_factory.api_callable.__code__, {}),
                model_function,
                view_function,
            )
            function_map[shortcut] = types.MethodType(
                function_with_doc, function_factory
            )

        return function_map


openbb = Loader(functions=functions)
