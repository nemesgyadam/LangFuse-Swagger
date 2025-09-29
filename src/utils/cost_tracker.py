"""
Cost tracking utilities for OpenRouter + Langfuse.
Estimates token usage and fetches dynamic pricing from OpenRouter to compute costs.
"""

from __future__ import annotations

import logging
import os
import json
from datetime import datetime
from typing import Dict, Optional, Any, List

try:
    import tiktoken  # type: ignore
except Exception:  # pragma: no cover
    tiktoken = None

import requests  # type: ignore


def _get_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


logger = _get_logger()

PRICE_CACHE_FILE = "openrouter_prices.json"
PRICE_REFRESH_HOURS = 24


def _load_price_cache() -> Dict[str, Any]:
    try:
        if os.path.exists(PRICE_CACHE_FILE):
            with open(PRICE_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"Error loading price cache: {e}")
    return {}


def _save_price_cache(cache_data: Dict[str, Any]) -> None:
    try:
        with open(PRICE_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Price cache saved to {PRICE_CACHE_FILE}")
    except Exception as e:
        logger.error(f"Error saving price cache: {e}")


def fetch_openrouter_pricing(model_name: str) -> Optional[Dict[str, Any]]:
    """Fetch dynamic pricing for a specific model from OpenRouter.

    Returns per-million token pricing dict with keys: prompt_cost, completion_cost.
    """
    now = datetime.now()
    cache = _load_price_cache()
    cached = cache.get("models", {}).get(model_name)
    if cached and cached.get("cached_at"):
        try:
            cached_at = datetime.fromisoformat(cached["cached_at"])
            age_h = (now - cached_at).total_seconds() / 3600
            if age_h < PRICE_REFRESH_HOURS:
                logger.info(
                    f"Using cached pricing for {model_name} (age {age_h:.1f}h, refresh {PRICE_REFRESH_HOURS}h)"
                )
                return cached
        except Exception:
            pass

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        logger.warning("OPENROUTER_API_KEY not set; cannot fetch pricing")
        return None

    try:
        resp = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=10,
        )
        if resp.status_code != 200:
            logger.error(f"OpenRouter pricing error: {resp.status_code} - {resp.text}")
            return None
        data = resp.json().get("data", [])
        for item in data:
            model_id = item.get("id", "")
            if model_id == model_name or model_name in model_id or model_id.endswith(model_name):
                pricing = item.get("pricing", {})
                if "prompt" in pricing and "completion" in pricing:
                    result = {
                        "prompt_cost": float(pricing.get("prompt", 0)) * 1_000_000,  # per-million
                        "completion_cost": float(pricing.get("completion", 0)) * 1_000_000,
                        "model_id": model_id,
                        "cached_at": now.isoformat(),
                    }
                    cache.setdefault("models", {})[model_name] = result
                    _save_price_cache(cache)
                    return result
        logger.warning(f"Pricing not found for model {model_name}")
    except Exception as e:
        logger.error(f"Error fetching OpenRouter pricing: {e}")
    return None


class CostTracker:
    def __init__(self, model_name: Optional[str]):
        self.model_name = model_name or ""
        self.encoding = self._prepare_encoding(self.model_name)

    def _prepare_encoding(self, model_name: str):
        if tiktoken is None:
            return None
        try:
            if not model_name:
                return tiktoken.get_encoding("cl100k_base")
            normalized = model_name.split("/")[-1]
            return tiktoken.encoding_for_model(normalized)
        except Exception:
            return tiktoken.get_encoding("cl100k_base")

    def count_text_tokens(self, text: str) -> int:
        if not text:
            return 0
        if self.encoding is None:
            return max(1, len(text) // 4)
        try:
            return len(self.encoding.encode(text))
        except Exception:
            return max(1, len(text) // 4)

    def count_messages_tokens(self, messages: List[Any]) -> int:
        total = 0
        for m in messages:
            if hasattr(m, "content"):
                total += self.count_text_tokens(str(m.content))
            elif isinstance(m, (tuple, list)) and len(m) >= 2:
                total += self.count_text_tokens(str(m[1]))
            elif isinstance(m, str):
                total += self.count_text_tokens(m)
        return total

    def compute_usage_and_cost(self, input_messages: List[Any], output_text: str) -> Dict[str, Any]:
        input_tokens = self.count_messages_tokens(input_messages)
        output_tokens = self.count_text_tokens(output_text)
        usage = {
            "input": input_tokens,
            "output": output_tokens,
            "total": input_tokens + output_tokens,
            "unit": "TOKENS",
        }

        pricing = fetch_openrouter_pricing(self.model_name) if self.model_name else None
        if pricing:
            in_cost = (input_tokens / 1_000_000) * pricing["prompt_cost"]
            out_cost = (output_tokens / 1_000_000) * pricing["completion_cost"]
            usage.update(
                {
                    "input_cost": round(in_cost, 6),
                    "output_cost": round(out_cost, 6),
                    "total_cost": round(in_cost + out_cost, 6),
                    "pricing_source": "openrouter_api",
                }
            )
        else:
            usage.update(
                {
                    "input_cost": 0.0,
                    "output_cost": 0.0,
                    "total_cost": 0.0,
                    "pricing_source": "no_pricing_available",
                }
            )
        return usage


