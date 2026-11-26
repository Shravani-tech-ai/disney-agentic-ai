import os
from dotenv import load_dotenv
load_dotenv()
from typing import Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from disney_assistant.agent import root_agent
from disney_assistant.observability import (
    create_trace,
    record_event,
    finish_trace,
    get_trace,
    list_traces,
    get_metrics,
)
import time

APP_NAME = "disney_agentic_ai"
app = FastAPI(title="Disney ADK Bridge", version="1.0.0")
session_service = InMemorySessionService()
runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=session_service)

class ChatConfiguration(BaseModel):
    mock_mode: bool = True
    enabled_agents: list[str] = Field(default_factory=list)

class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=200)
    user_id: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=4000)
    configuration: ChatConfiguration = Field(default_factory=ChatConfiguration)

@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "disney-adk-bridge"}

@app.post("/api/chat")
async def chat(request: ChatRequest) -> dict[str, Any]:

    if not request.configuration.mock_mode:
        raise HTTPException(
            status_code=400,
            detail="Only mock mode is implemented in this demo."
        )

    trace_id = create_trace(
        request.message,
        request.session_id
    )

    start_time = time.perf_counter()

    try:
        existing = await session_service.get_session(
            app_name=APP_NAME,
            user_id=request.user_id,
            session_id=request.session_id
        )

        if existing is None:
            await session_service.create_session(
                app_name=APP_NAME,
                user_id=request.user_id,
                session_id=request.session_id
            )

        enabled = ", ".join(
            request.configuration.enabled_agents
        ) or "none"

        guarded_message = (
            "For this request, the Salesforce administrator has "
            "enabled only these specialist agents: "
            + enabled
            + ". Do not use a specialist that is not in this list. "
            "If the user's request needs a disabled specialist, "
            "explain that this capability is currently disabled.\n\n"
            + request.message
        )

        content = types.Content(
            role="user",
            parts=[types.Part(text=guarded_message)]
        )

        answer_parts: list[str] = []
        observed_agents: list[str] = []

        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=request.session_id,
            new_message=content
        ):

            # Capture actual ADK agent execution.
            author = getattr(event, "author", None)

            if author and author not in (
                "user",
                "system",
                "model"
            ):

                if author not in observed_agents:
                    observed_agents.append(author)

                record_event(
                    "AGENT",
                    author,
                    {"status": "OBSERVED"}
                )

            # Capture final response.
            if (
                event.is_final_response()
                and event.content
                and event.content.parts
            ):
                answer_parts.extend([
                    part.text
                    for part in event.content.parts
                    if getattr(part, "text", None)
                ])

        answer = (
            "\n".join(answer_parts).strip()
            or "I could not generate a response. Please try again."
        )

        latency_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2
        )

        finish_trace("SUCCESS")

        return {
            "session_id": request.session_id,
            "success": True,
            "intent": _intent_hint(request.message),
            "selected_agents": observed_agents,
            "routing_observed": True,
            "answer": answer,
            "data": {},
            "mock": True,
            "trace_id": trace_id,
            "latency_ms": latency_ms
        }

    except HTTPException:
        finish_trace("ERROR", "HTTPException")
        raise

    except Exception as exc:

        finish_trace(
            "ERROR",
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=502,
            detail=(
                f"ADK execution failed: "
                f"{type(exc).__name__}: {exc}"
            )
        ) from exc

def _intent_hint(message: str) -> str:
    m=message.lower()
    if any(x in m for x in ["duplicate", "friends and family", "friends & family"]): return "FRIENDS_FAMILY_DUPLICATE"
    if any(x in m for x in ["claimed", "claim", "linked", "link reservation", "only some"]): return "RESERVATION_PARTIAL_CLAIM"
    if any(x in m for x in ["dining", "restaurant", "table", "meal"]): return "DINING_AVAILABILITY"
    if any(x in m for x in ["lightning lane", "attraction availability", "space mountain"]): return "LIGHTNING_LANE_AVAILABILITY"
    return "PRODUCT_KNOWLEDGE"

def _agent_for(intent: str) -> str:
    return {"PRODUCT_KNOWLEDGE":"ProductKnowledgeAgent", "FRIENDS_FAMILY_DUPLICATE":"FriendsFamilyDuplicateAgent", "RESERVATION_PARTIAL_CLAIM":"ReservationPartialClaimAgent", "DINING_AVAILABILITY":"DiningAvailabilityAgent", "LIGHTNING_LANE_AVAILABILITY":"LightningLaneAvailabilityAgent"}.get(intent, "")

@app.get("/api/observability/traces")
async def observability_traces():
    return {
        "traces": list_traces()
    }


@app.get("/api/observability/traces/{trace_id}")
async def observability_trace(trace_id: str):

    trace = get_trace(trace_id)

    if not trace:
        raise HTTPException(
            status_code=404,
            detail="Trace not found"
        )

    return trace


@app.get("/api/observability/metrics")
async def observability_metrics():
    return get_metrics()