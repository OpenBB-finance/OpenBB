"""Tests for main API endpoints."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient
from openbb_ai.testing import CopilotResponse

from rag_financial_research_agent.main import app

test_client = TestClient(app)


def test_health_check() -> None:
    """Test health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_agents_json() -> None:
    """Test agents.json descriptor endpoint."""
    response = test_client.get("/agents.json")
    assert response.status_code == 200

    data = response.json()
    assert "rag_financial_research" in data

    agent = data["rag_financial_research"]
    assert agent["name"] == "RAG Financial Research"
    assert agent["features"]["streaming"] is True
    assert agent["features"]["widget-dashboard-select"] is True
    assert agent["features"]["widget-dashboard-search"] is True
    assert agent["endpoints"]["query"] == "/v1/query"


def _mock_openai_stream():
    """Create a mock OpenAI streaming response."""

    async def _stream():
        mock_event = MagicMock()
        mock_event.choices = [MagicMock()]
        mock_event.choices[0].delta.content = "Test response"
        yield mock_event

        mock_event2 = MagicMock()
        mock_event2.choices = [MagicMock()]
        mock_event2.choices[0].delta.content = None
        yield mock_event2

    return _stream()


def test_query_single_message() -> None:
    """Test querying with a single message."""
    test_payload_path = (
        Path(__file__).parent.parent
        / "testing"
        / "test_payloads"
        / "single_message.json"
    )
    test_payload = json.loads(test_payload_path.read_text())

    with (
        patch(
            "rag_financial_research_agent.main.retriever"
        ) as mock_retriever,
        patch(
            "rag_financial_research_agent.main.openai.AsyncOpenAI"
        ) as mock_openai_cls,
    ):
        mock_retriever.retrieve.return_value = []
        mock_retriever.format_context.return_value = ""

        mock_client = AsyncMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=_mock_openai_stream()
        )

        response = test_client.post("/v1/query", json=test_payload)
        assert response.status_code == 200

        copilot_response = CopilotResponse(response.text)
        copilot_response.starts("copilotStatusUpdate")


def test_query_multiple_messages() -> None:
    """Test querying with conversation history."""
    test_payload_path = (
        Path(__file__).parent.parent
        / "testing"
        / "test_payloads"
        / "multiple_messages.json"
    )
    test_payload = json.loads(test_payload_path.read_text())

    with (
        patch(
            "rag_financial_research_agent.main.retriever"
        ) as mock_retriever,
        patch(
            "rag_financial_research_agent.main.openai.AsyncOpenAI"
        ) as mock_openai_cls,
    ):
        mock_retriever.retrieve.return_value = []
        mock_retriever.format_context.return_value = ""

        mock_client = AsyncMock()
        mock_openai_cls.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            return_value=_mock_openai_stream()
        )

        response = test_client.post("/v1/query", json=test_payload)
        assert response.status_code == 200

        copilot_response = CopilotResponse(response.text)
        copilot_response.starts("copilotStatusUpdate")


def test_query_returns_remote_function_call() -> None:
    """Test that widget data requests trigger a remote function call."""
    test_payload_path = (
        Path(__file__).parent.parent
        / "testing"
        / "test_payloads"
        / "message_with_primary_widget.json"
    )
    test_payload = json.loads(test_payload_path.read_text())

    response = test_client.post("/v1/query", json=test_payload)
    assert response.status_code == 200

    (
        CopilotResponse(response.text)
        .starts("copilotFunctionCall")
        .with_({"function": "get_widget_data"})
        .with_(
            {
                "input_arguments": {
                    "data_sources": [
                        {
                            "widget_uuid": "123e4567-e89b-12d3-a456-426614174000",
                            "origin": "openbb",
                            "id": "company_news",
                            "input_args": {"ticker": "AAPL"},
                        }
                    ]
                }
            }
        )
    )


def test_query_no_messages() -> None:
    """Test that empty messages list is handled."""
    test_payload = {"messages": []}
    response = test_client.post("/v1/query", json=test_payload)
    assert "messages" in response.text.lower() or response.status_code >= 400


def test_stats_endpoint() -> None:
    """Test stats endpoint returns collection info."""
    response = test_client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "count" in data
