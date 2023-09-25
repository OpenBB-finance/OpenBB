import os
from typing import Callable, Dict, List, Type, get_args, get_type_hints

import requests
from openbb_core.app.router import CommandMap


def get_http_method(api_paths: Dict[str, dict], route: str):
    route_info = api_paths.get(route, None)
    if not route_info:
        return route_info
    return list(route_info.keys())[0]


def get_get_flat_params(hints: Dict[str, Type]):
    params = {}

    for k, v in hints.items():
        models = get_args(v)[0]
        params[k] = list(get_type_hints(models).keys())

    flat_params = []
    for _, value in params.items():
        if isinstance(value, list):
            for item in value:
                flat_params.append(item)
        else:
            flat_params.append(value)
    return flat_params


def get_post_flat_params(hints: Dict[str, Type]):
    return list(hints.keys())


def write_init_test_template(path: str):
    template = """
import pytest
import requests
from openbb_provider.utils.helpers import get_querystring


def get_token():
    return requests.post(
        "http://0.0.0.0:8000/api/v1/account/token",
        data={"username": "openbb", "password": "openbb"},
    )


@pytest.fixture(scope="session")
def headers():
    access_token = get_token().json()["access_token"]
    return {"Authorization": f"Bearer {access_token}"}
"""

    with open(path, "w") as f:
        f.write(template)


def write_test_w_template(params: Dict[str, str], route: str, path: str):
    template = f"""
@pytest.mark.parametrize(
    "params",
    [({params})],
)
def test_{route.replace("/", "_")[1:]}(params, headers):
    params = {{p: v for p, v in params.items() if v}}

    query_str = get_querystring(params, [])
    url = f"http://0.0.0.0:8000/api/v1{route}?{{query_str}}"
    result = requests.get(url, headers=headers)
    assert isinstance(result, requests.Response)
    assert result.status_code == 200
"""

    with open(path, "a") as f:
        f.write(template)


def write_integration_tests(
    commandmap_map: Dict[str, Callable], api_paths: Dict[str, dict]
) -> List[str]:
    commands_not_found = []

    http_method_get_params = {"get": get_get_flat_params, "post": get_post_flat_params}

    for route in commandmap_map:
        http_method = get_http_method(api_paths, f"/api/v1{route}")

        menu = route.split("/")[1]
        path = os.path.join(
            "openbb_sdk", "extensions", menu, "integration", f"test_{menu}_api.py"
        )
        if not os.path.exists(path):
            write_init_test_template(path=path)

        if not http_method:
            commands_not_found.append(route)
        else:
            hints = get_type_hints(commandmap_map[route])
            hints.pop("cc", None)
            hints.pop("return", None)

            params = http_method_get_params[http_method](hints)
            params = {k: "" for k in params}

            write_test_w_template(params=params, route=route, path=path)

    return commands_not_found


if __name__ == "__main__":
    r = requests.get("http://0.0.0.0:8000/openapi.json").json()

    if not r:
        raise Exception("Could not get openapi.json")

    command_map = CommandMap()
    commands_not_found_in_openapi = write_integration_tests(
        commandmap_map=command_map.map, api_paths=r["paths"]
    )

    if commands_not_found_in_openapi:
        print(f"Commands not found in openapi.json: {commands_not_found_in_openapi}")
