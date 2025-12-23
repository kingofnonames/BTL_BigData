# import time
# import logging
# from datetime import datetime, timezone

# from config import Config
# from market_crawler import MarketCrawler
# from kafka_producer import KafkaHandler

# logger = logging.getLogger(__name__)

# class SpeedIngestService:
#     def __init__(self):
#         self.crawler = MarketCrawler()
#         self.producer = KafkaHandler()

#     def run(self):
#         logger.info("Speed crawler started")

#         while True:
#             start = time.time()
#             sent = 0

#             for symbol in Config.SYMBOLS:
#                 record = self.crawler.fetch_latest(symbol)
#                 if not record:
#                     continue

#                 record["ingestion_time"] = datetime.now(
#                     timezone.utc
#                 ).isoformat()

#                 self.producer.send(record)
#                 sent += 1

#             self.producer.flush()
#             logger.info(f"Sent {sent} records")

#             sleep = max(
#                 0,
#                 Config.INTERVAL_SECONDS - (time.time() - start)
#             )
#             time.sleep(sleep)


import time
import logging
from datetime import datetime, timezone

from config import Config
from market_crawler import MarketCrawler
from kafka_producer import KafkaHandler

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

class SpeedIngestService:
    def __init__(self, date: str):
        self.crawler = MarketCrawler()
        self.producer = KafkaHandler()
        self.date = date

        # Load dữ liệu hourly cho tất cả symbols
        for symbol in Config.SYMBOLS:
            self.crawler.load_day(symbol, date=self.date)

    def run(self):
        logger.info(f"Speed replay started for {self.date}")

        while True:
            batch_records = []

            for symbol in Config.SYMBOLS:
                record = self.crawler.fetch_next(symbol)
                if record is None:
                    continue

                # Giả lập ingestion_time theo thời điểm gửi
                record["ingestion_time"] = datetime.now(timezone.utc).isoformat()
                batch_records.append(record)

            if not batch_records:
                logger.info("All symbols finished replaying. Exiting.")
                break

            for record in batch_records:
                self.producer.send(record)

            self.producer.flush()
            logger.info(f"Sent {len(batch_records)} records in this batch")
            time.sleep(Config.INTERVAL_SECONDS)


if __name__ == "__main__":
    date_to_replay = "2025-12-19"
    service = SpeedIngestService(date=date_to_replay)
    service.run()
