# MCP Server + TMF APIs Backend (Python)

This repository contains three TMF API projects, each with a Python backend and MCP server, plus two standalone mock support MCP servers:

- TMF621
	- `tmf621_backend`: TMF621-style Trouble Ticket REST API
	- `tmf621_mcp_server`: MCP server for TMF621 Trouble Ticket
- TMF638
	- `tmf638_backend`: TMF638 Service Inventory REST API
	- `tmf638_mcp_server`: MCP server for TMF638 Service Inventory
- TMF637
	- `tmf637_backend`: TMF637 Product Inventory REST API
	- `tmf637_mcp_server`: MCP server for TMF637 Product Inventory
- WiFi Calling Support
	- `wifi_calling_mcp_server`: standalone MCP server with mock Siebel and Axiros-style support tools
- Troubleshooting Support
	- `troubleshooting_mcp_server`: standalone MCP server with mock troubleshooting tools (AAA, Axiros, NTS, WCRM, OTE/Nova, Siebel, TOA)

## Architecture

- TMF621 backend listens on `http://localhost:8080`
- TMF621 MCP endpoint is `http://localhost:8000/mcp`
- TMF621 backend stores trouble tickets in SQLite (`DB_PATH`, default `data/tickets.db`)
- TMF638 backend listens on `http://localhost:8081`
- TMF638 MCP endpoint is `http://localhost:8001/mcp`
- TMF638 backend stores services in SQLite (`DB_PATH`, default `data/services.db`)
- TMF637 backend listens on `http://localhost:8082`
- TMF637 MCP endpoint is `http://localhost:8002/mcp`
- TMF637 backend stores products in SQLite (`DB_PATH`, default `data/products.db`)
- WiFi Calling MCP endpoint is `http://localhost:8011/mcp`
- WiFi Calling server keeps demo customers, routers, and tickets in memory
- Troubleshooting MCP endpoint is `http://localhost:8012/mcp`
- Troubleshooting server keeps demo customers, tickets, and appointments in memory

## Local Python setup

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run without containers

Backend:

```bash
uvicorn tmf621_backend.app:app --host 0.0.0.0 --port 8080
```

Optional persistent DB path override:

```bash
DB_PATH=./data/tickets.db uvicorn tmf621_backend.app:app --host 0.0.0.0 --port 8080
```

TMF621 MCP server (stdio transport):

```bash
python -m tmf621_mcp_server.server
```

By default the MCP server starts with `streamable-http` at:

- `http://localhost:8000/mcp`

TMF638 backend:

```bash
uvicorn tmf638_backend.app:app --host 0.0.0.0 --port 8081
```

TMF638 MCP server:

```bash
python -m tmf638_mcp_server.server
```

TMF638 streamable HTTP endpoint:

- `http://localhost:8001/mcp`

TMF637 backend:

```bash
uvicorn tmf637_backend.app:app --host 0.0.0.0 --port 8082
```

TMF637 MCP server:

```bash
python -m tmf637_mcp_server.server
```

TMF637 streamable HTTP endpoint:

- `http://localhost:8002/mcp`

WiFi Calling MCP server:

```bash
python -m wifi_calling_mcp_server.server
```

WiFi Calling streamable HTTP endpoint:

- `http://localhost:8011/mcp`

Troubleshooting MCP server:

```bash
python -m troubleshooting_mcp_server.server
```

Troubleshooting streamable HTTP endpoint:

- `http://localhost:8012/mcp`

## Podman deployment

Build and run both containers:

```bash
podman compose up --build
```

Build and run TMF638 containers:

```bash
podman compose -f compose.tmf638.yaml up --build
```

Build and run TMF637 containers:

```bash
podman compose -f compose.tmf637.yaml up --build
```

Build and run the WiFi Calling MCP container:

```bash
podman compose -f compose.wifi_calling.yaml up --build
```

Services in compose:

- `tmf621-backend` (FastAPI backend)
- `tmf621-mcp-server` (Python MCP server)
- `wifi-calling-mcp-server` (Python MCP server)
- `troubleshooting-mcp-server` (Python MCP server)

Services in `compose.tmf638.yaml`:

- `tmf638-backend` (FastAPI backend)
- `tmf638-mcp-server` (Python MCP server)

Services in `compose.tmf637.yaml`:

- `tmf637-backend` (FastAPI backend)
- `tmf637-mcp-server` (Python MCP server)

Services in `compose.wifi_calling.yaml`:

- `wifi-calling-mcp-server` (Python MCP server)

The backend DB is persisted in the `tmf621-data` volume at `/data/tickets.db`.

Langflow MCP endpoints:

- TMF621: `http://localhost:8000/mcp`
- TMF638: `http://localhost:8001/mcp`
- TMF637: `http://localhost:8002/mcp`
- WiFi Calling: `http://localhost:8011/mcp`
- Troubleshooting: `http://localhost:8012/mcp`

## TMF621 endpoints (backend)

- `GET /tmf-api/troubleTicket/v5/troubleTicket`
- `POST /tmf-api/troubleTicket/v5/troubleTicket`
- `GET /tmf-api/troubleTicket/v5/troubleTicket/{id}`
- `PATCH /tmf-api/troubleTicket/v5/troubleTicket/{id}`
- `DELETE /tmf-api/troubleTicket/v5/troubleTicket/{id}`

Supported query parameters from the spec subset:

- `fields` on list/get/patch
- `offset`, `limit` on list

## MCP tools

- `health_check`
- `list_trouble_tickets`
- `get_trouble_ticket`
- `create_trouble_ticket`
- `patch_trouble_ticket`
- `delete_trouble_ticket`

## TMF638 endpoints (backend)

- `GET /tmf-api/serviceInventory/v5/service`
- `POST /tmf-api/serviceInventory/v5/service`
- `GET /tmf-api/serviceInventory/v5/service/{id}`
- `PATCH /tmf-api/serviceInventory/v5/service/{id}`
- `DELETE /tmf-api/serviceInventory/v5/service/{id}`

Supported query parameters from the spec subset:

- `fields` on list/get/patch
- `offset`, `limit` on list

## TMF638 MCP tools

- `health_check`
- `list_services`
- `get_service`
- `create_service`
- `patch_service`
- `delete_service`

## TMF637 endpoints (backend)

- `GET /tmf-api/productInventory/v5/product`
- `POST /tmf-api/productInventory/v5/product`
- `GET /tmf-api/productInventory/v5/product/{id}`
- `PATCH /tmf-api/productInventory/v5/product/{id}`
- `DELETE /tmf-api/productInventory/v5/product/{id}`

Supported query parameters from the spec subset:

- `fields` on list/get/patch
- `offset`, `limit` on list

## TMF637 MCP tools

- `health_check`
- `list_products`
- `get_product`
- `create_product`
- `patch_product`
- `delete_product`

## WiFi Calling MCP tools

- `health_check`
- `verify_customer_in_siebel`
- `create_ticket_in_siebel`
- `get_router_info_axiros`
- `apply_wifi_config_axiros`
- `update_ticket_notes`
- `close_ticket`

## Troubleshooting MCP tools

Input convention for troubleshooting tools:

- Use `landline_number` as the customer identifier
- Accepted formats include `2101111001`, `+302101111001`, and `00302101111001`
- Lookup is normalized internally to the same landline customer

- `health_check`
- `verify_customer`
- `aaa_get_disconnection_history`
- `axiros_check_ont_status`
- `axiros_check_router_status`
- `axiros_remote_reboot_ont`
- `axiros_remote_reboot_router`
- `nts_check_port_status`
- `nts_reset_port`
- `hubs_check_cabinet_status`
- `wcrm_check_service_status`
- `wcrm_check_planned_maintenance`
- `ote_check_network_status`
- `nova_check_backhaul_status`
- `siebel_check_existing_tickets`
- `siebel_create_trouble_ticket`
- `toa_check_technician_availability`
- `toa_schedule_appointment`
