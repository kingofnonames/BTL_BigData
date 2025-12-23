from fastapi import APIRouter, HTTPException, Query, Depends
from models.schemas import TechnicalIndicators, DataSourceEnum
from models.responses import IndicatorsResponse
from api.dependencies import get_redis_service, get_lambda_merger

router = APIRouter(prefix="/indicators", tags=["Indicators"])

@router.get("/{symbol}", response_model=IndicatorsResponse)
async def get_indicators(
    symbol: str,
    limit: int = Query(30, ge=1, le=365),
    use_cache: bool = Query(True),
    redis=Depends(get_redis_service),
    merger=Depends(get_lambda_merger)
):
    symbol = symbol.upper()
    
    # Check cache
    if use_cache:
        cached = redis.get_indicators(symbol)
        if cached:
            return IndicatorsResponse(**cached)
    
    # Get from merger
    indicators = merger.get_indicators(symbol, limit)
    
    if not indicators:
        raise HTTPException(status_code=404, detail=f"No indicators for {symbol}")
    
    # Parse to models
    parsed = [
        TechnicalIndicators(
            symbol=ind['symbol'],
            trade_date=ind['trade_date'],
            open=float(ind['open']),
            high=float(ind['high']),
            low=float(ind['low']),
            close=float(ind['close']),
            volume=float(ind['volume']),
            vwap=ind.get('vwap'),
            ma7=ind.get('ma7'),
            ma30=ind.get('ma30'),
            bollinger_upper=ind.get('bollinger_upper'),
            bollinger_lower=ind.get('bollinger_lower'),
            rsi14=ind.get('rsi14'),
            daily_return=ind.get('daily_return'),
            cumulative_return=ind.get('cumulative_return'),
            source=DataSourceEnum.BATCH
        )
        for ind in indicators
    ]
    
    response = IndicatorsResponse(
        symbol=symbol,
        data=parsed,
        total_records=len(parsed)
    )
    
    # Cache it
    if use_cache:
        redis.cache_indicators(symbol, response.dict())
    
    return response

@router.get("/{symbol}/latest")
async def get_latest_indicator(
    symbol: str,
    merger=Depends(get_lambda_merger)
):
    symbol = symbol.upper()
    indicators = merger.get_indicators(symbol, limit=1)
    
    if not indicators:
        raise HTTPException(status_code=404, detail=f"No indicators for {symbol}")
    
    ind = indicators[0]
    return TechnicalIndicators(
        symbol=ind['symbol'],
        trade_date=ind['trade_date'],
        open=float(ind['open']),
        high=float(ind['high']),
        low=float(ind['low']),
        close=float(ind['close']),
        volume=float(ind['volume']),
        vwap=ind.get('vwap'),
        ma7=ind.get('ma7'),
        ma30=ind.get('ma30'),
        bollinger_upper=ind.get('bollinger_upper'),
        bollinger_lower=ind.get('bollinger_lower'),
        rsi14=ind.get('rsi14'),
        daily_return=ind.get('daily_return'),
        cumulative_return=ind.get('cumulative_return'),
        source=DataSourceEnum.BATCH
    )

@router.get("/{symbol}/rsi")
async def get_rsi(
    symbol: str,
    days: int = Query(30, ge=1, le=365),
    merger=Depends(get_lambda_merger)
):
    symbol = symbol.upper()
    indicators = merger.get_indicators(symbol, limit=days)
    
    if not indicators:
        raise HTTPException(status_code=404, detail=f"No RSI data for {symbol}")
    
    rsi_data = [
        {
            "date": ind['trade_date'],
            "rsi": ind.get('rsi14'),
            "close": ind['close']
        }
        for ind in indicators
        if ind.get('rsi14') is not None
    ]
    
    return {
        "symbol": symbol,
        "data": rsi_data,
        "latest_rsi": rsi_data[0]["rsi"] if rsi_data else None
    }