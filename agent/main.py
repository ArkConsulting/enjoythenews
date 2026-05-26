"""Agent loop — model-agnostic chat service.

Run:  uvicorn agent.main:app --port 8766
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import agent.claude as claude

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8765"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)


class ChatRequest(BaseModel):
    messages: list[dict]
    system: str


@app.post("/chat")
def chat(body: ChatRequest):
    return StreamingResponse(
        claude.stream(body.messages, body.system),
        media_type="text/event-stream",
    )
