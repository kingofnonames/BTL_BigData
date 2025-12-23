"""
Crawler để thu thập dữ liệu thị trường chung
Bao gồm: chỉ số VN-Index, HNX-Index, thống kê giao dịch, danh sách cổ phiếu
"""
from vnstock import Vnstock
import pandas as pd
from datetime import datetime, timedelta
import os

class MarketCrawler:
    def __init__(self):
        self.vnstock = Vnstock()
        
    def get_market_index(self, index_code='VNINDEX', start_date=None, end_date=None):
        """
        Lấy dữ liệu chỉ số thị trường
        index_code: 'VNINDEX', 'HNX-INDEX', 'UPCOM-INDEX'
        """
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            print(f"\n[{index_code}] Đang lấy dữ liệu từ {start_date} đến {end_date}...")
            
            # Lấy dữ liệu chỉ số
            stock = self.vnstock.stock(symbol=index_code, source='VCI')
            data = stock.quote.history(start=start_date, end=end_date, interval='1D')
            
            if data is not None and not data.empty:
                print(f"✓ Đã lấy {len(data)} dòng dữ liệu")
                return data
            else:
                print("⚠ Không có dữ liệu")
                return None
                
        except Exception as e:
            print(f"✗ Lỗi khi lấy dữ liệu chỉ số: {e}")
            return None
    
    def get_all_symbols(self, exchange='HOSE'):
        """
        Lấy danh sách tất cả mã cổ phiếu
        exchange: 'HOSE', 'HNX', 'UPCOM'
        """
        try:
            print(f"\n[{exchange}] Đang lấy danh sách mã cổ phiếu...")
            
            # Lấy danh sách cổ phiếu
            listing = self.vnstock.stock(symbol='ACB', source='VCI')
            data = listing.listing.all_symbols()
            
            if data is not None and not data.empty:
                # Lọc theo sàn
                if exchange != 'ALL':
                    data = data[data['exchange'] == exchange]
                
                print(f"✓ Đã lấy {len(data)} mã cổ phiếu")
                return data
            else:
                print("⚠ Không có dữ liệu")
                return None
                
        except Exception as e:
            print(f"✗ Lỗi khi lấy danh sách cổ phiếu: {e}")
            return None
    
    def get_trading_statistics(self, date=None):
        """
        Lấy thống kê giao dịch trong ngày
        date: Ngày cần lấy thống kê (format: 'YYYY-MM-DD')
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            print(f"\nĐang lấy thống kê giao dịch ngày {date}...")
            
            # Sử dụng API để lấy thống kê
            # Note: Có thể cần điều chỉnh tùy theo API hiện có
            stock = self.vnstock.stock(symbol='VNM', source='VCI')
            data = stock.trading.price_depth(symbol_ls=['VNM', 'FPT', 'VCB'])
            
            if data is not None:
                print(f"✓ Đã lấy thống kê giao dịch")
                return data
            else:
                print("⚠ Không có dữ liệu")
                return None
                
        except Exception as e:
            print(f"✗ Lỗi khi lấy thống kê: {e}")
            return None
    
    def get_top_movers(self, group='top_gain'):
        """
        Lấy danh sách cổ phiếu biến động mạnh
        group: 'top_gain' (tăng mạnh), 'top_lose' (giảm mạnh), 'top_volume' (khối lượng lớn)
        """
        try:
            print(f"\nĐang lấy danh sách {group}...")
            
            # Note: Feature này có thể cần điều chỉnh tùy API
            # Đây là placeholder, cần update khi có API phù hợp
            print("⚠ Tính năng đang được phát triển")
            return None
                
        except Exception as e:
            print(f"✗ Lỗi: {e}")
            return None
    
    def save_data(self, data, filename):
        """Lưu dữ liệu vào file CSV"""
        if data is None or data.empty:
            print(f"Không có dữ liệu để lưu cho {filename}")
            return False
        
        try:
            os.makedirs('data/market', exist_ok=True)
            filepath = f"data/market/{filename}"
            data.to_csv(filepath, index=True, encoding='utf-8-sig')
            print(f"✓ Đã lưu: {filepath}")
            return True
        except Exception as e:
            print(f"✗ Lỗi khi lưu file: {e}")
            return False

def main():
    print(f"{'='*60}")
    print("BẮT ĐẦU THU THẬP DỮ LIỆU THỊ TRƯỜNG")
    print(f"{'='*60}")
    
    crawler = MarketCrawler()
    
    # 1. Lấy dữ liệu chỉ số VN-Index
    for index_code in ['VNINDEX', 'HNX-INDEX']:
        index_data = crawler.get_market_index(index_code)
        if index_data is not None:
            print(f"\n--- {index_code} ---")
            print(index_data.head())
            crawler.save_data(
                index_data,
                f"{index_code}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
    
    # 2. Lấy danh sách tất cả mã cổ phiếu
    for exchange in ['HOSE', 'HNX', 'UPCOM']:
        symbols = crawler.get_all_symbols(exchange)
        if symbols is not None:
            print(f"\n--- Danh sách {exchange} ---")
            print(symbols.head())
            crawler.save_data(
                symbols,
                f"symbols_{exchange}_{datetime.now().strftime('%Y%m%d')}.csv"
            )
    
    print(f"\n{'='*60}")
    print("HOÀN THÀNH!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()