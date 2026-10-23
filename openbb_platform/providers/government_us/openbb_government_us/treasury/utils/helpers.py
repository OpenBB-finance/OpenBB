"""Government US Helpers."""

from random_user_agent.user_agent import UserAgent


def get_random_agent() -> str:
    """Generate a random user agent for a request."""
    user_agent_rotator = UserAgent(limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent
