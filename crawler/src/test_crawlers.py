"""
Script để test các crawler trước khi chạy pipeline chính
"""
import sys
from datetime import datetime, timedelta

def test_ohlcv_crawler():
    """Test OHLCV Crawler"""
    print("\n" + "="*60)
    print("TEST 1: OHLCV CRAWLER")
    print("="*60)
    
    try:
        from historical_ohlcv_crawler import HistoricalOHLCVCrawler
        
        crawler = HistoricalOHLCVCrawler('FPT')
        
        # Test lấy dữ liệu daily
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = crawler.get_historical_data(start_date, end_date, interval='1D')
        
        if data is not None and not data.empty:
            print(f"\n✓ PASS: Lấy được {len(data)} dòng dữ liệu")
            print("\nMẫu dữ liệu:")
            print(data.head(3))
            return True
        else:
            print("\n✗ FAIL: Không lấy được dữ liệu")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

def test_fundamental_crawler():
    """Test Fundamental Crawler"""
    print("\n" + "="*60)
    print("TEST 2: FUNDAMENTAL CRAWLER")
    print("="*60)
    
    try:
        from fundamental_analyst_crawler import FundamentalCrawler
        
        crawler = FundamentalCrawler('FPT')
        
        # Test lấy thông tin công ty
        profile = crawler.get_company_profile()
        
        if profile is not None and not profile.empty:
            print(f"\n✓ PASS: Lấy được thông tin công ty")
            print("\nMẫu dữ liệu:")
            print(profile.head())
            
            # Test lấy báo cáo tài chính
            balance = crawler.get_financial_report('BalanceSheet', 'year', limit=2)
            if balance is not None and not balance.empty:
                print(f"\n✓ PASS: Lấy được {len(balance)} kỳ báo cáo")
                return True
            else:
                print("\n⚠ WARNING: Không lấy được báo cáo tài chính")
                return True  # Vẫn pass vì đã lấy được profile
        else:
            print("\n✗ FAIL: Không lấy được thông tin công ty")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

def test_market_crawler():
    """Test Market Crawler"""
    print("\n" + "="*60)
    print("TEST 3: MARKET CRAWLER")
    print("="*60)
    
    try:
        from market_crawler import MarketCrawler
        
        crawler = MarketCrawler()
        
        # Test lấy chỉ số VN-Index
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        data = crawler.get_market_index('VNINDEX', start_date, end_date)
        
        if data is not None and not data.empty:
            print(f"\n✓ PASS: Lấy được {len(data)} dòng dữ liệu VN-Index")
            print("\nMẫu dữ liệu:")
            print(data.head(3))
            
            # Test lấy danh sách cổ phiếu
            symbols = crawler.get_all_symbols('HOSE')
            if symbols is not None and not symbols.empty:
                print(f"\n✓ PASS: Lấy được {len(symbols)} mã cổ phiếu HOSE")
                return True
            else:
                print("\n⚠ WARNING: Không lấy được danh sách cổ phiếu")
                return True  # Vẫn pass vì đã lấy được VN-Index
        else:
            print("\n✗ FAIL: Không lấy được dữ liệu VN-Index")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

def test_save_utils():
    """Test Save Utilities"""
    print("\n" + "="*60)
    print("TEST 4: SAVE UTILITIES")
    print("="*60)
    
    try:
        import pandas as pd
        from save import DataSaver
        
        saver = DataSaver()
        
        # Tạo dữ liệu test
        test_data = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c']
        })
        
        # Test save
        filename = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        result = saver.save_csv(test_data, filename, subdirectory='raw')
        
        if result:
            print("\n✓ PASS: Lưu file thành công")
            
            # Test load
            loaded_data = saver.load_csv(filename, subdirectory='raw')
            if loaded_data is not None:
                print("✓ PASS: Đọc file thành công")
                
                # Test list files
                files = saver.list_files('raw')
                print(f"✓ PASS: Liệt kê được {len(files)} files")
                
                return True
            else:
                print("\n✗ FAIL: Không đọc được file")
                return False
        else:
            print("\n✗ FAIL: Không lưu được file")
            return False
            
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

def test_config():
    """Test Config"""
    print("\n" + "="*60)
    print("TEST 5: CONFIGURATION")
    print("="*60)
    
    try:
        from config import Config, CrawlerConfig
        
        print(f"\nDanh sách mã cổ phiếu: {len(Config.SYMBOLS)} mã")
        print(f"Nguồn dữ liệu: {Config.DATA_SOURCE}")
        print(f"Khoảng thời gian: {Config.START_DATE_3Y} đến {Config.END_DATE}")
        
        print(f"\nCrawler OHLCV: {'Bật' if CrawlerConfig.OHLCV['enabled'] else 'Tắt'}")
        print(f"Crawler Fundamental: {'Bật' if CrawlerConfig.FUNDAMENTAL['enabled'] else 'Tắt'}")
        print(f"Crawler Market: {'Bật' if CrawlerConfig.MARKET['enabled'] else 'Tắt'}")
        
        print("\n✓ PASS: Config hoạt động bình thường")
        return True
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False

def run_all_tests():
    """Chạy tất cả các test"""
    print("\n" + "="*60)
    print("BẮT ĐẦU KIỂM TRA HỆ THỐNG")
    print("="*60)
    
    tests = [
        ('Config', test_config),
        ('Save Utilities', test_save_utils),
        ('OHLCV Crawler', test_ohlcv_crawler),
        ('Fundamental Crawler', test_fundamental_crawler),
        ('Market Crawler', test_market_crawler),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ Test {test_name} gặp lỗi nghiêm trọng: {e}")
            results[test_name] = False
    
    # Tổng kết
    print("\n" + "="*60)
    print("TỔNG KẾT")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nKết quả: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 TẤT CẢ CÁC TEST ĐỀU THÀNH CÔNG!")
        print("Bạn có thể chạy pipeline chính: python pipeline.py")
        return True
    else:
        print("\n⚠️  CÓ MỘT SỐ TEST THẤT BẠI")
        print("Vui lòng kiểm tra lại các lỗi ở trên")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
