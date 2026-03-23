from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

from tmf638_backend.models import Service

DB_PATH = os.getenv("DB_PATH", "data/services.db")


def init_db() -> None:
    db_parent = Path(DB_PATH).parent
    db_parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS services (
                id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.commit()


def _serialize_service(service: Service) -> str:
    return json.dumps(service.model_dump(by_alias=True, mode="json"))


def _deserialize_service(payload: str) -> Service:
    return Service.model_validate(json.loads(payload))


def list_services(offset: int = 0, limit: int = 50) -> list[Service]:
    with sqlite3.connect(DB_PATH) as connection:
        rows = connection.execute(
            """
            SELECT payload
            FROM services
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (limit, offset),
        ).fetchall()

    return [_deserialize_service(row[0]) for row in rows]


def get_service(service_id: str) -> Service | None:
    with sqlite3.connect(DB_PATH) as connection:
        row = connection.execute(
            "SELECT payload FROM services WHERE id = ?",
            (service_id,),
        ).fetchone()

    if row is None:
        return None
    return _deserialize_service(row[0])


def create_service(service: Service) -> None:
    payload = _serialize_service(service)
    last_update = service.last_update.isoformat()

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            INSERT INTO services (id, payload, updated_at)
            VALUES (?, ?, ?)
            """,
            (service.id, payload, last_update),
        )
        connection.commit()


def update_service(service: Service) -> None:
    payload = _serialize_service(service)
    last_update = service.last_update.isoformat()

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            """
            UPDATE services
            SET payload = ?, updated_at = ?
            WHERE id = ?
            """,
            (payload, last_update, service.id),
        )
        connection.commit()


def delete_service(service_id: str) -> bool:
    with sqlite3.connect(DB_PATH) as connection:
        cursor = connection.execute(
            "DELETE FROM services WHERE id = ?",
            (service_id,),
        )
        connection.commit()

    return cursor.rowcount > 0
