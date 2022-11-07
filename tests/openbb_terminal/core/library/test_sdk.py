from importlib import import_module
from typing import Callable
from openbb_terminal.core.library.sdk import trail_map


def __get_method(method_path: str) -> Callable:
    module_path, function_name = method_path.rsplit(".", 1)
    module = import_module(module_path)
    method = getattr(module, function_name)

    return method

def test_load_models():
    map_list = trail_map.map_list

    for trail in map_list:
        if "model" in map_list[trail]:
            method_path = map_list[trail]["model"]
            __get_method(method_path=method_path)

def test_load_views():
    map_list = trail_map.map_list

    for trail in map_list:
        if "view" in map_list[trail]:
            method_path = map_list[trail]["model"]
            __get_method(method_path=method_path)
