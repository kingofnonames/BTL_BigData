import json
import logging
import time
import sqlite3
from datetime import datetime
import pandas as pd

try:
    from kafka import KafkaConsumer
except ImportError:
    print(" Lỗi: Chưa cài đặt thư viện kafka-python.")
    exit()

# CẤU HÌNH
KAFKA_TOPIC = 'stock_realtime_data'
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
DB_NAME = 'stock_data.db' # Tên file database

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

def init_db():
    """Khởi tạo database SQLite và bảng dữ liệu"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tạo bảng nếu chưa có. Lưu ý: Dùng ticker làm khóa chính để update giá mới nhất
    c.execute('''
        CREATE TABLE IF NOT EXISTS realtime_prices (
            ticker TEXT PRIMARY KEY,
            price REAL,
            volume INTEGER,
            time TEXT,
            ingestion_time TEXT,
            match_type TEXT
        )
    ''')
    conn.commit()
    conn.close()
    logger.info(f" Đã khởi tạo Database: {DB_NAME}")

def save_to_sqlite(df_batch):
    """Lưu batch dữ liệu vào SQLite"""
    if df_batch.empty:
        return

    conn = sqlite3.connect(DB_NAME)
    try:
        # Sử dụng to_sql không hỗ trợ UPSERT (Update if exists) tốt trong pandas cũ
        # Nên ta dùng executeMany của sqlite3 để tối ưu
        
        data_to_insert = []
        for _, row in df_batch.iterrows():
            data_to_insert.append((
                row.get('ticker'),
                row.get('price'),
                row.get('volume'),
                str(row.get('time')),
                str(row.get('ingestion_time')),
                row.get('match_type')
            ))

        # Câu lệnh SQL: INSERT OR REPLACE (Nếu mã đã có thì ghi đè giá mới nhất)
        conn.executemany('''
            INSERT OR REPLACE INTO realtime_prices (ticker, price, volume, time, ingestion_time, match_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', data_to_insert)
        
        conn.commit()
        logger.info(f" Đã lưu {len(df_batch)} bản ghi vào DB.")
    except Exception as e:
        logger.error(f"Lỗi lưu DB: {e}")
    finally:
        conn.close()

def run_consumer():
    init_db() # Tạo DB trước khi chạy
    
    logger.info("🎬 Đang khởi động Consumer...")
    
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        group_id='stock-db-saver-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    
    logger.info(f"✅ Đã kết nối Topic '{KAFKA_TOPIC}'.")
    
    batch_data = []
    last_process_time = time.time()
    
    for message in consumer:
        record = message.value
        record['ingestion_time'] = datetime.now().isoformat()
        batch_data.append(record)
        
        # Xử lý theo Batch (mỗi 5 bản ghi hoặc 2 giây) để giảm tải IO Database
        current_time = time.time()
        if len(batch_data) >= 5 or (current_time - last_process_time > 2 and len(batch_data) > 0):
            
            df = pd.DataFrame(batch_data)
            
            # 1. In ra màn hình để debug
            print(f"\n--- NHẬN {len(batch_data)} MÃ LÚC {datetime.now().strftime('%H:%M:%S')} ---")
            print(df[['ticker', 'price', 'time']].head(3).to_string(index=False)) # Chỉ in 3 dòng đầu
            
            # 2. Lưu vào Database (Serving Layer)
            save_to_sqlite(df)
            
            batch_data = []
            last_process_time = current_time

if __name__ == "__main__":
    run_consumer()
