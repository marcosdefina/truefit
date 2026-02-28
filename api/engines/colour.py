"""
Colour engine — colour harmony scoring for outfits.

Phase 1: basic colour-wheel harmony (complementary, analogous, neutral).
Phase 2 will add seasonal palette mapping and Delta-E scoring.
"""

import colorsys
import math


def hex_to_hsl(hex_colour: str) -> tuple[float, float, float]:
    """Convert #RRGGBB to (hue 0-360, saturation 0-1, lightness 0-1)."""
    hex_colour = hex_colour.lstrip("#")
    r, g, b = (int(hex_colour[i : i + 2], 16) / 255.0 for i in (0, 2, 4))
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, s, l


def is_neutral(hex_colour: str) -> bool:
    """Check if a colour is neutral (black, white, grey, navy, beige-ish)."""
    _, saturation, lightness = hex_to_hsl(hex_colour)
    # Very low saturation = grey/black/white
    if saturation < 0.15:
        return True
    # Very dark or very light with low-ish saturation
    if (lightness < 0.15 or lightness > 0.85) and saturation < 0.3:
        return True
    return False


def hue_distance(hex_a: str, hex_b: str) -> float:
    """Angular distance between two hues on the colour wheel (0-180)."""
    h_a, _, _ = hex_to_hsl(hex_a)
    h_b, _, _ = hex_to_hsl(hex_b)
    diff = abs(h_a - h_b)
    return min(diff, 360 - diff)


def colour_harmony_score(colours: list[str]) -> float:
    """
    Score the internal colour harmony of a set of hex colours (0.0 – 1.0).

    Scoring rules:
    - Neutrals pair well with everything → bonus.
    - Analogous colours (hue distance < 40°) → good harmony.
    - Complementary colours (hue distance 150-180°) → good contrast.
    - Clashing mid-range (hue distance 60-130°) → penalty.
    """
    if len(colours) < 2:
        return 1.0

    # Filter out empty/None
    colours = [c for c in colours if c]
    if len(colours) < 2:
        return 1.0

    neutrals = [c for c in colours if is_neutral(c)]
    chromatic = [c for c in colours if not is_neutral(c)]

    # All neutrals = safe, harmonious
    if not chromatic:
        return 0.9

    # Score each pair of chromatic colours
    pair_scores: list[float] = []
    for i in range(len(chromatic)):
        for j in range(i + 1, len(chromatic)):
            dist = hue_distance(chromatic[i], chromatic[j])
            if dist < 40:
                # Analogous — harmonious
                pair_scores.append(0.85 + (40 - dist) / 40 * 0.15)
            elif dist >= 150:
                # Complementary — bold but works
                pair_scores.append(0.75)
            elif dist < 60:
                # Close but not analogous — okay
                pair_scores.append(0.65)
            else:
                # Clashing zone
                pair_scores.append(0.3)

    base_score = sum(pair_scores) / len(pair_scores) if pair_scores else 0.7

    # Bonus for having neutrals to anchor the outfit
    neutral_bonus = min(len(neutrals) * 0.05, 0.1)

    return min(base_score + neutral_bonus, 1.0)
