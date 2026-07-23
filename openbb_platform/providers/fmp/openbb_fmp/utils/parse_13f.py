"""Utility functions for parsing FMP Form 13F-HR."""


def date_to_quarter_end(date: str) -> str:
    """Convert a date to the end of the calendar quarter."""
    # pylint: disable=import-outside-toplevel
    from pandas import to_datetime
    from pandas.tseries.offsets import QuarterEnd

    return (
        (to_datetime(date).to_period("Q").to_timestamp("D") + QuarterEnd())
        .date()
        .strftime("%Y-%m-%d")
    )
