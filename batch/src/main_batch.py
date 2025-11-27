from pyspark.sql import SparkSession
from config import Config

from etl import read_raw_data, clean_data, generate_features 
from ml import train_and_save_model, load_and_predict 
from persistence.data_writer import write_processed_data

def run_batch_pipeline():
    """
    Khởi tạo Spark Session và chạy toàn bộ quy trình xử lý batch.
    """
    print("--- 1. Bắt đầu quy trình Batch ---")
    
    # 1. Khởi tạo Spark Session
    spark = SparkSession.builder \
        .appName(Config.SPARK_APP_NAME) \
        .master(Config.SPARK_MASTER) \
        .getOrCreate()
    
    try:
        # 2. Đọc Dữ liệu (Dùng hàm đã được re-export từ etl)
        raw_df = read_raw_data(spark, Config.RAW_DATA_PATH)
        
        # 3. Làm sạch Dữ liệu (Dùng hàm đã được re-export từ etl)
        cleaned_df = clean_data(raw_df)
        
        # 4. Tính toán các Đặc trưng (Dùng hàm đã được re-export từ etl)
        feature_df = generate_features(cleaned_df)
        
        # 5. Huấn luyện Mô hình (Thực hiện nếu cần)
        train_and_save_model(feature_df, Config.MODEL_PATH)
        
        # 6. Tải Mô hình và Dự đoán (Dùng hàm đã được re-export từ ml)
        prediction_df = load_and_predict(feature_df, Config.MODEL_PATH)
        
        # 7. Ghi Dữ liệu Đã xử lý (Loading)
        write_processed_data(prediction_df, Config.DB_URI, Config.DB_TABLE)
        
        print("--- 8. Quy trình Batch hoàn thành thành công! ---")
        
    except Exception as e:
        print(f"LỖI trong quá trình xử lý Batch: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    run_batch_pipeline()