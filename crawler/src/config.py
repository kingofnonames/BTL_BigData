"""
File cấu hình cho dự án thu thập dữ liệu chứng khoán
"""
from datetime import datetime, timedelta

class Config:
    """Cấu hình chung cho toàn bộ dự án"""
    
    # Danh sách mã cổ phiếu cần thu thập
    SYMBOLS = [
        'VCB',   # Vietcombank
        'FPT',   # FPT Corporation
        'VNM',   # Vinamilk
        'HPG',   # Hòa Phát
        'VHM',   # Vinhomes
        'VIC',   # Vingroup
        'MSN',   # Masan
        'TCB',   # Techcombank
        'MBB',   # MBBank
        'VPB',   # VPBank
    ]
    
    # Nguồn dữ liệu (VCI, TCBS, MSN)
    # Note: VCI có thể bị 403, thử dùng TCBS
    DATA_SOURCE = 'VCI'
    
    # Cấu hình thời gian
    END_DATE = datetime.now().strftime('%Y-%m-%d')
    START_DATE_1Y = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    START_DATE_3Y = (datetime.now() - timedelta(days=365*3)).strftime('%Y-%m-%d')
    START_DATE_5Y = (datetime.now() - timedelta(days=365*5)).strftime('%Y-%m-%d')
    
    # Các khung thời gian cho OHLCV
    INTERVALS = ['1D', '1W', '1M']
    
    # Các loại báo cáo tài chính
    FINANCIAL_REPORTS = ['BalanceSheet', 'IncomeStatement', 'CashFlow']
    
    # Chu kỳ báo cáo
    PERIODS = ['year', 'quarter']
    
    # Số lượng kỳ báo cáo cần lấy
    REPORT_LIMIT = 10
    
    # Thư mục lưu trữ
    DATA_DIR = 'data'
    OHLCV_DIR = f'{DATA_DIR}/ohlcv'
    FUNDAMENTAL_DIR = f'{DATA_DIR}/fundamental'
    TECHNICAL_DIR = f'{DATA_DIR}/technical'
    MARKET_DIR = f'{DATA_DIR}/market'
    
    # Cấu hình logging
    LOG_DIR = 'logs'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # Cấu hình retry
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    
    # Delay giữa các request (để tránh bị block)
    REQUEST_DELAY = 1  # seconds

class CrawlerConfig:
    """Cấu hình riêng cho từng loại crawler"""
    
    OHLCV = {
        'enabled': True,
        'start_date': Config.START_DATE_3Y,
        'intervals': Config.INTERVALS,
        'include_intraday': True,
    }
    
    FUNDAMENTAL = {
        'enabled': True,
        'reports': Config.FINANCIAL_REPORTS,
        'periods': Config.PERIODS,
        'limit': Config.REPORT_LIMIT,
        'include_profile': True,
        'include_ratios': True,
        'include_dividends': True,
    }
    
    MARKET = {
        'enabled': True,
        'include_index': True,  # VN-Index, HNX-Index, UpCOM-Index
        'include_trading_statistics': True,
    }
    
    TECHNICAL = {
        'enabled': False,  # Sẽ implement sau
    }

if __name__ == "__main__":
    print("=== THÔNG TIN CẤU HÌNH ===\n")
    print(f"Danh sách mã cổ phiếu ({len(Config.SYMBOLS)} mã):")
    for symbol in Config.SYMBOLS:
        print(f"  - {symbol}")
    
    print(f"\nNguồn dữ liệu: {Config.DATA_SOURCE}")
    print(f"Khoảng thời gian: {Config.START_DATE_3Y} đến {Config.END_DATE}")
    print(f"Thư mục lưu trữ: {Config.DATA_DIR}")
    
    print("\n=== CẤU HÌNH CRAWLER ===")
    print(f"OHLCV: {'Bật' if CrawlerConfig.OHLCV['enabled'] else 'Tắt'}")
    print(f"Fundamental: {'Bật' if CrawlerConfig.FUNDAMENTAL['enabled'] else 'Tắt'}")
    print(f"Market: {'Bật' if CrawlerConfig.MARKET['enabled'] else 'Tắt'}")
    print(f"Technical: {'Bật' if CrawlerConfig.TECHNICAL['enabled'] else 'Tắt'}")