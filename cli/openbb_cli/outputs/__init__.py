"""Output adapters for different display modes."""

from openbb_cli.outputs.base import OutputAdapter
from openbb_cli.outputs.html import HtmlOutput
from openbb_cli.outputs.json import JsonOutput
from openbb_cli.outputs.rich import RichTableOutput
from openbb_cli.outputs.tsv import TsvOutput

__all__ = [
    "OutputAdapter",
    "HtmlOutput",
    "JsonOutput",
    "RichTableOutput",
    "TsvOutput",
]
