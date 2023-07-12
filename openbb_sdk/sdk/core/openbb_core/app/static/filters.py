import builtins
import warnings

from openbb_core.app.model.abstract.warning import OpenBBWarning
from openbb_core.app.model.command_output import CommandOutput


def filter_inputs(**kwargs) -> dict:
    """Filter command inputs"""
    return kwargs


def filter_output(command_output: CommandOutput) -> CommandOutput:
    """Filter command output"""
    if command_output.warnings:
        for w in command_output.warnings:
            category = getattr(builtins, w.category, OpenBBWarning)
            warnings.warn(w.message, category)

    if command_output.error:
        raise Exception(command_output.error.message)

    return command_output
