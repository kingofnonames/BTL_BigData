import time
import json
from kafka import KafkaProducer
from vnstock import stock_quote
from datetime import datetime

# --- CẤU HÌNH ---
TOPIC_NAME = "stock_realtime"
BOOTSTRAP_SERVERS = ['localhost:9092']
WATCH_LIST = ["FPT", "MWG", "TCB", "HPG", "VNM"]

# [CACHE] Lưu trữ tổng volume của lần quét trước đó
# Cấu trúc: { "TCB": 10500, "FPT": 5000, ... }
cache_volume = {}

def create_producer():
    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

def fetch_and_send():
    producer = create_producer()
    print(f"--- [INGESTION] Bắt đầu theo dõi: {WATCH_LIST} ---")
    print("--- [INFO] Chỉ gửi dữ liệu khi có giao dịch khớp lệnh mới (Volume tăng) ---")

    while True:
        try:
            # Lấy dữ liệu snapshot hiện tại
            df = stock_quote(WATCH_LIST)

            if df.empty:
                time.sleep(1)
                continue

            for index, row in df.iterrows():
                ticker = str(row['ticker'])
                current_total_vol = int(row['volume'])
                current_price = float(row['price'])
                
                # --- LOGIC TÍNH DELTA VOLUME ---
                tick_vol = 0
                
                if ticker not in cache_volume:
                    # Lần đầu tiên chạy script:
                    # Ta chỉ lưu lại trạng thái, KHÔNG gửi total volume vào Kafka 
                    # để tránh cây nến đầu tiên bị sai lệch (quá to).
                    cache_volume[ticker] = current_total_vol
                    print(f"[INIT] Đã khởi tạo cache cho {ticker}. Vol tích lũy: {current_total_vol}")
                    continue 
                else:
                    # Các lần sau: Tính chênh lệch
                    prev_vol = cache_volume[ticker]
                    
                    # Xử lý trường hợp qua ngày mới (Volume reset về 0) hoặc dữ liệu bị reset
                    if current_total_vol < prev_vol:
                        tick_vol = current_total_vol
                    else:
                        tick_vol = current_total_vol - prev_vol

                    # Cập nhật cache
                    cache_volume[ticker] = current_total_vol

                # --- CHỈ GỬI KHI CÓ GIAO DỊCH MỚI ---
                # Nếu tick_vol == 0 nghĩa là trong 1s qua không ai mua bán gì cả -> Bỏ qua
                if tick_vol > 0:
                    message = {
                        "ticker": ticker,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "price": current_price,
                        "volume": tick_vol  # Gửi volume thực tế của tick này
                    }
                    
                    producer.send(TOPIC_NAME, value=message)
                    print(f"[SENT] {ticker} | Price: {current_price} | Vol+: {tick_vol}")
            
            # Thời gian nghỉ giữa các lần request
            time.sleep(1)

        except Exception as e:
            print(f"!!! [ERROR]: {e}")
            time.sleep(3) # Nghỉ lâu hơn xíu nếu gặp lỗi mạng
        except KeyboardInterrupt:
            print("\n--- Đã dừng Producer ---")
            break

if __name__ == "__main__":
    fetch_and_send()
