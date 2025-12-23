from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from models.schemas import MarketIndexRecord, MarketIndicators, DataSourceEnum
from models.responses import (
    LatestMarketResponse, 
    HistoricalMarketResponse,
    MarketIndicatorsResponse,
    MarketCompareResponse
)
from api.dependencies import get_redis_service, get_lambda_merger

router = APIRouter(prefix="/market", tags=["Market Indices"])

@router.get("/latest/{index_code}", response_model=LatestMarketResponse)
async def get_latest_market_index(
    index_code: str,
    use_cache: bool = Query(True),
    redis=Depends(get_redis_service),
    merger=Depends(get_lambda_merger)
):
    """
    Get latest market index data (VNINDEX, VN30, HNX)
    
    - **index_code**: Market index code (VNINDEX, VN30, HNX)
    - **use_cache**: Use Redis cache (default: True)
    """
    index_code = index_code.upper()
    
    # Check cache
    if use_cache:
        cached = redis.get_latest_market(index_code)
        if cached:
            return LatestMarketResponse(**cached)
    
    # Get from merger (lambda merge)
    data = merger.get_latest_market_index(index_code)
    
    if not data:
        raise HTTPException(
            status_code=404, 
            detail=f"No data for market index: {index_code}"
        )
    
    # Parse to model
    record = MarketIndexRecord(
        index_code=data['index_code'],
        trade_date=data['trade_date'],
        open=float(data['open']),
        high=float(data['high']),
        low=float(data['low']),
        close=float(data['close']),
        volume=float(data['volume']),
        source=DataSourceEnum(data.get('source', 'batch'))
    )
    
    response = LatestMarketResponse(
        index_code=index_code,
        latest_data=record
    )
    
    # Cache it
    if use_cache:
        redis.cache_latest_market(index_code, response.dict())
    
    return response

@router.get("/historical/{index_code}", response_model=HistoricalMarketResponse)
async def get_historical_market_data(
    index_code: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    merger=Depends(get_lambda_merger)
):
    """
    Get historical market index data
    
    - **index_code**: Market index code
    - **start_date**: Start date (YYYY-MM-DD)
    - **end_date**: End date (YYYY-MM-DD)
    - **page**: Page number
    - **page_size**: Records per page
    """
    index_code = index_code.upper()
    
    records, total = merger.get_historical_market_data(
        index_code, start_date, end_date, page, page_size
    )
    
    if not records:
        raise HTTPException(
            status_code=404, 
            detail=f"No historical data for {index_code}"
        )
    
    parsed = [
        MarketIndexRecord(
            index_code=r['index_code'],
            trade_date=r['trade_date'],
            open=float(r['open']),
            high=float(r['high']),
            low=float(r['low']),
            close=float(r['close']),
            volume=float(r['volume']),
            source=DataSourceEnum.BATCH
        )
        for r in records
    ]
    
    return HistoricalMarketResponse(
        index_code=index_code,
        data=parsed,
        total_records=total,
        page=page,
        page_size=page_size
    )

@router.get("/indicators/{index_code}", response_model=MarketIndicatorsResponse)
async def get_market_indicators(
    index_code: str,
    limit: int = Query(30, ge=1, le=365),
    use_cache: bool = Query(True),
    redis=Depends(get_redis_service),
    merger=Depends(get_lambda_merger)
):
    """
    Get technical indicators for market index
    
    **Note**: Market indicators may not be available yet if batch job is not implemented.
    Returns empty data if not available.
    
    - **index_code**: Market index code
    - **limit**: Number of records to return
    """
    index_code = index_code.upper()
    
    # Check cache
    if use_cache:
        cached = redis.get_market_indicators(index_code)
        if cached:
            return MarketIndicatorsResponse(**cached)
    
    # Get from merger
    indicators = merger.get_market_indicators(index_code, limit)
    
    if not indicators:
        # Return empty response (not an error - indicators may not be implemented yet)
        return MarketIndicatorsResponse(
            index_code=index_code,
            data=[],
            total_records=0
        )
    
    # Parse to models
    parsed = [
        MarketIndicators(
            index_code=ind['index_code'],
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
            source=DataSourceEnum(ind.get('source', 'batch'))
        )
        for ind in indicators
    ]
    
    response = MarketIndicatorsResponse(
        index_code=index_code,
        data=parsed,
        total_records=len(parsed)
    )
    
    # Cache it
    if use_cache:
        redis.cache_market_indicators(index_code, response.dict())
    
    return response

@router.get("/indicators/{index_code}/latest")
async def get_latest_market_indicator(
    index_code: str,
    merger=Depends(get_lambda_merger)
):
    """Get latest market indicator for index"""
    index_code = index_code.upper()
    indicators = merger.get_market_indicators(index_code, limit=1)
    
    if not indicators:
        return {
            "index_code": index_code,
            "message": "Market indicators not available yet (batch job may not be implemented)",
            "data": None
        }
    
    ind = indicators[0]
    return MarketIndicators(
        index_code=ind['index_code'],
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
        source=DataSourceEnum(ind.get('source', 'batch'))
    )

@router.get("/compare", response_model=MarketCompareResponse)
async def compare_market_indices(
    indices: str = Query(..., description="Comma-separated index codes (e.g. VNINDEX,VN30,HNX)"),
    use_cache: bool = Query(True),
    redis=Depends(get_redis_service),
    merger=Depends(get_lambda_merger)
):
    """
    Compare multiple market indices
    
    - **indices**: Comma-separated list (e.g. "VNINDEX,VN30,HNX")
    
    Example: `/market/compare?indices=VNINDEX,VN30,HNX`
    """
    index_list = [idx.strip().upper() for idx in indices.split(',')]
    
    if len(index_list) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 indices can be compared at once"
        )
    
    # Create cache key
    cache_key = "_".join(sorted(index_list))
    
    # Check cache
    if use_cache:
        cached = redis.get_market_compare(cache_key)
        if cached:
            return MarketCompareResponse(**cached)
    
    # Get data
    data = merger.get_multiple_market_indices(index_list)
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No data found for indices: {', '.join(index_list)}"
        )
    
    # Parse to models
    parsed = [
        MarketIndexRecord(
            index_code=d['index_code'],
            trade_date=d['trade_date'],
            open=float(d['open']),
            high=float(d['high']),
            low=float(d['low']),
            close=float(d['close']),
            volume=float(d['volume']),
            source=DataSourceEnum(d.get('source', 'batch'))
        )
        for d in data
    ]
    
    response = MarketCompareResponse(
        indices=index_list,
        data=parsed
    )
    
    # Cache it
    if use_cache:
        redis.cache_market_compare(cache_key, response.dict())
    
    return response

@router.get("/list")
async def list_available_indices():
    """List all available market indices"""
    return {
        "available_indices": [
            {
                "code": "VNINDEX",
                "name": "VN-Index",
                "description": "Ho Chi Minh Stock Exchange Index"
            },
            {
                "code": "VN30",
                "name": "VN30 Index",
                "description": "Top 30 stocks by market cap and liquidity"
            },
            {
                "code": "HNX",
                "name": "HNX-Index",
                "description": "Hanoi Stock Exchange Index"
            }
        ]
    }