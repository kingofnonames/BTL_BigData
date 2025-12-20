from vnstock import Vnstock

class FundamentalCrawler:
    def __init__(self, symbol):
        self.symbol = symbol
        self.stock = Vnstock().stock(symbol=symbol, source="VCI")

    def crawl(self):
        profile = self.stock.company.overview()
        if profile is None:
            return []

        records = profile.to_dict(orient="records")
        for r in records:
            r["symbol"] = self.symbol
            r["type"] = "fundamental"
        return records