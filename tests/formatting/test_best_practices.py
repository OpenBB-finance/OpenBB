from inspect import signature

from docs.generate import all_functions

# This is a list of modules to ignore
ignore_modules = ["os"]

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
}


def assert_overlaps(overlaps: list[str], sub_item: str, new_parent: str):
    if overlaps:
        overlap_str = "\n"
        for item in overlaps:
            overlap_str += f"{item}->{bad_params[item]}\n"
        raise NameError(
            f"Forbidden parameter{'s' if len(overlaps) > 1 else ''} in funcition"
            f" '{sub_item}' at {new_parent}. Replace the following: {overlap_str}"
        )


def test_bad_parameters():
    all_funcs = all_functions()
    for path, _, function in all_funcs:
        params = signature(function)
        overlaps = list(set(bad_params) & set(params.parameters.keys()))
        assert_overlaps(overlaps, function.__name__, path)
