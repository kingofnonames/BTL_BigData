from pyspark.sql.dataframe import DataFrame
from pyspark.sql.window import Window
from pyspark.sql.functions import col, avg, lag

def generate_features(df: DataFrame) -> DataFrame:
    """
    Tính toán các chỉ số kỹ thuật và các đặc trưng ML cần thiết.

    :param df: Spark DataFrame đã được làm sạch.
    :return: Spark DataFrame với các cột đặc trưng mới.
    """
    print("   -> Bắt đầu tính toán các đặc trưng...")
    
    window_spec = Window.partitionBy("symbol").orderBy("date")

    # 1. Tính toán Trung bình động Đơn giản (SMA) 20 ngày
    feature_df = df.withColumn(
        "SMA_20", 
        avg(col("close")).over(window_spec.rowsBetween(-19, 0)) # SMA 20
    )
    
    # 2. Tính toán Lợi suất (Return) 1 ngày
    feature_df = feature_df.withColumn(
        "prev_close", 
        lag(col("close"), 1).over(window_spec)
    ).withColumn(
        "daily_return", 
        (col("close") / col("prev_close")) - 1
    )
    feature_df = feature_df.drop("prev_close")
    feature_df = feature_df.dropna(subset=['SMA_20', 'daily_return'])
    
    print(f"   -> Đã tạo {len(feature_df.columns) - len(df.columns)} đặc trưng mới.")
    return feature_df.select('symbol', 'date', 'close', 'SMA_20', 'daily_return') # Chọn các cột quan trọng