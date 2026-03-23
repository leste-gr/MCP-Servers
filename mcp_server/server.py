from __future__ import annotations

import os
from typing import Any, Literal

import httpx
from mcp.server.fastmcp import FastMCP

MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))
MCP_PATH = os.getenv("MCP_PATH", "/mcp")

TMF621_BASE_URL = os.getenv(
    "TMF621_BASE_URL",
    "http://tmf621-backend:8080/tmf-api/troubleTicket/v5",
).rstrip("/")

mcp = FastMCP(
    "tmf621-mcp-server",
    host=MCP_HOST,
    port=MCP_PORT,
    streamable_http_path=MCP_PATH,
)


def _endpoint(path: str) -> str:
    return f"{TMF621_BASE_URL}{path}"


def _fields_str(fields: list[str] | str | None) -> str | None:
    if fields is None:
        return None
    if isinstance(fields, list):
        return ",".join(fields)
    return fields


def _to_int(v: Any) -> int | None:
    if v is None or isinstance(v, dict):
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


@mcp.tool()
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "server": "tmf621-mcp-server",
        "tmf621BaseUrl": TMF621_BASE_URL,
    }


@mcp.tool()
def list_trouble_tickets(
    fields: list[str] | str | None = None,
    offset: Any = None,
    limit: Any = None,
) -> list[dict[str, Any]]:
    params = {"fields": _fields_str(fields), "offset": _to_int(offset), "limit": _to_int(limit)}
    params = {k: v for k, v in params.items() if v is not None}
    with httpx.Client(timeout=30.0) as client:
        response = client.get(_endpoint("/troubleTicket"), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def get_trouble_ticket(ticket_id: str, fields: list[str] | str | None = None) -> dict[str, Any]:
    f = _fields_str(fields)
    params = {"fields": f} if f else None
    with httpx.Client(timeout=30.0) as client:
        response = client.get(_endpoint(f"/troubleTicket/{ticket_id}"), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def create_trouble_ticket(
    name: str,
    description: str | None = None,
    severity: str | None = None,
    external_id: str | None = None,
    at_type: str = "TroubleTicket",
) -> dict[str, Any]:
    payload = {
        "@type": at_type,
        "name": name,
        "description": description,
        "severity": severity,
        "externalId": external_id,
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    with httpx.Client(timeout=30.0) as client:
        response = client.post(_endpoint("/troubleTicket"), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def patch_trouble_ticket(
    ticket_id: str,
    at_type: str | None = None,
    name: str | None = None,
    description: str | None = None,
    severity: str | None = None,
    status: Literal["acknowledged", "inProgress", "pending", "held", "resolved", "closed", "cancelled"] | None = None,
    fields: list[str] | str | None = None,
) -> dict[str, Any]:
    payload = {
        "@type": at_type,
        "name": name,
        "description": description,
        "severity": severity,
        "status": status,
    }
    payload = {k: v for k, v in payload.items() if v is not None}
    f = _fields_str(fields)
    params = {"fields": f} if f else None

    with httpx.Client(timeout=30.0) as client:
        response = client.patch(_endpoint(f"/troubleTicket/{ticket_id}"), json=payload, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def delete_trouble_ticket(ticket_id: str) -> dict[str, Any]:
    with httpx.Client(timeout=30.0) as client:
        response = client.delete(_endpoint(f"/troubleTicket/{ticket_id}"))
        response.raise_for_status()
    return {"status": "deleted", "ticketId": ticket_id}


if __name__ == "__main__":
    if MCP_TRANSPORT == "stdio":
        mcp.run(transport="stdio")
    elif MCP_TRANSPORT == "sse":
        mcp.run(transport="sse", mount_path=MCP_PATH)
    else:
        mcp.run(transport="streamable-http")
