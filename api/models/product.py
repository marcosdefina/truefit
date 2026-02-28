"""Pydantic models for products and colours."""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class Category(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    SHOES = "shoes"
    OUTERWEAR = "outerwear"
    ACCESSORY = "accessory"


class Style(str, Enum):
    CASUAL = "casual"
    SMART_CASUAL = "smart-casual"
    FORMAL = "formal"
    STREETWEAR = "streetwear"
    MINIMAL = "minimal"


class Colour(BaseModel):
    name: str
    hex: str
    swatch: str | None = None


class Product(BaseModel):
    id: str
    retailer: str
    name: str
    url: str
    image_url: str
    category: Category
    style_tags: list[str] = Field(default_factory=list)
    price: Decimal
    currency: str = "EUR"
    colours: list[Colour] = Field(default_factory=list)
    sizes: list[str] = Field(default_factory=list)
    scraped_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def primary_colour(self) -> str | None:
        """Return hex of the first colour, or None."""
        return self.colours[0].hex if self.colours else None
