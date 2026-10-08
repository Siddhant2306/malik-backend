import asyncio
import os
import time
import httpx
from dotenv import load_dotenv

load_dotenv()


CARIMAGES_API_URL = os.getenv(
    "CARIMAGES_API_URL",
    "https://carimagesapi.com",
)

CARIMAGES_API_KEY = os.getenv("CARIMAGES_API_KEY")
CARIMAGES_API_SECRET = os.getenv("CARIMAGES_API_SECRET")

_BRAND_CACHE_TTL_SECONDS = 21600
_brand_cache: tuple[float, dict] | None = None
_brand_fetch_lock = asyncio.Lock()


async def fetch_external_brands():
    cached = _cached_brands()
    if cached is not None:
        return cached

    async with _brand_fetch_lock:
        cached = _cached_brands()
        if cached is not None:
            return cached

        response = await _fetch_external_brands()
        global _brand_cache
        _brand_cache = (time.monotonic(), response)
        return response


def _cached_brands():
    if _brand_cache is None:
        return None

    cached_at, brands = _brand_cache
    if time.monotonic() - cached_at >= _BRAND_CACHE_TTL_SECONDS:
        return None
    return brands


async def _fetch_external_brands():
    if not CARIMAGES_API_KEY:
        raise ValueError("CARIMAGES_API_KEY is not configured")

    if not CARIMAGES_API_SECRET:
        raise ValueError("CARIMAGES_API_SECRET is not configured")

    url = f"{CARIMAGES_API_URL}/api/v1/makes"

    headers = {
        "X-Api-Secret": CARIMAGES_API_SECRET,
    }

    params = {
        "api_key": CARIMAGES_API_KEY,
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(30.0, connect=10.0)) as client:
        response = await client.get(
            url,
            headers=headers,
            params=params,
        )

    response.raise_for_status()

    return response.json()
