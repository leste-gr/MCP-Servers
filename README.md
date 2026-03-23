# MCP Server + TMF621 Backend (Python)

This repository contains two TMF API projects, each with a Python backend and MCP server:

- TMF621
	- `tmf621_backend`: TMF621-style Trouble Ticket REST API
	- `tmf621_mcp_server`: MCP server for TMF621 Trouble Ticket
- TMF638
	- `tmf638_backend`: TMF638 Service Inventory REST API
	- `tmf638_mcp_server`: MCP server for TMF638 Service Inventory

## Architecture

- TMF621 backend listens on `http://localhost:8080`
- TMF621 MCP endpoint is `http://localhost:8000/mcp`
- TMF621 backend stores trouble tickets in SQLite (`DB_PATH`, default `data/tickets.db`)
- TMF638 backend listens on `http://localhost:8081`
- TMF638 MCP endpoint is `http://localhost:8001/mcp`
- TMF638 backend stores services in SQLite (`DB_PATH`, default `data/services.db`)

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

## Podman deployment

Build and run both containers:

```bash
podman compose up --build
```

Build and run TMF638 containers:

```bash
podman compose -f compose.tmf638.yaml up --build
```

Services in compose:

- `tmf621-backend` (FastAPI backend)
- `tmf621-mcp-server` (Python MCP server)

Services in `compose.tmf638.yaml`:

- `tmf638-backend` (FastAPI backend)
- `tmf638-mcp-server` (Python MCP server)

The backend DB is persisted in the `tmf621-data` volume at `/data/trouble_tickets.db`.

Langflow MCP endpoint:

- `http://localhost:8000/mcp`

TMF638 Langflow MCP endpoint:

- `http://localhost:8001/mcp`

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
