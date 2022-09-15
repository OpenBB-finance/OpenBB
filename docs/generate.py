from typing import Callable, Any, Optional
from inspect import signature
import importlib
import os

# This is temporary, import this from API
functions = {
    "alt.covid.case_slopes": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_case_slopes"
    },
    "alt.covid.global_cases": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_global_cases"
    },
    "alt.covid.global_deaths": {
        "model": "openbb_terminal.alternative.covid.covid_model.get_global_deaths"
    },
    "alt.oss.github_data": {
        "model": "openbb_terminal.alternative.oss.github_model.get_github_data"
    },
    "alt.oss.repo_summary": {
        "model": "openbb_terminal.alternative.oss.github_model.get_repo_summary",
        "view": "openbb_terminal.alternative.oss.github_view.display_repo_summary",
    },
    "alt.oss.stars_history": {
        "model": "openbb_terminal.alternative.oss.github_model.get_stars_history"
    },
    "alt.oss.top_repos": {
        "model": "openbb_terminal.alternative.oss.github_model.get_top_repos",
        "view": "openbb_terminal.alternative.oss.github_view.display_top_repos",
    },
    "alt.oss.search_repos": {
        "model": "openbb_terminal.alternative.oss.github_model.search_repos"
    },
    "alt.oss._make_request": {
        "model": "openbb_terminal.alternative.oss.runa_model._make_request"
    },
    "alt.oss._retry_session": {
        "model": "openbb_terminal.alternative.oss.runa_model._retry_session"
    },
    "common.behavioural_analysis.sentiment": {
        "model": "openbb_terminal.common.behavioural_analysis.reddit_model.get_sentiment",
        "view": "openbb_terminal.common.behavioural_analysis.twitter_view.display_sentiment",
    },
    "common.behavioural_analysis.sentiment_stats": {
        "model": "openbb_terminal.common.behavioural_analysis.finnhub_model.get_sentiment_stats",
        "view": "openbb_terminal.common.behavioural_analysis.finnhub_view.display_sentiment_stats",
    },
}


def all_functions() -> list[tuple[str, str, Callable[..., Any]]]:
    """Uses the base api functions dictionary to get a list of all functions we have linked
    in our API.

    Returns
    ----------
    func_list: list[Tuple[str, str, Callable[..., Any]]]
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


def groupby(orig_list: list[Any], index: int) -> dict[Any, Any]:
    """Groups a list of iterable by the index provided

    Parameters
    ----------
    orig_list: list[Any]
        A list of iterables
    index: int
        The index to groupby

    Returns
    ----------
    grouped: dict[Any, Any]
        Group information where keys are the groupby item and values are the iterables
    """
    grouped: dict[Any, Any] = {}
    for item in orig_list:
        if item[index] in grouped:
            grouped[item[index]].append(item)
        else:
            grouped[item[index]] = [item]
    return grouped


def generate_documentation(
    base: str, key: str, value: list[tuple[str, str, Callable[..., Any]]]
):
    models = list(filter(lambda x: x[1] == "model", value))
    views = list(filter(lambda x: x[1] == "view", value))
    model_type = Optional[tuple[str, str, Callable[..., Any]]]
    model: model_type = models[0] if models else None
    view: model_type = views[0] if views else None
    for end in key.split("."):
        base += f"/{end}"
        if not os.path.isdir(base):
            os.mkdir(base)
    with open(f"{base}/_index.md", "w") as f:
        f.write(f"# {key}\n\n")
        if view:
            f.write(
                "To obtain charts, make sure to add `chart=True` as the last parameter\n\n"
            )
        if model:
            f.write(f"## Get underlying data \n###{key}{signature(model[2])}\n\n")
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
            f.write(f"## Getting charts \n###{key}{new_signature}\n\n")
            f.write(f"{v_docs}\n")


if __name__ == "__main__":
    folder_path = os.path.realpath("./website/content/api")
    funcs = all_functions()
    grouped_funcs = groupby(funcs, 0)
    for k, v in grouped_funcs.items():
        generate_documentation(folder_path, k, v)
