"""OpenBB filters."""

import builtins
from functools import wraps

import pandas as pd
from pydantic import ValidationError

from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.obbject import Obbject
from openbb_core.app.utils import df_to_basemodel


class OpenBBError(Exception):
    """A custom exception for OpenBB errors."""


def filter_call(func):
    """Filter command call."""

    @wraps(wrapped=func)
    def inner(*args, **kwargs):
        self = args[0]
        debug_mode = (
            self._command_runner_session.command_runner.system_settings.debug_mode
        )
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            if debug_mode:
                raise

            msg = ""
            for error in e.errors():
                msg += f"\narg: {error['loc'][-1]} -> {error['msg']}"

            raise OpenBBError(msg) from e

    return inner


def filter_inputs(**kwargs) -> dict:
    """Filter command inputs."""
    for key, value in kwargs.items():
        if isinstance(value, pd.DataFrame):
            kwargs[key] = df_to_basemodel(value, index=True)

    return kwargs


def filter_output(obbject: Obbject) -> Obbject:
    """Filter command output."""
    if obbject.warnings:
        for w in obbject.warnings:
            category = getattr(builtins, w.category, OpenBBWarning)
            print(f"{category.__name__}: {w.message}")

    error = obbject.error
    if error:
        raise OpenBBError(error.message)

    chart = obbject.chart
    if chart and chart.error:
        raise OpenBBError(chart.error.message)

    return obbject
