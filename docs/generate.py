from typing import Callable, Any, Optional, List, Tuple, Dict
from inspect import signature
import importlib
import os
from ruamel.yaml import YAML

from openbb_terminal.sdk import functions

# NOTE: The main.yml and documentation _index.md files are automaticallty overridden
# every time this is ran. Folder level _index.md files are NOT overridden after creation

yaml = YAML()
yaml.indent(mapping=2, sequence=4, offset=2)


def all_functions() -> List[Tuple[str, str, Callable[..., Any]]]:
    """Uses the base SDK functions dictionary to get a list of all functions we have linked
    in our SDK.

    Returns
    ----------
    func_list: List[Tuple[str, str, Callable[..., Any]]]
        A list of functions organized as (path_to_func, view/model, the_function)
    """
    func_list = []
    for key, sub_dict in functions.items():
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
    with open(f"{base}/_index.md", "w") as f:
        if view:
            f.write(
                "To obtain charts, make sure to add `chart=True` as the last parameter\n\n"
            )
        if model:
            f.write(f"## Get underlying data \n### {key}{signature(model[2])}\n\n")
            m_docs = str(model[2].__doc__)[:-5]
            f.write(f"{m_docs}\n")
        if view:
            if model:
                f.write("\n")
            v_docs = str(view[2].__doc__)[:-5]
            temp = str(signature(view[2]))
            # TODO: This breaks if there is a ')' inside the function arguments
            idx = temp.find(")")
            new_signature = temp[:idx] + ", chart=True" + temp[idx:]
            f.write(f"## Getting charts \n### {key}{new_signature}\n\n")
            f.write(f"{v_docs}\n")


def find_line(path: str, to_match: str) -> int:
    """Returns the file line of a string based on given file path"""
    with open(path) as file:
        for i, line in enumerate(file):
            if to_match in line:
                return i
    return -1


def delete_lines(path: str, start: int):
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


def crawl_folders(path: str):
    """Crawls created folders to get a list of what has been created"""
    target = "website/content/"
    results = os.walk(path)
    new_list = []
    for item in list(results):
        if item[1]:
            new_item = list(item[:2])
            loc = item[0]
            new_item[0] = loc[loc.index(target) + len(target) :]
            new_list.append(new_item)
    return new_list


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
        if not final_dict and path == "sdk":
            final_dict = {"name": "sdk", "ref": "/sdk", "sub": []}
            for sub in subs:
                final_dict["sub"].append({"name": sub, "ref": f"/{path}/{sub}"})
            added_paths.append("sdk")
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
    base_folder_path = os.path.realpath("./website/content/sdk")
    target_path = os.path.realpath("./website/data/menu/main.yml")
    main_path = os.path.realpath("./website/content/sdk")
    folder_list = crawl_folders(main_path)
    for folder_path in [x[0] for x in folder_list]:
        folder_documentation(folder_path)
    funcs = all_functions()
    grouped_funcs = groupby(funcs, 0)
    # Create the documentation files
    for k, v in grouped_funcs.items():
        generate_documentation(base_folder_path, k, v)
    # Delete our old entry to main.yaml
    start_line = find_line(target_path, "# CODE BELOW THIS WILL BE DELETED FREQUENTLY")
    delete_lines(target_path, start_line)
    # Add our new entry to main.yaml
    folders_dict = generate_dict(folder_list)
    with open(target_path, "a") as fp:
        yaml.dump({"ignore": [folders_dict]}, fp)
    delete_line(target_path, start_line + 1)
