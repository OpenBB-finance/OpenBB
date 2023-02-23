from typing import Dict, List, Optional, Tuple

import pandas as pd

from openbb_terminal.portfolio.portfolio_optimization import (
    excel_model,
    optimizer_helper,
    optimizer_model,
)
from openbb_terminal.portfolio.portfolio_optimization.parameters import params_view
from openbb_terminal.rich_config import console


class PoEngine:
    """Portfolio Optimization Engine"""

    def __init__(
        self,
        symbols_categories: Optional[Dict[str, Dict[str, str]]] = None,
        symbols_file_path: Optional[str] = None,
        parameters_file_path: Optional[str] = None,
    ):
        """Initialize the engine

        Parameters
        ----------
        symbols_categories : Dict[str, float], optional
            Categories, by default None
        symbols_file_path : str, optional
            Symbols file path, by default None
        parameters_file_path : str, optional
            Parameters file path, by default None
        """

        self._categories: Dict[str, Dict[str, str]] = {}
        self._symbols: List[str] = []
        self._weights: Dict[str, float] = {}
        self._returns: pd.DataFrame = None
        self._params: Dict[str, float] = {}
        self._current_model: str

        if symbols_categories is not None:
            self._symbols, self._categories = PoEngine.__parse_dictionary(
                symbols_categories
            )

        elif symbols_file_path is not None:
            self._symbols, self._categories = excel_model.load_allocation(
                symbols_file_path
            )
        else:
            raise ValueError("symbols or file_path must be provided")

        if parameters_file_path is not None:
            self._params, self._current_model = params_view.load_file(
                parameters_file_path
            )

    @staticmethod
    def __parse_dictionary(
        symbols_categories: Dict[str, Dict[str, str]]
    ) -> Tuple[List[str], Dict[str, Dict[str, str]]]:
        """Parse the categories dictionary

        Parameters
        ----------
        symbols_categories : Dict[str, Dict[str, str]]
            Categories

        Returns
        -------
        Tuple[List[str], Dict[str, Dict[str, str]]]
            Symbols and categories
        """
        if isinstance(symbols_categories, dict):
            symbols = PoEngine.__get_symbols_from_categories(symbols_categories)
        else:
            raise TypeError("'symbols_categories' must be a dictionary.")

        for symbol in symbols:
            symbols_categories["CURRENCY"].setdefault(symbol, "USD")
            symbols_categories["CURRENT_INVESTED_AMOUNT"].setdefault(symbol, "0")

        return symbols, symbols_categories

    @staticmethod
    def __get_symbols_from_categories(
        symbols_categories: Dict[str, Dict[str, str]]
    ) -> List[str]:
        """Get the symbols from the categories dictionary

        Parameters
        ----------
        symbols_categories : Dict[str, Dict[str, str]], optional
            Categories

        Returns
        -------
        List[str]
            List of symbols
        """

        try:
            symbols = []
            for item in symbols_categories.items():
                _, values = item
                for v in values:
                    symbols.append(v)

            return list(set(symbols))

        except Exception:
            console.print(
                "Unsupported dictionary format. See `portfolio.po.load` examples for correct format."
            )
            return []

    def get_symbols(self):
        return self._symbols

    def get_available_categories(self) -> List[str]:
        """Get the available categories

        Returns
        -------
        List[str]
            Available categories
        """
        available_categories = list(self._categories.keys())

        if "CURRENT_INVESTED_AMOUNT" in available_categories:
            available_categories.remove("CURRENT_INVESTED_AMOUNT")

        return available_categories

    def get_category(self, category: Optional[str] = None) -> Dict[str, str]:
        """Get the category

        Parameters
        ----------
        category : str, optional
            Category, by default None

        Returns
        -------
        Dict[str, str]
            Category
        """
        if category is None:
            console.print("No category provided. Please provide a category.")
            return {}

        d = self.get_categories_dict()
        if category in d:
            return d[category]
        return {}

    def get_categories_dict(self) -> Dict[str, Dict[str, str]]:
        """Get the categories

        Returns
        -------
        Dict[str, Dict[str, str]]
            Categories
        """
        if not self._categories:
            console.print("No categories found. Use 'load' to load a file.")
            return {}
        return self._categories

    def get_category_df(self, category: Optional[str] = None) -> pd.DataFrame:
        """Get the category df

        Returns
        -------
        pd.DataFrame
            Category DataFrame
        """
        if category is None:
            console.print("No category provided. Please provide a category.")
            return pd.DataFrame()
        if not self._categories:
            console.print("No categories found. Use 'load' to load a file.")
            return pd.DataFrame()
        return optimizer_model.get_categories(
            weights=self._weights, categories=self._categories, column=category
        )

    def set_weights(self, weights: Dict[str, float]):
        """Set the weights

        Parameters
        ----------
        weights : Dict[str, float]
            Weights
        """
        self._weights = weights

    def get_weights(self, warning=True) -> Dict[str, float]:
        """Get the weights

        Parameters
        ----------
        warning : bool, optional
            Display warning, by default True

        Returns
        -------
        Dict[str, float]
            Weights
        """
        if not self._weights:
            if warning:
                console.print("No weights found. Please perform some optimization.")
            return {}
        return self._weights

    def get_weights_df(self, warning=True) -> pd.DataFrame:
        """Get the weights

        Parameters
        ----------
        warning : bool, optional
            Display warning, by default True

        Returns
        -------
        pd.DataFrame
            Weights
        """
        if not self._weights:
            if warning:
                console.print("No weights found. Please perform some optimization.")
            return pd.DataFrame()
        return optimizer_helper.dict_to_df(self._weights)

    def set_params(self, params: Dict[str, float], update=False):
        """Set the parameters

        Parameters
        ----------
        params : Dict[str, float]
            Parameters
        update : bool, optional
            Update the current model, by default False
        """
        if update:
            self._params.update(params)
        else:
            self._params = params

    def get_params(self) -> Dict:
        """Get the parameters

        Returns
        -------
        Dict
            Parameters
        """
        return self._params

    def set_params_from_file(self, file_path: str):
        """Set the parameters from a file

        Parameters
        ----------
        file_path : str
            File path
        """
        self._params, self._current_model = params_view.load_file(file_path)

    def set_current_model(self, model: str):
        """Set the current model

        Parameters
        ----------
        model : str
            Model
        """
        self._current_model = model

    def get_current_model(self) -> str:
        """Get the current model

        Returns
        -------
        str
            Current model
        """
        return self._current_model

    def set_returns(self, returns: pd.DataFrame):
        """Set the stock returns

        Parameters
        ----------
        returns : pd.DataFrame
            Stock returns
        """
        self._returns = returns

    def get_returns(self) -> pd.DataFrame:
        """Get the stock returns

        Returns
        -------
        pd.DataFrame
            Stock returns
        """
        if self._returns.empty:
            console.print("No returns found. Please perform some optimization.")
            return pd.DataFrame()
        return self._returns
