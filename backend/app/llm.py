from contextlib import AsyncExitStack

from fastapi.concurrency import run_in_threadpool
from openai import OpenAI

from backend.app.mcp_client import call_tools, mcp_session
from shared.config import get

LLM_BASE_URL = get("LLM_BASE_URL", "https://api.deepseek.com")
LLM_API_KEY = get("LLM_API_KEY", "")
LLM_MODEL = get("LLM_MODEL", "deepseek-chat")
MAX_TOOL_STEPS = int(get("MAX_TOOL_STEPS", "3"))

SYSTEM_PROMPT = """
You are a support assistant for a small online store.
Use the available tools to answer questions about products, accounts, and orders.
Never invent product details, prices, stock levels, user data, or order numbers.
If a tool returns an error, tell the customer what went wrong and offer to help with something else.
Before placing an order, list the items, quantities, and shipping address, and ask the customer to confirm.
Only call place_order after the customer confirms.
If an order request is missing items or a shipping address, ask for the missing details.
Keep replies short, specific, and in plain language.
Write replies as plain text without markdown formatting.
Do not use em dashes in replies.
The signed in customer has user_id {user_id}.
""".strip()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Fetch product details by product id or SKU.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "Product id as a number string."},
                    "sku": {"type": "string", "description": "Product SKU."},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_data",
            "description": "Fetch account information and recent orders for a user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User id as a number string."},
                },
                "required": ["user_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "place_order",
            "description": "Place a new order for a user. Call only after the user confirms items and shipping address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "User id as a number string."},
                    "items": {
                        "type": "array",
                        "description": "Order items.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "product_id": {"type": "string", "description": "Product id as a number string."},
                                "quantity": {"type": "integer", "description": "Quantity to order."},
                            },
                            "required": ["product_id", "quantity"],
                        },
                    },
                    "shipping_address": {"type": "string", "description": "Full shipping address."},
                },
                "required": ["user_id", "items", "shipping_address"],
            },
        },
    },
]

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY or "missing", timeout=60.0)
    return _client


def _chat_completion(messages):
    return _get_client().chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=TOOLS,
        temperature=0.2,
    )


def _assistant_dict(message):
    data = {"role": "assistant", "content": message.content or ""}
    if message.tool_calls:
        data["tool_calls"] = [
            {
                "id": call.id,
                "type": "function",
                "function": {
                    "name": call.function.name,
                    "arguments": call.function.arguments,
                },
            }
            for call in message.tool_calls
        ]
    return data


async def build_assistant_reply(history, user_id):
    messages = [{"role": "system", "content": SYSTEM_PROMPT.format(user_id=user_id)}]
    for row in history:
        messages.append({"role": row["role"], "content": row["content"]})
    async with AsyncExitStack() as stack:
        session = None
        for _ in range(MAX_TOOL_STEPS):
            response = await run_in_threadpool(_chat_completion, messages)
            message = response.choices[0].message
            if message.tool_calls:
                if session is None:
                    session = await stack.enter_async_context(mcp_session())
                messages.append(_assistant_dict(message))
                results = await call_tools(session, message.tool_calls)
                for result in results:
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": result["id"],
                            "content": result["content"],
                        }
                    )
                continue
            return message.content or ""
    return "I could not complete that request. Please try again."
