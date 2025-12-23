from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

# ============= ENUMS =============

class DataSourceEnum(str, Enum):
    BATCH = "batch"
    SPEED = "speed"
    MERGED = "merged"

# ============= OHLCV MODELS =============

class OHLCVRecord(BaseModel):
    """OHLCV record from Elasticsearch"""
    symbol: str
    trade_date: str  # Keep as string to match ES format
    interval: str = "1D"
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: DataSourceEnum = DataSourceEnum.BATCH

# ============= MARKET INDEX MODELS =============

class MarketIndexRecord(BaseModel):
    """Market index record (VNINDEX, VN30, HNX, etc.)"""
    index_code: str  # VNINDEX, VN30, HNX
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: DataSourceEnum = DataSourceEnum.BATCH
    
class MarketIndicators(BaseModel):
    """Technical indicators for market indices"""
    index_code: str
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    ma7: Optional[float] = None
    ma30: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    rsi14: Optional[float] = None
    daily_return: Optional[float] = None
    cumulative_return: Optional[float] = None
    source: DataSourceEnum = DataSourceEnum.BATCH

# ============= TECHNICAL INDICATORS =============

class TechnicalIndicators(BaseModel):
    """Technical indicators from analyst job"""
    symbol: str
    trade_date: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    vwap: Optional[float] = None
    ma7: Optional[float] = None
    ma30: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    rsi14: Optional[float] = None
    daily_return: Optional[float] = None
    cumulative_return: Optional[float] = None
    source: DataSourceEnum = DataSourceEnum.BATCH

# ============= ML PREDICTIONS =============

class PredictionModel(BaseModel):
    """Single model prediction"""
    model_name: str
    predicted_close: float
    rmse: Optional[float] = None

class StockPrediction(BaseModel):
    """Price prediction response"""
    symbol: str
    prediction_date: str
    target_date: str
    current_close: float
    predictions: List[PredictionModel]