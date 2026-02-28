"""
Outfit engine v1 — generates and scores complete outfits.

Given a catalogue of products and user constraints (budget, style, size),
produces the top N outfit combinations ranked by a weighted scoring function.
"""

import itertools
import logging
import random
from decimal import Decimal

from config import settings
from engines.colour import colour_harmony_score
from models.outfit import GenerateRequest, Outfit, OutfitItem
from models.product import Category, Product

logger = logging.getLogger(__name__)

# Required slots for a complete outfit
REQUIRED_SLOTS = [Category.TOP, Category.BOTTOM, Category.SHOES]

# Scoring weights (Phase 1 — no personal colour yet)
WEIGHTS = {
    "style_match": 0.45,
    "colour_harmony": 0.35,
    "budget_utilisation": 0.20,
}


def _matches_size(product: Product, size_input: dict[str, str]) -> bool:
    """Check if the product is available in the requested size for its category."""
    size_map = {
        Category.TOP: size_input.get("top", "M"),
        Category.BOTTOM: size_input.get("bottom", "32"),
        Category.SHOES: size_input.get("shoes", "43"),
        Category.OUTERWEAR: size_input.get("top", "M"),
        Category.ACCESSORY: "ONE SIZE",  # accessories are usually one-size
    }
    required_size = size_map.get(product.category, "M")

    if not product.sizes:
        return True  # No size info → assume available

    # Direct match or case-insensitive match
    return any(
        s.upper() == required_size.upper() or s == required_size
        for s in product.sizes
    )


def _style_match_score(product: Product, target_style: str) -> float:
    """Score how well a product's tags match the target style (0.0 – 1.0)."""
    if not product.style_tags:
        return 0.5  # Unknown tags → neutral score

    target = target_style.lower()
    tags = [t.lower() for t in product.style_tags]

    if target in tags:
        return 1.0

    # Partial credit for adjacent styles
    adjacent_map = {
        "casual": ["smart-casual", "streetwear", "minimal"],
        "smart-casual": ["casual", "formal", "minimal"],
        "formal": ["smart-casual"],
        "streetwear": ["casual"],
        "minimal": ["casual", "smart-casual"],
    }
    adjacents = adjacent_map.get(target, [])
    if any(adj in tags for adj in adjacents):
        return 0.6

    return 0.2  # Poor match


def _budget_utilisation_score(total: Decimal, budget: Decimal) -> float:
    """
    Score budget usage (0.0 – 1.0).
    Prefer using 70-95% of budget. Penalise under-utilisation.
    Over-budget returns 0 (should be filtered out, but safety net).
    """
    if total > budget:
        return 0.0
    ratio = float(total / budget)
    if ratio >= 0.70:
        return 1.0
    elif ratio >= 0.50:
        return 0.7
    elif ratio >= 0.30:
        return 0.4
    else:
        return 0.2


def generate_outfits(
    products: list[Product],
    request: GenerateRequest,
) -> list[Outfit]:
    """
    Main entry point: filter, combine, score, return top N outfits.
    """
    size_dict = request.size.model_dump()
    budget = request.budget
    style = request.style.value

    # ── Step 1: Filter by size ──
    sized = [p for p in products if _matches_size(p, size_dict)]
    logger.info("After size filter: %d / %d products", len(sized), len(products))

    # ── Step 2: Group by category ──
    by_category: dict[Category, list[Product]] = {}
    for p in sized:
        by_category.setdefault(p.category, []).append(p)

    # Check all required slots are filled
    for slot in REQUIRED_SLOTS:
        if slot not in by_category or not by_category[slot]:
            logger.warning("No products available for required slot: %s", slot.value)
            return []

    # ── Step 3: Generate candidate combinations ──
    slot_lists = [by_category[slot] for slot in REQUIRED_SLOTS]

    # If the combinatorial space is huge, sample randomly
    total_combos = 1
    for sl in slot_lists:
        total_combos *= len(sl)

    if total_combos > settings.max_outfit_candidates:
        candidates = _sampled_combinations(slot_lists, settings.max_outfit_candidates)
    else:
        candidates = list(itertools.product(*slot_lists))

    logger.info("Evaluating %d outfit candidates", len(candidates))

    # ── Step 4: Filter by budget and score ──
    scored_outfits: list[Outfit] = []

    for combo in candidates:
        total = sum(p.price for p in combo)
        if total > budget:
            continue

        # Style score (average across items)
        style_scores = [_style_match_score(p, style) for p in combo]
        avg_style = sum(style_scores) / len(style_scores)

        # Colour harmony
        item_colours = [p.primary_colour for p in combo if p.primary_colour]
        harmony = colour_harmony_score(item_colours)

        # Budget utilisation
        budget_util = _budget_utilisation_score(total, budget)

        # Weighted total
        final_score = (
            WEIGHTS["style_match"] * avg_style
            + WEIGHTS["colour_harmony"] * harmony
            + WEIGHTS["budget_utilisation"] * budget_util
        )

        items = []
        for p in combo:
            # Pick best colour (first available for Phase 1)
            colour_hex = p.primary_colour
            colour_name = p.colours[0].name if p.colours else None
            matched_size = size_dict.get(
                {
                    Category.TOP: "top",
                    Category.BOTTOM: "bottom",
                    Category.SHOES: "shoes",
                }.get(p.category, "top"),
                "M",
            )

            items.append(
                OutfitItem(
                    category=p.category.value,
                    name=p.name,
                    price=p.price,
                    colour=colour_hex,
                    colour_name=colour_name,
                    size=matched_size,
                    image=p.image_url,
                    url=p.url,
                )
            )

        scored_outfits.append(
            Outfit(
                shop="Zara",
                total=total,
                score=round(final_score, 4),
                items=items,
                score_breakdown={
                    "style_match": round(avg_style, 3),
                    "colour_harmony": round(harmony, 3),
                    "budget_utilisation": round(budget_util, 3),
                },
            )
        )

    # ── Step 5: Sort and return top N ──
    scored_outfits.sort(key=lambda o: o.score, reverse=True)

    # Deduplicate — avoid returning outfits with the same items in different order
    seen: set[frozenset[str]] = set()
    unique: list[Outfit] = []
    for outfit in scored_outfits:
        key = frozenset(item.name + item.category for item in outfit.items)
        if key not in seen:
            seen.add(key)
            unique.append(outfit)
        if len(unique) >= settings.top_n_outfits:
            break

    logger.info("Returning %d outfits (from %d scored)", len(unique), len(scored_outfits))
    return unique


def _sampled_combinations(
    slot_lists: list[list[Product]], n: int
) -> list[tuple[Product, ...]]:
    """Randomly sample N unique combinations from the cartesian product."""
    seen: set[tuple[str, ...]] = set()
    results: list[tuple[Product, ...]] = []
    attempts = 0
    max_attempts = n * 5

    while len(results) < n and attempts < max_attempts:
        combo = tuple(random.choice(sl) for sl in slot_lists)
        key = tuple(p.id for p in combo)
        if key not in seen:
            seen.add(key)
            results.append(combo)
        attempts += 1

    return results
