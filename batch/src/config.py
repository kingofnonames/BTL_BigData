import os
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env (nếu có)
load_dotenv()

class Config:
    """Class chứa các cấu hình quan trọng của dự án."""
    
    # Cấu hình Spark
    SPARK_APP_NAME = "StockBatchProcessor"
    SPARK_MASTER = os.getenv("SPARK_MASTER", "local[*]") 
    
    # Cấu hình Nguồn Dữ liệu Thô
    RAW_DATA_PATH = os.getenv("RAW_DATA_PATH", "s3a://your-bucket/raw_data/")
    
    # Cấu hình Cơ sở Dữ liệu Đích (Dùng cho SQLAlchemy)
    DB_URI = os.getenv("DB_URI", "sqlite:///processed_data.db")
    DB_TABLE = "stock_features"
    
    # Đường dẫn lưu mô hình ML (dùng cho joblib/pickle)
    MODEL_PATH = os.getenv("MODEL_PATH", "/tmp/models/stock_predictor.pkl")