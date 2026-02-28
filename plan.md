# TrueFit — Project Plan

## Vision

An AI-powered outfit generator that takes three inputs — **budget**, **style**, and **size** — and returns a complete, coordinated outfit sourced entirely from a single shop. The system pulls real product data, harmonises colours to the user's physical characteristics (skin tone, hair colour, body shape from an uploaded photo), and presents a styled preview.

---

## Phases

### Phase 1 — Foundation (MVP)

> Goal: end-to-end flow with one retailer, text-only output.

| # | Task | Detail |
|---|------|--------|
| 1.1 | Project scaffold | FastAPI backend, React (Vite) frontend, Docker Compose |
| 1.2 | User input form | Budget slider, style selector (casual / smart-casual / formal / streetwear / minimal), size picker (XS–3XL + shoe size) |
| 1.3 | Retailer scraper — Zara | Build a scraper/adapter that pulls catalogue items (name, price, colour, image URL, sizes, category) |
| 1.4 | Outfit engine v1 | Given constraints, select a valid outfit (top + bottom + shoes + optional layer) that fits budget, available sizes, and style tag |
| 1.5 | API endpoint | `POST /generate` → returns outfit JSON |
| 1.6 | Results UI | Card layout showing each item with image, price, link to shop, and total cost |

### Phase 2 — Photo Analysis & Colour Matching

> Goal: personalise outfits to the user's appearance.

| # | Task | Detail |
|---|------|--------|
| 2.1 | Photo upload endpoint | Accept face/body photo, store temporarily (no persistence) |
| 2.2 | Physical feature extraction | Use a vision model (or MediaPipe + colour sampling) to extract: skin tone (hex), hair colour, estimated body shape |
| 2.3 | Colour harmony engine | Map extracted tones to a seasonal colour palette (warm/cool, muted/bright). Score each product colour against the palette |
| 2.4 | Outfit engine v2 | Integrate colour scores into outfit ranking — prefer items that complement the user's palette |
| 2.5 | Virtual colour swap | For items available in multiple shades, surface the best-matching colourway automatically |

### Phase 3 — Multi-Shop & Intelligence

> Goal: support multiple retailers, smarter matching.

| # | Task | Detail |
|---|------|--------|
| 3.1 | Retailer adapter — H&M | Second scraper, same interface |
| 3.2 | Retailer adapter — ASOS | Third scraper |
| 3.3 | Shop selector UI | Let user pick preferred shop or "best match across all" |
| 3.4 | LLM style advisor | Use an LLM (OpenAI / local Ollama) to interpret free-text style descriptions ("I want something for a summer wedding in Lisbon") and map to structured filters |
| 3.5 | Outfit preview composite | Overlay selected items onto a silhouette or mannequin matched to the user's proportions |

### Phase 4 — Polish & Deploy

| # | Task | Detail |
|---|------|--------|
| 4.1 | Caching layer | Redis cache for scraped catalogues (TTL 6h) to avoid hammering retailers |
| 4.2 | Rate limiting & ethics | Respectful scraping (headers, delays, robots.txt compliance) |
| 4.3 | Auth (optional) | Save favourite outfits, wardrobe history |
| 4.4 | Mobile-responsive UI | Tailwind responsive breakpoints |
| 4.5 | Dockerised deploy | Single `docker compose up` on the mainframe, reverse-proxy via gateway |
| 4.6 | Subdomain | `truefit.stillwaters.cz` on the gateway |

---

## Open Questions

- **Legal / ToS:** Scraping retailer sites may violate terms. Investigate affiliate APIs (Zara doesn't have a public one; ASOS has an affiliate programme). Consider using aggregator APIs (ShopStyle, RapidAPI fashion endpoints) as a compliant alternative.
- **Photo privacy:** Photos should never be stored on disk. Process in-memory only and discard after response.
- **LLM hosting:** Local Ollama on the mainframe vs. OpenAI API calls? Budget and latency trade-off.
- **Colour alteration scope:** Are we recolouring product images for preview, or just selecting the best existing colourway? Recolouring is complex and may mislead.

---

## Timeline Estimate

| Phase | Effort |
|-------|--------|
| Phase 1 | 2–3 weeks |
| Phase 2 | 2 weeks |
| Phase 3 | 2–3 weeks |
| Phase 4 | 1–2 weeks |
| **Total** | **~7–10 weeks** |
