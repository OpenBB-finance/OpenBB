from collections.abc import MutableMapping
from functools import reduce
from typing import Any, Dict, List


def nested_dict(test_str, sep, value) -> Dict:
    if sep not in test_str:
        return {test_str: value}
    key, val = test_str.split(sep, 1)
    return {key: nested_dict(val, sep, value)}


def get_list_of_dicts(d: Dict[str, str]) -> List[Dict[str, Any]]:
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
        list_of_dicts.append(nested_dict(k, "/", v.replace(" ", "").split(",")))
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


def generate_sources_dict(sources: Dict[str, str]) -> Dict[str, Any]:
    """Generate a dictionary of sources.

    Parameters
    ----------
    sources : Dict[str, str]
        The sources dictionary.

    Returns
    -------
    Dict[str, Any]
        The sources dictionary.
    """
    return merge_dicts(get_list_of_dicts(sources))
