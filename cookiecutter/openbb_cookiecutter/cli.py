"""CLI for OpenBB Cookiecutter template."""

# pylint: disable=W0718

import argparse
import sys

from cookiecutter.main import cookiecutter
from rich.prompt import Prompt

from . import get_template_path

VALID_EXTENSION_TYPES = [
    "router",
    "provider",
    "obbject",
    "on_command_output",
    "charting",
    "all",
]


def _parse_extension_types(value: str) -> list[str]:
    types = [t.strip() for t in value.split(",") if t.strip()]
    invalid = [t for t in types if t not in VALID_EXTENSION_TYPES]
    if invalid:
        raise ValueError(
            f"Invalid extension type(s): {', '.join(invalid)}. "
            f"Valid choices: {', '.join(VALID_EXTENSION_TYPES)}"
        )
    if not types:
        raise ValueError("At least one extension type must be selected.")
    return types


def _prompt_context(preset_extension_types: list[str] | None = None) -> dict:
    context = {}

    context["full_name"] = Prompt.ask("  full_name", default="Hello World")
    context["email"] = Prompt.ask("  email", default="hello@world.com")
    context["project_name"] = Prompt.ask(
        "  project_name", default="OpenBB Python Extension Template"
    )
    default_tag = context["project_name"].lower().replace(" ", "-").replace("_", "-")
    context["project_tag"] = Prompt.ask("  project_tag", default=default_tag)
    default_pkg = context["project_name"].lower().replace(" ", "_").replace("-", "_")
    context["package_name"] = Prompt.ask("  package_name", default=default_pkg)

    if preset_extension_types:
        types = preset_extension_types
    else:
        while True:
            raw = Prompt.ask(
                "  extension_types"
                " - router | provider | obbject | on_command_output | charting | all",
                default="router",
            )
            try:
                types = _parse_extension_types(raw)
                break
            except ValueError as e:
                print(f"  Error: {e}")

    context["extension_types"] = ",".join(types)
    is_all = "all" in types

    if is_all or "provider" in types:
        context["provider_name"] = Prompt.ask("  provider_name", default="template")
    else:
        context["provider_name"] = "template"

    if is_all or "router" in types or "charting" in types:
        context["router_name"] = Prompt.ask("  router_name", default="template")
    else:
        context["router_name"] = "template"

    if is_all or "obbject" in types or "on_command_output" in types:
        context["obbject_name"] = Prompt.ask("  obbject_name", default="template")
    else:
        context["obbject_name"] = "template"

    return context


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
    parser.add_argument(
        "-e",
        "--extension-types",
        nargs="+",
        choices=VALID_EXTENSION_TYPES,
        default=None,
        help="Extension types to include (default: all). "
        "Choices: router, provider, obbject, on_command_output, charting, all",
    )

    args = parser.parse_args(argv)

    extra_context = {}
    if args.extra_context:
        for item in args.extra_context:
            if "=" not in item:
                print(f"Error: extra-context must be in KEY=VALUE format: {item}")
                return 1
            key, value = item.split("=", 1)
            extra_context[key] = value

    if args.no_input:
        if args.extension_types:
            extra_context["extension_types"] = ",".join(args.extension_types)
    else:
        preset_types = args.extension_types if args.extension_types else None
        context = _prompt_context(preset_extension_types=preset_types)
        extra_context.update(context)

    template_path = get_template_path()

    try:
        cookiecutter(
            str(template_path),
            output_dir=args.output_dir,
            no_input=True,
            overwrite_if_exists=args.overwrite_if_exists,
            extra_context=extra_context if extra_context else None,
        )
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)  # noqa
        return 1


if __name__ == "__main__":
    sys.exit(main())
