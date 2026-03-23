from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class TroubleTicketStatus(str, Enum):
    acknowledged = "acknowledged"
    in_progress = "inProgress"
    pending = "pending"
    held = "held"
    resolved = "resolved"
    closed = "closed"
    cancelled = "cancelled"


class TmfModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class TroubleTicketCreate(TmfModel):
    at_type: str = Field(default="TroubleTicket", alias="@type")
    external_id: str | None = Field(default=None, alias="externalId")
    name: str
    description: str | None = None
    severity: str | None = None


class TroubleTicketPatch(TmfModel):
    at_type: str | None = Field(default=None, alias="@type")
    name: str | None = None
    description: str | None = None
    severity: str | None = None
    status: TroubleTicketStatus | None = None


class TroubleTicket(TmfModel):
    at_type: str = Field(default="TroubleTicket", alias="@type")
    id: str
    href: str
    external_id: str | None = Field(default=None, alias="externalId")
    name: str
    description: str | None = None
    severity: str | None = None
    status: TroubleTicketStatus = TroubleTicketStatus.acknowledged
    creation_date: datetime = Field(alias="creationDate")
    last_update: datetime = Field(alias="lastUpdate")
    note: list[dict[str, Any]] = Field(default_factory=list)


class ErrorResponse(TmfModel):
    at_type: str = Field(default="Error", alias="@type")
    code: str
    reason: str
    message: str
