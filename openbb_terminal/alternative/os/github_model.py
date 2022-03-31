"""GitHub Model"""
__docformat__ = "numpy"

import logging
import requests
import math
import pandas as pd
from datetime import datetime 

from openbb_terminal import config_terminal as cfg
from openbb_terminal.decorators import log_start_end
from openbb_terminal.rich_config import console
from openbb_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)

def get_repo_stars(repo, page):
	"""Get repository stargazers

	Parameters
	----------
	repo : str
		Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal
	page : int
		Page number to get stars

	Returns
	-------
	dict with stargazers
	"""
	res = requests.get(f"https://api.github.com/repos/{repo}/stargazers", 
		headers={"Accept": "application/vnd.github.v3.star+json", "Authorization": f"token {cfg.API_GITHUB_KEY}"},
        params={"per_page": 100, "page": page}
	)
	if res.status_code == 200:
		return res.json()
	elif res.status_code == 403:
		console.print("[red]Rate limit reached, please provide a GitHub API key.[/red]")
		return None
	else:
		console.print(f"[red]Error occurred f{res.json()}[/red]")
		return None

def get_repo_stats(repo):
	"""Get repository stats

	Parameters
	----------
	repo : str
		Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

	Returns
	-------
	dict with stats
	"""
	res = requests.get(f"https://api.github.com/repos/{repo}", 
		headers={"Authorization": f"token {cfg.API_GITHUB_KEY}", "User-Agent": get_user_agent()},
	)
	if res.status_code == 200:
		return res.json()
	elif res.status_code == 403:
		console.print("[red]Rate limit reached, please provide a GitHub API key.[/red]")
		return None
	else:
		console.print(f"[red]Error occurred f{res.json()}[/red]")
		return None

def get_repo_releases_stats(repo):
	"""Get repository releases stats

	Parameters
	----------
	repo : str
		Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

	Returns
	-------
	dict with releases stats
	"""
	res = requests.get(f"https://api.github.com/repos/{repo}/releases", 
		headers={"Accept": "application/vnd.github.v3.star+json", "Authorization": f"token {cfg.API_GITHUB_KEY}", "User-Agent": get_user_agent()},
	)
	if res.status_code == 200:
		return res.json()
	elif res.status_code == 403:
		console.print("[red]Rate limit reached, please provide a GitHub API key.[/red]")
		return None
	else:
		console.print(f"[red]Error occurred f{res.json()}[/red]")
		return None


def search_repos(sortby: str = "stars", page: int = 1, categories: str = "") -> pd.DataFrame:
	"""Get repos sorted by stars or forks. Can be filtered by categories

	Parameters
	----------
	sortby : str
		Sort repos by {stars, forks}
	categories : str
		Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
	page : int
		Page number to get repos
	Returns
	-------
	pd.DataFrame with list of repos
	"""
	payload = { "page": page }
	if categories:
		payload["sort"] = sortby
		payload["q"] = categories.replace(",", "+")
	else:
		payload["q"] = f"{sortby}:>1"
	res = requests.get('https://api.github.com/search/repositories', 
	headers={"Accept": "application/vnd.github.v3.star+json", "Authorization": f"token {cfg.API_GITHUB_KEY}", "User-Agent": get_user_agent()}, 
	params=payload)
	if res.status_code == 200:
		data = res.json()
		if "items" in data:
			return pd.DataFrame(data['items'])
	elif res.status_code == 403:
		console.print("[red]Rate limit reached, please provide a GitHub API key.[/red]")
	else:
		console.print(f"[red]Error occurred f{res.json()}[/red]")
	return pd.DataFrame()


@log_start_end(log=logger)
def get_stars_history(repo: str):
	"""Get repository star history

	Parameters
	----------
	repo : str
		Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

	Returns
	-------
	pd.DataFrame - Columns: Date, Stars
	"""
	stars_number = get_repo_stats(repo)["stargazers_count"]
	stars = {}
	pages = math.ceil(stars_number / 100)
	for page in range(0, pages):
		data = get_repo_stars(repo, page)
		for star in data:
			day = star["starred_at"].split("T")[0]
			if day in stars:
				stars[day] += 1
			else:
				stars[day] = 1
	sorted_keys = sorted(stars.keys())
	for i in range(1, len(sorted_keys)):
		stars[sorted_keys[i]] += stars[sorted_keys[i - 1]] 
	df = pd.DataFrame({"Date": [datetime.strptime(date, '%Y-%m-%d').date() for date in stars.keys()], "Stars": stars.values() })
	df.set_index("Date")
	return df


@log_start_end(log=logger)
def get_top_repos(sortby: str, top: int, categories: str) -> pd.DataFrame:
	"""Get repos sorted by stars or forks. Can be filtered by categories

	Parameters
	----------
	sortby : str
		Sort repos by {stars, forks}
	categories : str
		Check for repo categories. If more than one separate with a comma: e.g., finance,investment. Default: None
	top : int
		Number of repos to search for
	Returns
	-------
	pd.DataFrame with list of repos
	"""
	initial_top = top
	df = pd.DataFrame(columns=['full_name','open_issues', 'stargazers_count', 'forks_count', 'language', 'created_at', 'updated_at', 'html_url'])
	if top <= 100:
		df2 = search_repos(sortby=sortby, page=1, categories=categories)
		df = pd.concat([df, df2], ignore_index=True)
	else:
		p = 2
		while top > 0:
			df2 = search_repos(sortby=sortby, page=p, categories=categories)
			df = pd.concat([df, df2], ignore_index=True)
			top -= 100
			p += 1
	df.set_index('full_name')
	return df.head(initial_top)

@log_start_end(log=logger)
def get_repo_summary(repo: str):
	"""Get repository summary

	Parameters
	----------
	repo : str
		Repo to search for Format: org/repo, e.g., openbb-finance/openbbterminal

	Returns
	-------
	pd.DataFrame - Columns: Metric, Value
	"""
	data = get_repo_stats(repo)
	release_data = get_repo_releases_stats(repo)
	total_release_downloads = "N/A"
	if len(release_data) > 0:
		total_release_downloads = 0
		for asset in release_data[0]["assets"]:
			total_release_downloads += asset["download_count"]
	dict = {
		"Metric": ["Name", "Owner", "Creation Date", "Last Update", "Topics", "Stars", "Forks", "Open Issues", "Language", "License", "Releases", "Last Release Downloads"],
		"Value": [data["name"], data["owner"]["login"], data["created_at"].split("T")[0], data["updated_at"].split("T")[0], ", ".join(data["topics"]), data["stargazers_count"], data["forks"], data["open_issues"], data["language"], data["license"]["name"], len(release_data), total_release_downloads]
	}
	return pd.DataFrame(dict)
