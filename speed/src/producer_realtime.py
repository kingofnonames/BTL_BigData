import time
import json
import logging
from datetime import datetime
import pandas as pd

# --- IMPORT MỚI CHO VNSTOCK V3 ---
# Thay vì import price_board, ta import class Vnstock
try:
    from vnstock import Vnstock
except ImportError:
    print("Lỗi: Chưa cài đặt thư viện vnstock hoặc phiên bản không đúng.")
    print("Vui lòng chạy: pip install vnstock --upgrade")
    exit()

# CẤU HÌNH
# Danh sách mã cổ phiếu cần theo dõi (Ví dụ: VN30)
SYMBOLS = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
]

# Chu kỳ lấy dữ liệu (giây) - Nên để > 5s để tránh bị chặn IP
SLEEP_TIME = 15 

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_market_data(symbols_list):
    """
    Hàm lấy dữ liệu realtime sử dụng Vnstock v3
    Nguồn: VCI (Vietcap)
    Cơ chế: Lấy từng mã (Iterative) do API VCI/Vnstock validation chặn batch string.
    """
    all_dfs = []
    
    # Duyệt qua từng mã để lấy dữ liệu (An toàn nhất để tránh lỗi Invalid Symbol)
    for symbol in symbols_list:
        symbol = symbol.strip().upper()
        try:
            # Khởi tạo đối tượng Vnstock với nguồn VCI cho từng mã riêng biệt
            stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
            
            df_one = None
            
            # --- CƠ CHẾ TỰ ĐỘNG TÌM HÀM LẤY GIÁ (UPDATED) ---
            # Dựa trên log debug: ['history', 'intraday', 'price_depth', ...]
            
            # Ưu tiên 1: 'intraday' - Lấy dữ liệu khớp lệnh trong ngày
            if hasattr(stock_obj.quote, 'intraday'):
                try:
                    # Lấy dữ liệu intraday
                    df_temp = stock_obj.quote.intraday()
                    if df_temp is not None and not df_temp.empty:
                        # Chỉ lấy dòng cuối cùng (giá mới nhất hiện tại)
                        df_one = df_temp.tail(1).copy()
                        # Đảm bảo có cột ticker để định danh
                        if 'ticker' not in df_one.columns:
                            df_one['ticker'] = symbol
                except Exception as e_intra:
                    logger.warning(f"Lỗi gọi intraday cho {symbol}: {e_intra}")

            # Ưu tiên 2: 'price_depth' - Độ sâu giá (nếu intraday lỗi)
            if df_one is None and hasattr(stock_obj.quote, 'price_depth'):
                try:
                    df_one = stock_obj.quote.price_depth()
                except:
                    pass

            # Ưu tiên 3: Các hàm cũ (price, snapshot) để backup
            if df_one is None:
                if hasattr(stock_obj.quote, 'price'):
                    df_one = stock_obj.quote.price()
                elif hasattr(stock_obj.quote, 'snapshot'):
                    df_one = stock_obj.quote.snapshot()
            
            # Nếu vẫn không tìm thấy hàm nào phù hợp
            if df_one is None and symbol == symbols_list[0]:
                 attrs = [d for d in dir(stock_obj.quote) if not d.startswith('__')]
                 logger.error(f"DEBUG: Không lấy được data. Các hàm có sẵn: {attrs}")

            # Kiểm tra và gom dữ liệu
            if df_one is not None and not df_one.empty:
                all_dfs.append(df_one)
            
            # Nghỉ cực ngắn để tránh spam request liên tục gây overload cục bộ
            time.sleep(0.05)
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy mã {symbol}: {e}")
            continue

    # Gộp tất cả dataframe đơn lẻ thành 1 bảng lớn
    if all_dfs:
        try:
            final_df = pd.concat(all_dfs, ignore_index=True)
            return final_df
        except Exception as e:
            logger.error(f"Lỗi khi gộp dữ liệu: {e}")
            return None
    else:
        logger.warning("Không lấy được dữ liệu nào từ danh sách.")
        return None

def json_serializer(data):
    """Helper để convert object sang JSON string"""
    return json.dumps(data).encode('utf-8')

def run_producer():
    logger.info("Bắt đầu chạy Producer Realtime (Vnstock v3 - Source: VCI)...")
    
    while True:
        try:
            start_time = time.time()
            
            # 1. Lấy dữ liệu
            df = get_market_data(SYMBOLS)
            
            if df is not None and not df.empty:
                # 2. Xử lý dữ liệu
                # Convert DataFrame sang list of dicts để gửi đi
                records = df.to_dict(orient='records')
                
                logger.info(f"Đã lấy thành công {len(records)} bản ghi.")
                
                # 3. Gửi dữ liệu (MÔ PHỎNG)
                for record in records:
                    # --- KAFKA PRODUCER CODE ---
                    # producer.send('stock-topic', value=record)
                    pass
                
                # Hiển thị mẫu 1 dòng dữ liệu để kiểm tra
                if records:
                    # Tìm key chứa mã chứng khoán (thường là 'ticker', 'symbol' hoặc 'code')
                    first_record = records[0]
                    ticker_key = next((k for k in first_record.keys() if k.lower() in ['ticker', 'symbol', 'code']), None)
                    ticker_val = first_record.get(ticker_key, 'N/A') if ticker_key else 'N/A'
                    
                    print(f"Sample Data ({datetime.now().strftime('%H:%M:%S')}): {ticker_val} - {first_record}")

            # 4. Nghỉ (Rate limit)
            # Tính toán thời gian thực thi để sleep chính xác
            elapsed_time = time.time() - start_time
            sleep_duration = max(0, SLEEP_TIME - elapsed_time)
            
            logger.info(f"Đang chờ {sleep_duration:.2f}s cho lần lấy tiếp theo...")
            time.sleep(sleep_duration)

        except KeyboardInterrupt:
            logger.info("Đã dừng Producer.")
            break
        except Exception as e:
            logger.error(f"Lỗi không mong muốn trong vòng lặp chính: {e}")
            time.sleep(5) # Nghỉ ngắn nếu lỗi hệ thống

if __name__ == "__main__":
    run_producer()
