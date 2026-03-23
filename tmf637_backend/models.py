"""TMF637 Product Inventory Management data models."""
from datetime import datetime, UTC
from typing import Optional
from pydantic import BaseModel, Field


class ProductStatusType(str):
    """Valid values for the lifecycle status of a product."""
    PENDING = "pending"
    ORDERED = "ordered"
    PROVISIONED = "provisioned"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    INACTIVE = "inactive"
    TERMINATED = "terminated"


class ProductCreate(BaseModel):
    """Product creation model."""
    type: str = Field(..., alias="@type")
    name: str
    description: Optional[str] = None
    productOffering: Optional[dict] = None
    account: Optional[dict] = None
    relatedParty: Optional[list[dict]] = None
    status: Optional[str] = "pending"

    class Config:
        populate_by_name = True


class ProductPatch(BaseModel):
    """Product patch model."""
    type: Optional[str] = Field(None, alias="@type")
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    productOffering: Optional[dict] = None
    relatedParty: Optional[list[dict]] = None

    class Config:
        populate_by_name = True


class Product(BaseModel):
    """Product inventory model (response)."""
    id: str
    type: str = Field(..., alias="@type")
    name: str
    description: Optional[str] = None
    productOffering: Optional[dict] = None
    account: Optional[dict] = None
    relatedParty: Optional[list[dict]] = None
    status: str
    creationDate: str
    lastUpdate: str

    class Config:
        populate_by_name = True
