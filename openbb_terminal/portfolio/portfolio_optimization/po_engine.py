import pandas as pd
from typing import Dict, List

from openbb_terminal.portfolio.portfolio_optimization import (
    excel_model,
    optimizer_model,
    optimizer_helper,
)
from openbb_terminal.portfolio.portfolio_optimization.parameters import params_view


class PoEngine:
    """Portfolio Optimization Engine"""

    def __init__(
        self,
        symbols: List[str] = None,
        categories: Dict[str, float] = None,
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

        self._categories: Dict[str, float] = categories or {}
        self._weights: Dict[str, float] = {}
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

    def get_categories(self):
        return self._categories

    def set_weights(self, weights: Dict[str, float]):
        """Set the weights

        Parameters
        ----------
        weights : Dict[str, float]
            Weights
        """
        self._weights = weights

    def get_weights(self) -> pd.DataFrame:
        """Get the weights

        Returns
        -------
        pd.DataFrame
            Weights
        """
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

    def get_category_df(self, category: str = "ASSET_CLASS") -> pd.DataFrame:
        """Get the category df

        Returns
        -------
        pd.DataFrame
            Category DataFrame
        """
        return optimizer_model.get_categories(
            weights=self._weights, categories=self._categories, column=category
        )
