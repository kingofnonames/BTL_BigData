import logging
import os
from typing import Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class KafkaSpeedLayerService:
    """
    Speed layer service - Currently MOCK
    To enable: Set ENABLE_SPEED_LAYER=true and uncomment real code
    """
    
    def __init__(self):
        self.enabled = os.getenv("ENABLE_SPEED_LAYER", "false").lower() == "true"
        self.latest_data = {}
        
        if self.enabled:
            logger.info("Speed layer ENABLED (mock mode)")
        else:
            logger.info("Speed layer DISABLED")
    
    def get_latest_speed_data(self, symbol: str) -> Optional[dict]:
        """Get latest data from speed layer"""
        if not self.enabled:
            return None
        
        # MOCK: Generate fake real-time data
        today = datetime.now().strftime("%Y-%m-%d")
        base = 100000 + random.randint(-5000, 5000)
        
        return {
            "symbol": symbol,
            "trade_date": today,
            "interval": "1D",
            "open": base,
            "high": base + random.randint(100, 2000),
            "low": base - random.randint(100, 2000),
            "close": base + random.randint(-1000, 1000),
            "volume": random.randint(100000, 5000000),
            "source": "speed"
        }
    
    def health_check(self) -> bool:
        return True  # Always healthy in mock mode