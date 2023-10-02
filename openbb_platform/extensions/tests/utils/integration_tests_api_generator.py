import os
from typing import Dict, List, Type, get_type_hints

import requests
from extensions.tests.utils.integration_tests_generator import get_test_params
from openbb_core.app.provider_interface import ProviderInterface
from openbb_core.app.router import CommandMap


def get_http_method(api_paths: Dict[str, dict], route: str):
    route_info = api_paths.get(route, None)
    if not route_info:
        return route_info
    return list(route_info.keys())[0]


def get_post_flat_params(hints: Dict[str, Type]):
    return list(hints.keys())


def write_init_test_template(http_method: str, path: str):
    http_template_imports = {"get": "", "post": "import json"}
    template = http_template_imports[http_method]
    template += """
import pytest
import requests
from openbb_provider.utils.helpers import get_querystring


def get_token():
    return requests.post(
        "http://0.0.0.0:8000/api/v1/account/token",
        data={"username": "openbb", "password": "openbb"},
        timeout=5,
    )


@pytest.fixture(scope="session")
def headers():
    access_token = get_token().json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}
"""

    with open(path, "w") as f:
        f.write(template)


def write_test_w_template(
    http_method: str, params_list: List[Dict[str, str]], route: str, path: str
):
    params_str = ",\n".join([f"({params})" for params in params_list])

    http_template_request = {
        "get": "requests.get(url, headers=headers, timeout=5)",
        "post": "requests.post(url, headers=headers, timeout=5, data=data)",
    }

    http_template_params = {"get": "", "post": "data = json.dumps(params.pop('data'))"}

    template = f"""
@pytest.mark.parametrize(
    "params",
    [{params_str}],
)
@pytest.mark.integration
def test_{route.replace("/", "_")[1:]}(params, headers):
    params = {{p: v for p, v in params.items() if v}}
    {http_template_params[http_method]}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1{route}?{{query_str}}"
    result = {http_template_request[http_method]}
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
"""

    with open(path, "a") as f:
        f.write(template)


def test_exists(route: str, path: str):
    with open(path) as f:
        return route.replace("/", "_")[1:] in f.read()


def write_integration_tests(
    command_map: CommandMap,
    provider_interface: ProviderInterface,
    api_paths: Dict[str, dict],
) -> List[str]:
    commands_not_found = []

    commandmap_map = command_map.map
    commandmap_models = command_map.commands_model
    provider_interface_map = provider_interface.map

    for route in commandmap_map:
        http_method = get_http_method(api_paths, f"/api/v1{route}")

        menu = route.split("/")[1]
        path = os.path.join(
            "openbb_platform", "extensions", menu, "integration", f"test_{menu}_api.py"
        )
        if not os.path.exists(path):
            write_init_test_template(http_method=http_method, path=path)

        if not http_method:
            commands_not_found.append(route)
        else:
            hints = get_type_hints(commandmap_map[route])
            hints.pop("cc", None)
            hints.pop("return", None)

            params_list = (
                [{k: "" for k in get_post_flat_params(hints)}]
                if http_method == "post"
                else get_test_params(
                    model_name=commandmap_models[route],
                    provider_interface_map=provider_interface_map,
                )
            )

            if not test_exists(route=route, path=path):
                write_test_w_template(
                    http_method=http_method,
                    params_list=params_list,
                    route=route,
                    path=path,
                )

    return commands_not_found


if __name__ == "__main__":
    r = requests.get("http://0.0.0.0:8000/openapi.json", timeout=5).json()

    if not r:
        raise Exception("Could not get openapi.json")

    command_map = CommandMap()
    provider_interface = ProviderInterface()

    commands_not_found_in_openapi = write_integration_tests(
        command_map=command_map,
        provider_interface=provider_interface,
        api_paths=r["paths"],
    )

    if commands_not_found_in_openapi:
        print(  # noqa
            f"Commands not found in openapi.json: {commands_not_found_in_openapi}"
        )
