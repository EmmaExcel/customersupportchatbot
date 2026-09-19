from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from shared import db

DB_FILE = Path("test_support.db")


def setup_module(_module):
    if DB_FILE.exists():
        DB_FILE.unlink()
    db.init_db()


def teardown_module(_module):
    if DB_FILE.exists():
        DB_FILE.unlink()


def test_health():
    from backend.app.main import app

    with TestClient(app) as client:
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


def test_get_product_by_sku():
    product = db.get_product(sku="KB-101")
    assert product["name"] == "Mechanical Keyboard K10"
    assert product["price_cents"] == 8900
    assert product["stock"] == 24


def test_get_product_by_id():
    product = db.get_product(product_id=3)
    assert product["sku"] == "MON-27Q"


def test_get_user_data():
    user = db.get_user_data(1)
    assert user["email"] == "alice@example.com"
    assert len(user["orders"]) == 2
    assert user["orders"][0]["order_number"] == "ORD-2B8D4E11"


def test_place_order():
    before = db.get_product(product_id=4)["stock"]
    order = db.place_order(
        1,
        [{"product_id": 4, "quantity": 2}],
        "48 Market Street, San Francisco, CA 94103",
    )
    assert order["order_number"].startswith("ORD-")
    assert order["status"] == "confirmed"
    assert order["total_cents"] == 5800
    after = db.get_product(product_id=4)["stock"]
    assert after == before - 2


def test_place_order_rejects_missing_product():
    try:
        db.place_order(1, [{"product_id": 999, "quantity": 1}], "48 Market Street")
        raised = False
    except ValueError:
        raised = True
    assert raised


def test_mcp_tool_functions():
    from mcp_server import server

    result = server.get_product_details(sku="KB-101")
    assert result["name"] == "Mechanical Keyboard K10"
    result = server.get_user_data("1")
    assert result["email"] == "alice@example.com"
    result = server.place_order(
        "1",
        [{"product_id": 5, "quantity": 1}],
        "48 Market Street, San Francisco, CA 94103",
    )
    assert result["order_number"].startswith("ORD-")


class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


class FakeToolCall:
    def __init__(self, call_id, name, arguments):
        self.id = call_id
        self.function = FakeFunction(name, arguments)


class FakeMessage:
    def __init__(self, content="", tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls


class FakeChoice:
    def __init__(self, message):
        self.message = message


class FakeResponse:
    def __init__(self, message):
        self.choices = [FakeChoice(message)]


class FakeBlock:
    def __init__(self, text):
        self.text = text


class FakeToolResult:
    def __init__(self, text):
        self.content = [FakeBlock(text)]


class FakeSession:
    async def call_tool(self, name, arguments):
        if name == "get_product_details":
            return FakeToolResult('{"name": "Mechanical Keyboard K10", "price_cents": 8900}')
        if name == "get_user_data":
            return FakeToolResult('{"email": "alice@example.com", "orders": []}')
        if name == "place_order":
            return FakeToolResult('{"order_number": "ORD-TEST0001", "status": "confirmed"}')
        return FakeToolResult("{}")


@pytest.mark.asyncio
async def test_assistant_tool_loop(monkeypatch):
    import backend.app.llm as llm

    calls = []

    def fake_chat(messages):
        calls.append(messages)
        if len(calls) == 1:
            return FakeResponse(
                FakeMessage(
                    tool_calls=[
                        FakeToolCall("call_1", "get_product_details", '{"sku": "KB-101"}')
                    ]
                )
            )
        return FakeResponse(FakeMessage(content="The Mechanical Keyboard K10 costs $89.00."))

    @asynccontextmanager
    async def fake_session():
        yield FakeSession()

    monkeypatch.setattr(llm, "_chat_completion", fake_chat)
    monkeypatch.setattr(llm, "mcp_session", fake_session)

    reply = await llm.build_assistant_reply([{"role": "user", "content": "How much is KB-101?"}], 1)

    assert reply == "The Mechanical Keyboard K10 costs $89.00."
    assert len(calls) == 2
    assert calls[1][-1]["role"] == "tool"
    assert calls[1][-1]["tool_call_id"] == "call_1"
