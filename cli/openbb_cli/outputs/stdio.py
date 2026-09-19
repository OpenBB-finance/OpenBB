"""STDIO output adapter — alias for TsvOutput, kept for legacy callers."""

from openbb_cli.outputs.tsv import TsvOutput


class StdioOutput(TsvOutput):
    """STDIO output adapter — line-oriented TSV to stdout."""
