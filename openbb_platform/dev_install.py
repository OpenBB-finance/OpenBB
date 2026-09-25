"""Install the tracked, published OpenBB packages in editable mode."""

# flake8: noqa: S603, S607

import argparse
import os
import shutil
import subprocess
import sys
import time
from importlib.util import find_spec
from pathlib import Path

PLATFORM_PATH = Path(__file__).parent.resolve()
REPO_PATH = PLATFORM_PATH.parent
PACKAGE_GLOBS = (
    "openbb_platform/core/pyproject.toml",
    "openbb_platform/extensions/*/pyproject.toml",
    "openbb_platform/obbject_extensions/*/pyproject.toml",
    "openbb_platform/providers/*/pyproject.toml",
    "cli/pyproject.toml",
)
ROUTERS_PATH = Path("openbb_platform/extensions")
ALWAYS_INSTALLED_ROUTERS = frozenset({"openbb-news"})
UV_BUILD_LOG = "uv_build_frontend=debug"


def log(message: str) -> None:
    """Write a progress line to stdout immediately.

    Parameters
    ----------
    message : str
        The line to write.
    """
    sys.stdout.write(f"[dev_install] {message}\n")
    sys.stdout.flush()


def run_step(title: str, command: list[str], env: dict[str, str]) -> None:
    """Run one install step, streaming its output and reporting its duration.

    Parameters
    ----------
    title : str
        The step name shown in the progress lines.
    command : list[str]
        The command to run from the repository root.
    env : dict[str, str]
        The environment for the command.
    """
    log(f"{title}...")
    start = time.monotonic()
    subprocess.run(command, cwd=REPO_PATH, env=env, check=True)
    log(f"{title} finished in {time.monotonic() - start:.1f}s")


def get_uv() -> list[str]:
    """Return the command that invokes uv.

    Returns
    -------
    list[str]
        The uv module of the running interpreter, else the uv executable on PATH.

    Raises
    ------
    SystemExit
        If uv is not installed.
    """
    if find_spec("uv"):
        return [sys.executable, "-m", "uv"]
    uv = shutil.which("uv")
    if uv:
        return [uv]
    sys.exit(
        "dev_install.py requires uv: "
        "https://docs.astral.sh/uv/getting-started/installation/"
    )


def load_toml(path: Path) -> dict:
    """Parse a TOML file.

    Parameters
    ----------
    path : Path
        The TOML file to read.

    Returns
    -------
    dict
        The parsed document.
    """
    if sys.version_info >= (3, 11):
        import tomllib
    else:
        if find_spec("tomli") is None:
            subprocess.run(
                [*get_uv(), "pip", "install", "--python", sys.executable, "tomli>=2"],
                check=True,
            )
        import tomli as tomllib
    return tomllib.loads(path.read_text(encoding="utf-8"))


def get_tracked_packages() -> list[Path]:
    """Return the repository-relative directory of every tracked, published package.

    Returns
    -------
    list[Path]
        Package directories, sorted.
    """
    result = subprocess.run(
        ["git", "ls-files", "-z", "--", *(f":(glob){g}" for g in PACKAGE_GLOBS)],
        cwd=REPO_PATH,
        capture_output=True,
        text=True,
        check=True,
    )
    return sorted(Path(f).parent for f in result.stdout.split("\0") if f)


def is_optional_router(package: Path, pyproject: dict) -> bool:
    """Return whether a package is a router extension installed only with --routers.

    Parameters
    ----------
    package : Path
        The repository-relative package directory.
    pyproject : dict
        The package's parsed pyproject.toml.

    Returns
    -------
    bool
        True for an extension that registers an `openbb_core_extension` router,
        other than those in ALWAYS_INSTALLED_ROUTERS.
    """
    project = pyproject.get("project", {})
    return (
        package.parent == ROUTERS_PATH
        and "openbb_core_extension" in project.get("entry-points", {})
        and project.get("name") not in ALWAYS_INSTALLED_ROUTERS
    )


def get_install_args(package: Path, pyproject: dict) -> list[str]:
    """Return the uv arguments that install a package with its extras and dev group.

    Parameters
    ----------
    package : Path
        The repository-relative package directory.
    pyproject : dict
        The package's parsed pyproject.toml.

    Returns
    -------
    list[str]
        The editable requirement, followed by the dev group when the package has one.
    """
    extras = sorted(pyproject.get("project", {}).get("optional-dependencies", {}))
    target = package.as_posix() + (f"[{','.join(extras)}]" if extras else "")
    args = ["--editable", target]
    if "dev" in pyproject.get("dependency-groups", {}):
        args += ["--group", f"{package.as_posix()}/pyproject.toml:dev"]
    return args


def main(argv: list[str] | None = None) -> None:
    """Install the packages into the running interpreter and build the static assets.

    Parameters
    ----------
    argv : list[str] | None
        Command-line arguments, defaulting to sys.argv.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--routers",
        action="store_true",
        help="Also install the router extensions (equity, economy, fixedincome, ...).",
    )
    args = parser.parse_args(argv)
    log(f"Installing into {sys.executable}")
    install_args: list[str] = []
    skipped: list[str] = []
    for package in get_tracked_packages():
        pyproject = load_toml(REPO_PATH / package / "pyproject.toml")
        if args.routers or not is_optional_router(package, pyproject):
            install_args += get_install_args(package, pyproject)
            log(f"  + {package.as_posix()}")
        else:
            skipped.append(package.name)
    if skipped:
        log(f"Skipping routers (pass --routers to include): {', '.join(skipped)}")
    run_step(
        "Resolving, building, and installing with uv "
        "(package builds and their hook output stream below)",
        [*get_uv(), "pip", "install", "--python", sys.executable, *install_args],
        {**os.environ, "RUST_LOG": os.environ.get("RUST_LOG", UV_BUILD_LOG)},
    )
    run_step(
        "Building the openbb package",
        [sys.executable, "-c", "import openbb; openbb.build(verbose=True)"],
        {**os.environ, "OPENBB_AUTO_BUILD": "false"},
    )
    log("Done")


if __name__ == "__main__":
    main()
