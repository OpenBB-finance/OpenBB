from typing import Dict

import pandas as pd


def get_datasets(data: Dict[str, pd.DataFrame]):
    datasets = {}
    for key, value in data.items():
        for column in value:
            datasets[f"{key}.{column}"] = {column: None, key: None}
    return datasets


def get_ending(dataset: str, column: str) -> str:
    ending = ""
    if dataset:
        ending += f" from dataset '{dataset}'"
    if column:
        ending += f" of '{column}'"
    return ending
