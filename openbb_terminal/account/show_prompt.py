__show_prompt = False


def get_show_prompt():
    """Get the show_prompt flag.

    Returns
    -------
    bool
        The show_prompt flag.
    """
    return __show_prompt


def set_show_prompt(value: bool):
    """Set the show_prompt flag.

    Parameters
    ----------
    value : bool
        The show_prompt flag.
    """
    global __show_prompt  # pylint: disable=global-statement
    __show_prompt = value
