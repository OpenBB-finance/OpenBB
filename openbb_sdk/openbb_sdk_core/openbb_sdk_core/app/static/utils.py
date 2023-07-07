import builtins
import warnings

from openbb_sdk_core.app.model.abstract.warning import OpenBBWarning
from openbb_sdk_core.app.model.command_output import CommandOutput


def parse_command_input(**kwargs) -> dict:
    # Here we can inject provider defaults
    # Covert data from pandas.DataFrame to BaseModel
    # And other input parsing stuff
    if "provider_choices" in kwargs:
        if kwargs["provider_choices"].get("provider", None) is None:
            raise NotImplementedError(
                "'provider' cannot be None, defaults are not implemented yet."
            )
    return kwargs


# POC
# if "data" in parameter_map:
#     code += "        if isinstance(data, pandas.DataFrame):\n"
#     code += "            data = df_to_basemodel(data, data.index.name is not None)\n"
#     code += "\n"

# if "provider_choices" in parameter_map:
#     code += "        if provider is None:\n"
#     code += "            defaults = self._command_runner_session.user_settings.defaults.endpoints.get(\n"
#     code += f'                "{path}",\n'
#     code += "                None,\n"
#     code += "            )\n"
#     code += '            provider = defaults.get("provider", None) if defaults else Parameter.empty\n'
#     code += "\n"


def parse_command_output(command_output: CommandOutput) -> CommandOutput:
    if command_output.warnings:
        for w in command_output.warnings:
            category = getattr(builtins, w.category, OpenBBWarning)
            warnings.warn(w.message, category)

    if command_output.error:
        raise Exception(command_output.error.message)

    return command_output
