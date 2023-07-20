import builtins

import pandas as pd
from pydantic import ValidationError

from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.command_output import CommandOutput
from openbb_core.app.utils import df_to_basemodel


def filter_call(func):
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
            print("ValidationError:\n")
            for error in e.errors():
                print(f"{error['loc'][-1]}: {error['msg']}")
        except Exception as e:
            if debug_mode:
                raise
            print(f"UnexpectedError: {e}")

    return inner


def filter_inputs(**kwargs) -> dict:
    """Filter command inputs"""
    for key, value in kwargs.items():
        if isinstance(value, pd.DataFrame):
            kwargs[key] = df_to_basemodel(value, index=True)

    return kwargs


def filter_output(command_output: CommandOutput) -> CommandOutput:
    """Filter command output"""
    if command_output.warnings:
        for w in command_output.warnings:
            category = getattr(builtins, w.category, OpenBBWarning)
            print(f"{category.__name__}: {w.message}")

    error = command_output.error
    if error:
        kind = error.error_kind or "CommandError"
        print(f"{kind}: {error.message}")

    chart = command_output.chart
    if chart and chart.error:
        kind = chart.error.error_kind or "ChartError"
        print(f"{kind}: {chart.error.message}")

    return command_output
