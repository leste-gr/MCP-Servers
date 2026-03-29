"""TMF637 Product Inventory Management SQLite storage."""
import json
import os
import sqlite3
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Optional

DB_PATH = os.getenv("DB_PATH", "data/products.db")


def _materialize_product(product_id: str, payload: dict) -> dict:
    result = dict(payload)
    result.setdefault("id", product_id)
    result.setdefault("href", f"/tmf-api/productInventory/v5/product/{product_id}")
    return result


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
    payload = _materialize_product(product_id, payload)
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
            "SELECT id, payload FROM products WHERE id = ?", (product_id,)
        ).fetchone()

    if not row:
        return None

    payload = _materialize_product(row[0], json.loads(row[1]))
    if fields:
        payload = {k: v for k, v in payload.items() if k in fields}

    return payload


def _extract_values(obj: Any, path_parts: list[str]) -> list[Any]:
    """Extract all values for a dot-path from nested dict/list payloads."""
    if not path_parts:
        return [obj]

    head, *tail = path_parts
    values: list[Any] = []

    if isinstance(obj, list):
        for item in obj:
            values.extend(_extract_values(item, path_parts))
        return values

    if isinstance(obj, dict) and head in obj:
        return _extract_values(obj[head], tail)

    return values


def _as_text(value: Any) -> str:
    return str(value).strip().lower()


def _match_operator(candidate: Any, operator: str, expected: str) -> bool:
    """Evaluate a candidate value against a filter operator."""
    c_text = _as_text(candidate)
    e_text = expected.strip().lower()

    if operator == "contains":
        return e_text in c_text
    if operator == "startswith":
        return c_text.startswith(e_text)
    if operator == "endswith":
        return c_text.endswith(e_text)
    if operator == "ne":
        return c_text != e_text
    if operator == "in":
        options = {_as_text(v) for v in expected.split(",") if v.strip()}
        return c_text in options
    return c_text == e_text


def _matches_filters(product: dict[str, Any], filters: dict[str, str]) -> bool:
    """Return True when product matches all provided filter expressions.

    Supported filter key format:
    - `<path>` (default equals)
    - `<path>__contains`
    - `<path>__startswith`
    - `<path>__endswith`
    - `<path>__ne`
    - `<path>__in` (comma-separated values)

    `path` supports nested fields with dot notation, e.g.
    `relatedParty.partyOrPartyRole.name`.
    """
    for raw_key, raw_value in filters.items():
        if raw_value is None:
            continue

        key = raw_key.strip()
        if not key:
            continue

        if "__" in key:
            path, operator = key.rsplit("__", 1)
        else:
            path, operator = key, "eq"

        values = _extract_values(product, [p for p in path.split(".") if p])
        if not values:
            return False

        if not any(_match_operator(v, operator, str(raw_value)) for v in values):
            return False

    return True


def list_products(
    offset: int = 0,
    limit: int = 100,
    fields: Optional[list[str]] = None,
    filters: Optional[dict[str, str]] = None,
) -> tuple[list[dict], int]:
    """List products with optional filtering, pagination and field projection."""
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute("SELECT id, payload FROM products ORDER BY id").fetchall()

    all_products = []
    for row in rows:
        payload = _materialize_product(row[0], json.loads(row[1]))
        all_products.append(payload)

    if filters:
        all_products = [p for p in all_products if _matches_filters(p, filters)]

    total_count = len(all_products)
    products = all_products[offset: offset + limit]

    if fields:
        products = [{k: v for k, v in p.items() if k in fields} for p in products]

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
