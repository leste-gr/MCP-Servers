from __future__ import annotations

import os
import random
from datetime import date as _date
from datetime import datetime, timedelta
from typing import Any

from mcp.server.fastmcp import FastMCP

MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8012"))
MCP_PATH = os.getenv("MCP_PATH", "/mcp")

mcp = FastMCP(
    "troubleshooting-mcp-server",
    host=MCP_HOST,
    port=MCP_PORT,
    streamable_http_path=MCP_PATH,
    stateless_http=True,
)

CUSTOMERS: dict[str, dict[str, Any]] = {
    "2101111001": {
        "customerId": "CUST-1001",
        "fullName": "John Doe",
        "technology": "FTTH",
        "lineStatus": "active",
        "landlineNumber": "2101111001",
        "contactPhone": "+302101111001",
        "serviceAddress": "Athens Center",
    },
    "2101111002": {
        "customerId": "CUST-1002",
        "fullName": "Jane Smith",
        "technology": "FTTC",
        "lineStatus": "active",
        "landlineNumber": "2101111002",
        "contactPhone": "+302101111002",
        "serviceAddress": "Piraeus",
    },
    "2101111003": {
        "customerId": "CUST-1003",
        "fullName": "Alice Johnson",
        "technology": "ADSL_VOIP",
        "lineStatus": "active",
        "landlineNumber": "2101111003",
        "contactPhone": "+302101111003",
        "serviceAddress": "Peristeri",
    },
}

SIEBEL_TICKETS: dict[str, dict[str, Any]] = {}
TOA_APPOINTMENTS: dict[str, dict[str, Any]] = {}


def _normalize_landline(value: str) -> str:
    digits = "".join(ch for ch in value if ch.isdigit())
    if digits.startswith("0030"):
        digits = digits[4:]
    elif digits.startswith("30") and len(digits) > 10:
        digits = digits[2:]
    return digits


def _get_customer(landline_number: str) -> dict[str, Any] | None:
    normalized_input = _normalize_landline(landline_number)
    direct = CUSTOMERS.get(normalized_input)
    if direct:
        return direct

    for customer in CUSTOMERS.values():
        if _normalize_landline(customer.get("landlineNumber", "")) == normalized_input:
            return customer
        if _normalize_landline(customer.get("contactPhone", "")) == normalized_input:
            return customer
    return None


def _generate_ticket_id() -> str:
    return f"TT-{datetime.now().strftime('%Y%m%d')}-{random.randint(10000, 99999)}"


def _generate_appointment_id() -> str:
    return f"TOA-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"


def _next_business_days(n: int) -> list[str]:
    out: list[str] = []
    day = _date.today() + timedelta(days=1)
    while len(out) < n:
        if day.weekday() < 5:
            out.append(day.isoformat())
        day += timedelta(days=1)
    return out


@mcp.tool()
def health_check() -> dict[str, Any]:
    return {
        "status": "ok",
        "server": "troubleshooting-mcp-server",
        "transport": MCP_TRANSPORT,
        "customerCount": len(CUSTOMERS),
        "ticketCount": len(SIEBEL_TICKETS),
        "appointmentCount": len(TOA_APPOINTMENTS),
    }


@mcp.tool()
def verify_customer(landline_number: str) -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer:
        return {"status": "not_found", "message": f"No customer found for landline: {landline_number}"}
    return {"status": "verified", **customer}


@mcp.tool()
def aaa_get_disconnection_history(landline_number: str) -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer:
        return {"status": "error", "message": "No disconnection data found"}

    technology = customer["technology"]
    count = {
        "FTTH": random.randint(0, 4),
        "FTTC": random.randint(0, 6),
        "ADSL_VOIP": random.randint(1, 8),
        "ADSL_POTS": random.randint(1, 8),
    }.get(technology, 0)
    threshold = {"FTTH": 3, "FTTC": 5, "ADSL_VOIP": 7, "ADSL_POTS": 7}.get(technology, 5)
    return {
        "status": "success",
        "technology": technology,
        "last_7_days_disconnections": count,
        "threshold": threshold,
        "threshold_exceeded": count >= threshold,
        "last_disconnection_at": datetime.now().isoformat(),
        "reasons": ["PPPoE timeout", "line retrain"],
    }


@mcp.tool()
def axiros_check_ont_status(landline_number: str) -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer or customer["technology"] != "FTTH":
        return {"status": "error", "message": "ONT status not available"}
    return {
        "status": "success",
        "ont_online": True,
        "optical_power_dbm": -18.4,
        "registration_status": "registered",
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def axiros_check_router_status(landline_number: str) -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer:
        return {"status": "error", "message": "Router status not available"}
    return {
        "status": "success",
        "router_online": True,
        "sync_down_mbps": 98,
        "sync_up_mbps": 11,
        "wan_ip": "100.64.10.25",
        "line_attenuation_db": 9.2,
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def axiros_remote_reboot_ont(landline_number: str, reason: str = "troubleshooting") -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer or customer["technology"] != "FTTH":
        return {"status": "error", "message": "ONT reboot not supported for this customer"}
    return {
        "status": "success",
        "reboot_initiated": True,
        "expected_recovery_time": "2-3 minutes",
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def axiros_remote_reboot_router(landline_number: str, reason: str = "troubleshooting") -> dict[str, Any]:
    if not _get_customer(landline_number):
        return {"status": "error", "message": "Router reboot failed"}
    return {
        "status": "success",
        "reboot_initiated": True,
        "expected_recovery_time": "2-3 minutes",
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def nts_check_port_status(landline_number: str) -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer or customer["technology"] == "FTTH":
        return {"status": "error", "message": "Port status not available"}
    return {
        "status": "success",
        "port_status": "up",
        "sync_status": "in_sync",
        "error_seconds": random.randint(0, 30),
        "line_profile": "17a",
        "attainable_rate_mbps": random.randint(35, 120),
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def nts_reset_port(landline_number: str, reason: str = "troubleshooting") -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer or customer["technology"] == "FTTH":
        return {"status": "error", "message": "Port reset not supported for this customer"}
    return {
        "status": "success",
        "reset_initiated": True,
        "expected_recovery_time": "3-5 minutes",
        "reason": reason,
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def hubs_check_cabinet_status(landline_number: str) -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer or customer["technology"] != "FTTC":
        return {"status": "error", "message": "Cabinet status not available"}
    return {
        "status": "success",
        "cabinet_id": "ATH-FTTC-204",
        "cabinet_status": "operational",
        "affected_customers": 0,
        "known_issues": [],
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def wcrm_check_service_status(landline_number: str) -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer:
        return {"status": "error", "message": "Service status not available"}
    return {
        "status": "success",
        "service_active": customer["lineStatus"] == "active",
        "provisioning_status": "completed",
        "last_modified": datetime.now().isoformat(),
    }


@mcp.tool()
def wcrm_check_planned_maintenance(landline_number: str) -> dict[str, Any]:
    if not _get_customer(landline_number):
        return {"status": "error", "message": "Service status not available"}
    return {
        "status": "success",
        "maintenance_scheduled": False,
        "message": "No planned maintenance affecting this service",
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def ote_check_network_status(landline_number: str) -> dict[str, Any]:
    if not _get_customer(landline_number):
        return {"status": "error", "message": "Network status unavailable"}
    return {
        "status": "success",
        "network_status": "operational",
        "known_outages": [],
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def nova_check_backhaul_status(landline_number: str) -> dict[str, Any]:
    if not _get_customer(landline_number):
        return {"status": "error", "message": "Backhaul status unavailable"}
    return {
        "status": "success",
        "backhaul_status": "operational",
        "latency_ms": 12,
        "packet_loss_percent": 0.0,
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def siebel_check_existing_tickets(landline_number: str) -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer:
        return {"status": "error", "message": "Customer not found"}

    customer_id = customer["customerId"]
    open_tickets = [
        {
            "ticket_id": ticket_id,
            "status": ticket["status"],
            "assigned_team": ticket["assigned_team"],
            "created_at": ticket["created_at"],
        }
        for ticket_id, ticket in SIEBEL_TICKETS.items()
        if ticket["customer_id"] == customer_id and ticket["status"].lower() == "open"
    ]
    return {
        "status": "success",
        "open_tickets": open_tickets,
        "message": "No open tickets found for this customer" if not open_tickets else "Open tickets retrieved",
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def siebel_create_trouble_ticket(
    landline_number: str,
    priority: str,
    issue_description: str,
    diagnostic_summary: str,
    escalation_reason: str = "",
) -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer:
        return {"status": "error", "message": "Customer not found"}

    ticket_id = _generate_ticket_id()
    assigned_team = "Technical Support L2" if priority.lower() in {"1", "2", "high", "medium"} else "Technical Support L1"
    created_at = datetime.now().isoformat()

    SIEBEL_TICKETS[ticket_id] = {
        "ticket_id": ticket_id,
        "customer_id": customer["customerId"],
        "priority": priority,
        "issue_description": issue_description,
        "diagnostic_summary": diagnostic_summary,
        "escalation_reason": escalation_reason,
        "status": "Open",
        "assigned_team": assigned_team,
        "created_at": created_at,
    }

    return {
        "status": "success",
        "ticket_number": ticket_id,
        "priority": priority,
        "assigned_team": assigned_team,
        "message": f"Trouble ticket {ticket_id} created successfully",
        "created_at": created_at,
    }


@mcp.tool()
def toa_check_technician_availability(landline_number: str) -> dict[str, Any]:
    if not _get_customer(landline_number):
        return {"status": "error", "message": "Customer not found"}

    business_days = _next_business_days(5)
    windows = [
        {"start": "08:00", "end": "12:00"},
        {"start": "12:00", "end": "16:00"},
        {"start": "14:00", "end": "18:00"},
    ]

    slots: list[dict[str, Any]] = []
    for day in business_days:
        for win in random.sample(windows, random.randint(2, 3)):
            slots.append(
                {
                    "date": day,
                    "time_window": f"{win['start']} - {win['end']}",
                    "available": True,
                }
            )

    return {
        "status": "success",
        "available_slots": slots,
        "earliest_appointment": f"{business_days[0]} 08:00 - 12:00",
        "service_area": "Athens Metropolitan",
        "timestamp": datetime.now().isoformat(),
    }


@mcp.tool()
def toa_schedule_appointment(
    landline_number: str,
    appointment_date: str,
    time_window: str,
    ticket_number: str,
    contact_phone: str | None = None,
) -> dict[str, Any]:
    customer = _get_customer(landline_number)
    if not customer:
        return {"status": "error", "message": "Customer not found"}

    appointment_id = _generate_appointment_id()
    created_at = datetime.now().isoformat()
    TOA_APPOINTMENTS[appointment_id] = {
        "appointment_id": appointment_id,
        "customer_id": customer["customerId"],
        "appointment_date": appointment_date,
        "time_window": time_window,
        "ticket_number": ticket_number,
        "contact_phone": contact_phone,
        "status": "Confirmed",
        "technician_name": "Technical Team",
        "created_at": created_at,
    }

    return {
        "status": "success",
        "appointment_confirmed": True,
        "appointment_id": appointment_id,
        "appointment_date": appointment_date,
        "time_window": time_window,
        "ticket_number": ticket_number,
        "technician_name": "Technical Team",
        "confirmation_sms_sent": True,
        "message": f"Appointment confirmed for {appointment_date} between {time_window}",
        "reminder": "Please ensure someone over 18 is present at the premises during the appointment window.",
        "created_at": created_at,
    }


if __name__ == "__main__":
    if MCP_TRANSPORT == "stdio":
        mcp.run(transport="stdio")
    elif MCP_TRANSPORT == "sse":
        mcp.run(transport="sse", mount_path=MCP_PATH)
    else:
        mcp.run(transport="streamable-http")