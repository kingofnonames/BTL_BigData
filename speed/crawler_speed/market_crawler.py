# import time
# import logging
# from vnstock import Vnstock
# from config import Config

# logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
# logger = logging.getLogger(__name__)
# class MarketCrawler:
#     def __init__(self):
#         self.client = Vnstock()

#     def fetch_latest(self, symbol: str):
#         try:
#             stock = self.client.stock(
#                 symbol=symbol.strip().upper(),
#                 source=Config.DATA_SOURCE
#             )

#             if not hasattr(stock.quote, "intraday"):
#                 return None

#             df = stock.quote.intraday()
#             if df is None or df.empty:
#                 return None
#             record = df.tail(1).to_dict("records")[0]
#             record["symbol"] = symbol

#             time.sleep(Config.REQUEST_DELAY)
#             return record

#         except Exception as e:
#             logger.warning(f"Fail symbol {symbol}: {e}")
#             return None


# import logging
# from datetime import datetime, timezone
# import pandas as pd
# from vnstock import Vnstock
# from config import Config  # Giả sử có danh sách SYMBOLS, DATA_SOURCE, REQUEST_DELAY
# import time
# logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
# logger = logging.getLogger(__name__)

# class MarketCrawler:
#     def __init__(self):
#         self.client = Vnstock()
#         self.buffers = {}  # lưu DataFrame theo symbol
#         self.cursors = {}  # cursor cho mỗi symbol

#     def load_day(self, symbol: str, date: str):
#         """
#         Load dữ liệu hourly cho 1 symbol trong 1 ngày cụ thể.
#         """
#         try:
#             stock = self.client.stock(symbol=symbol.strip().upper(), source=Config.DATA_SOURCE)
#             df = stock.quote.history(
#                 start=date,
#                 end=date,
#                 interval="1H"
#             )

#             if df is None or df.empty:
#                 logger.warning(f"No hourly data for {symbol} on {date}")
#                 return None

#             df = df.sort_values("time").reset_index(drop=True)
#             self.buffers[symbol] = df
#             self.cursors[symbol] = 0
#             logger.info(f"Loaded {len(df)} hourly records for {symbol} on {date}")
#             return df
#         except Exception as e:
#             logger.warning(f"Fail to load {symbol} on {date}: {e}")
#             return None

#     def fetch_next(self, symbol: str):
#         """
#         Trả về record tiếp theo theo giờ từ buffer.
#         """
#         if symbol not in self.buffers:
#             logger.warning(f"No buffer loaded for {symbol}")
#             return None

#         idx = self.cursors[symbol]
#         df = self.buffers[symbol]

#         if idx >= len(df):
#             return None  # đã hết dữ liệu trong ngày

#         record = df.iloc[idx].to_dict()
#         record["symbol"] = symbol
#         record["ingestion_time"] = datetime.now(timezone.utc).isoformat()

#         self.cursors[symbol] += 1
#         return record

# if __name__ == "__main__":
#     crawler = MarketCrawler()
#     # Ví dụ lấy dữ liệu hourly cho FPT ngày 2025-12-22
#     crawler.load_day("FPT", "2025-12-19")

#     while True:
#         rec = crawler.fetch_next("FPT")
#         if not rec:
#             break
#         print(rec)
#         time.sleep(1)
import logging
from datetime import datetime, timezone
import pandas as pd
from vnstock import Vnstock
from config import Config
import time
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

class MarketCrawler:
    def __init__(self):
        self.client = Vnstock()
        self.buffers = {}
        self.cursors = {}

    def load_day(self, symbol: str, date: str, end_hour: int = 15):
        try:
            stock = self.client.stock(symbol=symbol.strip().upper(), source=Config.DATA_SOURCE)
            df = stock.quote.history(start=date, end=date, interval=Config.INTERVALS)
            if df is None or df.empty:
                logger.warning(f"No {Config.INTERVALS} data for {symbol} on {date}")
                return

            if "time" in df.columns:
                df["time"] = pd.to_datetime(df["time"])
            else:
                df.index = pd.to_datetime(df.index)
                df["time"] = df.index

            df = df.dropna(subset=["open", "high", "low", "close"])
            # df = df[df["time"].dt.date == pd.to_datetime(date).date()] 
            df = df[df["time"].dt.hour < end_hour]

            df = df.sort_values("time").reset_index(drop=True)
            df["symbol"] = symbol
            self.buffers[symbol] = df
            self.cursors[symbol] = 0

            logger.info(f"Loaded {len(df)} {Config.INTERVALS} records for {symbol} on {date}")

        except Exception as e:
            logger.warning(f"Fail to load {symbol} on {date}: {e}")

    def fetch_next(self, symbol: str):
        if symbol not in self.buffers:
            return None

        idx = self.cursors.get(symbol, 0)
        df = self.buffers[symbol]

        if idx >= len(df):
            return None

        record = df.iloc[idx].to_dict()
        record["symbol"] = symbol
        self.cursors[symbol] += 1
        logger.debug(f"Fetched record: {record}")
        return record


if __name__ == "__main__":
    crawler = MarketCrawler()
    crawler.load_day("FPT", "2025-12-19", end_hour=15)

    while True:
        rec = crawler.fetch_next("FPT")
        if not rec:
            break
        print(rec)
        time.sleep(1)