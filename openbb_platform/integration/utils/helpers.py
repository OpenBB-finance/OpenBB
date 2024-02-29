"""Test helpers."""
import doctest
import glob
import importlib
import logging
import os
from typing import Dict, List

logging.basicConfig(level=logging.INFO)


def get_packages_info() -> Dict[str, str]:
    """Get the paths and names of all the static packages."""
    paths_and_names: Dict[str, str] = {}
    package_paths = glob.glob("openbb_platform/openbb/package/*.py")
    for path in package_paths:
        name = os.path.basename(path).split(".")[0]
        paths_and_names[path] = name

    paths_and_names = {
        path: name for path, name in paths_and_names.items() if not name.startswith("_")
    }
    return paths_and_names


def execute_docstring_examples(
    module_name: str, file_path: str, verbose: bool = False
) -> List[str]:
    """Execute the docstring examples of a module."""
    errors = []
    module_name = f"openbb.package.{module_name}"
    module = importlib.import_module(module_name)
    examples = doctest.DocTestFinder().find(module)

    def execute_script(script, source_info):
        try:
            local_namespace = {}
            exec(  # noqa: S102 pylint: disable=exec-used
                script, local_namespace, local_namespace
            )
            if verbose:
                logging.info("Executed a test from %s", source_info)
        except Exception as e:
            errors.append(
                f"An exception occurred while executing script from {source_info} - {str(e)}"
            )

    for example in examples:
        script_lines = []

        for test in example.examples:
            script_lines.append(test.source)

        script_content = "".join(script_lines)
        execute_script(script_content, file_path)

    return errors


def check_docstring_examples() -> List[str]:
    """Test that the docstring examples execute without errors."""
    errors = []
    paths_and_names = get_packages_info()

    for path, name in paths_and_names.items():
        result = execute_docstring_examples(name, path, verbose=True)
        if result:
            errors.extend(result)

    return errors
