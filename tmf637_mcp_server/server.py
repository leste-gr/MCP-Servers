"""TMF637 Product Inventory Management MCP server."""
import os
from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP

# Configuration
MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")
MCP_PORT = int(os.getenv("MCP_PORT", 8002))
MCP_PATH = os.getenv("MCP_PATH", "/mcp")
MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")
TMF637_BASE_URL = os.getenv("TMF637_BASE_URL", "http://localhost:8082/tmf-api/productInventory/v5")

# Initialize MCP server
server = FastMCP("tmf637-product-inventory-server", transport=MCP_TRANSPORT)


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


@server.tool()
def health_check() -> dict:
    """Check health of TMF637 backend."""
    try:
        response = httpx.get(f"{TMF637_BASE_URL.rsplit('/', 1)[0]}/health", timeout=5)
        return {"status": "healthy" if response.status_code == 200 else "unhealthy"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@server.tool()
def list_products(
    fields: list[str] | str | None = None,
    offset: Any = None,
    limit: Any = None,
) -> dict:
    """List all products from inventory."""
    params = {}
    
    fields_str = _fields_str(fields)
    if fields_str:
        params["fields"] = fields_str
    
    offset_int = _to_int(offset)
    if offset_int is not None:
        params["offset"] = offset_int
    
    limit_int = _to_int(limit)
    if limit_int is not None:
        params["limit"] = limit_int

    try:
        response = httpx.get(f"{TMF637_BASE_URL}/product", params=params, timeout=10)
        response.raise_for_status()
        return {
            "products": response.json(),
            "total_count": response.headers.get("X-Total-Count", "0"),
            "result_count": response.headers.get("X-Result-Count", "0"),
        }
    except Exception as e:
        return {"error": str(e), "products": []}


@server.tool()
def get_product(
    product_id: str,
    fields: list[str] | str | None = None,
) -> dict:
    """Get a specific product by ID."""
    params = {}
    fields_str = _fields_str(fields)
    if fields_str:
        params["fields"] = fields_str

    try:
        response = httpx.get(f"{TMF637_BASE_URL}/product/{product_id}", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": "Product not found"}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


@server.tool()
def create_product(
    name: str,
    description: str | None = None,
    product_offering: dict | None = None,
    account: dict | None = None,
    status: str | None = None,
    fields: list[str] | str | None = None,
) -> dict:
    """Create a new product in inventory."""
    payload = {
        "@type": "Product",
        "name": name,
    }
    
    if description:
        payload["description"] = description
    if product_offering:
        payload["productOffering"] = product_offering
    if account:
        payload["account"] = account
    if status:
        payload["status"] = status

    params = {}
    fields_str = _fields_str(fields)
    if fields_str:
        params["fields"] = fields_str

    try:
        response = httpx.post(
            f"{TMF637_BASE_URL}/product",
            json=payload,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": str(e)}


@server.tool()
def patch_product(
    product_id: str,
    name: str | None = None,
    description: str | None = None,
    status: str | None = None,
    product_offering: dict | None = None,
    fields: list[str] | str | None = None,
) -> dict:
    """Update a product partially."""
    payload = {}
    
    if name:
        payload["name"] = name
    if description:
        payload["description"] = description
    if status:
        payload["status"] = status
    if product_offering:
        payload["productOffering"] = product_offering

    params = {}
    fields_str = _fields_str(fields)
    if fields_str:
        params["fields"] = fields_str

    try:
        response = httpx.patch(
            f"{TMF637_BASE_URL}/product/{product_id}",
            json=payload,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": "Product not found"}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


@server.tool()
def delete_product(product_id: str) -> dict:
    """Delete a product from inventory."""
    try:
        response = httpx.delete(f"{TMF637_BASE_URL}/product/{product_id}", timeout=10)
        response.raise_for_status()
        return {"status": "deleted"}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return {"error": "Product not found"}
        return {"error": str(e)}
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    if MCP_TRANSPORT == "streamable-http":
        import uvicorn
        uvicorn.run(
            "tmf637_mcp_server.server:app",
            host=MCP_HOST,
            port=MCP_PORT,
            log_level="info",
        )
    else:
        server.run()
