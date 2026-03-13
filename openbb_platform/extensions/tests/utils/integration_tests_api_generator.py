"""Generate API integration tests."""

import argparse
import os
from pathlib import Path
import inspect as _inspect
from typing import Literal

import pytest
import requests
from openbb_charting import Charting
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap

from .integration_tests_generator import get_test_params


def get_http_method(api_paths: dict[str, dict], route: str):
    """Given a set of paths and a route, return the http method for that route."""
    route_info = api_paths.get(route)
    if not route_info:
        return route_info
    return list(route_info.keys())[0]


def get_post_flat_params(hints: dict[str, type]):
    """Flattens the params for a post request."""
    return list(hints.keys())


def write_init_test_template(http_method: str, path: str):
    """Write some common initialization for the tests with the defined template."""
    http_template_imports = {"get": "", "post": "import json"}
    template = http_template_imports[http_method]
    template += """import base64

import pytest
import requests
from openbb_core.env import Env
from openbb_core.provider.utils.helpers import get_querystring


@pytest.fixture(scope="session")
def headers():
    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return {"Authorization": f"Basic {base64_bytes.decode('ascii')}"}


# pylint: disable=redefined-outer-name

"""

    with open(path, "w") as f:
        f.write(template)


def write_test_w_template(
    http_method: Literal["post", "get"],
    params_list: list[dict[str, str | bool]],
    route: str,
    path: str,
    chart: bool = False,
):
    """Write the test with the defined template."""
    params_str = ",\n".join([f"({params})" for params in params_list])

    http_template_request = {
        "get": "requests.get(url, headers=headers, timeout=10)",
        "post": "requests.post(url, headers=headers, timeout=10, data=body)",
    }

    http_template_params = {"get": "", "post": "body = json.dumps(params.pop('data'))"}

    test_name_extra = "chart_" if chart else ""

    chart_extra_template = """
    assert result.json()["chart"]
    assert list(result.json()["chart"].keys()) == ["content", "format"]
    """

    template = f"""
@pytest.mark.parametrize(
    "params",
    [{params_str}],
)
@pytest.mark.integration
def test_{test_name_extra}{route.replace("/", "_")[1:]}(params, headers):
    params = {{p: v for p, v in params.items() if v}}
    {http_template_params[http_method]}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1{route}?{{query_str}}"
    result = {http_template_request[http_method]}
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
"""
    if chart:
        template += chart_extra_template

    with open(path, "a") as f:
        f.write(template)


@pytest.fixture(scope="function")
def test_exists(route: str, path: str):
    """Check if a test exists."""
    with open(path) as f:
        return route.replace("/", "_")[1:] in f.read()


# pylint: disable=W0621
def write_commands_integration_tests(
    command_map: CommandMap,
    provider_interface: ProviderInterface,
    api_paths: dict[str, dict],
) -> list[str]:
    """Write the commands integration tests."""
    commands_not_found = []

    cm_map = command_map.map
    cm_models = command_map.commands_model
    provider_interface_map = provider_interface.map

    for route in cm_map:
        http_method = get_http_method(api_paths, f"/api/v1{route}")

        menu = route.split("/")[1]
        path = os.path.join(
            "openbb_platform", "extensions", menu, "integration", f"test_{menu}_api.py"
        )
        if not os.path.exists(path):
            write_init_test_template(http_method=http_method, path=path)  # type: ignore

        if not http_method:
            commands_not_found.append(route)
        else:
            sig = _inspect.signature(cm_map[route])
            param_names = [k for k in sig.parameters.keys() if k not in ("cc", "return")]

            params_list = (
                [{k: "" for k in param_names}]
                if http_method == "post"
                else get_test_params(
                    model_name=cm_models[route],  # type: ignore
                    provider_interface_map=provider_interface_map,
                )
            )

            if not test_exists(route=route, path=path):
                write_test_w_template(
                    http_method=http_method,  # type: ignore
                    params_list=params_list,  # type: ignore
                    route=route,
                    path=path,
                )

    return commands_not_found


def write_charting_extension_integration_tests():
    """Write the charting extension integration tests."""
    import openbb_charting  # pylint: disable=import-outside-toplevel

    functions = Charting.functions()

    charting_ext_path = Path(openbb_charting.__file__).parent.parent
    test_file = charting_ext_path / "integration" / "test_charting_api.py"

    for function in functions:
        route = "/" + function.replace("_", "/")
        if not test_exists(route=function, path=str(test_file)):
            write_test_w_template(
                http_method="post",
                params_list=[{"chart": True}],
                route=route,
                path=str(test_file),
                chart=True,
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

    r = requests.get("http://0.0.0.0:8000/openapi.json", timeout=10).json()

    if not r:
        raise Exception("Could not get openapi.json")

    command_map = CommandMap()
    provider_interface = ProviderInterface()

    if commands:
        commands_not_found_in_openapi = write_commands_integration_tests(
            command_map=command_map,
            provider_interface=provider_interface,
            api_paths=r["paths"],
        )
        if commands_not_found_in_openapi:
            print(  # noqa
                f"Commands not found in openapi.json: {commands_not_found_in_openapi}"
            )

    if charting:
        write_charting_extension_integration_tests()
