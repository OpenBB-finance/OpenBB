"""Integration test generator."""
from pathlib import Path, PosixPath
from platform.core.openbb_core.app.provider_interface import ProviderInterface
from platform.core.openbb_core.app.router import CommandMap
from typing import Any, Dict, List, Literal, get_origin

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

cm = CommandMap(coverage_sep=".")


def find_extensions():
    """Find extensions."""
    filter_ext = ["tests", "ta", "qa", "econometrics", "charting"]
    extensions = [x for x in Path("openbb_platform/extensions").iterdir() if x.is_dir()]
    extensions = [x for x in extensions if x.name not in filter_ext]
    return extensions


def create_integration_test_files(extensions: List[PosixPath]) -> None:
    """Create integration test files for the python interface."""
    for extension in extensions:
        extension_name = extension.name
        test_file_name = f"test_{extension_name}_python.py"
        test_file = extension / "integration" / test_file_name
        if not test_file.exists():
            with open(test_file, "w", encoding="utf-8", newline="\n") as f:
                f.write(
                    f'''"""Test {extension_name} extension."""
import pytest
from openbb_core.app.model.obbject import OBBject

@pytest.fixture(scope="session")
def obb(pytestconfig):
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb

        return openbb.obb
    '''
                )


def get_model_params(param_fields: Dict[str, FieldInfo]) -> Dict[str, Any]:
    """Get the test params for the fetcher based on the required standard params."""
    test_params: Dict[str, Any] = {}
    for field_name, field in param_fields.items():
        if field.default and field.default is not PydanticUndefined:
            test_params[field_name] = field.default
        elif not field.default or field.default is PydanticUndefined:
            example_dict = {
                "symbol": "AAPL",
                "symbols": "AAPL,MSFT",
                "start_date": "2023-01-01",
                "end_date": "2023-06-06",
                "country": "Portugal",
                "date": "2023-01-01",
                "countries": ["portugal", "spain"],
            }
            if field_name in example_dict:
                test_params[field_name] = example_dict[field_name]
            elif field.annotation == str:
                test_params[field_name] = "TEST_STRING"
            elif field.annotation == int:
                test_params[field_name] = 1
            elif field.annotation == float:
                test_params[field_name] = 1.0
            elif field.annotation == bool:
                test_params[field_name] = True
            elif get_origin(field.annotation) is Literal:
                test_params[field_name] = field.annotation.__args__[0]

    return test_params


def get_test_params(
    model_name: str, provider_interface_map: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Get the test params for the integration test."""
    test_params_list: List[Dict[str, Any]] = []
    standard_params = get_model_params(
        param_fields=provider_interface_map[model_name]["openbb"]["QueryParams"][
            "fields"
        ]
    )

    test_params_list.append(standard_params)

    for provider in provider_interface_map[model_name]:
        if provider != "openbb":
            test_params: Dict[str, Any] = get_model_params(
                param_fields=provider_interface_map[model_name][provider][
                    "QueryParams"
                ]["fields"]
            )
            if test_params:
                test_params["provider"] = provider
                test_params.update(standard_params)
                test_params_list.append(test_params)

    return test_params_list


def add_test_commands_to_file(  # pylint: disable=W0102
    extensions: List[PosixPath],
    commands_model: Dict[str, str] = cm.commands_model,
) -> None:
    """Add test commands to file."""
    provider_interface = ProviderInterface()
    provider_interface_map = provider_interface.map

    template = """\n\n@pytest.mark.parametrize(
    "params",
    [
        {params}
    ],
)
@pytest.mark.integration
def test_{test_name}(**params, obb):
    result = obb.{command_name}(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
"""
    for extension in extensions:
        extension_name = extension.name
        test_file_name = f"test_{extension_name}_python.py"
        test_file = extension / "integration" / test_file_name
        with open(test_file, "a", encoding="utf-8", newline="\n") as f:
            for command in commands_model:
                if extension_name in command and command.startswith(
                    f".{extension_name}."
                ):
                    extension_name = command.split(".")[1]

                    if len(command.split(".")) > 3:
                        test_name = (
                            extension_name
                            + "_"
                            + command.split(".")[2]
                            + "_"
                            + command.split(".")[3]
                        )
                    elif len(command.split(".")) == 3:
                        test_name = extension_name + "_" + command.split(".")[2]

                    command_name = command.split(".")[-1]
                    if "_" in command_name:
                        full_command_name = test_name.replace("_", ".", 2)
                        # The code below double checks if the full command name is correct.
                        # This eliminates edge cases.
                        fix_full_command_name = full_command_name.split(".")
                        for i, part in enumerate(fix_full_command_name):
                            if part == command_name.split("_")[0]:
                                fix_full_command_name[i] = command_name
                                fix_full_command_name.pop()

                        full_command_name = ".".join(fix_full_command_name)

                    else:
                        full_command_name = test_name.replace("_", ".")

                    test_params_list = get_test_params(
                        model_name=commands_model[command],
                        provider_interface_map=provider_interface_map,
                    )

                    params = ""
                    for test_params in test_params_list:
                        params += f"({test_params}),\n"

                    read_file = open(test_file)  # noqa
                    if full_command_name not in read_file.read():
                        f.write(
                            template.format(
                                test_name=test_name,
                                command_name=full_command_name,
                                params=params,
                            )
                        )


def write_integration_test() -> None:
    """Write integration test."""
    extensions = find_extensions()
    create_integration_test_files(extensions)
    add_test_commands_to_file(extensions)


if __name__ == "__main__":
    write_integration_test()
