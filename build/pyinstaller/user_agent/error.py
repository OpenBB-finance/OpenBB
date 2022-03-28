__all__ = ('UserAgentError', 'InvalidOption')


class UserAgentError(Exception):
    """
    Base class for all errors
    raising from the user_agent library
    """


class InvalidOption(Exception):
    """
    Raises when user call user_agent library methods
    with incorrect arguments.
    """
