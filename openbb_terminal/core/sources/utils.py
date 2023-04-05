from collections.abc import MutableMapping
from functools import reduce
from typing import Any, Dict, List, Tuple


def nested_dict(test_str, sep, value) -> Dict:
    if sep not in test_str:
        return {test_str: value}
    key, val = test_str.split(sep, 1)
    return {key: nested_dict(val, sep, value)}


def get_list_of_dicts(d: Dict[str, str], sep: str) -> List[Dict[str, Any]]:
    """Get list of dictionaries from a dictionary.

    Parameters
    ----------
    d : dict
        The dictionary to convert.

    Returns
    -------
    List[Dict[str, Any]]
        The list of dictionaries.
    """
    list_of_dicts = []
    for k, v in d.items():
        list_of_dicts.append(nested_dict(k, sep, v))
    return list_of_dicts


def recursive_merge(d1: Dict, d2: Dict) -> Dict:
    """Recursively merge dict d2 into dict d1.

    Source: https://stackoverflow.com/questions/7204805/how-to-merge-dictionaries-of-dictionaries

    Parameters
    ----------
    d1 : Dict
        The dictionary to be merged into.
    d2 : Dict
        The dictionary to merge into d1.

    Returns
    -------
    Dict
        The merged dictionary.
    """
    for k, v in d1.items():
        if k in d2 and all(isinstance(e, MutableMapping) for e in (v, d2[k])):
            d2[k] = recursive_merge(v, d2[k])

    d3 = d1.copy()
    d3.update(d2)
    return d3


def merge_dicts(list_of_dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge a list of dictionaries.

    Parameters
    ----------
    list_of_dicts : List[Dict[str, Any]]
        The list of dictionaries to merge.

    Returns
    -------
    Dict[str, Any]
        The merged dictionary.
    """
    result: Dict[str, Any] = {}
    for d in list_of_dicts:
        result = reduce(recursive_merge, (result, d))
    return result


def extend(d: Dict[str, str], sep: str = "/") -> Dict[str, Any]:
    """Extend a dictionary to nested dictionaries.

    Parameters
    ----------
    d : Dict[str, str]
        The dictionary to extend.
    sep : str, optional
        The separator to use, by default "/"

    Returns
    -------
    Dict[str, Any]
        The extended dictionary.
    """
    return merge_dicts(get_list_of_dicts(d, sep))


def flatten(d, parent_key="", sep="/") -> Dict[str, Any]:
    """Flatten a dictionary.

    Source: https://stackoverflow.com/questions/6027558/flatten-nested-dictionaries-compressing-keys

    Parameters
    ----------
    d : Dict
        The dictionary to flatten.
    parent_key : str, optional
        The parent key, by default ""
    sep : str, optional
        The separator to use, by default "/"

    Returns
    -------
    Dict[str, Any]
        The flattened dictionary.
    """
    items: List[Tuple[str, List[str]]] = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)
