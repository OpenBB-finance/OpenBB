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
            check=False,
        )
        logger.info(result.stdout)
        building_found = any(
            line.startswith("Building") for line in result.stdout.splitlines()
        )

        if result.returncode != 0:
            logger.error(result.stderr)

            if not result.stderr.endswith(
                "ModuleNotFoundError: No module named 'openbb'\n"
            ):
                sys.exit(1)
            raise subprocess.CalledProcessError(
                returncode=result.returncode,
                cmd=f"{sys.executable} -c import openbb",
                output=result.stdout,
                stderr=result.stderr,
            )

    except (ModuleNotFoundError, subprocess.CalledProcessError) as exc:
        logger.info(
            "The OpenBB build package"
            "may have been uninstalled or corrupted. "
            "Try `pip uninstall openbb` and reinstalling `openbb-core` in the environment.\n"
        )
        raise exc from None

    if not building_found:
        logger.info("Did not build on import, triggering rebuild...\n")
        try:
            import openbb  # noqa

            openbb.build()
        except Exception as e:  # pylint: disable=broad-except
            raise RuntimeError(  # noqa
                "Failed to build the OpenBB platform static assets. \n"
                f"{e} -> {e.__traceback__.tb_frame.f_code.co_filename}:"  # type:ignore  # pylint: disable=E1101
                f"{e.__traceback__.tb_lineno}"  # type:ignore
                if hasattr(e, "__traceback__")
                and hasattr(e.__traceback__, "tb_frame")  # type:ignore
                and hasattr(
                    e.__traceback__.tb_frame,  # type:ignore
                    "f_code",
                )
                and hasattr(
                    e.__traceback__.tb_frame.f_code,  # type:ignore  # pylint: disable=E1101
                    "co_filename",
                )
                and hasattr(
                    e.__traceback__,  # type:ignore
                    "tb_lineno",
                )
                else f"Failed to build the OpenBB platform static assets. \n{e}"
            ) from e
    sys.exit(0)


if __name__ == "__main__":
    main()
