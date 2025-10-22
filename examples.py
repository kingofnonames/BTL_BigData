"""
Ví dụ sử dụng các crawler - Demo đầy đủ
Chạy file này để xem cách sử dụng từng crawler
"""
from datetime import datetime, timedelta
import pandas as pd

def example_1_ohlcv():
    """Ví dụ 1: Lấy dữ liệu OHLCV"""
    print("\n" + "="*60)
    print("VÍ DỤ 1: THU THẬP DỮ LIỆU OHLCV")
    print("="*60)
    
    from historical_ohlcv_crawler import HistoricalOHLCVCrawler
    
    # Khởi tạo crawler cho FPT
    crawler = HistoricalOHLCVCrawler('FPT', source='TCBS')
    
    # Thiết lập khoảng thời gian
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    print(f"\nLấy dữ liệu FPT từ {start_date} đến {end_date}")
    
    # 1. Dữ liệu daily
    print("\n[1.1] Dữ liệu Daily (1D):")
    daily_data = crawler.get_historical_data(start_date, end_date, interval='1D')
    if daily_data is not None:
        print(f"- Số dòng: {len(daily_data)}")
        print(f"- Columns: {list(daily_data.columns)}")
        print("\nMẫu dữ liệu:")
        print(daily_data.head(3))
        
        # Tính toán đơn giản
        print(f"\n- Giá cao nhất: {daily_data['high'].max():.2f}")
        print(f"- Giá thấp nhất: {daily_data['low'].min():.2f}")
        print(f"- Khối lượng TB: {daily_data['volume'].mean():.0f}")
    
    # 2. Dữ liệu weekly
    print("\n[1.2] Dữ liệu Weekly (1W):")
    weekly_data = crawler.get_historical_data(start_date, end_date, interval='1W')
    if weekly_data is not None:
        print(f"- Số dòng: {len(weekly_data)}")
        print(weekly_data.head(2))

def example_2_fundamental():
    """Ví dụ 2: Lấy dữ liệu Fundamental"""
    print("\n" + "="*60)
    print("VÍ DỤ 2: THU THẬP DỮ LIỆU FUNDAMENTAL")
    print("="*60)
    
    from fundamental_analyst_crawler import FundamentalCrawler
    
    # Khởi tạo crawler cho VNM (Vinamilk)
    crawler = FundamentalCrawler('VNM')
    
    # 1. Thông tin công ty
    print("\n[2.1] Thông tin công ty:")
    profile = crawler.get_company_profile()
    if profile is not None:
        print(profile.T)  # Transpose để dễ đọc
    
    # 2. Báo cáo tài chính - Bảng cân đối kế toán
    print("\n[2.2] Bảng cân đối kế toán (5 năm gần nhất):")
    balance_sheet = crawler.get_financial_report('BalanceSheet', 'year', limit=5)
    if balance_sheet is not None:
        print(f"- Số kỳ báo cáo: {len(balance_sheet)}")
        print(f"- Columns: {list(balance_sheet.columns)[:10]}...")  # Show first 10 columns
        print("\nMẫu:")
        print(balance_sheet.head(2))
    
    # 3. Kết quả kinh doanh
    print("\n[2.3] Kết quả kinh doanh (4 quý gần nhất):")
    income = crawler.get_financial_report('IncomeStatement', 'quarter', limit=4)
    if income is not None:
        print(f"- Số kỳ báo cáo: {len(income)}")
        print(income.head(2))
    
    # 4. Chỉ số tài chính
    print("\n[2.4] Chỉ số tài chính (3 năm gần nhất):")
    ratios = crawler.get_financial_ratios('year', limit=3)
    if ratios is not None:
        print(f"- Số kỳ: {len(ratios)}")
        print(f"- Columns: {list(ratios.columns)[:10]}...")
        print(ratios.head(2))
    
    # 5. Cổ tức
    print("\n[2.5] Lịch sử cổ tức:")
    dividends = crawler.get_dividends()
    if dividends is not None:
        print(f"- Số lần chia cổ tức: {len(dividends)}")
        print(dividends.head(3))

def example_3_market():
    """Ví dụ 3: Lấy dữ liệu thị trường"""
    print("\n" + "="*60)
    print("VÍ DỤ 3: THU THẬP DỮ LIỆU THỊ TRƯỜNG")
    print("="*60)
    
    from market_crawler import MarketCrawler
    
    crawler = MarketCrawler()
    
    # 1. VN-Index
    print("\n[3.1] Chỉ số VN-Index (30 ngày gần nhất):")
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    vnindex = crawler.get_market_index('VNINDEX', start_date, end_date)
    if vnindex is not None:
        print(f"- Số điểm: {len(vnindex)}")
        print(vnindex.head(3))
        
        # Phân tích đơn giản
        print(f"\n- Điểm cao nhất: {vnindex['high'].max():.2f}")
        print(f"- Điểm thấp nhất: {vnindex['low'].min():.2f}")
        print(f"- Thay đổi: {vnindex['close'].iloc[0] - vnindex['close'].iloc[-1]:.2f}")
    
    # 2. Danh sách cổ phiếu HOSE
    print("\n[3.2] Danh sách cổ phiếu HOSE:")
    hose_symbols = crawler.get_all_symbols('HOSE')
    if hose_symbols is not None:
        print(f"- Tổng số mã: {len(hose_symbols)}")
        print(f"- Columns: {list(hose_symbols.columns)}")
        print("\n10 mã đầu tiên:")
        print(hose_symbols.head(10)[['symbol', 'exchange', 'companyName']])

def example_4_save_load():
    """Ví dụ 4: Lưu và đọc dữ liệu"""
    print("\n" + "="*60)
    print("VÍ DỤ 4: LƯU VÀ ĐỌC DỮ LIỆU")
    print("="*60)
    
    from save import DataSaver
    from historical_ohlcv_crawler import HistoricalOHLCVCrawler
    
    # 1. Thu thập dữ liệu
    print("\n[4.1] Thu thập dữ liệu HPG:")
    crawler = HistoricalOHLCVCrawler('HPG', source='TCBS')
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    data = crawler.get_historical_data(start_date, end_date, interval='1D')
    
    # 2. Lưu dữ liệu
    print("\n[4.2] Lưu dữ liệu:")
    saver = DataSaver()
    filename = f"HPG_example_{datetime.now().strftime('%Y%m%d')}.csv"
    saver.save_csv(data, filename, subdirectory='ohlcv', index=True)
    
    # 3. Đọc lại dữ liệu
    print("\n[4.3] Đọc lại dữ liệu:")
    loaded_data = saver.load_csv(filename, subdirectory='ohlcv')
    if loaded_data is not None:
        print(f"- Đã đọc {len(loaded_data)} dòng")
        print(loaded_data.head(2))
    
    # 4. Liệt kê files
    print("\n[4.4] Danh sách files trong thư mục ohlcv:")
    files = saver.list_files('ohlcv')
    for f in files[:5]:  # Show first 5
        print(f"  - {f}")
    
    # 5. Thông tin chi tiết
    print("\n[4.5] Thông tin chi tiết:")
    info = saver.get_file_info('ohlcv')
    if not info.empty:
        print(info.head())

def example_5_batch_crawl():
    """Ví dụ 5: Crawl nhiều mã cùng lúc"""
    print("\n" + "="*60)
    print("VÍ DỤ 5: CRAWL NHIỀU MÃ CÙNG LÚC")
    print("="*60)
    
    from historical_ohlcv_crawler import HistoricalOHLCVCrawler
    from save import DataSaver
    import time
    
    # Danh sách mã cần crawl
    symbols = ['FPT', 'VNM', 'VCB']
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    
    saver = DataSaver()
    
    print(f"\nCrawl {len(symbols)} mã: {', '.join(symbols)}")
    print(f"Khoảng thời gian: {start_date} đến {end_date}\n")
    
    results = {}
    
    for i, symbol in enumerate(symbols, 1):
        print(f"[{i}/{len(symbols)}] Đang crawl {symbol}...")
        
        try:
            # Crawl
            crawler = HistoricalOHLCVCrawler(symbol, source='TCBS')
            data = crawler.get_historical_data(start_date, end_date, interval='1D')
            
            if data is not None and not data.empty:
                # Lưu
                filename = f"{symbol}_batch_{datetime.now().strftime('%Y%m%d')}.csv"
                saver.save_csv(data, filename, subdirectory='ohlcv')
                
                results[symbol] = {
                    'status': 'success',
                    'rows': len(data),
                    'file': filename
                }
                print(f"  ✓ Thành công: {len(data)} dòng")
            else:
                results[symbol] = {'status': 'failed', 'reason': 'No data'}
                print(f"  ✗ Thất bại: Không có dữ liệu")
        
        except Exception as e:
            results[symbol] = {'status': 'error', 'reason': str(e)}
            print(f"  ✗ Lỗi: {e}")
        
        # Delay để tránh rate limit
        if i < len(symbols):
            time.sleep(1)
    
    # Tổng kết
    print("\n" + "="*60)
    print("TỔNG KẾT:")
    print("="*60)
    for symbol, result in results.items():
        status = result['status']
        if status == 'success':
            print(f"✓ {symbol}: {result['rows']} dòng - {result['file']}")
        else:
            print(f"✗ {symbol}: {result.get('reason', 'Unknown error')}")

def example_6_pipeline():
    """Ví dụ 6: Sử dụng Pipeline"""
    print("\n" + "="*60)
    print("VÍ DỤ 6: SỬ DỤNG PIPELINE")
    print("="*60)
    
    from pipeline import StockDataPipeline
    
    print("\nTạo pipeline với danh sách mã custom:")
    
    # Custom pipeline với ít mã để demo
    pipeline = StockDataPipeline(symbols=['FPT', 'VNM'])
    
    print("\nChạy pipeline (chỉ OHLCV và Market):")
    print("Note: Quá trình này có thể mất vài phút...\n")
    
    # Chạy chỉ OHLCV và Market để demo nhanh
    pipeline.run(
        crawl_ohlcv=True,
        crawl_fundamental=False,  # Bỏ qua để nhanh hơn
        crawl_market=True
    )

def main():
    """Chạy tất cả các ví dụ"""
    print("\n" + "="*60)
    print("BẮT ĐẦU DEMO CÁC VÍ DỤ SỬ DỤNG")
    print("="*60)
    
    examples = [
        ("OHLCV Crawler", example_1_ohlcv),
        ("Fundamental Crawler", example_2_fundamental),
        ("Market Crawler", example_3_market),
        ("Save & Load", example_4_save_load),
        ("Batch Crawl", example_5_batch_crawl),
        # ("Pipeline", example_6_pipeline),  # Comment out vì mất thời gian
    ]
    
    for name, func in examples:
        try:
            print(f"\n>>> Bắt đầu: {name}")
            func()
            print(f">>> Hoàn thành: {name}")
        except Exception as e:
            print(f">>> Lỗi trong {name}: {e}")
            import traceback
            traceback.print_exc()
        
        input("\nNhấn Enter để tiếp tục...")
    
    print("\n" + "="*60)
    print("ĐÃ HOÀN THÀNH TẤT CẢ VÍ DỤ")
    print("="*60)
    print("\nBạn có thể:")
    print("1. Xem dữ liệu đã lưu trong thư mục data/")
    print("2. Xem log trong thư mục logs/")
    print("3. Chỉnh sửa config.py để tùy chỉnh")
    print("4. Chạy pipeline.py để crawl toàn bộ")

if __name__ == "__main__":
    # Chạy từng ví dụ một
    main()
    
    # Hoặc chạy riêng lẻ:
    # example_1_ohlcv()
    # example_2_fundamental()
    # example_3_market()
    # example_4_save_load()
    # example_5_batch_crawl()
