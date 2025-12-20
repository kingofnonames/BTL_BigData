from vnstock import Vnstock

class OHLCVCrawler:
    def __init__(self, symbol, source):
        self.symbol = symbol
        self.stock = Vnstock().stock(symbol=symbol, source=source)

    def crawl(self, start, end, interval):
        df = self.stock.quote.history(
            start=start,
            end=end,
            interval=interval
        )
        if df is None or df.empty:
            return []

        records = df.reset_index().to_dict(orient="records")
        for r in records:
            r["symbol"] = self.symbol
            r["interval"] = interval
            r["type"] = "ohlcv"
        return records