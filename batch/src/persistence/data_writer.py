from pyspark.sql.dataframe import DataFrame
from config import Config

def write_processed_data(df: DataFrame, db_uri: str, db_table: str):
    """
    Ghi dữ liệu đã xử lý vào cơ sở dữ liệu đích (dùng JDBC/SQLAlchemy).

    :param df: Spark DataFrame chứa dữ liệu cuối cùng.
    :param db_uri: Chuỗi kết nối cơ sở dữ liệu.
    :param db_table: Tên bảng trong DB.
    """
    print(f"   -> Ghi {df.count()} hàng vào DB: {db_table}")
    
    final_df = df.select('symbol', 'date', 'close', 'SMA_20', 'daily_return', 'prediction')

    final_df.write \
        .format("jdbc") \
        .option("url", db_uri) \
        .option("dbtable", db_table) \
        .option("user", Config.DB_USER) 
        .option("password", Config.DB_PASSWORD) \
        .mode("overwrite")  # Thay đổi thành "append" nếu cần
        .save()
        
    print("   -> Đã ghi dữ liệu thành công.")