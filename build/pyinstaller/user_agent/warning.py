import warnings


class UserAgentDeprecationWarning(UserWarning):
    """
    Warning category used to generate warning message
    about deprecated feature of user_agent library.
    """


def warn(msg, stacklevel=2):
    warnings.warn(msg, category=UserAgentDeprecationWarning,
                  stacklevel=stacklevel)
