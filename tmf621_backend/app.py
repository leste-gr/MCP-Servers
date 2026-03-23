from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Path, Query, Response

from tmf621_backend.models import TroubleTicket, TroubleTicketCreate, TroubleTicketPatch
from tmf621_backend.storage import create_ticket, delete_ticket, get_ticket, init_db, list_tickets, update_ticket

BASE_PATH = "/tmf-api/troubleTicket/v5"

app = FastAPI(title="TMF621 Trouble Ticket API", version="0.1.0")


def _ticket_href(ticket_id: str) -> str:
    return f"{BASE_PATH}/troubleTicket/{ticket_id}"


def _select_fields(ticket: TroubleTicket, fields: str | None) -> dict:
    data = ticket.model_dump(by_alias=True)
    if not fields:
        return data
    requested = {name.strip() for name in fields.split(",") if name.strip()}
    return {key: value for key, value in data.items() if key in requested}


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get(f"{BASE_PATH}/troubleTicket")
def list_trouble_tickets(
    fields: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1),
) -> list[dict]:
    tickets = list_tickets(offset=offset, limit=limit)
    return [_select_fields(ticket, fields) for ticket in tickets]


@app.post(f"{BASE_PATH}/troubleTicket", response_model=TroubleTicket, status_code=201)
def create_trouble_ticket(payload: TroubleTicketCreate) -> TroubleTicket:
    now = datetime.now(UTC)
    ticket_id = str(uuid4())
    ticket = TroubleTicket(
        id=ticket_id,
        href=_ticket_href(ticket_id),
        **{"@type": payload.at_type or "TroubleTicket"},
        externalId=payload.external_id,
        name=payload.name,
        description=payload.description,
        severity=payload.severity,
        creationDate=now,
        lastUpdate=now,
    )
    create_ticket(ticket)
    return ticket


@app.get(
    f"{BASE_PATH}/troubleTicket/{{ticket_id}}",
)
def get_trouble_ticket(
    ticket_id: str = Path(description="Trouble ticket identifier"),
    fields: str | None = Query(default=None),
) -> dict:
    ticket = get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="TroubleTicket not found")
    return _select_fields(ticket, fields)


@app.patch(
    f"{BASE_PATH}/troubleTicket/{{ticket_id}}",
)
def patch_trouble_ticket(
    payload: TroubleTicketPatch,
    ticket_id: str = Path(description="Trouble ticket identifier"),
    fields: str | None = Query(default=None),
) -> dict:
    ticket = get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="TroubleTicket not found")

    ticket_data = ticket.model_dump(by_alias=True)
    patch_data = payload.model_dump(exclude_none=True, by_alias=True)
    patch_data["lastUpdate"] = datetime.now(UTC)
    updated = TroubleTicket(**(ticket_data | patch_data))
    update_ticket(updated)
    return _select_fields(updated, fields)


@app.delete(
    f"{BASE_PATH}/troubleTicket/{{ticket_id}}",
    status_code=204,
)
def delete_trouble_ticket(
    ticket_id: str = Path(description="Trouble ticket identifier"),
) -> Response:
    deleted = delete_ticket(ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="TroubleTicket not found")
    return Response(status_code=204)
