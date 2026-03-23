from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from tmf621_backend.models import TroubleTicket

DB_PATH = os.getenv("DB_PATH", "data/trouble_tickets.db")


def init_db() -> None:
    db_parent = Path(DB_PATH).parent
    db_parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS trouble_tickets (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def _serialize_ticket(ticket: TroubleTicket) -> str:
    return json.dumps(ticket.model_dump(by_alias=True, mode="json"))


def _deserialize_ticket(payload: str) -> TroubleTicket:
    return TroubleTicket.model_validate(json.loads(payload))


def list_tickets(offset: int = 0, limit: int = 50) -> list[TroubleTicket]:
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            """
            SELECT payload
            FROM trouble_tickets
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

    return [_deserialize_ticket(row[0]) for row in rows]


def get_ticket(ticket_id: str) -> TroubleTicket | None:
    with sqlite3.connect(DB_PATH) as connection:
        row = connection.execute(
            "SELECT payload FROM trouble_tickets WHERE id = ?",
            (ticket_id,),
        ).fetchone()

    if row is None:
        return None
    return _deserialize_ticket(row[0])


def create_ticket(ticket: TroubleTicket) -> None:
    payload = _serialize_ticket(ticket)
    last_update = ticket.last_update.isoformat()

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO trouble_tickets (id, payload, updated_at)
            VALUES (?, ?, ?)
            """,
            (ticket.id, payload, last_update),
        )
        connection.commit()


def update_ticket(ticket: TroubleTicket) -> None:
    payload = _serialize_ticket(ticket)
    last_update = ticket.last_update.isoformat()

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            UPDATE trouble_tickets
            SET payload = ?, updated_at = ?
            WHERE id = ?
            """,
            (payload, last_update, ticket.id),
        )
        connection.commit()


def delete_ticket(ticket_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            "DELETE FROM trouble_tickets WHERE id = ?",
            (ticket_id,),
        )
        connection.commit()

    return cursor.rowcount > 0
