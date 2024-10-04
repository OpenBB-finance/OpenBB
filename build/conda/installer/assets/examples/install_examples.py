"""Script to install the example extensions in develop mode to the current Python environment."""


def main():
    """Run the setup script."""
    # pylint: disable=import-outside-toplevel
    import glob
    import os
    import subprocess
    from pathlib import Path

    try:
        import openbb  # noqa: F401  # pylint: disable=unused-import
    except ImportError:
        subprocess.check_call("openbb-build", shell=True)  # noqa: S602, S607

    base_dir = Path(__file__).parent

    directories = [
        os.path.join(base_dir, d)
        for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d))
        and glob.glob(os.path.join(base_dir, d, "*.toml"))
    ]

    for directory in directories:
        subprocess.check_call(
            [  # noqa: S603
                os.sys.executable,
                "-m",
                "poetry",
                "install",
                "-C",
                directory,
                "--only-root",
            ]
        )

    subprocess.check_call("openbb-build", shell=True)  # noqa: S602, S607

    print(  # noqa: T201
        "\nExample extensions have been installed and are ready-to-use."
        "\nTo connect the examples to OpenBB Pro and edit the code live, run: openbb-api --reload\n"
    )


if __name__ == "__main__":
    main()
