"""
Crawler để thu thập dữ liệu giá lịch sử (OHLCV - Open, High, Low, Close, Volume)
Hỗ trợ nhiều khung thời gian: 1D, 1W, 1M
"""
from vnstock import Vnstock
import pandas as pd
from datetime import datetime, timedelta
import os

class HistoricalOHLCVCrawler:
    def __init__(self, symbol, source='VCI'):
        """
        Khởi tạo crawler
        symbol: Mã cổ phiếu (vd: 'FPT', 'VNM', 'VCB')
        source: Nguồn dữ liệu - 'VCI' hoặc 'TCBS'
        """
        self.symbol = symbol.upper()
        self.stock = Vnstock().stock(symbol=self.symbol, source=source)
        
    def get_historical_data(self, start_date, end_date, interval='1D'):
        """
        Lấy dữ liệu OHLCV
        interval: '1m', '5m', '15m', '30m', '1H', '1D', '1W', '1M'
        """
        try:
            print(f"\n[{self.symbol}] Đang lấy dữ liệu từ {start_date} đến {end_date} (interval: {interval})...")
            
            data = self.stock.quote.history(
                start=start_date,
                end=end_date,
                interval=interval
            )
            
            if data is not None and not data.empty:
                print(f"✓ Đã lấy {len(data)} dòng dữ liệu")
                return data
            else:
                print("⚠ Không có dữ liệu")
                return None
                
        except Exception as e:
            print(f"✗ Lỗi khi lấy dữ liệu: {e}")
            return None
    
    def get_intraday_data(self, date=None, page_size=500):
        """
        Lấy dữ liệu trong ngày (intraday) theo từng phút
        date: Ngày cần lấy (format: 'YYYY-MM-DD'), mặc định là hôm nay
        """
        try:
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            
            print(f"\n[{self.symbol}] Đang lấy dữ liệu intraday ngày {date}...")
            
            data = self.stock.quote.intraday(date=date, page_size=page_size)
            
            if data is not None and not data.empty:
                print(f"✓ Đã lấy {len(data)} tick")
                return data
            else:
                print("⚠ Không có dữ liệu intraday")
                return None
                
        except Exception as e:
            print(f"✗ Lỗi khi lấy dữ liệu intraday: {e}")
            return None
    
    def save_data(self, data, filename):
        """Lưu dữ liệu vào file CSV"""
        if data is None or data.empty:
            print(f"Không có dữ liệu để lưu cho {filename}")
            return False
        
        try:
            # Tạo thư mục data nếu chưa có
            os.makedirs('data/ohlcv', exist_ok=True)
            
            filepath = f"data/ohlcv/{filename}"
            data.to_csv(filepath, index=True, encoding='utf-8-sig')
            print(f"✓ Đã lưu: {filepath}")
            return True
        except Exception as e:
            print(f"✗ Lỗi khi lưu file: {e}")
            return False

    def resample_ohlcv(self, data: pd.DataFrame, interval: str):
        # 1️⃣ Tìm cột thời gian hợp lệ
        time_cols = ['timestamp', 'time', 'date', 'Date', 'datetime']
        time_col = None
        for col in time_cols:
            if col in data.columns:
                time_col = col
                break

        if time_col is None:
            logging.error(f"[Resample] Không tìm thấy cột thời gian trong DataFrame! Các cột hiện có: {data.columns.tolist()}")
            return None

        # 2️⃣ Chuẩn hóa thời gian
        data[time_col] = pd.to_datetime(data[time_col], errors='coerce')
        data = data.dropna(subset=[time_col])
        data.set_index(time_col, inplace=True)

        # 3️⃣ Chọn quy tắc resample
        if interval == '1D':
            return data.reset_index()
        elif interval == '1W':
            rule = 'W'
        elif interval == '1M':
            rule = 'M'
        else:
            raise ValueError(f"Unsupported interval: {interval}")

        # 4️⃣ Thực hiện resample
        ohlcv_resampled = data.resample(rule).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()

        ohlcv_resampled.reset_index(inplace=True)
        return ohlcv_resampled


def main():
    # Thiết lập tham số
    symbol = 'FPT'
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 năm dữ liệu
    
    print(f"{'='*60}")
    print(f"BẮT ĐẦU THU THẬP DỮ LIỆU OHLCV - {symbol}")
    print(f"{'='*60}")
    
    # Khởi tạo crawler
    crawler = HistoricalOHLCVCrawler(symbol)
    
    # 1. Dữ liệu theo ngày (1D)
    daily_data = crawler.get_historical_data(start_date, end_date, interval='1D')
    if daily_data is not None:
        print("\n--- 5 dòng đầu tiên (Daily) ---")
        print(daily_data.head())
        print("\n--- Thông tin DataFrame ---")
        print(daily_data.info())
        crawler.save_data(
            daily_data,
            f"{symbol}_daily_{start_date}_to_{end_date}.csv"
        )
    
    # 2. Dữ liệu theo tuần (1W)
    weekly_data = crawler.resample_ohlcv(daily_data, interval='1W') if daily_data is not None else None
    if weekly_data is not None:
        print("\n--- 5 dòng đầu tiên (Weekly) ---")
        print(weekly_data.head())
        crawler.save_data(
            weekly_data,
            f"{symbol}_weekly_{start_date}_to_{end_date}.csv"
        )
    
    # 3. Dữ liệu theo tháng (1M)
    monthly_data = crawler.resample_ohlcv(daily_data, interval='1M') if daily_data is not None else None
    if monthly_data is not None:
        print("\n--- 5 dòng đầu tiên (Monthly) ---")
        print(monthly_data.head())
        crawler.save_data(
            monthly_data,
            f"{symbol}_monthly_{start_date}_to_{end_date}.csv"
        )
    
    # 4. Dữ liệu intraday (nếu là ngày giao dịch)
    intraday_data = crawler.get_intraday_data()
    if intraday_data is not None:
        print("\n--- 5 tick đầu tiên (Intraday) ---")
        print(intraday_data.head())
        crawler.save_data(
            intraday_data,
            f"{symbol}_intraday_{datetime.now().strftime('%Y%m%d')}.csv"
        )
    
    print(f"\n{'='*60}")
    print("HOÀN THÀNH!")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()