import threading
import uuid
from datetime import datetime, timezone

import libsql_experimental

from shared.config import get

DATABASE_URL = get("DATABASE_URL", "file:support.db")
DATABASE_AUTH_TOKEN = get("DATABASE_AUTH_TOKEN", "")

_conn = None
_lock = threading.RLock()

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        price_cents INTEGER NOT NULL,
        stock INTEGER NOT NULL,
        category TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        full_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        address TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT NOT NULL UNIQUE,
        user_id INTEGER NOT NULL,
        status TEXT NOT NULL,
        total_cents INTEGER NOT NULL,
        shipping_address TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        unit_price_cents INTEGER NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS conversations (
        id TEXT PRIMARY KEY,
        user_id INTEGER,
        created_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        conversation_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """,
]

SEED_PRODUCTS = [
    (1, "KB-101", "Mechanical Keyboard K10", "Tenkeyless mechanical keyboard with hot swappable switches and a white backlight.", 8900, 24, "Keyboards"),
    (2, "HUB-7", "USB-C Hub 7 in 1", "Seven port USB-C hub with HDMI, card reader, and 100W pass through charging.", 4900, 41, "Accessories"),
    (3, "MON-27Q", "Monitor 27 QHD", "27 inch QHD IPS monitor with a 75 Hz refresh rate and a height adjustable stand.", 21900, 12, "Displays"),
    (4, "MOU-M4", "Wireless Mouse M4", "Compact wireless mouse with silent clicks and a 12 month battery life.", 2900, 60, "Accessories"),
    (5, "LMP-LED", "LED Desk Lamp", "Adjustable LED desk lamp with three color temperatures and a USB charging port.", 3500, 18, "Workspace"),
]

SEED_USERS = [
    (1, "alice@example.com", "Alice Chen", "+1 555 010 0101", "48 Market Street, San Francisco, CA 94103", "2025-11-02T09:00:00+00:00"),
    (2, "bob@example.com", "Bob Patel", "+1 555 010 0102", "900 Lake Drive, Austin, TX 78701", "2026-01-15T09:00:00+00:00"),
]

SEED_ORDERS = [
    (1, "ORD-7F3A9C21", 1, "delivered", 13800, "48 Market Street, San Francisco, CA 94103", "2026-08-28T14:30:00+00:00"),
    (2, "ORD-2B8D4E11", 1, "processing", 2900, "48 Market Street, San Francisco, CA 94103", "2026-09-14T10:15:00+00:00"),
]

SEED_ORDER_ITEMS = [
    (1, 1, 1, 1, 8900),
    (2, 1, 2, 1, 4900),
    (3, 2, 4, 1, 2900),
]


def _now():
    return datetime.now(timezone.utc).isoformat()


def _params(args):
    if args is None:
        return ()
    if isinstance(args, (list, tuple)):
        return tuple(args)
    return args


def _get_conn():
    global _conn
    if _conn is None:
        if DATABASE_URL.startswith("libsql://"):
            _conn = libsql_experimental.connect(
                DATABASE_URL,
                auth_token=DATABASE_AUTH_TOKEN or "",
                check_same_thread=False,
            )
        else:
            _conn = libsql_experimental.connect(DATABASE_URL, check_same_thread=False)
    return _conn


def _rows(cursor):
    rows = cursor.fetchall()
    if not rows:
        return []
    columns = [column[0] for column in (cursor.description or [])]
    return [dict(zip(columns, row)) for row in rows]


def _execute(sql, args=None):
    conn = _get_conn()
    cursor = conn.cursor()
    cursor.execute(sql, _params(args))
    rows = _rows(cursor)
    statement = sql.lstrip()
    if not statement.upper().startswith(("SELECT", "WITH", "PRAGMA", "EXPLAIN")):
        conn.commit()
    return rows


class _Transaction:
    def __init__(self, conn):
        self._conn = conn

    def execute(self, sql, args=None):
        cursor = self._conn.cursor()
        cursor.execute(sql, _params(args))
        return _rows(cursor)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()


def _transaction():
    return _Transaction(_get_conn())


def init_db():
    with _lock:
        for statement in SCHEMA:
            _execute(statement)
        for product in SEED_PRODUCTS:
            _execute(
                "INSERT OR IGNORE INTO products (id, sku, name, description, price_cents, stock, category) VALUES (?, ?, ?, ?, ?, ?, ?)",
                product,
            )
        for user in SEED_USERS:
            _execute(
                "INSERT OR IGNORE INTO users (id, email, full_name, phone, address, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                user,
            )
        for order in SEED_ORDERS:
            _execute(
                "INSERT OR IGNORE INTO orders (id, order_number, user_id, status, total_cents, shipping_address, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                order,
            )
        for item in SEED_ORDER_ITEMS:
            _execute(
                "INSERT OR IGNORE INTO order_items (id, order_id, product_id, quantity, unit_price_cents) VALUES (?, ?, ?, ?, ?)",
                item,
            )


def get_product(product_id=None, sku=None):
    with _lock:
        if sku:
            rows = _execute("SELECT * FROM products WHERE sku = ?", [sku])
        elif product_id is not None:
            rows = _execute("SELECT * FROM products WHERE id = ?", [int(product_id)])
        else:
            rows = []
        return rows[0] if rows else None


def get_user_data(user_id):
    with _lock:
        rows = _execute(
            "SELECT id, email, full_name, phone, address, created_at FROM users WHERE id = ?",
            [int(user_id)],
        )
        if not rows:
            return None
        user = rows[0]
        user["orders"] = _execute(
            "SELECT id, order_number, status, total_cents, shipping_address, created_at FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 10",
            [int(user_id)],
        )
        return user


def place_order(user_id, items, shipping_address):
    with _lock:
        user_rows = _execute("SELECT id FROM users WHERE id = ?", [int(user_id)])
        if not user_rows:
            raise ValueError("user not found")
        prepared = []
        total = 0
        for item in items:
            product_id = int(item.get("product_id"))
            quantity = int(item.get("quantity"))
            if quantity < 1:
                raise ValueError("quantity must be at least 1")
            product_rows = _execute(
                "SELECT id, price_cents, stock FROM products WHERE id = ?",
                [product_id],
            )
            if not product_rows:
                raise ValueError(f"product {product_id} not found")
            product = product_rows[0]
            if product["stock"] < quantity:
                raise ValueError(f"not enough stock for product {product_id}")
            total += product["price_cents"] * quantity
            prepared.append(
                {
                    "product_id": product_id,
                    "quantity": quantity,
                    "unit_price_cents": product["price_cents"],
                }
            )
        order_number = "ORD-" + uuid.uuid4().hex[:8].upper()
        created_at = _now()
        transaction = _transaction()
        try:
            order_rows = transaction.execute(
                "INSERT INTO orders (order_number, user_id, status, total_cents, shipping_address, created_at) VALUES (?, ?, ?, ?, ?, ?) RETURNING id, order_number, user_id, status, total_cents, shipping_address, created_at",
                [order_number, int(user_id), "confirmed", total, shipping_address, created_at],
            )
            order_id = order_rows[0]["id"]
            for item in prepared:
                transaction.execute(
                    "INSERT INTO order_items (order_id, product_id, quantity, unit_price_cents) VALUES (?, ?, ?, ?)",
                    [order_id, item["product_id"], item["quantity"], item["unit_price_cents"]],
                )
                transaction.execute(
                    "UPDATE products SET stock = stock - ? WHERE id = ?",
                    [item["quantity"], item["product_id"]],
                )
            transaction.commit()
        except Exception:
            transaction.rollback()
            raise
        order = order_rows[0]
        order["items"] = prepared
        return order


def create_conversation(user_id):
    with _lock:
        conversation_id = uuid.uuid4().hex
        _execute(
            "INSERT INTO conversations (id, user_id, created_at) VALUES (?, ?, ?)",
            [conversation_id, user_id, _now()],
        )
        return conversation_id


def add_message(conversation_id, role, content):
    with _lock:
        message_id = uuid.uuid4().hex
        _execute(
            "INSERT INTO messages (id, conversation_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
            [message_id, conversation_id, role, content, _now()],
        )
        return message_id


def get_messages(conversation_id, limit=50):
    with _lock:
        return _execute(
            "SELECT role, content FROM messages WHERE conversation_id = ? ORDER BY created_at ASC LIMIT ?",
            [conversation_id, int(limit)],
        )
