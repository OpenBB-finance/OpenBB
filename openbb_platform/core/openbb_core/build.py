"""Script to build the OpenBB platform static assets."""

# flake8: noqa: S603
# pylint: disable=import-outside-toplevel

import subprocess
import sys


def main():
    """Build the OpenBB platform static assets."""
    try:
        import openbb  # noqa
    except (
        ImportError,
        ModuleNotFoundError,
        AttributeError,
    ):
        print(  # noqa: T201
            "\nOpenBB build script not found, installing from PyPI...\n",
        )
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "openbb", "--no-deps"],
            check=True,
        )

        try:
            subprocess.run(
                [sys.executable, "-c", "import openbb; openbb.build()"],
                check=True,
            )
        except Exception as e:
            raise RuntimeError(
                f"Failed to build the OpenBB platform static assets. \n{e}"
            ) from e


if __name__ == "__main__":
    main()
