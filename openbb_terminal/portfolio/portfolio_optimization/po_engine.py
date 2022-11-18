from typing import Dict, List
import pandas as pd
from openbb_terminal.portfolio.portfolio_optimization import (
    excel_model,
    optimizer_model,
    optimizer_helper,
)
from openbb_terminal.portfolio.portfolio_optimization.parameters import params_view
from openbb_terminal.rich_config import console


class PoEngine:
    """Portfolio Optimization Engine"""

    def __init__(
        self,
        symbols: List[str] = None,
        categories: Dict[str, Dict[str, str]] = None,
        symbols_file_path: str = None,
        parameters_file_path: str = None,
    ):
        """Initialize the engine

        Parameters
        ----------
        symbols : List[str]
            List of symbols
        categories : Dict[str, float], optional
            Categories, by default None
        symbols_file_path : str, optional
            Symbols file path, by default None
        parameters_file_path : str, optional
            Parameters file path, by default None
        """

        self._categories: Dict[str, Dict[str, str]] = categories or {}
        self._weights: Dict[str, float] = {}
        self._returns: pd.DataFrame = None
        self._params: Dict[str, float] = {}
        self._current_model: str

        if symbols is not None:
            self._symbols: List[str] = symbols
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

    def get_symbols(self):
        return self._symbols

    def get_available_categories(self) -> List[str]:
        """Get the available categories

        Returns
        -------
        List[str]
            Available categories
        """
        return list(self._categories.keys())

    def set_categories_dict(self, categories: Dict[str, Dict[str, str]]):
        """Set the categories

        Parameters
        ----------
        categories : Dict[str, Dict[str, str]]
            Categories
        """
        self._categories = categories

    def get_category(self, category: str = None) -> Dict[str, str]:
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

    def get_category_df(self, category: str = None) -> pd.DataFrame:
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

    def get_weights(self) -> Dict[str, float]:
        """Get the weights

        Returns
        -------
        Dict[str, float]
            Weights
        """
        if not self._weights:
            console.print("No weights found. Please perform some optimization.")
            return {}
        return self._weights

    def get_weights_df(self) -> pd.DataFrame:
        """Get the weights

        Returns
        -------
        pd.DataFrame
            Weights
        """
        if not self._weights:
            console.print("No weights found. Please perform some optimization.")
            return pd.DataFrame()
        return optimizer_helper.dict_to_df(self._weights)

    def set_params(self, params: Dict[str, float]):
        """Set the parameters

        Parameters
        ----------
        params : Dict[str, float]
            Parameters
        """
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
