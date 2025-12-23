from vnstock import Vnstock
from datetime import datetime, timedelta, timezone
import pandas as pd

class OHLCVCrawler:
    def __init__(self, symbol: str, source: str = "VCI"):
        self.symbol = symbol
        self.source = source
        self.stock = None
        try:
            self.stock = Vnstock().stock(symbol=symbol, source=source)
        except ValueError as e:
            print(f"✗ Invalid symbol '{symbol}' or source '{source}': {e}")
        except Exception as e:
            print(f"✗ Unexpected error initializing stock '{symbol}': {e}")

    def crawl(self, start: str = None, end: str = None, interval: str = "1D"):
        if self.stock is None:
            print(f"⚠ Cannot crawl, stock object not initialized for '{self.symbol}'")
            return []

        if end is None:
            end = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if start is None:
            start = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")

        try:
            df = self.stock.quote.history(
                start=start,
                end=end,
                interval=interval
            )

            if df is None or df.empty:
                print(f"⚠ No data returned for {self.symbol} ({interval})")
                return []

            df = df.reset_index()
            if "time" in df.columns:
                df.rename(columns={"time": "date"}, inplace=True)
            elif "Date" in df.columns:
                df.rename(columns={"Date": "date"}, inplace=True)

            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])  # loại bỏ dòng không có ngày

            ingest_time = datetime.now(timezone.utc).isoformat()
            events = []

            for _, row in df.iterrows():
                events.append({
                    "event_type": "ohlcv",
                    "symbol": self.symbol,
                    "interval": interval,
                    "event_date": row["date"].strftime("%Y-%m-%d"),
                    "event_time": ingest_time,
                    "source": self.source,
                    "data": {
                        "open": float(row["open"]) if pd.notnull(row.get("open")) else 0.0,
                        "high": float(row["high"]) if pd.notnull(row.get("high")) else 0.0,
                        "low": float(row["low"]) if pd.notnull(row.get("low")) else 0.0,
                        "close": float(row["close"]) if pd.notnull(row.get("close")) else 0.0,
                        "volume": int(row["volume"]) if pd.notnull(row.get("volume")) else 0
                    }
                })

            print(f"✓ Fetched {len(events)} OHLCV events for {self.symbol} ({interval})")
            return events

        except Exception as e:
            print(f"✗ Error crawling data for {self.symbol}: {e}")
            return []

if __name__ == "__main__":
    crawler = OHLCVCrawler("VNINDEX")
    events = crawler.crawl()
    print(events[:3])
