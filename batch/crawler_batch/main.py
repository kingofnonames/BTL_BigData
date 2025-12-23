# from config import Config
# from kafka_producer import KafkaHandler
# from crawlers.ohlcv_crawler import OHLCVCrawler
# from crawlers.fundamental_crawler import FundamentalCrawler
# from crawlers.market_crawler import MarketCrawler

# def main():
#     kafka = KafkaHandler(Config.KAFKA_BOOTSTRAP)

#     market = MarketCrawler()
#     for idx in ["VNINDEX", "HNX-INDEX"]:
#         for record in market.crawl_index(idx):
#             kafka.send(Config.TOPIC_MARKET, record)

#     for symbol in Config.SYMBOLS:
#         ohlcv = OHLCVCrawler(symbol, Config.DATA_SOURCE)
#         for interval in Config.INTERVALS:
#             records = ohlcv.crawl(Config.START_DATE, Config.END_DATE, interval)
#             for r in records:
#                 kafka.send(Config.TOPIC_OHLCV, r)
#         fund = FundamentalCrawler(symbol)
#         for r in fund.crawl():
#             kafka.send(Config.TOPIC_FUNDAMENTAL, r)

# if __name__ == "__main__":
#     main()

from config import Config
from kafka_producer import KafkaHandler
from crawlers.ohlcv_crawler import OHLCVCrawler
from crawlers.market_crawler import MarketCrawler
import time

def main():
    kafka = KafkaHandler(Config.KAFKA_BOOTSTRAP)

    market = MarketCrawler()
    for index_code in ["VNINDEX", "HNX-INDEX"]:
        events = market.crawl_index(index_code)
        for event in events:
            kafka.send(
                topic=Config.TOPIC_MARKET_RAW,
                key=index_code,
                payload=event
            )
            pass
    for symbol in Config.SYMBOLS:
        crawler = OHLCVCrawler(symbol=symbol, source=Config.DATA_SOURCE)
        events = crawler.crawl(
            start=Config.START_DATE,
            end=Config.END_DATE,
            interval="1D"
        )

        if not events:
            continue

        for event in events:
            kafka.send(
                topic=Config.TOPIC_OHLCV_RAW,
                key=symbol,
                payload=event
            )
            pass

        time.sleep(1)

    kafka.close()

if __name__ == "__main__":
    main()
