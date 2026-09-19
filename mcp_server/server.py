import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from mcp.server.fastmcp import FastMCP

from shared import db
from shared.config import get

mcp = FastMCP(
    "support-tools",
    host=get("MCP_HOST", "127.0.0.1"),
    port=int(get("MCP_PORT", "8001")),
)


@mcp.tool(description="Fetch product details by product id or SKU.")
def get_product_details(product_id: str = "", sku: str = "") -> dict:
    try:
        product = db.get_product(product_id=product_id or None, sku=sku or None)
    except ValueError:
        product = None
    if product is None:
        return {"error": "product not found"}
    return product


@mcp.tool(description="Fetch account information and recent orders for a user.")
def get_user_data(user_id: str) -> dict:
    try:
        user = db.get_user_data(int(user_id))
    except ValueError:
        user = None
    if user is None:
        return {"error": "user not found"}
    return user


@mcp.tool(description="Place a new order for a user. Call only after the user confirms items and shipping address.")
def place_order(user_id: str, items: list[dict], shipping_address: str) -> dict:
    try:
        return db.place_order(int(user_id), items, shipping_address)
    except ValueError as exc:
        return {"error": str(exc)}


if __name__ == "__main__":
    db.init_db()
    mcp.run(transport="streamable-http")
