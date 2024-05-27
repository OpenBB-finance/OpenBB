"""Platform V4 Markdown Generator Script."""

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from openbb_core.provider import standard_models
from poetry.core.constraints.version import Version, VersionConstraint, parse_constraint
from poetry.core.pyproject.toml import PyProjectTOML

# Number of spaces to substitute tabs for indentation
TAB_WIDTH = 4

# Maximum number of commands to display on the cards
MAX_COMMANDS = 8

# Input paths
PLATFORM_PATH = Path(__file__).parent.parent / "openbb_platform"
PLATFORM_PYPROJECT_PATH = Path(PLATFORM_PATH / "pyproject.toml")
REFERENCE_FILE_PATH = Path(PLATFORM_PATH / "openbb/assets/reference.json")

# Output paths
WEBSITE_PATH = Path(__file__).parent.absolute()
SEO_METADATA_PATH = Path(WEBSITE_PATH / "metadata/platform_v4_seo_metadata.json")
PLATFORM_CONTENT_PATH = Path(WEBSITE_PATH / "content/platform")
PLATFORM_REFERENCE_PATH = Path(WEBSITE_PATH / "content/platform/reference")
PLATFORM_DATA_MODELS_PATH = Path(WEBSITE_PATH / "content/platform/data_models")

# Markdown imports and elements
PLATFORM_REFERENCE_IMPORT = "import ReferenceCard from '@site/src/components/General/NewReferenceCard';"  # fmt: skip
PLATFORM_REFERENCE_UL_ELEMENT = '<ul className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6">'  # noqa: E501


# pylint: disable=redefined-outer-name


class Console:
    """Console class to log messages to the console."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def log(self, message: str) -> None:
        if self.verbose:
            print(message)


console = Console(verbose=True)


def create_reference_markdown_seo(path: str, description: str) -> str:
    """Create the SEO section for the markdown file.

    Parameters
    ----------
    path: str
        Command path relative to the obb class
    description: str
        Description of the command

    Returns
    -------
    str
        SEO section for the markdown file
    """

    with open(SEO_METADATA_PATH) as f:
        seo_metadata = json.load(f)

    # Formatting path to match the key format in the SEO metadata
    path = path.replace("/", ".")

    if seo_metadata.get(path, None):
        cleaned_title = seo_metadata[path]["title"]
        cleaned_description = (
            seo_metadata[path]["description"]
            .strip()
            .replace("\n", " ")
            .replace("  ", " ")
            .replace('"', "'")
        )
        keywords = "- " + "\n- ".join(seo_metadata[path]["keywords"])
    else:
        # Get the router name as the title
        cleaned_title = path.split(".")[-1]
        # Get the first sentence of the description
        cleaned_description = description.split(".")[0].strip()
        keywords = "- " + "\n- ".join(path.split("."))

    markdown = (
        "---\n"
        f'title: "{cleaned_title}"\n'
        f'description: "{cleaned_description}"\n'
        f"keywords:\n{keywords}\n"
    )

    return markdown


def create_reference_markdown_intro(
    path: str, description: str, deprecated: Dict[str, str]
) -> str:
    """Create the introduction section for the markdown file.

    Parameters
    ----------
    path: str
        Command path relative to the obb class
    description: str
        Description of the command
    deprecated: Dict[str, str]
        Deprecated flag and message

    Returns
    -------
    str
        Introduction section for the markdown file
    """

    deprecation_message = (
        ":::caution Deprecated\n" f"{deprecated['message']}\n" ":::\n\n"
        if deprecated["flag"]
        else ""
    )

    markdown = (
        "---\n\n"
        "import HeadTitle from '@site/src/components/General/HeadTitle.tsx';\n\n"
        f'<HeadTitle title="{path} - Reference | OpenBB Platform Docs" />\n\n'
        f"{deprecation_message}"
        "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
        "import Tabs from '@theme/Tabs';\n"
        "import TabItem from '@theme/TabItem';\n\n"
        f"{description}\n\n"
    )

    return markdown


def create_reference_markdown_tabular_section(
    parameters: Dict[str, List[Dict[str, Optional[str]]]], heading: str
) -> str:
    """Create the tabular section for the markdown file.

    Parameters
    ----------
    parameters: Dict[str, List[Dict[str, str]]]
        Dictionary of providers and their corresponding parameters
    heading: str
        Section heading for the tabular section

    Returns
    -------
    str
        Tabular section for the markdown file
    """

    tables_list = []

    # params_list is a list of dictionaries containing the
    # information for all the parameters of the provider.
    for provider, params_list in parameters.items():

        if provider != "standard":
            result = {v.get("name"): v for v in parameters["standard"]}
            provider_params = {v.get("name"): v for v in params_list}
            result.update(provider_params)
            params = [{**{"name": k}, **v} for k, v in result.items()]
        else:
            params = params_list

        # Exclude default and optional columns in the Data section
        filtered = (
            [
                {k: v for k, v in p.items() if k not in ["default", "optional"]}
                for p in params
            ]
            if heading == "Data"
            else params
        )

        # Parameter information for every provider is extracted from the dictionary
        # and joined to form a row of the table.
        # A `|` is added at the start and end of the row to create the table cell.
        rows = "\n".join([f"| {' | '.join(map(str, p.values()))} |" for p in filtered])

        if heading == "Parameters":
            tables_list.append(
                f"\n<TabItem value='{provider}' label='{provider}'>\n\n"
                "| Name | Type | Description | Default | Optional |\n"
                "| ---- | ---- | ----------- | ------- | -------- |\n"
                f"{rows}\n"
                "</TabItem>\n"
            )
        elif heading == "Data":
            tables_list.append(
                f"\n<TabItem value='{provider}' label='{provider}'>\n\n"
                "| Name | Type | Description |\n"
                "| ---- | ---- | ----------- |\n"
                f"{rows}\n"
                "</TabItem>\n"
            )

    # For easy debugging of the created strings
    tables = "".join(tables_list)
    markdown = f"---\n\n## {heading}\n\n<Tabs>\n{tables}\n</Tabs>\n\n"

    return markdown


def create_reference_markdown_returns_section(returns: List[Dict[str, str]]) -> str:
    """Create the returns section for the markdown file.

    Parameters
    ----------
    returns: List[Dict[str, str]]
        List of dictionaries containing the name, type and description of the returns

    Returns
    -------
    str
        Returns section for the markdown file
    """

    returns_str = ""

    for params in returns:
        returns_str += f"{TAB_WIDTH*' '}{params['name']} : {params['type']}\n"
        returns_str += f"{TAB_WIDTH*' '}{TAB_WIDTH*' '}{params['description']}\n\n"

    # Remove the last two newline characters to render Returns section properly
    returns_str = returns_str.rstrip("\n\n")

    # For easy debugging of the created strings
    markdown = (
        f"---\n\n## Returns\n\n```python wordwrap\nOBBject\n{returns_str}\n```\n\n"
    )

    return markdown


def create_data_model_markdown(title: str, description: str, model: str) -> str:
    """Create the basic markdown file content for the data model.

    Parameters
    ----------
    title: str
        Title of the data model
    description: str
        Description of the data model
    model: str
        Model name

    Returns
    -------
    str
        Basic markdown file content for the data model
    """

    # File name is used in the import statement
    model_import_file = find_data_model_implementation_file(model)

    # Get the first sentence of the description
    cleaned_description = description.split(".")[0].strip()
    # SEO section for the markdown file
    seo_section = (
        "---\n"
        f'title: "{title}"\n'
        f'description: "{cleaned_description}"\n'
        "---\n\n"
    )
    # Introduction section for the markdown file
    intro_section = (
        "<!-- markdownlint-disable MD012 MD031 MD033 -->\n\n"
        "import Tabs from '@theme/Tabs';\n"
        "import TabItem from '@theme/TabItem';\n\n"
        "---\n\n"
        "## Implementation details\n\n"
    )
    # Tabular section for the markdown file
    tables_section = (
        "### Class names\n\n"
        "| Model name | Parameters class | Data class |\n"
        "| ---------- | ---------------- | ---------- |\n"
        f"| `{model}` | `{model}QueryParams` | `{model}Data` |\n"
    )
    # Import statement for the markdown file
    import_section = (
        "\n### Import Statement\n\n"
        "```python\n"
        f"from openbb_core.provider.standard_models.{model_import_file} import (\n"
        f"{model}Data,\n{model}QueryParams,\n"
        ")\n"
        "```\n\n"
    )
    # For easy debugging of the created strings
    markdown = seo_section + intro_section + tables_section + import_section

    return markdown


def find_data_model_implementation_file(data_model: str) -> str:
    """Find the file name containing the data model class.

    Parameters
    ----------
    data_model: str
        Data model name

    Returns
    -------
    str
        File name containing the data model class
    """

    # Function to search for the data model class in the file
    def search_in_file(file_path: Path, search_string: str) -> bool:
        with open(file_path, encoding="utf-8", errors="ignore") as file:
            if search_string in file.read():
                return True
        return False

    # Path is derived using the openbb-core package from the
    # provider/standard_models folder
    standard_models_path = Path(standard_models.__file__).parent
    file_name = ""

    for file in standard_models_path.glob("**/*.py"):
        if search_in_file(file, f"class {data_model}Data"):
            file_name = file.with_suffix("").name

    return file_name


def generate_reference_index_files(reference_content: Dict[str, str]) -> None:
    """Generate index.mdx and _category_.json files for directories and sub-directories
    in the reference directory.

    Parameters
    ----------
    reference_content: Dict[str, str]
        Endpoints and their corresponding descriptions.
    """

    def generate_index_and_category(
        path: Path, parent_label: str = "Reference", position: int = 5
    ):
        # Check for sub-directories and markdown files in the current directory
        sub_dirs = [d for d in path.iterdir() if d.is_dir()]
        markdown_files = [
            f for f in path.iterdir() if f.is_file() and f.suffix == ".md"
        ]

        # Generate _category_.json for the current directory
        category_content = {"label": parent_label, "position": position}
        with open(path / "_category_.json", "w", encoding="utf-8") as f:
            json.dump(category_content, f, indent=2)

        # Initialize index.mdx content with the parent label and import statement
        index_content = f"# {parent_label}\n\n{PLATFORM_REFERENCE_IMPORT}\n\n"

        # Menus section for sub-directories
        if sub_dirs:
            index_content += "### Menus\n"
            index_content += PLATFORM_REFERENCE_UL_ELEMENT + "\n"
            for sub_dir in sub_dirs:
                # Initialize the sub-directory description
                sub_dir_description = ""
                # Capitalize the sub-directory name to use as a title for display
                title = sub_dir.name.capitalize()
                # Get the relative path of the sub-directory from the platform reference path
                # and convert it to POSIX style for consistency across OS
                sub_dir_path = sub_dir.relative_to(PLATFORM_REFERENCE_PATH).as_posix()
                # List all markdown files in the sub-directory, excluding the index.mdx file,
                # to include in the description
                sub_dir_markdown_files = [
                    f.stem for f in sub_dir.glob("*.md") if f.name != "index.mdx"
                ]
                # If there are markdown files found, append their names to the sub-directory
                # description, separated by commas
                if sub_dir_markdown_files:
                    if len(sub_dir_markdown_files) <= MAX_COMMANDS:
                        sub_dir_description += ", ".join(sub_dir_markdown_files)
                    else:
                        sub_dir_description += (
                            f"{', '.join(sub_dir_markdown_files[:MAX_COMMANDS])},..."
                        )

                url = f"/platform/reference/{sub_dir_path}"
                index_content += f'<ReferenceCard title="{title}" description="{sub_dir_description}" url="{url}" />\n'
            index_content += "</ul>\n\n"

        # Commands section for markdown files
        if markdown_files:
            index_content += "### Commands\n"
            index_content += PLATFORM_REFERENCE_UL_ELEMENT + "\n"
            for file in markdown_files:
                # Check if the current file is not the index file to avoid self-referencing
                if file.name != "index.mdx":
                    # Extract the file name without extension to use as a title
                    title = file.stem.replace("_", " ")
                    # Generate a relative file path from the PLATFORM_REFERENCE_PATH,
                    # remove the file extension, and convert it to POSIX path format
                    # for consistency across OS
                    file_path = file.relative_to(PLATFORM_REFERENCE_PATH).with_suffix("").as_posix()  # fmt: skip
                    # Attempt to fetch the file's description from reference_content
                    # using its path,split by the first period to get the first sentence,
                    # and default to an empty string if not found
                    file_description = reference_content.get(f"/{file_path}", "").split(".")[0]  # fmt: skip
                    url = f"/platform/reference/{file_path}"
                    index_content += f'<ReferenceCard title="{title}" description="{file_description}" url="{url}" />\n'
            index_content += "</ul>\n\n"

        # Save the index.mdx file
        with open(path / "index.mdx", "w", encoding="utf-8") as f:
            f.write(index_content)

        # Recursively generate for sub-directories
        for i, sub_dir in enumerate(sub_dirs, start=1):
            generate_index_and_category(sub_dir, sub_dir.name.capitalize(), i)

    # Start the recursive generation from the PLATFORM_REFERENCE_PATH
    generate_index_and_category(PLATFORM_REFERENCE_PATH)


def generate_reference_top_level_index() -> None:
    """Generate the top-level index.mdx file for the reference directory."""

    # Get the sub-directories in the reference directory
    reference_dirs = [d for d in PLATFORM_REFERENCE_PATH.iterdir() if d.is_dir()]
    reference_dirs.sort()
    reference_cards_content = ""

    for dir_path in reference_dirs:
        # Sub-directory name is used as the title for the ReferenceCard component
        title = dir_path.name
        markdown_files = []

        # Recursively find all markdown files in the directory and subdirectories
        for file in dir_path.rglob("*.md"):
            markdown_files.append(file.stem)

        # Format description as a comma-separated string
        if len(markdown_files) <= MAX_COMMANDS:
            description_str = f"{', '.join(markdown_files)}"
        else:
            description_str = f"{', '.join(markdown_files[:MAX_COMMANDS])},..."

        reference_cards_content += (
            f"<ReferenceCard\n"
            f'{TAB_WIDTH*" "}title="{title.capitalize()}"\n'
            f'{TAB_WIDTH*" "}description="{description_str}"\n'
            f'{TAB_WIDTH*" "}url="/platform/reference/{title}"\n'
            "/>\n"
        )

    index_content = (
        "# Reference\n\n"
        f"{PLATFORM_REFERENCE_IMPORT}\n\n"
        "<ul className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6'>\n"
        f"{reference_cards_content}"
        "</ul>\n"
    )

    # Generate the top-level index.mdx file for the reference directory
    with (PLATFORM_REFERENCE_PATH / "index.mdx").open("w", encoding="utf-8") as f:
        f.write(index_content)


def create_data_models_index(title: str, description: str, model: str) -> str:
    """Create the index content for the data models.

    Parameters
    ----------
    title: str
        Title of the data model
    description: str
        Description of the data model
    model: str
        Model name

    Returns
    -------
    str
        Index content for the data models
    """

    # Get the first sentence of the description
    description = description.split(".")[0].strip()

    # For easy debugging of the created strings
    index_content = (
        "<ReferenceCard\n"
        f'{TAB_WIDTH*" "}title="{title}"\n'
        f'{TAB_WIDTH*" "}description="{description}"\n'
        f'{TAB_WIDTH*" "}url="/platform/data_models/{model}"\n'
        "/>\n"
    )

    return index_content


def generate_data_models_index_files(content: str) -> None:
    """Generate index.mdx and _category_.json files for the data_models directory.

    Parameters
    ----------
    content: str
        Content for the data models index file
    """

    index_content = (
        "# Data Models\n\n"
        f"{PLATFORM_REFERENCE_IMPORT}\n\n"
        "<ul className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 -ml-6'>\n"
        f"{content}\n"
        "</ul>\n"
    )

    # Generate the index.mdx file for the data_models directory
    with open(PLATFORM_DATA_MODELS_PATH / "index.mdx", "w", encoding="utf-8") as f:
        f.write(index_content)

    # Generate the _category_.json file for the data_models directory
    category_content = {"label": "Data Models", "position": 6}
    with open(
        PLATFORM_DATA_MODELS_PATH / "_category_.json", "w", encoding="utf-8"
    ) as f:
        json.dump(category_content, f, indent=2)


def generate_markdown_file(path: str, markdown_content: str, directory: str) -> None:
    """Generate markdown file using the content of the specified path and directory.

    Parameters
    ----------
    path: str
        Path to the markdown file
    markdown_content: str
        Content for the markdown file
    directory: str
        Directory to save the markdown file

    Raises
    ------
    ValueError:
        If the content type is invalid
    """

    # For reference, split the path to separate the
    # directory structure from the file name
    if directory == "reference":
        parts = path.strip("/").split("/")
        file_name = f"{parts[-1]}.md"
        directory_path = PLATFORM_REFERENCE_PATH / "/".join(parts[:-1])
    # For data models, the file name is derived from the last
    # part of the path, and there's no additional directory structure
    elif directory == "data_models":
        file_name = f"{path.split('/')[-1]}.md"
        directory_path = PLATFORM_DATA_MODELS_PATH
    else:
        raise ValueError(f"Invalid directory: {directory}")

    # Ensure the directory exists
    directory_path.mkdir(parents=True, exist_ok=True)

    # Generate the markdown file for the specified path and directory
    with open(directory_path / file_name, "w", encoding="utf-8") as md_file:
        md_file.write(markdown_content)


# pylint: disable=redefined-outer-name
def generate_platform_markdown(paths: Dict) -> None:
    """Generate markdown files for OpenBB Docusaurus website."""

    data_models_index_content = []
    reference_index_content_dict = {}

    # Clear the platform/reference folder
    console.log(f"\n[INFO] Clearing the {PLATFORM_REFERENCE_PATH} folder...")
    shutil.rmtree(PLATFORM_REFERENCE_PATH, ignore_errors=True)

    # Clear the platform/data_models folder
    console.log(f"\n[INFO] Clearing the {PLATFORM_DATA_MODELS_PATH} folder...")
    shutil.rmtree(PLATFORM_DATA_MODELS_PATH, ignore_errors=True)

    console.log(
        f"\n[INFO] Generating the markdown files for the {PLATFORM_REFERENCE_PATH} sub-directories..."
    )  # noqa: E501
    console.log(f"\n[INFO] Generating the markdown files for the {PLATFORM_DATA_MODELS_PATH} directory...")  # fmt: skip

    for path, path_data in paths.items():
        reference_markdown_content = ""
        data_markdown_content = ""

        description = path_data["description"]
        path_parameters_fields = path_data["parameters"]
        path_data_fields = path_data["data"]

        reference_index_content_dict[path] = description

        reference_markdown_content = create_reference_markdown_seo(
            path[1:], description
        )
        reference_markdown_content += create_reference_markdown_intro(
            path[1:], description, path_data["deprecated"]
        )
        # reference_markdown_content += create_reference_markdown_examples(path_data["examples"])
        reference_markdown_content += path_data["examples"]

        if path_parameters_fields := path_data["parameters"]:
            reference_markdown_content += create_reference_markdown_tabular_section(
                path_parameters_fields, "Parameters"
            )

        reference_markdown_content += create_reference_markdown_returns_section(
            path_data["returns"]["OBBject"]
        )

        if path_data_fields := path_data["data"]:
            reference_markdown_content += create_reference_markdown_tabular_section(
                path_data_fields, "Data"
            )

        generate_markdown_file(path, reference_markdown_content, "reference")

        if model := path_data["model"]:
            data_markdown_title = re.sub(
                r"([A-Z]{1}[a-z]+)|([A-Z]{3}|[SP500]|[EU])([A-Z]{1}[a-z]+)|([A-Z]{5,})",  # noqa: W605
                lambda m: (
                    f"{m.group(1) or m.group(4)} ".title()
                    if not any([m.group(2), m.group(3)])
                    else f"{m.group(2)} {m.group(3)} "
                ),
                path_data["model"],
            ).strip()
            data_markdown_content = create_data_model_markdown(
                data_markdown_title,
                description,
                model,
            )
            data_markdown_content += create_reference_markdown_tabular_section(
                path_parameters_fields, "Parameters"
            )
            data_markdown_content += create_reference_markdown_tabular_section(
                path_data_fields, "Data"
            )
            data_models_index_content.append(
                create_data_models_index(data_markdown_title, description, model)
            )

            generate_markdown_file(model, data_markdown_content, "data_models")

    # Generate the index.mdx and _category_.json files for the reference directory
    console.log(f"\n[INFO] Generating the index files for the {PLATFORM_REFERENCE_PATH} sub-directories...")  # fmt: skip
    generate_reference_index_files(reference_index_content_dict)
    console.log(
        f"\n[INFO] Generating the index files for the {PLATFORM_REFERENCE_PATH} directory..."
    )
    generate_reference_top_level_index()

    # Sort the data models index content alphabetically to display in the same order
    data_models_index_content.sort()
    data_models_index_content_str = "".join(data_models_index_content)

    # Generate the index.mdx and _category_.json files for the data_models directory
    console.log(f"\n[INFO] Generating the index files for the {PLATFORM_DATA_MODELS_PATH} directory...")  # fmt: skip
    generate_data_models_index_files(data_models_index_content_str)
    console.log("\n[INFO] Markdown files generated successfully!")


def read_reference() -> dict:
    """Read the reference.json file."""
    console.log(f"\n[INFO] Reading the {REFERENCE_FILE_PATH} file...")
    # Load the reference.json file
    try:
        with open(REFERENCE_FILE_PATH) as f:
            reference = json.load(f)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            "File not found! Please ensure the file exists."
        ) from exc

    return reference


def get_openbb_versions() -> Dict[str, VersionConstraint]:
    """Get the openbb package version constraints from pyproject.toml."""
    pyproject = PyProjectTOML(PLATFORM_PYPROJECT_PATH)
    deps = pyproject.data["tool"]["poetry"]["dependencies"]
    dep_spec = {}
    for p, v in deps.items():
        if p.startswith("openbb"):
            if isinstance(v, str):
                dep_spec[p] = parse_constraint(v)
            elif isinstance(v, dict):
                dep_spec[p] = parse_constraint(v["version"])
    return dep_spec


def check_installed(openbb_versions: Dict[str, VersionConstraint]) -> None:
    """Check all the openbb packages are installed and have the correct version."""
    console.log("\n[INFO] Ensuring all packages installed...")
    pip_list_output = subprocess.run(
        "pip list | grep openbb",  # noqa: S607
        shell=True,  # noqa: S602
        capture_output=True,
        text=True,
        check=False,
    )
    result = pip_list_output.stdout.splitlines()
    installed = {
        line.split()[0].lower(): Version.parse(line.split()[1]) for line in result
    }

    failures = set()
    for o, v in openbb_versions.items():
        if o not in installed:
            console.log(f"[INFO] Package '{o}' not installed.")
            failures.add(o)
        elif not v.allows(installed[o]):
            console.log(
                f"[INFO] Version '{installed[o]}' of '{o}' not compatible. Expected '{v}'."
            )
            failures.add(o)

    if failures:
        raise ValueError(f"Failures: {failures}")


def check_built(openbb_versions: Dict[str, VersionConstraint], reference: dict) -> None:
    """Check all the openbb packages installed are in the reference file."""
    console.log("\n[INFO] Ensuring all packages built...")
    core_version = reference.get("info", {}).get("core", "")
    extensions = reference.get("info", {}).get("extensions", {})
    built = {}
    built["openbb-core"] = Version.parse(core_version)
    for value in extensions.values():
        for v in value:
            name, version = v.split("@")
            if name.startswith("openbb_"):
                name = name[7:]
            name = "openbb-" + name.replace("_", "-")
            built[name] = Version.parse(version)

    failures = set()
    for o, v in openbb_versions.items():
        if o not in built:
            console.log(f"[INFO] Package '{o}' not in reference file.")
            failures.add(o)
        elif not v.allows(built[o]):
            console.log(
                f"[INFO] Version '{built[o]}' of '{o}' not compatible. Expected '{v}'."
            )
            failures.add(o)

    if failures:
        raise ValueError(f"Failures: {failures}")


if __name__ == "__main__":

    openbb_versions = get_openbb_versions()
    check_installed(openbb_versions)

    reference = read_reference()
    check_built(openbb_versions, reference)

    generate_platform_markdown(reference.get("paths", {}))
