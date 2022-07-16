"""OpenBB Terminal API."""


import types
import functools


def copy_func(f):
    """Based on https://stackoverflow.com/a/13503277"""
    g = types.FunctionType(f.__code__, f.__globals__, name=f.__name__,
                           argdefs=f.__defaults__,
                           closure=f.__closure__)
    g = functools.update_wrapper(g, f)
    g.__kwdefaults__ = f.__kwdefaults__
    return g


class API_Factory():
    def __init__(self, model, view):
        self.model_only = False
        if view is None:
            self.model_only = True
            self.model = copy_func(model)
            print(self.model.__doc__)
        else:
            # Get attributes from functions
            self.model = copy_func(model)
            self.view = copy_func(view)

    def __call__(self, *args, **kwargs):
        if "chart" not in kwargs:
            kwargs["chart"] = False
        if kwargs["chart"] and (not self.model_only):
            kwargs.pop("chart")
            return self.view(*args, **kwargs)
        else:
            kwargs.pop("chart")
            return self.model(*args, **kwargs)
