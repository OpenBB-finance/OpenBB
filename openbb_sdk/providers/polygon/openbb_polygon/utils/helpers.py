# IMPORT THIRD PARTY
import requests

# IMPORT INTERNAL


def get_data(url: str) -> dict:
    r = requests.get(url, timeout=10)
    if r.status_code != 200:
        data = r.json()
        message = data.get("message")
        error = data.get("error")
        value = message or error
        raise RuntimeError(f"Error in Polygon request -> {value}")

    return r.json()
