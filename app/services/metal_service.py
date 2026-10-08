import asyncio
import logging
import os
import time

import httpx
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file


METAL_API_URL = os.getenv(
    "METAL_API_URL",
    "https://metal-sentinel.p.rapidapi.com"
)

METAL_API_KEY = os.getenv("METAL_API_KEY")
METAL_API_HOST = os.getenv(
    "METAL_API_HOST",
    "metal-sentinel.p.rapidapi.com"
)

logger = logging.getLogger(__name__)

# RapidAPI can be slow when its connection is cold. A small cache makes the
# dashboard resilient to those upstream delays without changing the API
# contract exposed to the Flutter app.
_QUOTE_CACHE_TTL_SECONDS = 60
_HISTORY_CACHE_TTL_SECONDS = 300
_UPSTREAM_TIMEOUT = httpx.Timeout(30.0, connect=10.0)
_quote_cache: dict[tuple[str, str], tuple[float, dict]] = {}
_history_cache: dict[tuple[str, str, int], tuple[float, dict]] = {}
_quote_locks: dict[tuple[str, str], asyncio.Lock] = {}
_history_locks: dict[tuple[str, str, int], asyncio.Lock] = {}


def _cached_value(cache: dict, key: tuple, ttl_seconds: int):
    item = cache.get(key)
    if item is None:
        return None

    cached_at, value = item
    if time.monotonic() - cached_at >= ttl_seconds:
        cache.pop(key, None)
        return None

    # Return a copy so a route consumer cannot mutate the cached response.
    return value.copy()


async def _get_upstream_json(url: str, headers: dict, params: dict) -> dict:
    async with httpx.AsyncClient(timeout=_UPSTREAM_TIMEOUT) as client:
        response = await client.get(url, headers=headers, params=params)

    response.raise_for_status()
    return response.json()


async def get_metal_history(
    symbol: str,
    currency: str,
    start_time: int,
    end_time: int,
    limit: int = 30,
):
    # The route calculates the range with the current second. Use stable cache
    # identity so repeated dashboard refreshes during the TTL actually reuse
    # the same historical series.
    cache_key = (symbol.upper(), currency.upper(), limit)
    cached = _cached_value(
        _history_cache,
        cache_key,
        _HISTORY_CACHE_TTL_SECONDS,
    )
    if cached is not None:
        return cached

    lock = _history_locks.setdefault(cache_key, asyncio.Lock())
    async with lock:
        cached = _cached_value(
            _history_cache,
            cache_key,
            _HISTORY_CACHE_TTL_SECONDS,
        )
        if cached is not None:
            return cached

        data = await _fetch_metal_history(
            symbol=symbol,
            currency=currency,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
        )
        _history_cache[cache_key] = (time.monotonic(), data)
        return data


async def _fetch_metal_history(
    symbol: str,
    currency: str,
    start_time: int,
    end_time: int,
    limit: int,
):
    url = f"{METAL_API_URL}/metal-history"

    headers = {
        "X-RapidAPI-Key": METAL_API_KEY,
        "X-RapidAPI-Host": METAL_API_HOST,
    }

    params = {
        "symbol": symbol,
        "currency": currency,
        "startTime": start_time,
        "endTime": end_time,
        "limit": limit,
    }

    raw_data = await _get_upstream_json(url, headers, params)

    results = raw_data.get("results", [])

    results = list(reversed(results))

    data = []

    for item in results:
        data.append({
            "timestamp": item.get("timestamp"),
            "price": item.get("ask"),
        })

    return {
        "symbol": symbol,
        "currency": currency,
        "data": data,
    }

async def get_metal_quote(symbol: str, currency: str):
    cache_key = (symbol.upper(), currency.upper())
    cached = _cached_value(_quote_cache, cache_key, _QUOTE_CACHE_TTL_SECONDS)
    if cached is not None:
        return cached

    lock = _quote_locks.setdefault(cache_key, asyncio.Lock())
    async with lock:
        cached = _cached_value(_quote_cache, cache_key, _QUOTE_CACHE_TTL_SECONDS)
        if cached is not None:
            return cached

        data = await _fetch_metal_quote(symbol=symbol, currency=currency)
        _quote_cache[cache_key] = (time.monotonic(), data)
        return data


async def _fetch_metal_quote(symbol: str, currency: str):
    url = f"{METAL_API_URL}/metal-quote"

    headers = {
        "X-RapidAPI-Key": METAL_API_KEY,
        "X-RapidAPI-Host": METAL_API_HOST,
    }

    params = {
        "symbol": symbol,
        "currency": currency,
    }

    raw_data = await _get_upstream_json(url, headers, params)

    results = raw_data.get("results", [])

    if not results:
        raise ValueError(
            f"No price data returned for {symbol}"
        )

    result = results[0]

    quote = {
        "symbol": result.get("symbol"),
        "currency": result.get("currency"),
        "price": result.get("ask"),
        "bid": result.get("bid"),
        "high": result.get("high"),
        "low": result.get("low"),
        "change": result.get("change"),
        "changePercentage": result.get("changePercentage"),
        "timestamp": result.get("timestamp"),
        "unit": result.get("unit"),
    }
    logger.debug("Loaded live %s price in %s", symbol, currency)
    return quote
