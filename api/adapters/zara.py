"""
Zara retailer adapter.

Scrapes Zara's internal JSON API endpoints that power their website.
Zara's frontend fetches product lists from endpoints like:
  /api/products?categoryId=...&ajax=true

We replicate those calls with appropriate headers.
"""

import logging
from datetime import datetime
from decimal import Decimal

import httpx

from config import settings
from models.product import Category, Colour, Product, Style

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Zara category IDs — these map styles to Zara's internal section IDs.
# Found by inspecting network requests on zara.com.
# These may change; if scraping breaks, update these first.
# ---------------------------------------------------------------------------
ZARA_MAN_CATEGORIES: dict[str, list[dict]] = {
    "casual": [
        {"id": "t-shirts", "api_cat": "1564"},
        {"id": "jeans", "api_cat": "1659"},
        {"id": "sneakers", "api_cat": "1775"},
    ],
    "smart-casual": [
        {"id": "shirts", "api_cat": "1564"},
        {"id": "trousers", "api_cat": "1671"},
        {"id": "shoes-smart", "api_cat": "1775"},
    ],
    "formal": [
        {"id": "suits-blazers", "api_cat": "1564"},
        {"id": "trousers", "api_cat": "1671"},
        {"id": "shoes-smart", "api_cat": "1775"},
    ],
    "streetwear": [
        {"id": "sweatshirts", "api_cat": "1564"},
        {"id": "joggers", "api_cat": "1671"},
        {"id": "sneakers", "api_cat": "1775"},
    ],
    "minimal": [
        {"id": "basics", "api_cat": "1564"},
        {"id": "trousers", "api_cat": "1671"},
        {"id": "shoes-minimal", "api_cat": "1775"},
    ],
}

# Map Zara section keywords → our Category enum
SECTION_TO_CATEGORY: dict[str, Category] = {
    "t-shirts": Category.TOP,
    "shirts": Category.TOP,
    "suits-blazers": Category.TOP,
    "sweatshirts": Category.TOP,
    "basics": Category.TOP,
    "jeans": Category.BOTTOM,
    "trousers": Category.BOTTOM,
    "joggers": Category.BOTTOM,
    "sneakers": Category.SHOES,
    "shoes-smart": Category.SHOES,
    "shoes-minimal": Category.SHOES,
}

# Common headers to look like a real browser
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-GB,en;q=0.9",
    "Referer": "https://www.zara.com/",
}


class ZaraAdapter:
    """Scrapes Zara's website for product catalogue data."""

    name: str = "zara"

    def __init__(self) -> None:
        self._base = settings.zara_base_url
        self._region = settings.zara_region
        self._lang = settings.zara_language

    # ------------------------------------------------------------------
    # Public interface (matches RetailerAdapter protocol)
    # ------------------------------------------------------------------

    async def fetch_catalogue(self, style: str) -> list[Product]:
        """
        Fetch products from Zara matching the given style.

        In the MVP, this uses Zara's undocumented product-list JSON endpoint.
        If scraping fails (site structure change, rate-limited), falls back
        to the demo catalogue so development can continue.
        """
        products: list[Product] = []
        sections = ZARA_MAN_CATEGORIES.get(style, ZARA_MAN_CATEGORIES["casual"])

        async with httpx.AsyncClient(headers=HEADERS, timeout=15.0) as client:
            for section in sections:
                category = SECTION_TO_CATEGORY[section["id"]]
                try:
                    section_products = await self._fetch_section(
                        client, section, category, style
                    )
                    products.extend(section_products)
                except Exception as exc:
                    logger.warning(
                        "Zara scrape failed for section %s: %s — using demo data",
                        section["id"],
                        exc,
                    )
                    products.extend(self._demo_products(category, style))

        if not products:
            logger.warning("No products scraped from Zara — loading full demo catalogue")
            products = self._full_demo_catalogue(style)

        return products

    async def get_product_detail(self, product_id: str) -> Product | None:
        """Fetch single product detail (placeholder for Phase 1)."""
        return None

    # ------------------------------------------------------------------
    # Private: scraping logic
    # ------------------------------------------------------------------

    async def _fetch_section(
        self,
        client: httpx.AsyncClient,
        section: dict,
        category: Category,
        style: str,
    ) -> list[Product]:
        """
        Attempt to hit Zara's product-list API.
        The real endpoint pattern:
          GET https://www.zara.com/{region}/{lang}/category/{catId}/products
        Zara serves a JSON payload with product groups.
        """
        url = (
            f"{self._base}/{self._region}/{self._lang}"
            f"/category/{section['api_cat']}/products"
        )
        resp = await client.get(url)

        if resp.status_code != 200:
            raise RuntimeError(f"HTTP {resp.status_code} from {url}")

        data = resp.json()
        products: list[Product] = []

        # Zara's JSON typically nests products under "productGroups"
        for group in data.get("productGroups", []):
            for element in group.get("elements", []):
                commercial = element.get("commercialComponents", [{}])
                for item in commercial:
                    try:
                        products.append(self._parse_product(item, category, style))
                    except (KeyError, TypeError) as exc:
                        logger.debug("Skipping unparseable product: %s", exc)

        return products

    def _parse_product(self, item: dict, category: Category, style: str) -> Product:
        """Parse a single product from Zara's JSON into our Product model."""
        colours = []
        for c in item.get("detail", {}).get("colors", []):
            colours.append(
                Colour(
                    name=c.get("name", "Unknown"),
                    hex=f"#{c.get('hexCode', '000000')}",
                    swatch=c.get("image", {}).get("url"),
                )
            )

        sizes = []
        for c in item.get("detail", {}).get("colors", []):
            for s in c.get("sizes", []):
                size_name = s.get("name", "")
                if size_name and size_name not in sizes:
                    sizes.append(size_name)

        price_raw = item.get("price", 0)
        # Zara prices are in cents
        price = Decimal(str(price_raw)) / 100 if price_raw > 100 else Decimal(str(price_raw))

        return Product(
            id=str(item.get("id", "")),
            retailer="zara",
            name=item.get("name", "Unknown Item"),
            url=item.get("seo", {}).get("url", self._base),
            image_url=item.get("detail", {}).get("colors", [{}])[0]
            .get("image", {})
            .get("url", ""),
            category=category,
            style_tags=[style],
            price=price,
            currency="EUR",
            colours=colours,
            sizes=sizes,
            scraped_at=datetime.utcnow(),
        )

    # ------------------------------------------------------------------
    # Demo / fallback catalogue
    # ------------------------------------------------------------------

    def _demo_products(self, category: Category, style: str) -> list[Product]:
        """Return a handful of realistic demo products for one category."""
        demos = {
            Category.TOP: [
                ("ZT001", "Oxford Button-Down Shirt", Decimal("35.95"),
                 [Colour(name="White", hex="#FFFFFF"), Colour(name="Light Blue", hex="#ADD8E6")],
                 ["XS", "S", "M", "L", "XL"],
                 "https://static.zara.net/photos///2024/V/0/2/p/0706/350/250/2/w/750/0706350250_1_1_1.jpg"),
                ("ZT002", "Textured Knit Polo", Decimal("29.95"),
                 [Colour(name="Olive Green", hex="#4A5A3C"), Colour(name="Navy", hex="#1B2A4A")],
                 ["S", "M", "L", "XL"],
                 "https://static.zara.net/photos///2024/V/0/2/p/0962/400/505/2/w/750/0962400505_1_1_1.jpg"),
                ("ZT003", "Linen Blend T-Shirt", Decimal("22.95"),
                 [Colour(name="Sand", hex="#C2B280"), Colour(name="Black", hex="#1A1A1A")],
                 ["XS", "S", "M", "L", "XL", "XXL"],
                 "https://static.zara.net/photos///2024/V/0/2/p/6462/301/250/2/w/750/6462301250_1_1_1.jpg"),
                ("ZT004", "Structured Blazer", Decimal("79.95"),
                 [Colour(name="Charcoal", hex="#36454F"), Colour(name="Camel", hex="#C19A6B")],
                 ["S", "M", "L", "XL"],
                 "https://static.zara.net/photos///2024/V/0/2/p/1564/300/401/2/w/750/1564300401_1_1_1.jpg"),
                ("ZT005", "Oversized Graphic Sweatshirt", Decimal("39.95"),
                 [Colour(name="Grey Marl", hex="#B0B0B0"), Colour(name="Off-White", hex="#FAF9F6")],
                 ["S", "M", "L", "XL"],
                 "https://static.zara.net/photos///2024/V/0/2/p/4320/301/250/2/w/750/4320301250_1_1_1.jpg"),
            ],
            Category.BOTTOM: [
                ("ZB001", "Slim Fit Chinos", Decimal("35.95"),
                 [Colour(name="Khaki", hex="#BDB76B"), Colour(name="Navy", hex="#1B2A4A")],
                 ["30", "31", "32", "33", "34", "36"],
                 "https://static.zara.net/photos///2024/V/0/2/p/0706/235/707/2/w/750/0706235707_1_1_1.jpg"),
                ("ZB002", "Relaxed Fit Jeans", Decimal("39.95"),
                 [Colour(name="Mid Blue", hex="#6B8EC2"), Colour(name="Black", hex="#1A1A1A")],
                 ["30", "32", "34", "36"],
                 "https://static.zara.net/photos///2024/V/0/2/p/8062/401/406/2/w/750/8062401406_1_1_1.jpg"),
                ("ZB003", "Tailored Trousers", Decimal("45.95"),
                 [Colour(name="Charcoal", hex="#36454F"), Colour(name="Stone", hex="#928E85")],
                 ["30", "31", "32", "33", "34", "36"],
                 "https://static.zara.net/photos///2024/V/0/2/p/0706/360/800/2/w/750/0706360800_1_1_1.jpg"),
                ("ZB004", "Cargo Joggers", Decimal("32.95"),
                 [Colour(name="Olive", hex="#556B2F"), Colour(name="Black", hex="#1A1A1A")],
                 ["S", "M", "L", "XL"],
                 "https://static.zara.net/photos///2024/V/0/2/p/4087/350/505/2/w/750/4087350505_1_1_1.jpg"),
            ],
            Category.SHOES: [
                ("ZS001", "Leather Derby Shoes", Decimal("59.95"),
                 [Colour(name="Black", hex="#1A1A1A"), Colour(name="Brown", hex="#8B4513")],
                 ["40", "41", "42", "43", "44", "45"],
                 "https://static.zara.net/photos///2024/V/0/2/p/2201/520/040/2/w/750/2201520040_1_1_1.jpg"),
                ("ZS002", "Minimalist White Sneakers", Decimal("49.95"),
                 [Colour(name="White", hex="#FFFFFF")],
                 ["40", "41", "42", "43", "44", "45"],
                 "https://static.zara.net/photos///2024/V/0/2/p/2210/520/001/2/w/750/2210520001_1_1_1.jpg"),
                ("ZS003", "Suede Chelsea Boots", Decimal("69.95"),
                 [Colour(name="Tan", hex="#D2B48C"), Colour(name="Black", hex="#1A1A1A")],
                 ["40", "41", "42", "43", "44"],
                 "https://static.zara.net/photos///2024/V/0/2/p/2004/520/100/2/w/750/2004520100_1_1_1.jpg"),
                ("ZS004", "Chunky Platform Sneakers", Decimal("55.95"),
                 [Colour(name="Black/White", hex="#1A1A1A"), Colour(name="All White", hex="#FFFFFF")],
                 ["40", "41", "42", "43", "44", "45"],
                 "https://static.zara.net/photos///2024/V/0/2/p/2256/520/040/2/w/750/2256520040_1_1_1.jpg"),
            ],
        }

        products = []
        for pid, name, price, colours, sizes, img in demos.get(category, []):
            products.append(
                Product(
                    id=pid,
                    retailer="zara",
                    name=name,
                    url=f"https://www.zara.com/{self._region}/{self._lang}/product/{pid}",
                    image_url=img,
                    category=category,
                    style_tags=[style, "casual", "smart-casual"],  # demo items are versatile
                    price=price,
                    currency="EUR",
                    colours=colours,
                    sizes=sizes,
                    scraped_at=datetime.utcnow(),
                )
            )
        return products

    def _full_demo_catalogue(self, style: str) -> list[Product]:
        """Return demo products for all categories."""
        products: list[Product] = []
        for cat in [Category.TOP, Category.BOTTOM, Category.SHOES]:
            products.extend(self._demo_products(cat, style))
        return products
