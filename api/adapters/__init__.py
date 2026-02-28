"""Base adapter protocol and shared types for retailer integrations."""

from typing import Protocol, runtime_checkable

from models.product import Product


@runtime_checkable
class RetailerAdapter(Protocol):
    """Common interface every retailer adapter must implement."""

    name: str

    async def fetch_catalogue(self, style: str) -> list[Product]:
        """Fetch products from the retailer filtered by style category."""
        ...

    async def get_product_detail(self, product_id: str) -> Product | None:
        """Fetch full detail for one product (all colourways, sizes)."""
        ...
