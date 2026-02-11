"""FastAPI application for the RAG Financial Research Agent."""

import logging
import re
from typing import Any, AsyncGenerator

import openai
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai.types.chat import (
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from openbb_ai import (
    WidgetRequest,
    citations,
    cite,
    get_widget_data,
    message_chunk,
    reasoning_step,
)
from openbb_ai.models import (
    Citation,
    QueryRequest,
    SourceInfo,
)
from sse_starlette.sse import EventSourceResponse

from .config import settings
from .retriever import FinancialRetriever, RetrievedDocument
from .utils.prompts import SYSTEM_PROMPT
from .vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RAG Financial Research Agent",
    description="A RAG-powered financial research agent for OpenBB Workspace",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://pro.openbb.co"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = VectorStore()
retriever = FinancialRetriever(vector_store)


@app.get("/agents.json")
def get_agent_descriptor() -> JSONResponse:
    """Agent descriptor for OpenBB Workspace."""
    return JSONResponse(
        content={
            "rag_financial_research": {
                "name": "RAG Financial Research",
                "description": (
                    "AI-powered financial research assistant with access to "
                    "indexed SEC filings, earnings transcripts, and research "
                    "reports. Combines document retrieval with live market data."
                ),
                "image": "https://github.com/OpenBB-finance/copilot-for-terminal-pro/assets/14093308/7da2a512-93b9-478d-90bc-b8c3dd0cabcf",
                "endpoints": {"query": "/v1/query"},
                "features": {
                    "streaming": True,
                    "widget-dashboard-select": True,
                    "widget-dashboard-search": True,
                },
            }
        }
    )


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/stats")
def get_stats() -> dict[str, Any]:
    """Get vector store statistics."""
    return vector_store.get_collection_stats()


def extract_ticker_from_query(query: str) -> str | None:
    """Extract a likely ticker symbol from the query."""
    match = re.search(r"\b([A-Z]{1,5})\b", query)
    return match.group(1) if match else None


def create_document_citation(doc: RetrievedDocument) -> Citation:
    """Create a citation for a retrieved document."""
    return Citation(
        source_info=SourceInfo(
            type="direct retrieval",
            name=doc.source,
            description=f"Retrieved from {doc.document_type}",
            metadata={
                "ticker": doc.ticker or "",
                "document_type": doc.document_type,
                "relevance_score": str(doc.score),
            },
        ),
        details=[
            {
                "Source": doc.source,
                "Type": doc.document_type,
                "Ticker": doc.ticker or "N/A",
                "Relevance": f"{doc.score:.2%}",
            }
        ],
    )


@app.post("/v1/query")
async def query(request: QueryRequest) -> EventSourceResponse:
    """Query the RAG Financial Research Agent.

    Flow:
    1. Check if widget data should be fetched
    2. Retrieve relevant documents from vector store
    3. Combine with widget data (if any)
    4. Generate response using LLM
    5. Return with proper citations
    """
    last_message = request.messages[-1]

    # Phase 1: Fetch widget data if needed
    orchestration_requested = (
        last_message.role == "ai"
        and getattr(last_message, "agent_id", None) == "openbb-copilot"
    )

    if (
        (last_message.role == "human" or orchestration_requested)
        and request.widgets
        and request.widgets.primary
    ):
        widget_requests: list[WidgetRequest] = []
        for widget in request.widgets.primary:
            widget_requests.append(
                WidgetRequest(
                    widget=widget,
                    input_arguments={
                        param.name: param.current_value
                        for param in widget.params
                    },
                )
            )

        async def retrieve_widget_data() -> AsyncGenerator[dict[str, Any], None]:
            yield get_widget_data(widget_requests).model_dump()

        return EventSourceResponse(
            content=retrieve_widget_data(),
            media_type="text/event-stream",
        )

    # Phase 2: Build context and generate response
    async def execution_loop() -> AsyncGenerator[dict[str, Any], None]:
        citations_list: list[Citation] = []

        # Find the user's query
        user_query = ""
        for msg in reversed(request.messages):
            if msg.role == "human":
                user_query = str(getattr(msg, "content", ""))
                break

        # Step 1: Retrieve relevant documents
        yield reasoning_step(
            message="Searching financial documents...",
            event_type="INFO",
        ).model_dump()

        ticker = extract_ticker_from_query(user_query)
        retrieved_docs = retriever.retrieve(
            query=user_query,
            ticker=ticker,
            top_k=settings.rag_top_k,
        )

        if retrieved_docs:
            yield reasoning_step(
                message=f"Found {len(retrieved_docs)} relevant documents",
                event_type="INFO",
                details={"documents": [d.source for d in retrieved_docs]},
            ).model_dump()

            for doc in retrieved_docs:
                citations_list.append(create_document_citation(doc))
        else:
            yield reasoning_step(
                message="No matching documents found in knowledge base",
                event_type="WARNING",
            ).model_dump()

        # Step 2: Process widget data if present
        widget_context = ""
        for index, message in enumerate(request.messages):
            if message.role == "tool" and index == len(request.messages) - 1:
                widget_context += "--- Live Market Data ---\n"
                for data in message.data:  # type: ignore[union-attr]
                    for item in data.items:  # type: ignore[union-attr]
                        widget_context += f"{item.content}\n"  # type: ignore[union-attr]
                widget_context += "---\n"

                # Create widget citations
                if request.widgets and request.widgets.primary:
                    input_args = message.input_arguments  # type: ignore[union-attr]
                    for widget_data_req in input_args.get(
                        "data_sources", []
                    ):
                        filtered_widgets = list(
                            filter(
                                lambda w: str(w.uuid)
                                == widget_data_req["widget_uuid"],
                                request.widgets.primary,
                            )
                        )
                        if filtered_widgets:
                            citations_list.append(
                                cite(
                                    widget=filtered_widgets[0],
                                    input_arguments=widget_data_req.get(
                                        "input_args", {}
                                    ),
                                    extra_details={
                                        **widget_data_req.get(
                                            "input_args", {}
                                        ),
                                    },
                                )
                            )

        # Step 3: Build messages for LLM
        yield reasoning_step(
            message="Generating response...",
            event_type="INFO",
        ).model_dump()

        rag_context = retriever.format_context(retrieved_docs)

        openai_messages: list[ChatCompletionMessageParam] = [
            ChatCompletionSystemMessageParam(
                role="system",
                content=SYSTEM_PROMPT,
            )
        ]

        for message in request.messages:
            if message.role == "human":
                content = str(getattr(message, "content", ""))
                if content == user_query:
                    context_parts = []
                    if rag_context:
                        context_parts.append(rag_context)
                    if widget_context:
                        context_parts.append(widget_context)
                    if context_parts:
                        content = (
                            "\n\n".join(context_parts)
                            + f"\n\nQuestion: {content}"
                        )

                openai_messages.append(
                    ChatCompletionUserMessageParam(
                        role="user", content=content
                    )
                )
            elif message.role == "ai":
                msg_content = getattr(message, "content", None)
                if isinstance(msg_content, str):
                    openai_messages.append(
                        ChatCompletionAssistantMessageParam(
                            role="assistant",
                            content=msg_content,
                        )
                    )

        # Step 4: Stream LLM response (supports Ollama/local LLMs via base_url)
        client_kwargs: dict = {"api_key": settings.openai_api_key or "ollama"}
        if settings.openai_base_url:
            client_kwargs["base_url"] = settings.openai_base_url
        client = openai.AsyncOpenAI(**client_kwargs)

        async for event in await client.chat.completions.create(
            model=settings.llm_model,
            messages=openai_messages,
            stream=True,
            temperature=0.7,
        ):
            if chunk := event.choices[0].delta.content:
                yield message_chunk(chunk).model_dump()

        # Step 5: Return citations
        if citations_list:
            yield citations(citations_list).model_dump()

    return EventSourceResponse(
        content=execution_loop(),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "rag_financial_research_agent.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )
