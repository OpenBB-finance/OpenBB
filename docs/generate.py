import re
import sys
from typing import Callable, Any, Optional, List, Tuple, Dict
from inspect import signature
import importlib
import os
from ruamel.yaml import YAML

from openbb_terminal.sdk import functions, forecast_extras

# NOTE: The main.yml and documentation _index.md files are automaticallty overridden
# every time this is ran. Folder level _index.md files are NOT overridden after creation

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def list_endpoints_info(functions_: dict) -> List[Tuple[str, str, Callable[..., Any]]]:
    """Uses the base SDK functions dictionary to get a list of all functions we have linked
    in our SDK.

    Returns
    ----------
    func_list: List[Tuple[str, str, Callable[..., Any]]]
        A list of functions organized as (path_to_func, view/model, the_function)
    """
    func_list = []
    for key, sub_dict in functions_.items():
        for sub_key, item_path in sub_dict.items():
            full_path = item_path.split(".")
            module_path = ".".join(full_path[:-1])
            module = importlib.import_module(module_path)
            target_function = getattr(module, full_path[-1])
            func_list.append((key, sub_key, target_function))
    return func_list


def groupby(orig_list: List[Any], index: int) -> Dict[Any, Any]:
    """Groups a list of iterable by the index provided

    Parameters
    ----------
    orig_list: List[Any]
        A list of iterables
    index: int
        The index to groupby

    Returns
    ----------
    grouped: dict[Any, Any]
        Group information where keys are the groupby item and values are the iterables
    """
    grouped: Dict[Any, Any] = {}
    for item in orig_list:
        if item[index] in grouped:
            grouped[item[index]].append(item)
        else:
            grouped[item[index]] = [item]
    return grouped


def write_section(
    title: str, start: int, end: int, docstring: str, file, code_snippet: bool = False
):
    """Writes text to documentation files.

    Parameters
    ----------
        title: str
            Section title
        start: int
            Section start
        end: int
            Section end
        docstring: str
            Docstring text
        file:
            File to write documentation
        code_snippet: bool
            Format section content as code snippet
    """

    text = docstring[start:end]

    file.write(f"\n* **{title}**\n\n")

    if code_snippet:
        file.write("    {{< highlight python >}}\n")
        file.write(text)
        file.write("{{< /highlight >}}")
    else:
        file.write(text)


def format_docstring(docstring: str):
    """Format docstring section titles.

    Parameters
    ----------
        docstring: str
            Docstring text
    """

    # Wrap argument types around asterisks to .rst interpret them as italic
    docstring = re.sub(r"(: )([a-zA-Z0-9. _]+)(\n)(\d*)", r": *\2*\n", docstring)

    # Reformat dashes in case there is a size mismatch between title and number of dashes
    docstring = re.sub(r"(Parameters\n)(.*)(\n)(\d*)", r"\1    ----------\n", docstring)
    docstring = re.sub(r"(Returns\n)(.*)(\n)(\d*)", r"\1    -------\n", docstring)
    docstring = re.sub(r"(Examples\n)(.*)(\n)(\d*)", r"\1    --------\n", docstring)

    return docstring


def locate_section(title: str, docstring: str) -> Tuple[int, int]:
    """Locate section titles.

    Parameters
    ----------
        title: str
            Title string
        docstring: str
            Docstring text

    Returns
    -------
        Tuple[int, int]
            Title start and end positions
    """

    title_start = docstring.find(title)
    title_end = title_start + len(title)

    return title_start, title_end


def write_summary(bottom: int, docstring: str, file):
    """Locate section titles.

    Parameters
    ----------
        bottom: int
            Summary string bottom position
        docstring: str
            Docstring text
        file:
            File to write documentation
    """

    file.write(".. raw:: html\n\n")
    file.write("    <h3>\n")
    summary = "    > " + docstring[:bottom].strip() + "\n"
    file.write(summary)
    file.write("    </h3>\n\n")


def insert_chart_arg(has_parameters: bool, sig: str) -> str:
    """Insert chart argument in signature.

    Parameters
    ----------
        has_parameters: bool
            Flags if function already has parameters or not
        sig: str
            Function signature

    Returns
    -------
        str:
            String with chart argument
    """
    # TODO: This breaks if there is a ')' inside the function arguments
    if not has_parameters:
        sig = sig.replace(")", "chart: bool = False)")
    else:
        sig = sig.replace(")", ", chart: bool = False)")

    return sig


def format_signature(sig: str) -> str:
    """Indent and paragraph each signature argument.

    Parameters
    ----------
        sig: str
            Function signature

    Returns
    -------
        str:
            String with formatted signature
    """

    sig = sig.replace("(", "(\n    ")
    # TODO: This requires type int for args, adds new line after each arg
    sig = re.sub(
        r"([a-zA-Z0-9_ ]+)(:)([\[\]a-zA-Z0-9_ (,.='-]*)(,)",
        r"\1\2\3\4\n   ",
        sig,
    )
    sig = sig.replace(")", ",\n)")

    return sig


def generate_documentation(
    base: str, key: str, value: List[Tuple[str, str, Callable[..., Any]]]
):

    models = list(filter(lambda x: x[1] == "model", value))
    views = list(filter(lambda x: x[1] == "view", value))
    model_type = Optional[Tuple[str, str, Callable[..., Any]]]
    model: model_type = models[0] if models else None
    view: model_type = views[0] if views else None
    for end in key.split("."):
        base += f"/{end}"
        if not os.path.isdir(base):
            os.mkdir(base)

    docstring: Optional[str] = model[2].__doc__ if model else None

    if docstring:

        formatted_docstring = format_docstring(docstring=docstring)

        parameters_title_start, parameters_title_end = locate_section(
            title="Parameters\n    ----------\n", docstring=formatted_docstring
        )

        returns_title_start, returns_title_end = locate_section(
            title="Returns\n    -------\n", docstring=formatted_docstring
        )

        examples_title_start, examples_title_end = locate_section(
            title="Examples\n    --------\n", docstring=formatted_docstring
        )

        # Remove .md file if already there
        if os.path.exists(f"{base}/_index.md"):
            os.remove(f"{base}/_index.md")

        with open(f"{base}/_index.rst", "w") as f:
            f.write(
                ".. role:: python(code)\n    :language: python\n    :class: highlight"
            )
            f.write("\n\n|\n\n")

            if model:

                has_parameters = False
                if signature(model[2]).parameters:
                    has_parameters = True

                # Summary
                if has_parameters:
                    write_summary(
                        bottom=parameters_title_start,
                        docstring=formatted_docstring,
                        file=f,
                    )
                else:
                    write_summary(
                        bottom=returns_title_start,
                        docstring=formatted_docstring,
                        file=f,
                    )

                # Signature
                sig = str(signature(model[2]))

                if view:
                    f.write(
                        "To obtain charts, make sure to add :python:`chart = True` as the last parameter\n\n"
                    )
                    sig = insert_chart_arg(has_parameters, sig)
                    sig = format_signature(sig)
                else:
                    if has_parameters:
                        sig = format_signature(sig)

                f.write("{{< highlight python >}}\n")
                f.write(f"{key}{sig}\n")
                f.write("{{< /highlight >}}\n")

                # Parameters
                if parameters_title_start > 0:
                    write_section(
                        title="Parameters",
                        start=parameters_title_end,
                        end=returns_title_start,
                        docstring=formatted_docstring,
                        file=f,
                    )

                # Returns
                if returns_title_start > 0:
                    write_section(
                        title="Returns",
                        start=returns_title_end,
                        end=examples_title_start,
                        docstring=formatted_docstring,
                        file=f,
                    )

                # Examples
                if examples_title_start > 0:
                    write_section(
                        title="Examples",
                        start=examples_title_end,
                        end=len(formatted_docstring),
                        docstring=formatted_docstring,
                        file=f,
                        code_snippet=True,
                    )


def find_line(path: str, to_match: str) -> int:
    """Returns the file line of a string based on given file path"""
    with open(path) as file:
        for i, line in enumerate(file):
            if to_match in line:
                return i
    return -1


def delete_lines_after(path: str, start: int):
    """Deletes all file lines after a given number"""

    with open(path, "r+") as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()

        for i, line in enumerate(lines):
            if i <= start:
                file.write(line)


def delete_line(path: str, to_delete: int):
    """Deletes single file lines after a given number"""

    with open(path, "r+") as file:
        lines = file.readlines()
        file.seek(0)
        file.truncate()

        for i, line in enumerate(lines):
            if i != to_delete:
                file.write(line)


def crawl_folders(root: str) -> list:
    """Crawls created folders to get a list of what has been created"""
    target = "website/content/"
    ignore_length = root.index(target) + len(target)
    return [
        [path[ignore_length:], sorted(dirs)] for path, dirs, _ in os.walk(root) if dirs
    ]


def filter_dict(sub_dict, target: str):
    return sub_dict["name"] == target


def set_items(the_dict, path: str, subs):
    """Sets the sub items inside dictionaries"""
    temp_loc = the_dict["sub"]
    new_path = path[4:]
    for sub_path in new_path.split("/"):
        # pylint: disable=cell-var-from-loop
        if "sub" in temp_loc:
            temp_filter = filter(lambda x: filter_dict(x, sub_path), temp_loc["sub"])
        else:
            temp_filter = filter(lambda x: filter_dict(x, sub_path), temp_loc)
        temp_loc = list(temp_filter)[0]
    temp_loc["sub"] = []
    for sub in subs:
        temp_loc["sub"].append({"name": sub, "ref": f"/{path}/{sub}"})
    return the_dict


def generate_dict(paths: List):
    """Generates the dictionary that will be saved as YAML"""
    final_dict: Dict[str, Any] = {}
    added_paths = []
    for path, subs in paths:
        if not final_dict and path == "SDK":
            final_dict = {"name": "SDK", "ref": "/SDK", "sub": []}
            for sub in subs:
                final_dict["sub"].append({"name": sub, "ref": f"/{path}/{sub}"})
            added_paths.append("SDK")
        if path not in added_paths:
            final_dict = set_items(final_dict, path, subs)
            added_paths.append(path)
    return final_dict


def folder_documentation(path: str):
    name = path.split("/")[-1]
    local_path = os.path.realpath(f"./website/content/{path}")
    full_path = local_path + "/_index.md"
    if not os.path.exists(full_path):
        with open(full_path, "w") as f:
            f.write(f"---\ntitle: {name}\n")
            f.write('keywords: ""\nexcerpt: ""\n')
            f.write("geekdocCollapseSection: true\n")
            f.write("---\n")


if __name__ == "__main__":
    print(
        "Warning: files created in same session are not added to the yaml."
        " To remedy this run this script twice in a row"
    )
    base_folder_path = os.path.realpath("./website/content/SDK")
    if not os.path.exists(base_folder_path):
        os.mkdir(base_folder_path)
    target_path = os.path.realpath("./website/data/menu/main.yml")
    main_path = os.path.realpath("./website/content/SDK")
    folder_list = crawl_folders(main_path)
    for folder_path in [x[0] for x in folder_list]:
        folder_documentation(folder_path)
    funcs = list_endpoints_info(functions)
    grouped_funcs = groupby(funcs, 0)

    # Create the documentation files
    for k, v in grouped_funcs.items():
        generate_documentation(base_folder_path, k, v)

    # Delete our old entry to main.yaml
    start_line = find_line(target_path, "# CODE BELOW THIS WILL BE DELETED FREQUENTLY")
    delete_lines_after(target_path, start_line)

    # Add our new entry to main.yaml
    folders_dict = generate_dict(folder_list)
    with open(target_path, "a") as fp:
        yaml.dump({"ignore": [folders_dict]}, fp)
    delete_line(target_path, start_line + 1)
