"""Script to build the OpenBB platform static assets."""

# flake8: noqa: S603
# pylint: disable=import-outside-toplevel

import subprocess
import sys


def main():
    """Build the OpenBB platform static assets."""
    try:
        from openbb import build

        build()
    except (
        ImportError,
        ModuleNotFoundError,
        AttributeError,
    ) as e:
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
        except (subprocess.CalledProcessError, AttributeError):
            raise RuntimeError(
                "Failed to find the OpenBB build script. Install with `pip install openbb --no-deps`"
            ) from e


if __name__ == "__main__":
    main()
