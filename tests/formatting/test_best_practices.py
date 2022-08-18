from inspect import isfunction, ismodule, signature
from typing import List

from openbb_terminal import api

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


def assert_overlaps(overlaps: List[str], sub_item: str, new_parent: str):
    if overlaps:
        overlap_str = "\n"
        for item in overlaps:
            overlap_str += f"{item}->{bad_params[item]}\n"
        raise NameError(
            f"Forbidden parameter{'s' if len(overlaps) > 1 else ''} in funcition"
            f" '{sub_item}' at {new_parent}. Replace the following: {overlap_str}"
        )


def test_no_bad_parameters():
    command_count = 0
    pre_modules = []
    for module in dir(api):
        if ismodule(getattr(api, module)):
            pre_modules.append(module)
    modules = [(x, api) for x in pre_modules]
    i = 0
    while len(modules) > i:
        item, parent = modules[i]
        if str(item)[0] == "_":
            i += 1
            continue
        if ismodule(getattr(parent, item)):
            new_parent = getattr(parent, item)
            if "api" not in str(new_parent):
                i += 1
                continue
            for sub_item in dir(new_parent):
                if str(sub_item)[0] == "_":
                    continue
                # If we find a module we want to add it to our list to check
                if ismodule(getattr(new_parent, sub_item)):
                    if sub_item not in ignore_modules:
                        # print(f"{new_parent}: {sub_item}")
                        modules.append((sub_item, new_parent))
                # If we find a function we want to check it for forbidden parameters
                elif isfunction(getattr(new_parent, sub_item)):
                    command_count += 1
                    params = signature(getattr(new_parent, sub_item))
                    overlaps = list(set(bad_params) & set(params.parameters.keys()))
                    assert_overlaps(overlaps, sub_item, new_parent)
                    # print(command_count)
        i += 1
