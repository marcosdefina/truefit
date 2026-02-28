"""
TrueFit API — main application.

FastAPI app factory with CORS, routes, and startup events.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from adapters.zara import ZaraAdapter
from engines.outfit import generate_outfits
from models.outfit import GenerateRequest, GenerateResponse

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("truefit")

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered outfit generator — budget, style, size → coordinated outfit from a single shop.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Adapters (singleton instances)
# ---------------------------------------------------------------------------
zara = ZaraAdapter()

ADAPTERS = {
    "zara": zara,
}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}


@app.get("/shops")
async def list_shops():
    """Return available retailers."""
    return {
        "shops": [
            {"id": "zara", "name": "Zara", "available": True},
            {"id": "hm", "name": "H&M", "available": False},
            {"id": "asos", "name": "ASOS", "available": False},
        ]
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate_outfit(request: GenerateRequest):
    """
    Generate outfit(s) matching budget, style, and size constraints.

    1. Fetch catalogue from the selected shop (or all shops).
    2. Run the outfit engine to find top-scoring combinations.
    3. Return ranked outfits.
    """
    # Determine which adapters to query
    if request.shop and request.shop in ADAPTERS:
        adapters = [ADAPTERS[request.shop]]
    else:
        adapters = list(ADAPTERS.values())

    # Fetch catalogues
    all_products = []
    for adapter in adapters:
        logger.info("Fetching catalogue from %s (style=%s)", adapter.name, request.style.value)
        products = await adapter.fetch_catalogue(request.style.value)
        all_products.extend(products)
        logger.info("Got %d products from %s", len(products), adapter.name)

    if not all_products:
        return GenerateResponse(
            outfits=[],
            filters_applied={
                "budget": float(request.budget),
                "style": request.style.value,
                "size": request.size.model_dump(),
                "shop": request.shop,
                "note": "No products found in catalogue",
            },
        )

    # Generate outfits
    outfits = generate_outfits(all_products, request)

    return GenerateResponse(
        outfits=outfits,
        filters_applied={
            "budget": float(request.budget),
            "style": request.style.value,
            "size": request.size.model_dump(),
            "shop": request.shop,
            "products_in_catalogue": len(all_products),
        },
    )
