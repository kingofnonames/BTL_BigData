
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
