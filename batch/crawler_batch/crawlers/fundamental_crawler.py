from vnstock import Vnstock
from datetime import datetime, timezone

class FundamentalCrawler:
    def __init__(self, symbol: str, source="VCI"):
        self.symbol = symbol
        self.source = source
        self.stock = Vnstock().stock(symbol=symbol, source=source)

    def crawl_profile(self):
        df = self.stock.company.overview()
        if df is None or df.empty:
            return None

        now = datetime.now(timezone.utc).isoformat()
        record = df.iloc[0].to_dict()

        return {
            "event_type": "fundamental_profile",
            "symbol": self.symbol,
            "event_time": now,
            "source": self.source,
            "data": record
        }
