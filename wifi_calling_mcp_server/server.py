from __future__ import annotations

import os
from datetime import datetime, timezone
from itertools import count
from typing import Any

from mcp.server.fastmcp import FastMCP

MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8011"))
MCP_PATH = os.getenv("MCP_PATH", "/mcp")

mcp = FastMCP(
    "wifi-calling-mcp-server",
    host=MCP_HOST,
    port=MCP_PORT,
    streamable_http_path=MCP_PATH,
    stateless_http=True,
)

CUSTOMERS: dict[str, dict[str, Any]] = {
    "2101111001": {
        "name": "John Doe",
        "router": {
            "status": "Online",
            "model": "VodafonePowerHub",
            "ssid": "VF_Home",
            "password": "oldpass123",
        },
    },
    "2101234151": {
        "name": "Jane Smith",
        "router": {
            "status": "Offline",
            "model": "VodafoneMiniHub",
            "ssid": "VF_Office",
            "password": "secure456",
        },
    },
    "2101234999": {
        "name": "Alice Johnson",
        "router": {
            "status": "Online",
            "model": "VodafonePowerHub",
            "ssid": "VF_Alice",
            "password": "alice789",
        },
    },
}

TICKETS: dict[str, dict[str, Any]] = {}
_ticket_counter = count(1000)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _customer(line_number: str) -> dict[str, Any] | None:
    return CUSTOMERS.get(line_number)


def _ticket(ticket_id: str) -> dict[str, Any] | None:
    return TICKETS.get(ticket_id)


@mcp.tool()
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "server": "wifi-calling-mcp-server",
        "transport": MCP_TRANSPORT,
        "customerCount": len(CUSTOMERS),
        "ticketCount": len(TICKETS),
    }


@mcp.tool()
def verify_customer_in_siebel(name: str, line_number: str) -> dict[str, Any]:
    customer = _customer(line_number)
    if not customer or customer["name"].lower() != name.lower():
        return {"verified": False, "message": "Customer not found or mismatch."}
    return {
        "verified": True,
        "message": "Customer verified successfully.",
        "customer": {"lineNumber": line_number, "name": customer["name"]},
    }


@mcp.tool()
def create_ticket_in_siebel(name: str, line_number: str, area: str, subarea: str, note: str) -> dict[str, Any]:
    customer = _customer(line_number)
    if not customer or customer["name"].lower() != name.lower():
        return {"success": False, "message": "Customer not found or mismatch."}

    ticket_id = f"T-{next(_ticket_counter)}"
    ticket = {
        "ticketId": ticket_id,
        "name": name,
        "lineNumber": line_number,
        "area": area,
        "subarea": subarea,
        "status": "open",
        "createdAt": _utc_now(),
        "notes": [note],
    }
    TICKETS[ticket_id] = ticket
    return {
        "success": True,
        "ticket_id": ticket_id,
        "message": f"Ticket {ticket_id} created for {area}/{subarea}.",
        "ticket": ticket,
    }


@mcp.tool()
def get_router_info_axiros(line_number: str) -> dict[str, Any]:
    customer = _customer(line_number)
    if not customer:
        return {"success": False, "message": f"Line number {line_number} not found."}

    router = customer["router"]
    return {
        "success": True,
        "lineNumber": line_number,
        "status": router["status"],
        "model": router["model"],
        "ssid": router["ssid"],
        "password": router["password"],
    }


@mcp.tool()
def apply_wifi_config_axiros(line_number: str, new_ssid: str, new_password: str) -> dict[str, Any]:
    customer = _customer(line_number)
    if not customer:
        return {"success": False, "message": f"Line number {line_number} not found."}

    router = customer["router"]
    router["ssid"] = new_ssid
    router["password"] = new_password
    return {
        "success": True,
        "lineNumber": line_number,
        "message": f"Wi-Fi updated to SSID '{new_ssid}'.",
        "router": router,
    }


@mcp.tool()
def update_ticket_notes(ticket_id: str, note: str) -> dict[str, Any]:
    ticket = _ticket(ticket_id)
    if not ticket:
        return {"success": False, "message": f"Ticket {ticket_id} not found."}

    timestamped_note = f"[{_utc_now()}] {note}"
    ticket["notes"].append(timestamped_note)
    ticket["updatedAt"] = _utc_now()
    return {
        "success": True,
        "message": f"Note added to {ticket_id}.",
        "ticket": ticket,
    }


@mcp.tool()
def close_ticket(ticket_id: str, concern: str, cause: str) -> dict[str, Any]:
    ticket = _ticket(ticket_id)
    if not ticket:
        return {"success": False, "message": f"Ticket {ticket_id} not found."}

    ticket["status"] = "closed"
    ticket["closure"] = {
        "concern": concern,
        "cause": cause,
        "closedAt": _utc_now(),
    }
    return {
        "success": True,
        "message": f"Ticket {ticket_id} closed with concern '{concern}' and cause '{cause}'.",
        "ticket": ticket,
    }


if __name__ == "__main__":
    if MCP_TRANSPORT == "stdio":
        mcp.run(transport="stdio")
    elif MCP_TRANSPORT == "sse":
        mcp.run(transport="sse", mount_path=MCP_PATH)
    else:
        mcp.run(transport="streamable-http")