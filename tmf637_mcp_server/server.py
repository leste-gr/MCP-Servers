"""TMF637 Product Inventory Management MCP server."""
from __future__ import annotations

import os
from typing import Any, Literal

import httpx
from mcp.server.fastmcp import FastMCP

MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8002"))
MCP_PATH = os.getenv("MCP_PATH", "/mcp")

TMF637_BASE_URL = os.getenv(
    "TMF637_BASE_URL",
    "http://tmf637-backend:8082/tmf-api/productInventory/v5",
).rstrip("/")

mcp = FastMCP(
    "tmf637-mcp-server",
    host=MCP_HOST,
    port=MCP_PORT,
    streamable_http_path=MCP_PATH,
)


def _endpoint(path: str) -> str:
    return f"{TMF637_BASE_URL}{path}"


def _fields_str(fields: list[str] | str | None) -> str | None:
    """Convert fields list to comma-separated string."""
    if isinstance(fields, list):
        return ",".join(fields)
    return fields


def _to_int(v: Any) -> int | None:
    """Safely coerce value to int, return None for invalid values."""
    if v is None or v == {}:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


@mcp.tool()
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "server": "tmf637-mcp-server",
        "tmf637BaseUrl": TMF637_BASE_URL,
    }


@mcp.tool()
def list_products(
    fields: list[str] | str | None = None,
    offset: Any = None,
    limit: Any = None,
) -> list[dict[str, Any]]:
    params = {"fields": _fields_str(fields), "offset": _to_int(offset), "limit": _to_int(limit)}
    params = {k: v for k, v in params.items() if v is not None}

    with httpx.Client(timeout=30.0) as client:
        response = client.get(_endpoint("/product"), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def get_product(
    product_id: str,
    fields: list[str] | str | None = None,
) -> dict[str, Any]:
    f = _fields_str(fields)
    params = {"fields": f} if f else None
    with httpx.Client(timeout=30.0) as client:
        response = client.get(_endpoint(f"/product/{product_id}"), params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def create_product(
    name: str | None = None,
    description: str | None = None,
    product_offering: dict | None = None,
    account: dict | None = None,
    status: Literal["pending", "ordered", "provisioned", "active", "suspended", "inactive", "terminated"] | None = None,
    at_type: str = "Product",
) -> dict[str, Any]:
    payload = {
        "@type": at_type,
        "name": name,
        "description": description,
        "productOffering": product_offering,
        "account": account,
        "status": status,
    }
    payload = {k: v for k, v in payload.items() if v is not None}

    with httpx.Client(timeout=30.0) as client:
        response = client.post(_endpoint("/product"), json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def patch_product(
    product_id: str,
    at_type: str | None = None,
    name: str | None = None,
    description: str | None = None,
    status: Literal["pending", "ordered", "provisioned", "active", "suspended", "inactive", "terminated"] | None = None,
    product_offering: dict | None = None,
    fields: list[str] | str | None = None,
) -> dict[str, Any]:
    payload = {}
    if at_type:
        payload["@type"] = at_type
    if name is not None:
        payload["name"] = name
    if description is not None:
        payload["description"] = description
    if status is not None:
        payload["status"] = status
    if product_offering is not None:
        payload["productOffering"] = product_offering

    f = _fields_str(fields)
    params = {"fields": f} if f else None

    with httpx.Client(timeout=30.0) as client:
        response = client.patch(_endpoint(f"/product/{product_id}"), json=payload, params=params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def delete_product(product_id: str) -> dict[str, Any]:
    with httpx.Client(timeout=30.0) as client:
        response = client.delete(_endpoint(f"/product/{product_id}"))
        response.raise_for_status()
    return {"status": "deleted", "productId": product_id}


if __name__ == "__main__":
    if MCP_TRANSPORT == "stdio":
        mcp.run(transport="stdio")
    elif MCP_TRANSPORT == "sse":
        mcp.run(transport="sse", mount_path=MCP_PATH)
    else:
        mcp.run(transport="streamable-http")
