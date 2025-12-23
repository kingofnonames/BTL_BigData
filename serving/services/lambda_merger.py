import logging
from typing import Optional, List
from .elastic_search_service import ElasticsearchService
from .kafka_service import KafkaSpeedLayerService

logger = logging.getLogger(__name__)

class LambdaMerger:
    """Merge batch and speed layer data following Lambda Architecture"""
    
    def __init__(self, es_service: ElasticsearchService, kafka_service: KafkaSpeedLayerService):
        self.es = es_service
        self.kafka = kafka_service
        self.speed_enabled = es_service.speed_enabled
    
    # =============================================
    # OHLCV MERGE METHODS
    # =============================================
    
    def get_latest_price(self, symbol: str) -> Optional[dict]:
        """
        Get latest price with lambda merge
        Priority: Speed layer (if newer) > Batch layer
        """
        # Get batch data
        batch_data = self.es.get_latest_price(symbol, source="batch")
        
        # Get speed data (if enabled)
        speed_data = None
        if self.speed_enabled:
            speed_data = self.es.get_latest_price(symbol, source="speed")
        
        # Fallback to Kafka mock (legacy support)
        if not speed_data and self.speed_enabled:
            speed_data = self.kafka.get_latest_speed_data(symbol)
        
        # Merge logic
        if not batch_data and not speed_data:
            return None
        
        if batch_data and not speed_data:
            batch_data['source'] = 'batch'
            return batch_data
        
        if speed_data and not batch_data:
            speed_data['source'] = 'speed'
            return speed_data
        
        # Both available - use speed if newer
        batch_date = batch_data.get('trade_date', '')
        speed_date = speed_data.get('trade_date', '')
        
        if speed_date >= batch_date:
            speed_data['source'] = 'merged'
            return speed_data
        else:
            batch_data['source'] = 'batch'
            return batch_data
    
    def get_historical_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple[List[dict], int]:
        """
        Get historical data from batch layer
        Speed layer not used for historical queries (batch is authoritative)
        """
        return self.es.get_historical_data(symbol, start_date, end_date, page, page_size, source="batch")
    
    def get_indicators(self, symbol: str, limit: int = 30) -> List[dict]:
        """
        Get technical indicators
        Try speed layer first if enabled, fallback to batch
        """
        if self.speed_enabled:
            speed_indicators = self.es.get_indicators(symbol, limit, source="speed")
            if speed_indicators:
                logger.info(f"Returning indicators from speed layer for {symbol}")
                for ind in speed_indicators:
                    ind['source'] = 'speed'
                return speed_indicators
        
        # Fallback to batch
        batch_indicators = self.es.get_indicators(symbol, limit, source="batch")
        for ind in batch_indicators:
            ind['source'] = 'batch'
        return batch_indicators
    
    # =============================================
    # MARKET INDEX MERGE METHODS
    # =============================================
    
    def get_latest_market_index(self, index_code: str) -> Optional[dict]:
        """
        Get latest market index with lambda merge
        Priority: Speed layer (if newer) > Batch layer
        """
        # Get batch data
        batch_data = self.es.get_latest_market_index(index_code, source="batch")
        
        # Get speed data (if enabled)
        speed_data = None
        if self.speed_enabled:
            speed_data = self.es.get_latest_market_index(index_code, source="speed")
        
        # Merge logic
        if not batch_data and not speed_data:
            return None
        
        if batch_data and not speed_data:
            batch_data['source'] = 'batch'
            return batch_data
        
        if speed_data and not batch_data:
            speed_data['source'] = 'speed'
            return speed_data
        
        # Both available - use speed if newer
        batch_date = batch_data.get('trade_date', '')
        speed_date = speed_data.get('trade_date', '')
        
        if speed_date >= batch_date:
            speed_data['source'] = 'merged'
            logger.info(f"Using speed layer data for {index_code} (newer: {speed_date} vs {batch_date})")
            return speed_data
        else:
            batch_data['source'] = 'batch'
            return batch_data
    
    def get_historical_market_data(
        self,
        index_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> tuple[List[dict], int]:
        """Get historical market data from batch layer"""
        return self.es.get_historical_market_data(
            index_code, start_date, end_date, page, page_size, source="batch"
        )
    
    def get_market_indicators(self, index_code: str, limit: int = 30) -> List[dict]:
        """
        Get market indicators with fallback
        Try speed first, then batch, handle if not available yet (MOCK)
        """
        if self.speed_enabled:
            speed_indicators = self.es.get_market_indicators(index_code, limit, source="speed")
            if speed_indicators:
                logger.info(f"Returning market indicators from speed layer for {index_code}")
                for ind in speed_indicators:
                    ind['source'] = 'speed'
                return speed_indicators
        
        # Try batch
        batch_indicators = self.es.get_market_indicators(index_code, limit, source="batch")
        if batch_indicators:
            for ind in batch_indicators:
                ind['source'] = 'batch'
            return batch_indicators
        
        # MOCK: If no indicators available yet, return empty
        logger.warning(f"No market indicators available for {index_code} - batch job may not be implemented yet")
        return []
    
    def get_multiple_market_indices(self, index_codes: List[str]) -> List[dict]:
        """
        Get multiple market indices with merge
        Priority: Speed > Batch for each index
        """
        if self.speed_enabled:
            # Try to get from speed layer first
            speed_data = self.es.get_multiple_market_indices(index_codes, source="speed")
            speed_dict = {d['index_code']: d for d in speed_data}
            
            # Get from batch for any missing
            batch_data = self.es.get_multiple_market_indices(index_codes, source="batch")
            batch_dict = {d['index_code']: d for d in batch_data}
            
            # Merge: prefer speed if available and newer
            results = []
            for idx_code in index_codes:
                speed_record = speed_dict.get(idx_code)
                batch_record = batch_dict.get(idx_code)
                
                if speed_record and batch_record:
                    # Both exist, compare dates
                    if speed_record['trade_date'] >= batch_record['trade_date']:
                        speed_record['source'] = 'merged'
                        results.append(speed_record)
                    else:
                        batch_record['source'] = 'batch'
                        results.append(batch_record)
                elif speed_record:
                    speed_record['source'] = 'speed'
                    results.append(speed_record)
                elif batch_record:
                    batch_record['source'] = 'batch'
                    results.append(batch_record)
            
            return results
        else:
            # Speed disabled, only batch
            data = self.es.get_multiple_market_indices(index_codes, source="batch")
            for d in data:
                d['source'] = 'batch'
            return data