from openbb_terminal.sdk import openbb


def test_openbb():
    """Test the openbb function"""
    assert "stocks" in dir(openbb)


# from importlib import import_module
# from typing import Callable
# from openbb_terminal.sdk import trail_map


# def __get_method(method_path: str) -> Callable:
#     module_path, function_name = method_path.rsplit(".", 1)
#     module = import_module(module_path)
#     method = getattr(module, function_name)

#     return method


# def test_load_models():
#     map_dict = trail_map.map_dict

#     for trail in map_dict:
#         if "model" in map_dict[trail]:
#             method_path = map_dict[trail]["model"]
#             __get_method(method_path=method_path)


# def test_load_views():
#     map_dict = trail_map.map_dict

#     for trail in map_dict:
#         if "view" in map_dict[trail]:
#             method_path = map_dict[trail]["model"]
#             __get_method(method_path=method_path)
