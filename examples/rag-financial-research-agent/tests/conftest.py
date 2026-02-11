"""Pytest configuration and fixtures."""

import os

import pytest

# Set test environment variables before importing app
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["CHROMA_PERSIST_DIRECTORY"] = "./test_chroma_db"
os.environ["CHROMA_COLLECTION_NAME"] = "test_collection"


@pytest.fixture(autouse=True)
def reset_sse_starlette_appstatus_event():
    """Reset the appstatus event in sse_starlette.

    See https://github.com/sysid/sse-starlette/issues/59
    """
    from sse_starlette.sse import AppStatus

    AppStatus.should_exit_event = None
