from elasticsearch import Elasticsearch
from typing import List, Optional, Tuple
import logging
import os

logger = logging.getLogger(__name__)

class ElasticsearchService:
    def __init__(self):
        self.host = os.getenv("ES_HOST", "http://elasticsearch:9200")
        
        # ===== BATCH LAYER INDEXES =====
        self.index_ohlcv = os.getenv("ES_INDEX_OHLCV", "ohlcv_daily_v2")
        self.index_analysis = os.getenv("ES_INDEX_ANALYSIS", "ohlcv_analysis")
        self.index_market = os.getenv("ES_INDEX_MARKET", "market_daily_v2")
        self.index_market_analysis = os.getenv("ES_INDEX_MARKET_ANALYSIS", "market_analysis")
        
        # ===== SPEED LAYER INDEXES =====
        self.index_ohlcv_speed = os.getenv("ES_INDEX_OHLCV_SPEED", "ohlcv_daily_v2_speed")
        self.index_analysis_speed = os.getenv("ES_INDEX_ANALYSIS_SPEED", "ohlcv_analysis_speed")
        self.index_market_speed = os.getenv("ES_INDEX_MARKET_SPEED", "market_daily_speed")
        self.index_market_analysis_speed = os.getenv("ES_INDEX_MARKET_ANALYSIS_SPEED", "market_analysis_speed")
        
        # Speed layer enable flag
        self.speed_enabled = os.getenv("ENABLE_SPEED_LAYER", "false").lower() == "true"
        
        self.client = Elasticsearch([self.host], timeout=30)
        try:
            if self.client.ping():
                logger.info(f"Connected to ES: {self.host}")
                logger.info(f"Speed Layer: {'ENABLED' if self.speed_enabled else 'DISABLED'}")
            else:
                logger.error("Cannot ping ES")
        except Exception as e:
            logger.error(f"ES connection error: {e}")
    
    # =============================================
    # OHLCV METHODS (BATCH + SPEED)
    # =============================================
    
    def get_latest_price(self, symbol: str, source: str = "batch") -> Optional[dict]:
        """Get latest OHLCV for symbol from batch or speed layer"""
        try:
            index = self.index_ohlcv if source == "batch" else self.index_ohlcv_speed
            
            query = {
                "query": {"term": {"symbol.keyword": symbol}},
                "sort": [{"trade_date": {"order": "desc"}}],
                "size": 1
            }
            
            response = self.client.search(index=index, body=query)
            
            if response['hits']['hits']:
                return response['hits']['hits'][0]['_source']
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest price for {symbol} from {source}: {e}")
            return None
    
    def get_historical_data(
        self, 
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        source: str = "batch"
    ) -> Tuple[List[dict], int]:
        """Get historical OHLCV data"""
        try:
            index = self.index_ohlcv if source == "batch" else self.index_ohlcv_speed
            
            must_conditions = [{"term": {"symbol.keyword": symbol}}]
            
            if start_date or end_date:
                date_range = {}
                if start_date:
                    date_range["gte"] = start_date
                if end_date:
                    date_range["lte"] = end_date
                must_conditions.append({"range": {"trade_date": date_range}})
            
            query = {
                "query": {"bool": {"must": must_conditions}},
                "sort": [{"trade_date": {"order": "desc"}}],
                "from": (page - 1) * page_size,
                "size": page_size
            }
            
            response = self.client.search(index=index, body=query)
            
            total = response['hits']['total']['value']
            records = [hit['_source'] for hit in response['hits']['hits']]
            
            return records, total
            
        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return [], 0
    
    def get_indicators(
        self,
        symbol: str,
        limit: int = 30,
        source: str = "batch"
    ) -> List[dict]:
        """Get technical indicators"""
        try:
            index = self.index_analysis if source == "batch" else self.index_analysis_speed
            
            query = {
                "query": {"term": {"symbol.keyword": symbol}},
                "sort": [{"trade_date": {"order": "desc"}}],
                "size": limit
            }
            
            response = self.client.search(index=index, body=query)
            return [hit['_source'] for hit in response['hits']['hits']]
            
        except Exception as e:
            logger.error(f"Error getting indicators: {e}")
            return []
    
    # =============================================
    # MARKET DATA METHODS (BATCH + SPEED)
    # =============================================
    
    def get_latest_market_index(self, index_code: str, source: str = "batch") -> Optional[dict]:
        """Get latest market index data (VNINDEX, VN30, HNX)"""
        try:
            index = self.index_market if source == "batch" else self.index_market_speed
            
            query = {
                "query": {"term": {"index_code.keyword": index_code}},
                "sort": [{"trade_date": {"order": "desc"}}],
                "size": 1
            }
            
            response = self.client.search(index=index, body=query)
            
            if response['hits']['hits']:
                return response['hits']['hits'][0]['_source']
            return None
            
        except Exception as e:
            logger.error(f"Error getting latest market index {index_code} from {source}: {e}")
            return None
    
    def get_historical_market_data(
        self,
        index_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        source: str = "batch"
    ) -> Tuple[List[dict], int]:
        """Get historical market index data"""
        try:
            index = self.index_market if source == "batch" else self.index_market_speed
            
            must_conditions = [{"term": {"index_code.keyword": index_code}}]
            
            if start_date or end_date:
                date_range = {}
                if start_date:
                    date_range["gte"] = start_date
                if end_date:
                    date_range["lte"] = end_date
                must_conditions.append({"range": {"trade_date": date_range}})
            
            query = {
                "query": {"bool": {"must": must_conditions}},
                "sort": [{"trade_date": {"order": "desc"}}],
                "from": (page - 1) * page_size,
                "size": page_size
            }
            
            response = self.client.search(index=index, body=query)
            
            total = response['hits']['total']['value']
            records = [hit['_source'] for hit in response['hits']['hits']]
            
            return records, total
            
        except Exception as e:
            logger.error(f"Error getting historical market data: {e}")
            return [], 0
    
    def get_market_indicators(
        self,
        index_code: str,
        limit: int = 30,
        source: str = "batch"
    ) -> List[dict]:
        """Get technical indicators for market indices - MOCK support"""
        try:
            index = self.index_market_analysis if source == "batch" else self.index_market_analysis_speed
            
            query = {
                "query": {"term": {"index_code.keyword": index_code}},
                "sort": [{"trade_date": {"order": "desc"}}],
                "size": limit
            }
            
            response = self.client.search(index=index, body=query)
            return [hit['_source'] for hit in response['hits']['hits']]
            
        except Exception as e:
            # MOCK: Return empty if index doesn't exist yet
            logger.warning(f"Market indicators not available yet for {index_code}: {e}")
            return []
    
    def get_multiple_market_indices(
        self,
        index_codes: List[str],
        source: str = "batch"
    ) -> List[dict]:
        """Get latest data for multiple market indices"""
        try:
            index = self.index_market if source == "batch" else self.index_market_speed
            
            query = {
                "query": {
                    "terms": {"index_code.keyword": index_codes}
                },
                "size": len(index_codes) * 10,  # Get more to ensure we get latest for each
                "sort": [{"trade_date": {"order": "desc"}}]
            }
            
            response = self.client.search(index=index, body=query)
            
            # Get only the latest for each index_code
            seen = set()
            results = []
            for hit in response['hits']['hits']:
                idx_code = hit['_source']['index_code']
                if idx_code not in seen:
                    results.append(hit['_source'])
                    seen.add(idx_code)
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting multiple market indices: {e}")
            return []
    
    # =============================================
    # UTILITY METHODS
    # =============================================
    
    def health_check(self) -> bool:
        """Check ES health"""
        try:
            return self.client.ping()
        except:
            return False