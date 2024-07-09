"""Nasdaq Helpers Module."""


def remove_html_tags(text: str):
    """Remove HTML tags from a string."""
    # pylint: disable=import-outside-toplevel
    import re

    clean = re.compile("<.*?>")
    return re.sub(clean, " ", text)


def get_random_agent() -> str:
    """Generate a random user agent for a request."""
    # pylint: disable=import-outside-toplevel
    from random_user_agent.user_agent import UserAgent

    user_agent_rotator = UserAgent(limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent


def get_headers(accept_type: str = "json") -> dict:
    """Get the headers for the request."""
    if accept_type not in ["json", "text"]:
        raise ValueError("Invalid accept_type. Must be either 'json' or 'text'.")

    return (
        {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip",
            "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
            "Host": "api.nasdaq.com",
            "User-Agent": get_random_agent(),
            "Connection": "keep-alive",
        }
        if accept_type == "text"
        else {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip",
            "Accept-Language": "en-CA,en-US;q=0.7,en;q=0.3",
            "Host": "api.nasdaq.com",
            "Origin": "https://www.nasdaq.com",
            "Referer": "https://www.nasdaq.com/",
            "User-Agent": get_random_agent(),
            "Connection": "keep-alive",
        }
    )


def date_range(start_date, end_date):
    """Yield dates between start_date and end_date."""
    # pylint: disable=import-outside-toplevel
    from datetime import timedelta

    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)
