from typing import Optional, List, Tuple
from inspect import signature
import pytest

# Certain openbb distributions like pip do not include the docs folder,
# this is needed for those tests
try:
    from docs.generate import all_functions
except ImportError:
    pytest.skip(allow_module_level=True)


# A dictionary where keys are bad parameter names and values are the correct replacements
bad_params = {
    "ticker": "symbol",
    "descend": "ascend",
    "descending": "ascend",
    "ascending": "ascend",
    "num": "limit",
    "sort_by": "sortby",
    "start": "start_date",
    "end": "end_date",
    "df": "data",
    "x": "independent_series",
    "y": "dependent_series",
    "expire": "expiry",
    "exp": "expiry",
    "expiration": "expiry",
    "vs": "to_symbol",
    "coin": "symbol",
    "coin_id": "symbol",
    "token": "symbol",
    "currency": "symbol",
    "country_code": "country",
    "sort_col": "sortby",
    "sort_field": "sortby",
    "num_tickers": "limit",
    "num_stocks": "limit",
    "since": "start_date",
    "until": "end_date",
    "top": "limit",
}


def create_overlaps(
    overlaps: List[str], func_name: str, func_path: str
) -> Optional[Tuple[List[str], str, str, str]]:
    """
    Checks if there is a bad parameter name in a function

    Parameters
    ----------
    overlaps : List[str]
        Any overlaps between forbidden parameters and the function's parameters
    func_name: str
        The name of the function
    func_path: str
        The path for the function

    Returns
    -------
    overlaps: Optional[Tuple[List[str], str, str, str]]
        Tuple[overlaps, func_name, func_path, overlaps_str]
    """
    if overlaps:
        overlap_str = "\n"
        for item in overlaps:
            overlap_str += f"{item}->{bad_params[item]}\n"
        return overlaps, func_name, func_path, overlap_str
    return None


def test_bad_parameters():
    all_funcs = all_functions()
    total_overlaps = 0
    all_overlaps: List[Tuple[List[str], str, str, str]] = []
    for path, _, function in all_funcs:
        params = signature(function)
        overlaps = list(set(bad_params) & set(params.parameters.keys()))
        new_overlaps = create_overlaps(overlaps, function.__name__, path)
        if new_overlaps:
            total_overlaps += 1
            all_overlaps.append(new_overlaps)
    final_str = ""
    if all_overlaps:
        for overlaps, func_name, func_path, overlap_str in all_overlaps:
            final_str += (
                f"Forbidden parameter{'s' if len(overlaps) > 1 else ''} in function"
                f" '{func_name}' at {func_path}. Replace the following: {overlap_str}\n\n"
            )

        final_str += f"\n\nTotal bad functions: {total_overlaps}"
        raise NameError(final_str)
