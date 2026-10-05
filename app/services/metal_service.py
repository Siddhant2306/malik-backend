import os
from dotenv import load_dotenv
import httpx

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


async def get_metal_history(
    symbol: str,
    currency: str,
    start_time: int,
    end_time: int,
    limit: int = 30,
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

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
            params=params,
            timeout=10,
        )

    response.raise_for_status()

    raw_data = response.json()

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

async def get_metal_quote(
    symbol: str,
    currency: str,
):
    url = f"{METAL_API_URL}/metal-quote"

    headers = {
        "X-RapidAPI-Key": METAL_API_KEY,
        "X-RapidAPI-Host": METAL_API_HOST,
    }

    params = {
        "symbol": symbol,
        "currency": currency,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=headers,
            params=params,
            timeout=10,
        )

    response.raise_for_status()

    raw_data = response.json()

    print("RAW METAL RESPONSE:", raw_data)

    results = raw_data.get("results", [])

    if not results:
        raise ValueError(
            f"No price data returned for {symbol}"
        )

    result = results[0]

    return {
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