import ast
import contextlib
from typing import List

from IPython import get_ipython
from IPython.core.magic import register_cell_magic
from IPython.display import display


def has_assign(code: str):
    """Check if code does variable assignment"""
    try:
        parsed_code = ast.parse(code)
        for node in ast.walk(parsed_code):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        return True
    except SyntaxError:
        pass
    return False


def register_todf_magic():
    @register_cell_magic
    def todf(_, cell: List[str]):
        """Apply to_dataframe method to OBBject"""

        namespace = get_ipython().user_ns
        lines = list(filter(None, cell.split("\n")))
        method = ".to_dataframe()"

        for n, nb_line in enumerate(lines):
            line_code = nb_line.strip().replace(" ", "")
            func = eval if not has_assign(nb_line) and n == len(lines) - 1 else exec
            try:
                output = func(line_code + method, namespace)
            except Exception:
                output = func(line_code, namespace)

        # We only display the last line
        if output is not None:
            display(output)


with contextlib.suppress(AttributeError):
    register_todf_magic()
