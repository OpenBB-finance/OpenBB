"""Base output adapter protocol."""

from typing import Any, Protocol


class OutputAdapter(Protocol):
    """Protocol for output adapters."""

    def display(
        self,
        data: Any,
        title: str = "",
        export: bool = False,
        chart: bool = False,
    ) -> None:
        """Display data in the adapter's format.

        Parameters
        ----------
        data : Any
            Data to display - can be OBBject, DataFrame, Series, dict, list, scalar, etc.
        title : str
            Title for the output
        export : bool
            Whether we are exporting (don't display if True)
        chart : bool
            Whether to display as chart if available
        """
