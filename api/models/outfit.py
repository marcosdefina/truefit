"""Pydantic models for outfit generation request/response."""

from decimal import Decimal

from pydantic import BaseModel, Field

from models.product import Product, Style


class SizeInput(BaseModel):
    top: str = "M"
    bottom: str = "32"
    shoes: str = "43"


class GenerateRequest(BaseModel):
    budget: Decimal = Field(..., gt=0, description="Maximum total € for the outfit")
    style: Style
    size: SizeInput
    shop: str | None = None  # None = best across all shops


class OutfitItem(BaseModel):
    category: str
    name: str
    price: Decimal
    colour: str | None = None
    colour_name: str | None = None
    size: str
    image: str
    url: str


class Outfit(BaseModel):
    shop: str
    total: Decimal
    score: float
    items: list[OutfitItem]
    score_breakdown: dict[str, float] = Field(default_factory=dict)


class GenerateResponse(BaseModel):
    outfits: list[Outfit]
    filters_applied: dict = Field(default_factory=dict)
