"""Changelog v2 summary generator."""

import logging
import re
import sys

import requests


def fetch_pr_details(owner: str, repo: str, pr_number: str, github_token: str) -> dict:
    """Fetch details of a specific PR from GitHub."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
    headers = {"Authorization": f"token {github_token}"}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return response.json()

    logging.error(
        "Failed to fetch PR details for PR #%s. Status code: %s",
        pr_number,
        response.status_code,
    )
    return {}


def parse_and_fetch_pr_details(markdown_text: str, owner: str, repo: str, github_token: str) -> dict[str, str]:
    """Parse the markdown text and fetch details of PRs mentioned in the text."""
    sections = re.split(r"\n## ", markdown_text)
    categories: dict[str, str] = {}

    for section in sections:
        split_section = section.split("\n", 1)
        if len(split_section) < 2:
            continue

        category_name = split_section[0].strip()
        items_text = split_section[1].strip()
        items = re.findall(r"- (?:\[.*?\] - )?(.*?) @.*? \(#(\d+)\)", items_text)

        for _, pr_number in items:
            pr_details = fetch_pr_details(owner, repo, pr_number, github_token)
            if pr_details:
                try:
                    pr_info = {
                        "title": pr_details["title"],
                        "body": re.sub(r"\s+", " ", pr_details["body"].strip()).strip(),
                    }
                except Exception as e:
                    logging.error("Failed to fetch PR details for PR #%s: %s", pr_number, e)
                if category_name in categories:
                    categories[category_name].append(pr_info)  # type: ignore
                else:
                    categories[category_name] = [pr_info]  # type: ignore

    return categories


def insert_summary_into_markdown(markdown_text: str, category_name: str, summary: str) -> str:
    """Insert a summary into the markdown text directly under the specified category name."""
    marker = f"## {category_name}"
    if marker in markdown_text:
        # Find the position right after the category name
        start_pos = markdown_text.find(marker) + len(marker)
        # Find the position of the first newline after the category name to ensure we insert before any content
        newline_pos = markdown_text.find("\n", start_pos)
        if newline_pos != -1:
            # Insert the summary right after the newline that follows the category name
            # Ensuring it's on a new line and followed by two newlines before any subsequent content
            updated_markdown = markdown_text[: newline_pos + 1] + "\n" + summary + markdown_text[newline_pos + 1 :]
        else:
            # If there's no newline (e.g., end of file), just append the summary
            updated_markdown = markdown_text + "\n\n" + summary + "\n"
        return updated_markdown

    logging.error("Category '%s' not found in markdown.", category_name)
    return markdown_text


def summarize_text_with_openai(text: str, openai_api_key: str) -> str:
    """Summarize text using OpenAI's GPT model."""
    from openai import OpenAI  # pylint: disable=C0415

    openai = OpenAI(api_key=openai_api_key)
    response = openai.chat.completions.create(
        model="gpt-4",  # noqa: E501
        messages=[
            {
                "role": "system",
                "content": "Summarize the following text in a concise way to describe what happened in the new release. This will be used on top of the changelog to provide a high-level overview of the changes. Make sure it is well-written, concise, structured and that it captures the essence of the text. It should read like a concise story.",  # noqa: E501 # pylint: disable=C0301
            },
            {"role": "user", "content": text},
        ],
    )
    return response.choices[0].message.content  # type: ignore


def summarize_changelog_v2(
    github_token: str,
    openai_api_key: str,
    owner: str = "OpenBB-finance",
    repo: str = "OpenBBTerminal",
    changelog_v2: str = "CHANGELOG.md",
) -> None:
    """Summarize the Changelog v2 markdown text with PR details."""
    try:
        with open(changelog_v2) as file:
            logging.info("Reading file: %s", changelog_v2)
            data = file.read()
    except OSError as e:
        logging.error("Failed to open or read file: %s", e)
        return

    logging.info("Parsing and fetching PR details...")
    categories = parse_and_fetch_pr_details(data, owner, repo, github_token)

    categories_of_interest = [
        "🚨 OpenBB Platform Breaking Changes",
        "🦋 OpenBB Platform Enhancements",
        "🐛 OpenBB Platform Bug Fixes",
        "📚 OpenBB Documentation Changes",
    ]
    updated_markdown = data

    logging.info("Summarizing text with OpenAI...")
    for category_of_interest in categories_of_interest:
        if category_of_interest in categories:
            pattern = r"\[.*?\]\(.*?\)|[*_`]"
            aggregated_text = "\n".join(
                [
                    f"- {pr['title']}: {re.sub(pattern, '', pr['body'])}"  # type: ignore
                    for pr in categories[category_of_interest]  # type: ignore
                ]
            )
            summary = summarize_text_with_openai(aggregated_text, openai_api_key)
            updated_markdown = insert_summary_into_markdown(updated_markdown, category_of_interest, summary)

    with open(changelog_v2, "w") as file:
        logging.info("Writing updated file: %s", changelog_v2)
        file.write(updated_markdown)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        logging.error("Usage: python summarize_changelog.py <github_token> <openai_api_key>")
        sys.exit(1)

    token = sys.argv[1]
    openai_key = sys.argv[2]

    summarize_changelog_v2(github_token=token, openai_api_key=openai_key)
