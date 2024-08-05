"""Store Utilities."""


def get_random_agent() -> str:
    """Get a random user agent."""
    # pylint: disable=import-outside-toplevel
    from random_user_agent.user_agent import UserAgent

    user_agent_rotator = UserAgent(limit=100)
    user_agent = user_agent_rotator.get_random_user_agent()
    return user_agent
