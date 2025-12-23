from vnstock import Vnstock
import pandas as pd
from datetime import datetime, timedelta, timezone

class MarketCrawler:
    def __init__(self):
        self.vnstock = Vnstock()
    
    def crawl_index(self, index_code: str):

        VALID_INDEXES = ["VNINDEX", "HNX-INDEX", "UPCOM-INDEX"]
        if index_code not in VALID_INDEXES:
            print(f"✗ Invalid index_code: {index_code}")
            return []
        start = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%d")
        end = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        try:
            stock = self.vnstock.stock(symbol=index_code, source="VCI")
            df = stock.quote.history(start=start, end=end, interval="1D")

            if df is None or df.empty:
                print(f"⚠ No data returned for {index_code}")
                return []

            df = df.reset_index()
            if "time" in df.columns:
                df.rename(columns={"time": "date"}, inplace=True)

            df["date"] = pd.to_datetime(df["date"], errors="coerce")
            df = df.dropna(subset=["date"])

            ingest_time = datetime.now(timezone.utc).isoformat()
            events = []

            for _, row in df.iterrows():
                events.append({
                    "event_type": "market_index",
                    "index_code": index_code,
                    "event_date": row["date"].strftime("%Y-%m-%d"),
                    "event_time": row["date"].replace(tzinfo=timezone.utc).isoformat(),
                    "ingest_time": ingest_time,
                    "source": "VCI",
                    "year": row["date"].year,
                    "month": row["date"].month,
                    "data": {
                        "open": float(row["open"]) if pd.notnull(row["open"]) else 0.0,
                        "high": float(row["high"]) if pd.notnull(row["high"]) else 0.0,
                        "low": float(row["low"]) if pd.notnull(row["low"]) else 0.0,
                        "close": float(row["close"]) if pd.notnull(row["close"]) else 0.0,
                        "volume": int(row["volume"]) if pd.notnull(row["volume"]) else 0
                    }
                })

            print(f"✓ Fetched {len(events)} events for {index_code}")
            return events

        except ValueError as e:
            print(f"✗ Error fetching data for {index_code}: {e}")
            return []
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return []

if __name__ == "__main__":
    crawler = MarketCrawler()
    for idx in ["VNINDEX", "HNX-INDEX", "INVALID"]:
        events = crawler.crawl_index(idx)
        print(events[:3]) 
