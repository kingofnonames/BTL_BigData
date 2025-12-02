"""
Pipeline chính để điều phối toàn bộ quá trình thu thập dữ liệu
"""
import os
import time
import logging
from datetime import datetime
from config import Config, CrawlerConfig
from historical_ohlcv_crawler import HistoricalOHLCVCrawler
from fundamental_analyst_crawler import FundamentalCrawler
from market_crawler import MarketCrawler
from save import DataSaver

class StockDataPipeline:
    def __init__(self, symbols=None):
        """
        Khởi tạo pipeline
        symbols: Danh sách mã cổ phiếu cần crawl (None = lấy từ config)
        """
        self.symbols = symbols if symbols else Config.SYMBOLS
        self.saver = DataSaver(base_dir=Config.DATA_DIR)
        self.setup_logging()
        
    def setup_logging(self):
        """Thiết lập logging"""
        os.makedirs(Config.LOG_DIR, exist_ok=True)
        
        log_file = f"{Config.LOG_DIR}/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format=Config.LOG_FORMAT,
            datefmt=Config.LOG_DATE_FORMAT,
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*60)
        self.logger.info("KHỞI ĐỘNG PIPELINE THU THẬP DỮ LIỆU CHỨNG KHOÁN")
        self.logger.info("="*60)
    
    def crawl_ohlcv(self, symbol):
        """Thu thập dữ liệu OHLCV cho một mã cổ phiếu"""
        if not CrawlerConfig.OHLCV['enabled']:
            return
        
        self.logger.info(f"\n[OHLCV] Bắt đầu crawl {symbol}")
        
        try:
            crawler = HistoricalOHLCVCrawler(symbol, source=Config.DATA_SOURCE)
            
            for interval in CrawlerConfig.OHLCV['intervals']:
                if interval == '1D':
                     data = crawler.get_historical_data(
                     start_date=CrawlerConfig.OHLCV['start_date'],
                     end_date=Config.END_DATE,
                     interval=interval
                     )
                     if data is not None:
                          filename = f"{symbol}_{interval}_{datetime.now().strftime('%Y%m%d')}.csv"
                          self.saver.save_csv(data, filename, subdirectory='ohlcv')
                          time.sleep(Config.REQUEST_DELAY)
                else: 
                    data = crawler.get_historical_data(
                        start_date=CrawlerConfig.OHLCV['start_date'],
                        end_date=Config.END_DATE,
                        interval='1D' 
                    )
                    resampled_data = crawler.resample_ohlcv(data, interval)
                    if resampled_data is not None:
                        filename = f"{symbol}_{interval}_{datetime.now().strftime('%Y%m%d')}.csv"
                        self.saver.save_csv(resampled_data, filename, subdirectory='ohlcv')
                        time.sleep(Config.REQUEST_DELAY)
            
            # Crawl intraday nếu được bật
            if CrawlerConfig.OHLCV['include_intraday']:
                intraday_data = crawler.get_intraday_data()
                if intraday_data is not None:
                    filename = f"{symbol}_intraday_{datetime.now().strftime('%Y%m%d')}.csv"
                    self.saver.save_csv(intraday_data, filename, subdirectory='ohlcv')
            
            self.logger.info(f"[OHLCV] ✓ Hoàn thành {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"[OHLCV] ✗ Lỗi khi crawl {symbol}: {e}")
            return False
    
    def crawl_fundamental(self, symbol):
        """Thu thập dữ liệu fundamental cho một mã cổ phiếu"""
        if not CrawlerConfig.FUNDAMENTAL['enabled']:
            return
        
        self.logger.info(f"\n[FUNDAMENTAL] Bắt đầu crawl {symbol}")
        
        try:
            crawler = FundamentalCrawler(symbol)
            
            # Thông tin công ty
            if CrawlerConfig.FUNDAMENTAL['include_profile']:
                profile = crawler.get_company_profile()
                if profile is not None:
                    filename = f"{symbol}_profile_{datetime.now().strftime('%Y%m%d')}.csv"
                    self.saver.save_csv(profile, filename, subdirectory='fundamental')
                time.sleep(Config.REQUEST_DELAY)
            
            # Báo cáo tài chính
            for report_type in CrawlerConfig.FUNDAMENTAL['reports']:
                for period in CrawlerConfig.FUNDAMENTAL['periods']:
                    data = crawler.get_financial_report(
                        report_type, 
                        period, 
                        limit=CrawlerConfig.FUNDAMENTAL['limit']
                    )
                    if data is not None:
                        filename = f"{symbol}_{report_type}_{period}_{datetime.now().strftime('%Y%m%d')}.csv"
                        self.saver.save_csv(data, filename, subdirectory='fundamental')
                    time.sleep(Config.REQUEST_DELAY)
            
            # Chỉ số tài chính
            if CrawlerConfig.FUNDAMENTAL['include_ratios']:
                for period in CrawlerConfig.FUNDAMENTAL['periods']:
                    ratios = crawler.get_financial_ratios(
                        period, 
                        limit=CrawlerConfig.FUNDAMENTAL['limit']
                    )
                    if ratios is not None:
                        filename = f"{symbol}_ratios_{period}_{datetime.now().strftime('%Y%m%d')}.csv"
                        self.saver.save_csv(ratios, filename, subdirectory='fundamental')
                    time.sleep(Config.REQUEST_DELAY)
            
            # Lịch sử cổ tức
            if CrawlerConfig.FUNDAMENTAL['include_dividends']:
                dividends = crawler.get_dividends()
                if dividends is not None:
                    filename = f"{symbol}_dividends_{datetime.now().strftime('%Y%m%d')}.csv"
                    self.saver.save_csv(dividends, filename, subdirectory='fundamental')
            
            self.logger.info(f"[FUNDAMENTAL] ✓ Hoàn thành {symbol}")
            return True
            
        except Exception as e:
            self.logger.error(f"[FUNDAMENTAL] ✗ Lỗi khi crawl {symbol}: {e}")
            return False
    
    def crawl_market(self):
        """Thu thập dữ liệu thị trường chung"""
        if not CrawlerConfig.MARKET['enabled']:
            return
        
        self.logger.info("\n[MARKET] Bắt đầu crawl dữ liệu thị trường")
        
        try:
            crawler = MarketCrawler()
            
            # Chỉ số thị trường
            if CrawlerConfig.MARKET['include_index']:
                for index_code in ['VNINDEX', 'HNX-INDEX']:
                    data = crawler.get_market_index(
                        index_code,
                        start_date=CrawlerConfig.OHLCV['start_date'],
                        end_date=Config.END_DATE
                    )
                    if data is not None:
                        filename = f"{index_code}_{datetime.now().strftime('%Y%m%d')}.csv"
                        self.saver.save_csv(data, filename, subdirectory='market')
                    time.sleep(Config.REQUEST_DELAY)
            
            # Danh sách cổ phiếu
            for exchange in ['HOSE', 'HNX', 'UPCOM']:
                symbols = crawler.get_all_symbols(exchange)
                if symbols is not None:
                    filename = f"symbols_{exchange}_{datetime.now().strftime('%Y%m%d')}.csv"
                    self.saver.save_csv(symbols, filename, subdirectory='market')
                time.sleep(Config.REQUEST_DELAY)
            
            self.logger.info("[MARKET] ✓ Hoàn thành")
            return True
            
        except Exception as e:
            self.logger.error(f"[MARKET] ✗ Lỗi khi crawl: {e}")
            return False
    
    def run(self, crawl_ohlcv=True, crawl_fundamental=True, crawl_market=True):
        """
        Chạy toàn bộ pipeline
        
        Args:
            crawl_ohlcv: Có crawl dữ liệu OHLCV không
            crawl_fundamental: Có crawl dữ liệu fundamental không
            crawl_market: Có crawl dữ liệu thị trường không
        """
        start_time = time.time()
        
        self.logger.info(f"\nDanh sách mã cổ phiếu: {', '.join(self.symbols)}")
        self.logger.info(f"Tổng số: {len(self.symbols)} mã\n")
        
        # Crawl dữ liệu thị trường (chỉ chạy 1 lần)
        if crawl_market:
            self.crawl_market()
            time.sleep(Config.REQUEST_DELAY)
        
        # Crawl từng mã cổ phiếu
        success_count = 0
        for i, symbol in enumerate(self.symbols, 1):
            self.logger.info(f"\n{'='*60}")
            self.logger.info(f"Tiến độ: {i}/{len(self.symbols)} - {symbol}")
            self.logger.info(f"{'='*60}")
            
            try:
                # OHLCV
                if crawl_ohlcv:
                    self.crawl_ohlcv(symbol)
                
                # Fundamental
                if crawl_fundamental:
                    self.crawl_fundamental(symbol)
                
                success_count += 1
                
            except Exception as e:
                self.logger.error(f"Lỗi khi xử lý {symbol}: {e}")
            
            # Delay giữa các mã
            if i < len(self.symbols):
                time.sleep(Config.REQUEST_DELAY * 2)
        
        # Tổng kết
        elapsed_time = time.time() - start_time
        
        self.logger.info(f"\n{'='*60}")
        self.logger.info("TỔNG KẾT")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Tổng số mã: {len(self.symbols)}")
        self.logger.info(f"Thành công: {success_count}")
        self.logger.info(f"Thất bại: {len(self.symbols) - success_count}")
        self.logger.info(f"Thời gian: {elapsed_time:.2f} giây ({elapsed_time/60:.2f} phút)")
        self.logger.info(f"{'='*60}")
        
        # Hiển thị thông tin file đã lưu
        self.show_summary()
    
    def show_summary(self):
        """Hiển thị tóm tắt dữ liệu đã thu thập"""
        self.logger.info("\n=== TỔNG QUAN DỮ LIỆU ĐÃ THU THẬP ===\n")
        
        for subdir in ['ohlcv', 'fundamental', 'market']:
            info = self.saver.get_file_info(subdir)
            if not info.empty:
                self.logger.info(f"\n[{subdir.upper()}] - {len(info)} files")
                total_size = info['size_kb'].sum()
                self.logger.info(f"Tổng dung lượng: {total_size:.2f} KB ({total_size/1024:.2f} MB)")

def main():
    pipeline = StockDataPipeline()
    pipeline.run(
        crawl_ohlcv=True,
        crawl_fundamental=True,
        crawl_market=True
    )

if __name__ == "__main__":
    main()
