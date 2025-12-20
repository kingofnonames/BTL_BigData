from config import Config
from kafka_producer import KafkaHandler
from crawlers.ohlcv_crawler import OHLCVCrawler
from crawlers.fundamental_crawler import FundamentalCrawler
from crawlers.market_crawler import MarketCrawler

def main():
    kafka = KafkaHandler(Config.KAFKA_BOOTSTRAP)

    market = MarketCrawler()
    for idx in ["VNINDEX", "HNX-INDEX"]:
        for record in market.crawl_index(idx):
            kafka.send(Config.TOPIC_MARKET, record)

    for symbol in Config.SYMBOLS:
        ohlcv = OHLCVCrawler(symbol, Config.DATA_SOURCE)
        for interval in Config.INTERVALS:
            records = ohlcv.crawl(Config.START_DATE, Config.END_DATE, interval)
            for r in records:
                kafka.send(Config.TOPIC_OHLCV, r)
        fund = FundamentalCrawler(symbol)
        for r in fund.crawl():
            kafka.send(Config.TOPIC_FUNDAMENTAL, r)

if __name__ == "__main__":
    main()
