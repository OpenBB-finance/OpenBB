"""Entry point for the OpenBB Updater script."""

# pylint: disable=import-outside-toplevel,unused-import
# flake8: noqa

def main():
    """Update the OpenBB Platform and rebuild the Python interface."""

    import os
    import sys
    import subprocess
    from pathlib import Path

    args = os.sys.argv[1:].copy() if os.sys.argv[1:] else []

    cwd = Path(os.path.dirname(os.path.realpath(__file__))).parent.resolve()

    command = (
        f"{sys.executable} -m pip install -U pip && "
        f"{sys.executable} -m poetry lock && "
        f"{sys.executable} -m poetry install {' '.join(args)} && "
        "openbb-build"
    )

    subprocess.run(command, shell=True, cwd=cwd)

    input("\nUpdate complete. Press Enter to exit...")

if __name__ == "__main__":
    main()
