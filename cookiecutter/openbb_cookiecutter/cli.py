"""CLI for OpenBB Cookiecutter template."""

# pylint: disable=W0718

import argparse
import sys

from cookiecutter.main import cookiecutter

from . import get_template_path


def main(argv: list | None = None) -> int:
    """Run the OpenBB cookiecutter template.

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="Generate an OpenBB Platform extension from template"
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=".",
        help="Where to output the generated project (default: current directory)",
    )
    parser.add_argument(
        "--no-input",
        action="store_true",
        help="Do not prompt for parameters and use defaults",
    )
    parser.add_argument(
        "-f", "--overwrite-if-exists", action="store_true", help="Overwrite if exists"
    )
    parser.add_argument(
        "--extra-context",
        action="append",
        metavar="KEY=VALUE",
        help="Extra context variables (can be used multiple times)",
    )

    args = parser.parse_args(argv)

    # Build extra context from arguments
    extra_context = {}
    if args.extra_context:
        for item in args.extra_context:
            if "=" not in item:
                print(f"Error: extra-context must be in KEY=VALUE format: {item}")
                return 1
            key, value = item.split("=", 1)
            extra_context[key] = value

    # Get the bundled template path
    template_path = get_template_path()

    try:
        cookiecutter(
            str(template_path),
            output_dir=args.output_dir,
            no_input=args.no_input,
            overwrite_if_exists=args.overwrite_if_exists,
            extra_context=extra_context if extra_context else None,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)  # noqa
        return 1


if __name__ == "__main__":
    sys.exit(main())
