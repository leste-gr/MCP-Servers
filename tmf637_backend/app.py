"""TMF637 Product Inventory Management FastAPI backend."""
import uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse

from tmf637_backend.models import Product, ProductCreate, ProductPatch
from tmf637_backend.storage import (
    delete_product,
    get_product,
    init_db,
    list_products,
    patch_product,
    create_product as db_create_product,
)

app = FastAPI(title="TMF637 Product Inventory", version="5.0.0")

BASE_PATH = "/tmf-api/productInventory/v5"


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()


def _select_fields(obj: dict, fields: list[str] | None) -> dict:
    """Filter object to include only specified fields."""
    if not fields:
        return obj
    return {k: v for k, v in obj.items() if k in fields}


@app.get(f"{BASE_PATH}/product", tags=["product"])
def list_product_endpoint(
    fields: str | list[str] | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    """List or find Product objects."""
    # Coerce fields to list if needed
    if isinstance(fields, str):
        fields = [f.strip() for f in fields.split(",") if f.strip()]
    elif fields is None:
        fields = None

    # Coerce offset/limit safely
    try:
        offset = int(offset) if offset is not None else 0
    except (ValueError, TypeError):
        offset = 0
    try:
        limit = int(limit) if limit is not None else 100
    except (ValueError, TypeError):
        limit = 100

    products, total_count = list_products(offset=offset, limit=limit, fields=fields)
    return JSONResponse(
        content=products,
        headers={"X-Total-Count": str(total_count), "X-Result-Count": str(len(products))},
    )


@app.post(f"{BASE_PATH}/product", tags=["product"], status_code=201)
def create_product_endpoint(body: ProductCreate, fields: str | None = Query(None)):
    """Create a Product."""
    product_id = str(uuid.uuid4())
    payload = body.model_dump(by_alias=True, exclude_none=True)
    created = db_create_product(product_id, payload)

    if fields:
        fields_list = [f.strip() for f in fields.split(",") if f.strip()]
        created = _select_fields(created, fields_list)

    return JSONResponse(content=created, status_code=201)


@app.get(f"{BASE_PATH}/product/{{product_id}}", tags=["product"])
def get_product_endpoint(product_id: str, fields: str | None = Query(None)):
    """Retrieve a Product by ID."""
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if fields:
        fields_list = [f.strip() for f in fields.split(",") if f.strip()]
        product = _select_fields(product, fields_list)

    return product


@app.patch(f"{BASE_PATH}/product/{{product_id}}", tags=["product"])
def patch_product_endpoint(product_id: str, body: ProductPatch, fields: str | None = Query(None)):
    """Update partially a Product."""
    updates = body.model_dump(by_alias=True, exclude_none=True)
    patched = patch_product(product_id, updates)

    if not patched:
        raise HTTPException(status_code=404, detail="Product not found")

    if fields:
        fields_list = [f.strip() for f in fields.split(",") if f.strip()]
        patched = _select_fields(patched, fields_list)

    return patched


@app.delete(f"{BASE_PATH}/product/{{product_id}}", tags=["product"], status_code=202)
def delete_product_endpoint(product_id: str):
    """Delete a Product."""
    if not delete_product(product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    return {"status": "deleted"}


@app.get("/health", tags=["health"])
def health():
    """Health check endpoint."""
    return {"status": "healthy"}
