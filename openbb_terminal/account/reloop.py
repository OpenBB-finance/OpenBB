__reloop = False


def get_reloop():
    """Get the reloop flag.

    Returns
    -------
    bool
        The reloop flag.
    """
    return __reloop


def set_reloop(value: bool):
    """Set the reloop flag.

    Parameters
    ----------
    value : bool
        The reloop flag.
    """
    global __reloop  # pylint: disable=global-statement
    __reloop = value
