"""QVERISAI helper functions."""

from typing import Any


def get_api_key_from_credentials(credentials: dict[str, str] | None) -> str | None:
    """Extract QVERISAI API key from credentials dictionary.

    Parameters
    ----------
    credentials : dict[str, str] | None
        Credentials dictionary.

    Returns
    -------
    str | None
        API key if found, None otherwise.
    """
    if not credentials:
        return None

    # Try different possible key names
    possible_keys = [
        "qveris_api_key",
        "QVERIS_API_KEY",
        "qverisai_api_key",
        "QVERISAI_API_KEY",
    ]

    for key in possible_keys:
        if key in credentials:
            return credentials[key]

    return None


