from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Query, Request, status

from app.core.rate_limit import client_identifier, rate_limiter
from app.services.metal_service import get_metal_history, get_metal_quote


router = APIRouter(
    prefix="/api/v1/metals",
    tags=["Metals"],
)

_supported_symbols = {"PT", "PD", "RH"}
_supported_currencies = {"INR", "USD"}


def _validate_market_request(request: Request, symbol: str, currency: str) -> tuple[str, str]:
    normalized_symbol = symbol.upper().strip()
    normalized_currency = currency.upper().strip()
    if normalized_symbol not in _supported_symbols:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported metal symbol.",
        )
    if normalized_currency not in _supported_currencies:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unsupported currency.",
        )
    rate_limiter.check(
        key=f"market:{client_identifier(request)}",
        limit=120,
        window_seconds=60,
    )
    return normalized_symbol, normalized_currency


@router.get("/history")
async def metal_history(
    request: Request,
    symbol: str = Query(...),
    currency: str = Query("USD"),
    days: int = Query(30, ge=1, le=365),
):
    symbol, currency = _validate_market_request(request, symbol, currency)
    end_time = int(
        datetime.now(timezone.utc).timestamp()
    )

    start_time = int(
        (
            datetime.now(timezone.utc)
            - timedelta(days=days)
        ).timestamp()
    )

    data = await get_metal_history(
        symbol=symbol,
        currency=currency,
        start_time=start_time,
        end_time=end_time,
        limit=days,
    )

    return data

@router.get("/quote")
async def metal_quote(
    request: Request,
    symbol: str = Query(...),
    currency: str = Query("INR"),
):
    symbol, currency = _validate_market_request(request, symbol, currency)
    data = await get_metal_quote(
        symbol=symbol,
        currency=currency,
    )

    return data
