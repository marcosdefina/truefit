# TrueFit

> AI-powered outfit generator — budget, style, size → complete coordinated outfit from a single shop, colour-matched to your appearance.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React + Vite)                  │
│                                                                 │
│  ┌──────────┐  ┌──────────────┐  ┌───────────┐  ┌───────────┐  │
│  │  Input    │  │  Photo       │  │  Outfit   │  │  Shop     │  │
│  │  Form     │  │  Upload      │  │  Results  │  │  Links    │  │
│  │          │  │              │  │           │  │           │  │
│  │ • Budget  │  │ • Webcam /   │  │ • Cards   │  │ • Direct  │  │
│  │ • Style   │  │   file drop  │  │ • Prices  │  │   buy URL │  │
│  │ • Size    │  │ • Preview    │  │ • Colours │  │ • Total   │  │
│  └──────────┘  └──────────────┘  └───────────┘  └───────────┘  │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │  HTTP / WebSocket
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                     API GATEWAY (FastAPI)                        │
│                                                                 │
│  POST /generate      — generate outfit from criteria            │
│  POST /upload-photo  — extract physical characteristics         │
│  GET  /shops         — list available retailers                 │
│  GET  /health        — healthcheck                              │
│                                                                 │
└──────┬──────────┬──────────────┬──────────────┬─────────────────┘
       │          │              │              │
       ▼          ▼              ▼              ▼
┌──────────┐ ┌──────────┐ ┌───────────┐ ┌──────────────┐
│  Outfit  │ │  Colour  │ │  Photo    │ │  Retailer    │
│  Engine  │ │  Engine  │ │  Analyser │ │  Adapters    │
└──────────┘ └──────────┘ └───────────┘ └──────────────┘
```

---

## System Components

### 1. Frontend — React + Vite + Tailwind

Single-page app. Three-step flow:

1. **Configure** — user sets budget (€ slider), picks style preset, enters size (top / bottom / shoes).
2. **Upload (optional)** — user uploads or captures a photo. A silhouette overlay guides framing.
3. **Results** — outfit displayed as item cards with images, individual prices, total, colour swatches, and direct links to the shop.

No auth required for the MVP. State lives in React context; no backend sessions.

### 2. API Gateway — FastAPI (Python)

Thin orchestration layer. Receives the request, delegates to engines, returns structured JSON.

```
Request body (POST /generate):
{
  "budget":  120,               // max € total
  "style":   "smart-casual",   // enum
  "size": {
    "top":    "M",
    "bottom": "32",
    "shoes":  "43"
  },
  "shop":    "zara",            // optional — null = best across all
  "photo_features": {           // optional — output from /upload-photo
    "skin_tone":  "#C68642",
    "hair_colour": "#3B2F2F",
    "body_shape":  "rectangle",
    "season":      "autumn"
  }
}
```

```
Response:
{
  "outfit": {
    "shop":  "Zara",
    "total": 109.85,
    "items": [
      {
        "category": "top",
        "name":     "Textured Knit Polo",
        "price":    35.95,
        "colour":   "#4A5A3C",
        "size":     "M",
        "image":    "https://...",
        "url":      "https://zara.com/..."
      },
      ...
    ]
  },
  "colour_analysis": {
    "palette": "warm autumn",
    "recommended_colours": ["#4A5A3C", "#8B4513", "#C19A6B"],
    "avoid_colours": ["#FF69B4", "#00CED1"]
  }
}
```

### 3. Outfit Engine

The core algorithm. Responsibilities:

1. **Filter** — from the scraped catalogue, discard items that don't match size or exceed budget.
2. **Categorise** — group remaining items into slots: `top`, `bottom`, `shoes`, `outerwear` (optional), `accessory` (optional).
3. **Combine** — generate candidate outfits (one item per required slot) whose total ≤ budget.
4. **Score** — rank candidates by:
   - **Style match** — how well tags align with the chosen style.
   - **Colour harmony** — internal colour coherence (complementary / analogous palettes).
   - **Personal colour match** — if photo features are provided, prefer colours that score well against the user's season.
   - **Budget utilisation** — slight preference for using more of the budget (better value) without exceeding it.
5. **Return top 3** — let the user swipe between alternatives.

Scoring weights (configurable):

| Factor | Weight |
|--------|--------|
| Style match | 0.35 |
| Colour harmony | 0.25 |
| Personal colour | 0.25 |
| Budget utilisation | 0.15 |

### 4. Colour Engine

Handles all colour logic:

- **Seasonal palette mapping** — given skin tone + hair colour, classify into one of 12 seasonal sub-types (e.g., warm autumn, cool summer).
- **Product colour scoring** — compare a garment's colour (hex from scrape) against the user's recommended palette using Delta-E (CIEDE2000) in CIELAB space.
- **Outfit internal harmony** — ensure the items in a single outfit don't clash, using colour wheel relationships.
- **Colourway selection** — when a product has multiple colourways, pick the one that scores highest.

### 5. Photo Analyser

Processes the uploaded image (in-memory, never saved to disk):

| Step | Method | Output |
|------|--------|--------|
| Face detection | MediaPipe Face Mesh | Bounding box, landmarks |
| Skin tone extraction | Sample forehead + cheek pixels, median in LAB space | Hex colour |
| Hair colour extraction | Sample region above forehead landmarks | Hex colour |
| Body shape estimation | Pose landmarks → shoulder-to-hip ratio | Enum: rectangle, triangle, inverted-triangle, hourglass, oval |
| Season classification | Rules engine on skin undertone (warm/cool) + contrast level | e.g., "warm autumn" |

**Privacy:** The image is loaded into memory, processed, and immediately discarded. No file is written. The response contains only the extracted features (hex codes, enums), never the image data.

### 6. Retailer Adapters

Each adapter implements a common interface:

```python
class RetailerAdapter(Protocol):
    name: str

    async def fetch_catalogue(self, style: str) -> list[Product]:
        """Scrape or query the retailer's catalogue for the given style."""
        ...

    async def get_product_detail(self, product_id: str) -> ProductDetail:
        """Fetch full detail including all colourways and sizes."""
        ...
```

**Planned adapters:**

| Retailer | Method | Notes |
|----------|--------|-------|
| Zara | Web scraping (httpx + selectolax) | No public API; respect rate limits |
| H&M | Web scraping | Has some undocumented JSON endpoints |
| ASOS | Affiliate API | Official partner programme |
| *(future)* | ShopStyle Collective API | Aggregator, covers many brands |

**Caching:** Redis (TTL 6 hours) stores scraped catalogues to avoid repeated hits. Cache key: `{shop}:{style}:{date}`.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, Vite, Tailwind CSS, Zustand (state) |
| Backend | Python 3.12, FastAPI, Pydantic v2, uvicorn |
| Scraping | httpx, selectolax (CSS parsing), Playwright (JS-rendered pages) |
| Colour science | `colormath` (CIEDE2000), `colorsys` (stdlib) |
| Photo analysis | MediaPipe (face mesh + pose), Pillow, NumPy |
| LLM (Phase 3) | Ollama (local, mistral/llama3) or OpenAI API |
| Cache | Redis 7 |
| Database | SQLite (favourites, history — Phase 4 only) |
| Containerisation | Docker, Docker Compose |
| Reverse proxy | Nginx on gateway Pi (existing infra) |

---

## Data Model

```
Product
├── id:           str           (retailer-specific)
├── retailer:     str           ("zara", "hm", "asos")
├── name:         str
├── url:          str
├── image_url:    str
├── category:     enum          (top, bottom, shoes, outerwear, accessory)
├── style_tags:   list[str]     (["casual", "smart-casual"])
├── price:        Decimal
├── currency:     str           ("EUR")
├── colours:      list[Colour]  (available colourways)
├── sizes:        list[str]     (available sizes)
└── scraped_at:   datetime

Colour
├── name:    str    ("Olive Green")
├── hex:     str    ("#4A5A3C")
└── swatch:  str    (image URL, optional)

Outfit
├── items:   list[Product]
├── total:   Decimal
├── score:   float
└── breakdown: dict  (per-factor scores)

UserProfile (in-memory, not persisted)
├── skin_tone:   str (hex)
├── hair_colour: str (hex)
├── body_shape:  str (enum)
└── season:      str ("warm autumn", etc.)
```

---

## Directory Structure

```
truefit/
├── plan.md                     ← phased roadmap
├── README.md                   ← this file (architecture)
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.web
│
├── api/                        ← FastAPI backend
│   ├── main.py                 (app factory, routes)
│   ├── config.py               (settings via pydantic-settings)
│   ├── requirements.txt
│   │
│   ├── engines/
│   │   ├── outfit.py           (outfit generation + scoring)
│   │   └── colour.py           (colour harmony, season mapping)
│   │
│   ├── analysers/
│   │   └── photo.py            (MediaPipe face/pose analysis)
│   │
│   ├── adapters/
│   │   ├── base.py             (Protocol + Product model)
│   │   ├── zara.py
│   │   ├── hm.py
│   │   └── asos.py
│   │
│   └── models/
│       ├── product.py          (Product, Colour pydantic models)
│       ├── outfit.py           (Outfit response model)
│       └── profile.py          (UserProfile model)
│
├── web/                        ← React frontend
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── App.tsx
│       ├── pages/
│       │   ├── Configure.tsx
│       │   ├── Upload.tsx
│       │   └── Results.tsx
│       ├── components/
│       │   ├── BudgetSlider.tsx
│       │   ├── StylePicker.tsx
│       │   ├── SizePicker.tsx
│       │   ├── PhotoCapture.tsx
│       │   ├── OutfitCard.tsx
│       │   └── ColourSwatch.tsx
│       ├── hooks/
│       │   └── useGenerate.ts
│       └── store/
│           └── useStore.ts
│
├── deploy.sh                   ← SCP + SSH deploy to mainframe
├── orchestrate.sh              ← local management wrapper
├── tf-start.sh
├── tf-down.sh
└── tf-logs.sh
```

---

## Deployment

Follows the same pattern as other homelab services:

| Aspect | Detail |
|--------|--------|
| Host | Mainframe (`192.168.0.245`) |
| Port | `8100` (API), `8101` (web dev — prod served by API) |
| Subdomain | `truefit.stillwaters.cz` |
| Gateway | Nginx reverse proxy on Pi, TLS via Certbot |
| Deploy | `deploy.sh` → SCP files → SSH docker compose up |

Docker Compose runs:
- `truefit-api` — FastAPI (port 8100)
- `truefit-web` — Nginx serving built React assets, proxying `/api` to the API container
- `truefit-redis` — Redis for catalogue caching

---

## Key Design Decisions

### Why single-shop constraint?
Shipping from one shop is cheaper and arrives together. It also simplifies colour consistency since retailers photograph items under similar lighting.

### Why not use fashion APIs directly?
Most major retailers (Zara, H&M) don't offer public product APIs. Affiliate APIs (ASOS, ShopStyle) exist but have limited coverage. We start with scraping and migrate to APIs where available.

### Why seasonal colour analysis?
It's the most established system for matching clothing colours to personal colouring. The 12-season model provides enough granularity without overwhelming the user.

### Why process photos in-memory only?
Trust. Users uploading selfies need confidence the data isn't stored. Processing in-memory and returning only derived features (hex codes, enums) is the minimal-data approach.

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Retailer blocks scraping | No catalogue data | Rotate user agents, add delays, fall back to cached data, explore affiliate APIs |
| Site structure changes | Broken scraper | Adapter pattern isolates breakage; add scraper health checks |
| Colour extraction inaccurate | Poor recommendations | Calibrate against known colour swatches; let user manually adjust season |
| Budget too low for full outfit | Empty results | Return partial outfits with explanation; suggest increasing budget |
| Photo analysis fails (lighting, angle) | No personalisation | Graceful fallback to generic colour-neutral outfit |
