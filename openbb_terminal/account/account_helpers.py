def clean_keys_dict(the_dict: dict) -> dict:
    """Replace None keys with empty strings.

    Parameters
    ----------
    the_dict: dict
        The dictionary to clean

    Returns
    ---------
    dict
        The cleaned dictionary
    """

    for key, value in the_dict.items():
        if value is None:
            the_dict[key] = ""
    return the_dict
