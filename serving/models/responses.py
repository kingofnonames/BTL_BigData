from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .schemas import OHLCVRecord, TechnicalIndicators, MarketIndexRecord, MarketIndicators

class LatestPriceResponse(BaseModel):
    """Response for latest price query"""
    symbol: str
    latest_data: OHLCVRecord
    change: Optional[float] = None
    change_percent: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class HistoricalDataResponse(BaseModel):
    """Response for historical data query"""
    symbol: str
    interval: str
    data: List[OHLCVRecord]
    total_records: int
    page: int
    page_size: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class IndicatorsResponse(BaseModel):
    """Response for indicators query"""
    symbol: str
    data: List[TechnicalIndicators]
    total_records: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    elasticsearch: bool
    redis: bool
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# ============= MARKET RESPONSES =============

class LatestMarketResponse(BaseModel):
    """Response for latest market index query"""
    index_code: str
    latest_data: MarketIndexRecord
    change: Optional[float] = None
    change_percent: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class HistoricalMarketResponse(BaseModel):
    """Response for historical market data query"""
    index_code: str
    data: List[MarketIndexRecord]
    total_records: int
    page: int
    page_size: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class MarketIndicatorsResponse(BaseModel):
    """Response for market indicators query"""
    index_code: str
    data: List[MarketIndicators]
    total_records: int
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class MarketCompareResponse(BaseModel):
    """Response for comparing multiple market indices"""
    indices: List[str]
    data: List[MarketIndexRecord]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())