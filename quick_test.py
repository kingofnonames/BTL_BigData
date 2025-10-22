"""
Script đơn giản để chạy nhanh và test cơ bản
Thu thập dữ liệu cho 1 mã cổ phiếu
"""
from datetime import datetime, timedelta
import sys

def quick_test():
    """Test nhanh với 1 mã cổ phiếu"""
    symbol = 'FPT'
    
    print(f"\n{'='*60}")
    print(f"QUICK TEST - {symbol}")
    print(f"{'='*60}\n")
    
    try:
        # Test 1: OHLCV
        print("[1/3] Test OHLCV...")
        from historical_ohlcv_crawler import HistoricalOHLCVCrawler
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        ohlcv_crawler = HistoricalOHLCVCrawler(symbol, source='TCBS')
        data = ohlcv_crawler.get_historical_data(start_date, end_date, interval='1D')
        
        if data is not None and not data.empty:
            print(f"✓ OHLCV: {len(data)} dòng")
            print(data.head(2))
        else:
            print("✗ OHLCV: Không có dữ liệu")
        
        # Test 2: Fundamental
        print("\n[2/3] Test Fundamental...")
        from fundamental_analyst_crawler import FundamentalCrawler
        
        fund_crawler = FundamentalCrawler(symbol)
        profile = fund_crawler.get_company_profile()
        
        if profile is not None and not profile.empty:
            print(f"✓ Fundamental: Có dữ liệu")
            if 'companyName' in profile.columns:
                print(f"  Tên công ty: {profile['companyName'].iloc[0]}")
        else:
            print("✗ Fundamental: Không có dữ liệu")
        
        # Test 3: Market
        print("\n[3/3] Test Market...")
        from market_crawler import MarketCrawler
        
        market_crawler = MarketCrawler()
        vnindex = market_crawler.get_market_index('VNINDEX', start_date, end_date)
        
        if vnindex is not None and not vnindex.empty:
            print(f"✓ Market: {len(vnindex)} dòng VN-Index")
        else:
            print("✗ Market: Không có dữ liệu")
        
        print(f"\n{'='*60}")
        print("✓ QUICK TEST HOÀN TẤT!")
        print(f"{'='*60}\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Lỗi: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
