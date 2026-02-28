"""Pydantic models for user profile (photo analysis — Phase 2)."""

from pydantic import BaseModel


class UserProfile(BaseModel):
    skin_tone: str | None = None    # hex
    hair_colour: str | None = None  # hex
    body_shape: str | None = None   # rectangle, triangle, etc.
    season: str | None = None       # "warm autumn", etc.
