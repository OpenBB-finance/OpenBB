"""Integration test generator."""
import argparse
from pathlib import Path, PosixPath
from typing import (
    Any,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    get_origin,
    get_type_hints,
)

from openbb_core.app.charting_service import ChartingService
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

TEST_TEMPLATE = """\n\n@parametrize(
    "params",
    [
        {params}
    ],
)
@pytest.mark.integration
def test_{test_name}(params, obb):
    params = {{p: v for p, v in params.items() if v}}

    result = obb.{command_name}(**params)
    assert result
    assert isinstance(result, OBBject)
    assert len(result.results) > 0
    {extra}
"""


def find_extensions(filter_chart: Optional[bool] = True):
    """Find extensions."""
    filter_ext = ["tests", "__pycache__"]
    if filter_chart:
        filter_ext.append("charting")
    extensions = [x for x in Path("openbb_platform/extensions").iterdir() if x.is_dir()]
    extensions = [x for x in extensions if x.name not in filter_ext]
    return extensions


def create_integration_test_files(extensions: List[PosixPath]) -> None:
    """Create integration test files for the python interface."""
    for extension in extensions:
        extension_name = extension.name
        test_file_name = f"test_{extension_name}_python.py"
        if not (extension / "integration").exists():
            (extension / "integration").mkdir()
        test_file = extension / "integration" / test_file_name
        if not test_file.exists():
            with open(test_file, "w", encoding="utf-8", newline="\n") as f:
                f.write(
                    f'''"""Test {extension_name} extension."""
import pytest
from openbb_core.app.model.obbject import OBBject
from extensions.tests.conftest import parametrize


@pytest.fixture(scope="session")
def obb(pytestconfig):  # pylint: disable=inconsistent-return-statements
    """Fixture to setup obb."""

    if pytestconfig.getoption("markexpr") != "not integration":
        import openbb  # pylint: disable=import-outside-toplevel

        return openbb.obb


# pylint: disable=redefined-outer-name
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
                test_params[field_name] = field.annotation.__args__[0]  # type: ignore

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

            # We add provider even if `test_params` is empty to test the provider itself
            test_params["provider"] = provider
            test_params.update(standard_params)
            test_params_list.append(test_params)

    return test_params_list


def get_test_params_data_processing(hints: Dict[str, Type]):
    """Get the test params for the data processing commands."""
    return list(hints.keys())


def get_full_command_name_and_test_name(route: str) -> Tuple[str, str]:
    """Get the full command name and test name."""
    cmd_parts = route.split("/")
    del cmd_parts[0]

    menu = cmd_parts[0]
    command = cmd_parts[-1]
    sub_menus = cmd_parts[1:-1]

    sub_menus_str_test_name = f"_{'_'.join(sub_menus)}" if sub_menus else ""
    sub_menu_str_cmd = f".{'.'.join(sub_menus)}" if sub_menus else ""

    full_command = f"{menu}{sub_menu_str_cmd}.{command}"
    test_name = f"{menu}{sub_menus_str_test_name}_{command}"

    return test_name, full_command


def test_exists(command_name: str, path: str):
    """Check if test exists."""
    with open(path) as f:
        return command_name in f.read()


def write_to_file_w_template(test_file, params_list, full_command, test_name, extra=""):
    """Write to file with template."""
    params = ",\n".join(f"({test_params})" for test_params in params_list)

    if not test_exists(command_name=full_command, path=test_file):
        with open(test_file, "a", encoding="utf-8", newline="\n") as f:
            f.write(
                TEST_TEMPLATE.format(
                    test_name=test_name,
                    command_name=full_command,
                    params=params,
                    extra=extra,
                )
            )


def write_test(
    test_file: PosixPath,
    commands_model: Dict[str, str],
    extension_name: str,
    provider_interface_map: Dict[str, Any],
):
    """Write test."""
    for route, model in commands_model.items():
        if extension_name in route and route.startswith(f"/{extension_name}/"):
            test_name, full_command = get_full_command_name_and_test_name(route=route)

            test_params_list = get_test_params(
                model_name=model,
                provider_interface_map=provider_interface_map,
            )

            write_to_file_w_template(
                test_file=test_file,
                params_list=test_params_list,
                full_command=full_command,
                test_name=test_name,
            )


def write_test_data_processing(
    test_file: PosixPath, commands_map: Dict[str, str], extension_name: str
):
    """Write test for data processing commands."""
    for route, _ in commands_map.items():
        if extension_name in route and route.startswith(f"/{extension_name}/"):
            test_name, full_command = get_full_command_name_and_test_name(route=route)

            hints = get_type_hints(commands_map[route])
            hints.pop("cc", None)
            hints.pop("return", None)
            test_params_list = [{k: "" for k in get_test_params_data_processing(hints)}]

            write_to_file_w_template(
                test_file=test_file,
                params_list=test_params_list,
                full_command=full_command,
                test_name=test_name,
            )


def add_test_commands_to_file(  # pylint: disable=W0102
    extensions: List[PosixPath],
) -> None:
    """Add test commands to file."""
    provider_interface = ProviderInterface()
    provider_interface_map = provider_interface.map

    cm = CommandMap()
    commands_model = cm.commands_model
    commands_map = cm.map

    extensions_names = [path.name for path in extensions]
    extensions_w_models = list({route.split("/")[1] for route in commands_model})
    extensions_data_processing = [
        ext for ext in extensions_names if ext not in extensions_w_models
    ]

    for extension in extensions:
        extension_name = extension.name
        test_file_name = f"test_{extension_name}_python.py"
        test_file = extension / "integration" / test_file_name

        if extension_name in extensions_data_processing:
            write_test_data_processing(
                test_file=test_file,
                commands_map=commands_map,  # type: ignore
                extension_name=extension_name,
            )
        else:
            write_test(
                test_file=test_file,
                commands_model=commands_model,  # type: ignore
                extension_name=extension_name,
                provider_interface_map=provider_interface_map,
            )


def write_commands_integration_tests() -> None:
    """Write integration test."""
    extensions = find_extensions()
    create_integration_test_files(extensions)
    add_test_commands_to_file(extensions)


def write_charting_extension_integration_tests():
    """Write charting extension integration tests."""
    import openbb_charting  # pylint: disable=import-outside-toplevel

    functions = ChartingService.get_implemented_charting_functions()

    charting_ext_path = Path(openbb_charting.__file__).parent.parent
    test_file = charting_ext_path / "integration" / "test_charting_python.py"

    extra = """assert result.chart.content
    assert isinstance(result.chart.fig, OpenBBFigure)"""

    for func in functions:
        write_to_file_w_template(
            test_file=test_file,
            params_list=[{"chart": "True"}],
            full_command=func.replace("_", "."),
            test_name=f"chart_{func}",  # TODO: fix the name of the charting library
            extra=extra,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="API Integration Tests Generator",
        description="Generate API integration tests",
    )
    parser.add_argument(
        "--charting",
        dest="charting",
        default=True,
        action="store_false",
        help="Generate charting extension integration tests",
    )
    parser.add_argument(
        "--commands",
        dest="commands",
        default=True,
        action="store_false",
        help="Generate commands integration tests",
    )

    args = parser.parse_args()
    charting = args.charting
    commands = args.commands

    if commands:
        write_commands_integration_tests()

    if charting:
        write_charting_extension_integration_tests()
