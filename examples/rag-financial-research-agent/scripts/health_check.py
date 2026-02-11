#!/usr/bin/env python3
"""Health check script for the RAG Financial Research Agent."""

import sys

import httpx


def main() -> None:
    """Check if the agent server is running and healthy."""
    base_url = "http://localhost:7777"

    try:
        response = httpx.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200 and response.json().get("status") == "healthy":
            print("Agent is healthy!")

            # Also check stats
            stats_response = httpx.get(f"{base_url}/stats", timeout=5)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f"Collection: {stats['name']}")
                print(f"Document count: {stats['count']}")
        else:
            print(f"Agent returned unexpected response: {response.text}")
            sys.exit(1)
    except httpx.ConnectError:
        print(f"Could not connect to agent at {base_url}")
        sys.exit(1)


if __name__ == "__main__":
    main()
