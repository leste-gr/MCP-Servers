from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Path, Query, Response

from tmf638_backend.models import Service, ServiceCreate, ServicePatch
from tmf638_backend.storage import create_service, delete_service, get_service, init_db, list_services, update_service

BASE_PATH = "/tmf-api/serviceInventory/v5"

app = FastAPI(title="TMF638 Service Inventory API", version="0.1.0")


def _service_href(service_id: str) -> str:
    return f"{BASE_PATH}/service/{service_id}"


def _select_fields(service: Service, fields: str | None) -> dict:
    data = service.model_dump(by_alias=True)
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


@app.get(f"{BASE_PATH}/service")
def list_service(
    fields: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1),
) -> list[dict]:
    services = list_services(offset=offset, limit=limit)
    return [_select_fields(service, fields) for service in services]


@app.post(f"{BASE_PATH}/service", response_model=Service, status_code=201)
def create_service_item(payload: ServiceCreate) -> Service:
    now = datetime.now(UTC)
    service_id = str(uuid4())
    service = Service(
        id=service_id,
        href=_service_href(service_id),
        **{"@type": payload.at_type or "Service"},
        name=payload.name,
        description=payload.description,
        serviceType=payload.service_type,
        state=payload.state,
        operatingStatus=payload.operating_status,
        creationDate=now,
        lastUpdate=now,
    )
    create_service(service)
    return service


@app.get(f"{BASE_PATH}/service/{{service_id}}")
def get_service_item(
    service_id: str = Path(description="Service identifier"),
    fields: str | None = Query(default=None),
) -> dict:
    service = get_service(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return _select_fields(service, fields)


@app.patch(f"{BASE_PATH}/service/{{service_id}}")
def patch_service(
    payload: ServicePatch,
    service_id: str = Path(description="Service identifier"),
    fields: str | None = Query(default=None),
) -> dict:
    service = get_service(service_id)
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")

    service_data = service.model_dump(by_alias=True)
    patch_data = payload.model_dump(exclude_none=True, by_alias=True)
    patch_data["lastUpdate"] = datetime.now(UTC)
    updated = Service(**(service_data | patch_data))
    update_service(updated)
    return _select_fields(updated, fields)


@app.delete(f"{BASE_PATH}/service/{{service_id}}", status_code=204)
def delete_service_item(
    service_id: str = Path(description="Service identifier"),
) -> Response:
    deleted = delete_service(service_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Service not found")
    return Response(status_code=204)
