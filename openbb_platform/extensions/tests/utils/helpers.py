import base64

from openbb_core.env import Env


def get_auth() -> str:
    """Returns the basic auth header."""

    userpass = f"{Env().API_USERNAME}:{Env().API_PASSWORD}"
    userpass_bytes = userpass.encode("ascii")
    base64_bytes = base64.b64encode(userpass_bytes)

    return f"Basic {base64_bytes.decode('ascii')}"
