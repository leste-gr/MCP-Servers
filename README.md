# MCP Server + TMF621 Backend (Python)

This repository contains two Python services:

- `backend`: A TMF621-style Trouble Ticket REST API.
- `mcp_server`: An MCP server that exposes tools and forwards operations to the TMF621 backend.

## Architecture

- TMF621 backend listens on `http://localhost:8080`
- MCP server connects to backend via `TMF621_BASE_URL`
- MCP server uses Streamable HTTP transport for agent integrations
- Backend stores trouble tickets in SQLite (`DB_PATH`, default `data/trouble_tickets.db`)

## Local Python setup

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run without containers

Backend:

```bash
uvicorn backend.app:app --host 0.0.0.0 --port 8080
```

Optional persistent DB path override:

```bash
DB_PATH=./data/trouble_tickets.db uvicorn backend.app:app --host 0.0.0.0 --port 8080
```

MCP server (stdio transport):

```bash
python -m mcp_server.server
```

By default the MCP server starts with `streamable-http` at:

- `http://localhost:8000/mcp`

## Podman deployment

Build and run both containers:

```bash
podman compose up --build
```

Services in compose:

- `tmf621-backend` (FastAPI backend)
- `tmf621-mcp-server` (Python MCP server)

The backend DB is persisted in the `tmf621-data` volume at `/data/trouble_tickets.db`.

Langflow MCP endpoint:

- `http://localhost:8000/mcp`

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
