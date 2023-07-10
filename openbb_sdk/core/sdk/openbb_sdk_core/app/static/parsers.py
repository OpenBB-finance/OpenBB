import builtins
import warnings

from openbb_sdk_core.app.model.abstract.warning import OpenBBWarning
from openbb_sdk_core.app.model.command_output import CommandOutput


def parse_command_inputs(**kwargs) -> dict:
    """Parse and edit the inputs before running the command"""
    return kwargs


def parse_command_output(command_output: CommandOutput) -> CommandOutput:
    """Parse command output"""
    if command_output.warnings:
        for w in command_output.warnings:
            category = getattr(builtins, w.category, OpenBBWarning)
            warnings.warn(w.message, category)

    if command_output.error:
        raise Exception(command_output.error.message)

    return command_output
