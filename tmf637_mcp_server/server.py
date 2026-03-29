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


def _fields_str(fields: Any) -> str | None:
    """Convert fields list to comma-separated string."""
    if fields is None or fields == {}:
        return None
    if isinstance(fields, list):
        if not fields:
            return None
        value = ",".join(str(x).strip() for x in fields if str(x).strip())
        if not value or value == "*":
            return None
        return value
    if isinstance(fields, str):
        value = fields.strip()
        if not value or value == "*":
            return None
        return value
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
    """Internal health probe for the TMF637 MCP server.

    Returns server status and the configured TMF637 backend base URL.
    This is not part of the TMF637 swagger operations; it is provided for
    MCP runtime diagnostics.
    """
    return {
        "status": "ok",
        "server": "tmf637-mcp-server",
        "tmf637BaseUrl": TMF637_BASE_URL,
    }


@mcp.tool()
def list_products(
    fields: Any = None,
    offset: Any = None,
    limit: Any = None,
    filters: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """TMF637 listProduct (GET /product): List or find Product objects.

    Swagger mapping:
    - operationId: listProduct
    - method/path: GET /product

    Args:
        fields: Comma-separated properties to be provided in response.
            Accepts either a list of field names or a pre-joined string.
        offset: Requested index for start of resources to be provided in response.
        limit: Requested number of resources to be provided in response.
        filters: Optional backend filters as query params. Keys can target nested
            product fields with dot-notation and optional operators, for example:
            `status`, `name__contains`,
            `relatedParty.partyOrPartyRole.name__contains`.

        Agent instructions:
                - Convert user search intent into `filters` whenever the user asks to
                    narrow results (by customer, status, offering, text, etc.).
                - Prefer `__contains` for free-text/natural-language matching.
                - Use dot notation for nested properties from Product payload.
                - Use `__in` with comma-separated values for multi-value constraints.
                - Keep `fields` minimal when user asks for a concise result set.

        Filter operators:
                - `field`: case-insensitive equals
                - `field__contains`: case-insensitive substring
                - `field__startswith`: case-insensitive prefix
                - `field__endswith`: case-insensitive suffix
                - `field__ne`: not equals
                - `field__in`: comma-separated membership values

        Common examples:
                - Customer name contains Elena:
                    `filters={"relatedParty.partyOrPartyRole.name__contains": "Elena"}`
                - Active products only:
                    `filters={"status": "active"}`
                - Active or provisioned:
                    `filters={"status__in": "active,provisioned"}`
                - FTTH offerings with concise response:
                    `filters={"productOffering.name__contains": "FTTH"},
                    fields=["id", "name", "status", "relatedParty", "productOffering"]`

    Returns:
        A list of TMF637 Product resources.
    """
    params = {"fields": _fields_str(fields), "offset": _to_int(offset), "limit": _to_int(limit)}

    if filters:
        for key, value in filters.items():
            if value is None:
                continue
            if isinstance(value, list):
                value = ",".join(str(v) for v in value if v is not None)
            params[str(key)] = str(value)

    params = {k: v for k, v in params.items() if v is not None}
    query_params = params or None

    with httpx.Client(timeout=30.0) as client:
        response = client.get(_endpoint("/product"), params=query_params)
        response.raise_for_status()
        return response.json()


@mcp.tool()
def get_product(
    product_id: str,
    fields: Any = None,
) -> dict[str, Any]:
    """TMF637 retrieveProduct (GET /product/{id}): Retrieve a Product by ID.

    Swagger mapping:
    - operationId: retrieveProduct
    - method/path: GET /product/{id}

    Args:
        product_id: Identifier of the Resource (path parameter id).
        fields: Comma-separated properties to be provided in response.
            Accepts either a list of field names or a pre-joined string.

    Agent instructions:
        - Use this when the user already has a specific product id.
        - If the user asks for selected attributes only, pass `fields` to reduce
          payload size.

    Returns:
        A single TMF637 Product resource.
    """
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
    """TMF637 createProduct (POST /product): Create a Product entity.

    Swagger mapping:
    - operationId: createProduct
    - method/path: POST /product
    - request body: Product_FVO

    Args:
        name: Product name.
        description: Human-readable product description.
        product_offering: Product offering reference (`productOffering`).
        account: Account reference associated with the product.
        status: Product lifecycle status.
        at_type: TMF polymorphic type (`@type`), defaults to Product.

    Agent instructions:
        - Ensure values are mapped to TMF field names exactly.
        - Prefer including `product_offering` when user mentions package/plan.
        - Keep status within allowed enum values.

    Returns:
        The created TMF637 Product resource.
    """
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
    fields: Any = None,
) -> dict[str, Any]:
    """TMF637 patchProduct (PATCH /product/{id}): Partially update a Product.

    Swagger mapping:
    - operationId: patchProduct
    - method/path: PATCH /product/{id}
    - request body: Product_MVO

    Args:
        product_id: Identifier of the Resource (path parameter id).
        at_type: TMF polymorphic type override (`@type`).
        name: Updated product name.
        description: Updated product description.
        status: Updated product lifecycle status.
        product_offering: Updated product offering reference.
        fields: Comma-separated properties to be provided in response.
            Accepts either a list of field names or a pre-joined string.

    Agent instructions:
        - Only send fields the user asked to change.
        - Do not overwrite unspecified attributes.
        - Use `fields` to request a compact confirmation payload after update.

    Returns:
        The updated TMF637 Product resource.
    """
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
    """TMF637 deleteProduct (DELETE /product/{id}): Delete a Product entity.

    Swagger mapping:
    - operationId: deleteProduct
    - method/path: DELETE /product/{id}

    Args:
        product_id: Identifier of the Resource (path parameter id).

    Agent instructions:
        - Use only when user explicitly asks to remove a product.
        - Ask for confirmation before destructive actions when context is ambiguous.

    Returns:
        A local confirmation payload with deleted product id.
    """
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
