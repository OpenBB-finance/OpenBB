from typing import List, Callable, Any, Tuple
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


def all_functions() -> List[Tuple[str, str, Callable[..., Any]]]:
    """Uses the base api functions dictionary to get a list of all functions we have linked
    in our API.

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
            function = getattr(module, full_path[-1])
            func_list.append((key, sub_key, function))
    return func_list


if __name__ == "__main__":
    folder_path = os.path.realpath("./website/content/api")
    print(folder_path)
    funcs = all_functions()
    func = funcs[0]
