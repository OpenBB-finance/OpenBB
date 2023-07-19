import builtins

from pydantic import ValidationError

from openbb_core.api.dependency.system import get_system_settings_sync
from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.command_output import CommandOutput


def base_filter(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            if get_system_settings_sync().debug_mode:
                raise
            print("ValidationError:\n")
            for error in e.errors():
                print(f"{error['loc'][-1]}: {error['msg']}")
        except Exception as e:
            if get_system_settings_sync().debug_mode:
                raise
            print(f"UnexpectedError: {e}")

    return inner


def filter_inputs(**kwargs) -> dict:
    """Filter command inputs"""
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
