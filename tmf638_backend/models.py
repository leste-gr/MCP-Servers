from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ServiceStateType(str, Enum):
    feasibility_checked = "feasibilityChecked"
    designed = "designed"
    reserved = "reserved"
    inactive = "inactive"
    active = "active"
    terminated = "terminated"
    suspended = "suspended"


class ServiceOperatingStatusType(str, Enum):
    pending = "pending"
    configured = "configured"
    starting = "starting"
    running = "running"
    degraded = "degraded"
    failed = "failed"
    limited = "limited"
    stopping = "stopping"
    stopped = "stopped"
    unknown = "unknown"


class TmfModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="allow")


class ServiceCreate(TmfModel):
    at_type: str = Field(default="Service", alias="@type")
    name: str | None = None
    description: str | None = None
    service_type: str | None = Field(default=None, alias="serviceType")
    state: ServiceStateType | None = None
    operating_status: ServiceOperatingStatusType | None = Field(default=None, alias="operatingStatus")


class ServicePatch(TmfModel):
    at_type: str | None = Field(default=None, alias="@type")
    name: str | None = None
    description: str | None = None
    service_type: str | None = Field(default=None, alias="serviceType")
    state: ServiceStateType | None = None
    operating_status: ServiceOperatingStatusType | None = Field(default=None, alias="operatingStatus")


class Service(TmfModel):
    at_type: str = Field(default="Service", alias="@type")
    id: str
    href: str
    name: str | None = None
    description: str | None = None
    service_type: str | None = Field(default=None, alias="serviceType")
    state: ServiceStateType | None = None
    operating_status: ServiceOperatingStatusType | None = Field(default=None, alias="operatingStatus")
    creation_date: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="creationDate")
    last_update: datetime = Field(default_factory=lambda: datetime.now(UTC), alias="lastUpdate")
    note: list[dict[str, Any]] = Field(default_factory=list)
