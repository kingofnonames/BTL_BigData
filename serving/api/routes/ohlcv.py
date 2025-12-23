from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from models.schemas import OHLCVRecord, DataSourceEnum
from models.responses import LatestPriceResponse, HistoricalDataResponse
from api.dependencies import get_redis_service, get_lambda_merger

router = APIRouter(prefix="/ohlcv", tags=["OHLCV"])

@router.get("/latest/{symbol}", response_model=LatestPriceResponse)
async def get_latest_price(
    symbol: str,
    use_cache: bool = Query(True),
    redis=Depends(get_redis_service),
    merger=Depends(get_lambda_merger)
):
    symbol = symbol.upper()
    
    # Check cache
    if use_cache:
        cached = redis.get_latest_price(symbol)
        if cached:
            return LatestPriceResponse(**cached)
    
    # Get from merger
    data = merger.get_latest_price(symbol)
    
    if not data:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    
    # Parse to model
    record = OHLCVRecord(
        symbol=data['symbol'],
        trade_date=data['trade_date'],
        interval=data.get('interval', '1D'),
        open=float(data['open']),
        high=float(data['high']),
        low=float(data['low']),
        close=float(data['close']),
        volume=float(data['volume']),
        source=DataSourceEnum(data.get('source', 'batch'))
    )
    
    response = LatestPriceResponse(
        symbol=symbol,
        latest_data=record
    )
    
    # Cache it
    if use_cache:
        redis.cache_latest_price(symbol, response.dict())
    
    return response

@router.get("/historical/{symbol}", response_model=HistoricalDataResponse)
async def get_historical_data(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    merger=Depends(get_lambda_merger)
):
    symbol = symbol.upper()
    
    records, total = merger.get_historical_data(
        symbol, start_date, end_date, page, page_size
    )
    
    if not records:
        raise HTTPException(status_code=404, detail=f"No data for {symbol}")
    
    parsed = [
        OHLCVRecord(
            symbol=r['symbol'],
            trade_date=r['trade_date'],
            interval=r.get('interval', '1D'),
            open=float(r['open']),
            high=float(r['high']),
            low=float(r['low']),
            close=float(r['close']),
            volume=float(r['volume']),
            source=DataSourceEnum.BATCH
        )
        for r in records
    ]
    
    return HistoricalDataResponse(
        symbol=symbol,
        interval="1D",
        data=parsed,
        total_records=total,
        page=page,
        page_size=page_size
    )