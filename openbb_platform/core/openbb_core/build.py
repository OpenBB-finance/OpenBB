"""Script to build the OpenBB platform static assets."""

# flake8: noqa: S603
# pylint: disable=import-outside-toplevel,unused-import
import logging
import subprocess
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def main():
    """Build the OpenBB platform static assets."""
    try:
        logger.info("Attempting to import the OpenBB package...\n")
        # Try importing openbb in a subprocess and capture output
        result = subprocess.run(
            [sys.executable, "-c", "import openbb"],
            capture_output=True,
            text=True,
            check=True,
        )
        logger.info(result.stdout)
        building_found = any(
            line.startswith("Building") for line in result.stdout.splitlines()
        )

        if result.returncode != 0:
            raise ModuleNotFoundError(result.stderr)

    except ModuleNotFoundError:
        logger.info(
            "\nOpenBB build script not found, installing from PyPI...\n",
        )
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "openbb", "--no-deps"],
            check=True,
        )
        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "import openbb",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            logger.info(result.stdout)
            building_found = any(
                line.startswith("Building") for line in result.stdout.splitlines()
            )
        except Exception as e:
            raise RuntimeError(f"Failed to import the OpenBB package. \n{e}") from e

    if not building_found:
        logger.info("Did not build on import, triggering rebuild...\n")
        try:
            import openbb  # noqa

            openbb.build()

        except Exception as e:
            raise RuntimeError(
                "Failed to build the OpenBB platform static assets. \n"
                f"{e} -> {e.__traceback__.tb_frame.f_code.co_filename}:"
                f"{e.__traceback__.tb_lineno}"
            ) from e
    sys.exit(0)


if __name__ == "__main__":
    main()
