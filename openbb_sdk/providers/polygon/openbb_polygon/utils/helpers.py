# IMPORT THIRD PARTY
from openbb_provider import helpers


def get_data(url: str, **kwargs) -> dict:
    r = helpers.make_request(url, **kwargs)
    if r.status_code != 200:
        data = r.json()
        message = data.get("message")
        error = data.get("error")
        value = message or error
        raise RuntimeError(f"Error in Polygon request -> {value}")

    return r.json()
