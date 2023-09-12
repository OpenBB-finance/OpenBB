"""OpenBB Provider Package."""

import importlib
from pathlib import Path
from typing import Dict

from openbb_provider.abstract.data import Data

DATA_MODELS: Dict[str, Data] = {}


def _import_data_models():
    """Import all data BaseModels from current folder.

    e.g.:
        BalanceSheetData -> openbb_provider.standard_models.balance_sheet has BalanceSheetData class
    """

    def _import_data_model(model_name):
        """Import data model."""
        module = importlib.import_module(
            f"openbb_provider.standard_models.{model_name}"
        )
        # look for a class that ends with Data and is a subclass of Data
        try:
            model = next(
                getattr(module, attr)
                for attr in dir(module)
                if attr.endswith("Data")
                and issubclass(getattr(module, attr), Data)
                and attr != "Data"
            )
            DATA_MODELS[model.__name__.replace("Data", "")] = model
        except StopIteration:
            pass

    for file in Path(__file__).parent.glob("*.py"):
        if file.name.startswith("__"):
            continue
        _import_data_model(file.stem)


_import_data_models()

__all__ = ["DATA_MODELS"]
