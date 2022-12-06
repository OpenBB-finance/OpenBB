from openbb_terminal.core.exceptions.exceptions import OpenBBUserError


class CurrencyPairNotLoadedError(OpenBBUserError):
    """Raised when currency pair is not loaded"""

    def __init__(self):
        message = "No currency pair data is loaded. Use 'load' to load data."
        super().__init__(message=message)


class InvalidCurrencyPairError(OpenBBUserError):
    """Raised when currency pair is invalid"""

    def __init__(self, pair):
        message = f"{pair} not a valid forex pair."
        super().__init__(message=message)


class DataNotLoadedError(OpenBBUserError):
    def __init__(self, source):
        message = (
            "\n[red]No historical data loaded.\n\n"
            f"Make sure you have appropriate access for the '{source}' data source "
            f"and that '{source}' supports the requested range.[/red]\n"
        )
        super().__init__(message=message)


class InvalidMovingAverageError(OpenBBUserError):
    """Raised when currency pair is invalid"""

    def __init__(self, number):
        message = f"[red]{number} is not a valid moving average, must be an integer greater than 1."
        super().__init__(message=message)
