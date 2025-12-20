import time
import json
import logging
from datetime import datetime, date
import pandas as pd

# --- IMPORT KAFKA ---
try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    print("  Chưa cài thư viện kafka-python. Dữ liệu sẽ chỉ in ra màn hình.")
    print("  Chạy lệnh: pip install kafka-python")
    KAFKA_AVAILABLE = False

# --- IMPORT VNSTOCK V3 ---
try:
    from vnstock import Vnstock
except ImportError:
    print(" Lỗi: Chưa cài đặt thư viện vnstock.")
    exit()

# ================= CẤU HÌNH HỆ THỐNG =================
# 1. Cấu hình Kafka
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092'] # Đổi IP nếu chạy server khác
KAFKA_TOPIC = 'stock_realtime_data'

# 2. Danh sách cổ phiếu (VN30)
SYMBOLS = [
    "ACB", "BCM", "BID", "BVH", "CTG", "FPT", "GAS", "GVR", "HDB", "HPG",
    "MBB", "MSN", "MWG", "PLX", "POW", "SAB", "SHB", "SSB", "SSI", "STB",
    "TCB", "TPB", "VCB", "VHM", "VIB", "VIC", "VJC", "VNM", "VPB", "VRE"
]

# 3. Chu kỳ lấy dữ liệu (giây)
SLEEP_TIME = 15 

# 4. Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

# ================= HÀM XỬ LÝ =================

def json_serializer(data):
    """
    Chuyển đổi dữ liệu sang JSON để gửi vào Kafka.
    Sử dụng default=str để xử lý các kiểu dữ liệu ngày tháng của Pandas.
    """
    return json.dumps(data, default=str).encode('utf-8')

def get_market_data(symbols_list):
    """
    Hàm lấy dữ liệu realtime sử dụng Vnstock v3 (Nguồn VCI)
    """
    all_dfs = []
    
    # Lấy tuần tự từng mã để tránh lỗi API
    for symbol in symbols_list:
        symbol = symbol.strip().upper()
        try:
            stock_obj = Vnstock().stock(symbol=symbol, source='VCI')
            df_one = None
            
            # Ưu tiên lấy intraday (khớp lệnh)
            if hasattr(stock_obj.quote, 'intraday'):
                try:
                    df_temp = stock_obj.quote.intraday()
                    if df_temp is not None and not df_temp.empty:
                        df_one = df_temp.tail(1).copy() # Lấy dòng mới nhất
                        if 'ticker' not in df_one.columns:
                            df_one['ticker'] = symbol
                except: pass

            # Fallback sang các hàm khác
            if df_one is None:
                if hasattr(stock_obj.quote, 'price_depth'):
                    try: df_one = stock_obj.quote.price_depth()
                    except: pass
                elif hasattr(stock_obj.quote, 'price'):
                    try: df_one = stock_obj.quote.price()
                    except: pass
                elif hasattr(stock_obj.quote, 'snapshot'):
                    try: df_one = stock_obj.quote.snapshot()
                    except: pass

            if df_one is not None and not df_one.empty:
                all_dfs.append(df_one)
            
            time.sleep(0.05) # Nghỉ cực ngắn
            
        except Exception as e:
            logger.error(f"Lỗi lấy mã {symbol}: {e}")
            continue

    if all_dfs:
        try:
            return pd.concat(all_dfs, ignore_index=True)
        except: return None
    return None

def run_producer():
    # --- 1. KHỞI TẠO KAFKA PRODUCER ---
    producer = None
    if KAFKA_AVAILABLE:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=json_serializer, # Tự động nén JSON
                request_timeout_ms=5000
            )
            logger.info(f" Đã kết nối thành công tới Kafka: {KAFKA_BOOTSTRAP_SERVERS}")
        except Exception as e:
            logger.error(f" Không thể kết nối Kafka: {e}")
            logger.warning("-> Chạy ở chế độ DRY-RUN (chỉ in ra màn hình, không gửi data).")

    logger.info("🚀 Bắt đầu luồng dữ liệu chứng khoán...")
    
    # --- 2. VÒNG LẶP CHÍNH ---
    while True:
        try:
            start_time = time.time()
            
            # A. Lấy dữ liệu
            df = get_market_data(SYMBOLS)
            
            if df is not None and not df.empty:
                records = df.to_dict(orient='records')
                count = 0
                
                # B. Gửi dữ liệu
                for record in records:
                    # Thêm timestamp thời gian gửi để tiện đo độ trễ
                    record['ingestion_time'] = datetime.now().isoformat()
                    
                    if producer:
                        # Gửi vào Kafka Topic
                        producer.send(KAFKA_TOPIC, value=record)
                        count += 1
                    else:
                        # Nếu không có Kafka thì thôi (hoặc print debug nếu muốn)
                        pass
                
                # Quan trọng: Đẩy dữ liệu đi ngay
                if producer:
                    producer.flush()
                
                logger.info(f"Đã xử lý {len(records)} mã. Gửi thành công {count} bản ghi vào topic '{KAFKA_TOPIC}'.")
                
                # In mẫu 1 dòng để kiểm tra
                if records:
                    sample = records[0]
                    ticker = sample.get('ticker', 'UNKNOWN')
                    print(f"   -> Sample: {ticker} | Price: {sample.get('price', 'N/A')} | Time: {sample.get('time', 'N/A')}")

            else:
                logger.warning("Không lấy được dữ liệu nào trong phiên này.")

            # C. Rate Limit
            elapsed_time = time.time() - start_time
            sleep_duration = max(0, SLEEP_TIME - elapsed_time)
            
            if sleep_duration > 0:
                logger.info(f"Đợi {sleep_duration:.1f}s...")
                time.sleep(sleep_duration)

        except KeyboardInterrupt:
            logger.info(" Đã dừng chương trình thủ công.")
            if producer: producer.close()
            break
        except Exception as e:
            logger.error(f" Lỗi vòng lặp chính: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_producer()
