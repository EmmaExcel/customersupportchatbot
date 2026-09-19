import json
import sys
from contextlib import asynccontextmanager
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from backend.app.llm import build_assistant_reply
from shared import db
from shared.config import get


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


@asynccontextmanager
async def lifespan(_app):
    db.init_db()
    yield


app = FastAPI(title="Support Chat API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in get("CORS_ORIGINS", "http://localhost:5173").split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _sse(data):
    return f"data: {json.dumps(data)}\n\n"


def _split_text(text, size=100):
    for index in range(0, len(text), size):
        yield text[index:index + size]


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
async def chat(payload: ChatRequest, x_user_id: str | None = Header(default=None)):
    if x_user_id and x_user_id.isdigit():
        user_id = int(x_user_id)
    else:
        user_id = int(get("DEFAULT_USER_ID", "1"))

    conversation_id = payload.conversation_id or db.create_conversation(user_id)
    db.add_message(conversation_id, "user", payload.message)
    history = db.get_messages(conversation_id)

    async def event_stream():
        yield _sse({"type": "status", "state": "thinking"})
        try:
            content = await build_assistant_reply(history, user_id)
        except Exception:
            yield _sse({"type": "error", "text": "I ran into a problem while handling your request. Please try again."})
            return
        yield _sse({"type": "status", "state": "answering"})
        for chunk in _split_text(content):
            yield _sse({"type": "token", "text": chunk})
        db.add_message(conversation_id, "assistant", content)
        yield _sse({"type": "done", "conversation_id": conversation_id})

    return StreamingResponse(event_stream(), media_type="text/event-stream")
