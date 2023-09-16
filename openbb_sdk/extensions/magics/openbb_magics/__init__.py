import ast
import contextlib
from typing import List

from IPython import get_ipython
from IPython.core.magic import register_cell_magic
from IPython.display import display


def has_assign(code: str) -> bool:
    """Check if code does variable or attribute assignment"""
    return any(isinstance(node, ast.Assign) for node in ast.walk(ast.parse(code)))


def register_magics():
    """Register magic methods"""

    @register_cell_magic
    def todf(_, cell: List[str]):
        """Apply to_dataframe method to OBBject"""

        namespace = get_ipython().user_ns
        lines = list(filter(None, cell.split("\n")))

        for n, nb_line in enumerate(lines):
            line_code = nb_line.strip().replace(" ", "")
            if line_code.startswith("#"):
                output = None
                continue
            func = eval if not has_assign(nb_line) and n == len(lines) - 1 else exec
            try:
                output = func(line_code + ".to_dataframe()", namespace)
            except (SyntaxError, AttributeError):
                output = func(line_code, namespace)

        # We only display the last line
        if output is not None:
            display(output)

    # Other magics...


with contextlib.suppress(AttributeError):
    register_magics()
