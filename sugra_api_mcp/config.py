"""Configuration loading from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    api_base: str
    api_key: str
    timeout: float


def load_config() -> Config:
    api_key = os.environ.get("SUGRA_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "SUGRA_API_KEY environment variable is required. "
            "Get one free at https://app.sugra.ai/settings/billing"
        )
    return Config(
        api_base=os.environ.get("SUGRA_API_BASE", "https://sugra.ai").rstrip("/"),
        api_key=api_key,
        timeout=float(os.environ.get("SUGRA_TIMEOUT", "30")),
    )
