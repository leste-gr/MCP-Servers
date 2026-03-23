"""TMF637 Product Inventory Management SQLite storage."""
import json
import os
import sqlite3
from datetime import datetime, UTC
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "data/products.db")


def init_db():
    """Initialize the database with the products table."""
    db_parent = Path(DB_PATH).parent
    db_parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def create_product(product_id: str, payload: dict) -> dict:
    """Create a new product in the database."""
    now = datetime.now(UTC).isoformat()
    payload["creationDate"] = now
    payload["lastUpdate"] = now

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "INSERT INTO products (id, payload, updated_at) VALUES (?, ?, ?)",
            (product_id, json.dumps(payload), now),
        )
        connection.commit()

    return payload


def get_product(product_id: str, fields: Optional[list[str]] = None) -> dict | None:
    """Retrieve a product by ID, optionally filtering fields."""
    with sqlite3.connect(DB_PATH) as connection:
        row = connection.execute(
            "SELECT payload FROM products WHERE id = ?", (product_id,)
        ).fetchone()

    if not row:
        return None

    payload = json.loads(row[0])
    if fields:
        payload = {k: v for k, v in payload.items() if k in fields}

    return payload


def list_products(offset: int = 0, limit: int = 100, fields: Optional[list[str]] = None) -> tuple[list[dict], int]:
    """List all products with pagination and optional field filtering."""
    with sqlite3.connect(DB_PATH) as connection:
        # Get total count
        total_count = connection.execute("SELECT COUNT(*) FROM products").fetchone()[0]

        # Get paginated results
        rows = connection.execute(
            "SELECT payload FROM products ORDER BY id LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()

    products = []
    for row in rows:
        payload = json.loads(row[0])
        if fields:
            payload = {k: v for k, v in payload.items() if k in fields}
        products.append(payload)

    return products, total_count


def patch_product(product_id: str, updates: dict) -> dict | None:
    """Update a product with partial changes."""
    existing = get_product(product_id)
    if not existing:
        return None

    now = datetime.now(UTC).isoformat()
    existing.update(updates)
    existing["lastUpdate"] = now

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "UPDATE products SET payload = ?, updated_at = ? WHERE id = ?",
            (json.dumps(existing), now, product_id),
        )
        connection.commit()

    return existing


def delete_product(product_id: str) -> bool:
    """Delete a product from the database."""
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            "DELETE FROM products WHERE id = ?", (product_id,)
        )
        connection.commit()
        return cursor.rowcount > 0


from typing import Optional
