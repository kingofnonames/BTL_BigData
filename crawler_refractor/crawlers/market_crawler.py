from vnstock import Vnstock
from datetime import datetime, timedelta


class MarkerCrawler:
    def __init__(self):
        self.vnstock = Vnstock()

    def crawl_index(self, index_code):
        start = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        end = datetime.now().strftime("%Y-%m-%d")

        stock = self.vnstock.stock(symbol=index_code, source="VCI")
        df = stock.quote.history(start=start, end=end, interval="1D")
        if df is None:
            return []

        records = df.reset_index().to_dict(orient="records")
        for r in records:
            r["index"] = index_code
            r["type"] = "market_index"
        return records
