import json
import logging
from pathlib import Path
from typing import Dict

from poetry.core.constraints.version import Version, VersionConstraint, parse_constraint
from poetry.core.pyproject.toml import PyProjectTOML

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


def create_ext_map(extensions: dict) -> Dict[str, Version]:
    """Create the extension map from extension."""
    ext_map = {}
    for _, v in extensions.items():
        for value in v:
            name, version = value.split("@")
            ext_map[name] = Version.parse(version)
    return ext_map


def load_req_ext(file: Path) -> Dict[str, VersionConstraint]:
    """Load the required extensions from pyproject.toml."""
    pyproject = PyProjectTOML(file)
    deps = pyproject.data["tool"]["poetry"]["dependencies"]
    req_ext = {}
    for k, v in deps.items():
        if k.startswith("openbb-") and k not in ("openbb-core"):
            name = k[7:].replace("-", "_")
            if isinstance(v, str):
                req_ext[name] = parse_constraint(v)
            elif isinstance(v, dict) and not v.get("optional", False):
                req_ext[name] = parse_constraint(v["version"])
    return req_ext


def test_extension_map():
    """Ensure only required extensions are built and versions respect pyproject.toml."""
    this_dir = Path(__file__).parent
    with open(Path(this_dir, "..", "openbb", "assets", "reference.json")) as f:
        reference = json.load(f)

    ext_map = create_ext_map(reference.get("info", {}).get("extensions", {}))
    req_ext = load_req_ext(Path(this_dir, "..", "pyproject.toml"))

    missing_extensions = []
    incompatible_versions = []
    extra_extensions = []

    # Check if all required extensions are in the extension map
    for ext in req_ext:
        if ext not in ext_map:
            missing_extensions.append(ext)
            logger.error(
                f"Extension '{ext}' is required in pyproject.toml but is not built."
            )

    # Check if extensions in the map match required versions
    for name, version in ext_map.items():
        if name in req_ext:
            if not req_ext[name].allows(version):
                incompatible_versions.append((name, version, req_ext[name]))
                logger.error(
                    f"Version '{version}' of extension '{name}' is not compatible with"
                    f" the version constraint '{req_ext[name]}' in pyproject.toml."
                )
        else:
            extra_extensions.append(name)
            logger.warning(
                f"'{name}' is not a required extension in pyproject.toml. Consider"
                " uninstalling it or updating pyproject.toml."
            )

    # Report summary
    logger.info("\n--- Test Summary ---")
    if missing_extensions:
        logger.info(f"Missing extensions: {', '.join(missing_extensions)}")
    if incompatible_versions:
        for name, version, constraint in incompatible_versions:
            logger.info(
                f"Incompatible version for '{name}': version '{version}' doesn't meet"
                f" the constraint '{constraint}'"
            )
    if extra_extensions:
        logger.info(f"Extra installed extensions: {', '.join(extra_extensions)}")

    if not (missing_extensions or incompatible_versions or extra_extensions):
        logger.info("All extensions passed the test successfully!")


if __name__ == "__main__":
    test_extension_map()
