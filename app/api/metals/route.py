from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Query

from app.services.metal_service import get_metal_history, get_metal_quote


router = APIRouter(
    prefix="/api/v1/metals",
    tags=["Metals"],
)


@router.get("/history")
async def metal_history(
    symbol: str = Query(...),
    currency: str = Query("USD"),
    days: int = Query(30, ge=1, le=365),
):
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
    symbol: str = Query(...),
    currency: str = Query("INR"),
):
    data = await get_metal_quote(
        symbol=symbol.upper(),
        currency=currency.upper(),
    )

    return data