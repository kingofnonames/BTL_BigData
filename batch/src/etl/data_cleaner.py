from pyspark.sql.dataframe import DataFrame
from pyspark.sql.functions import col, when

def clean_data(df: DataFrame) -> DataFrame:
    """
    Thực hiện các bước làm sạch dữ liệu cơ bản.

    :param df: Spark DataFrame đầu vào.
    :return: Spark DataFrame đã được làm sạch.
    """
    print("   -> Bắt đầu làm sạch dữ liệu...")
    
    # 1. Xử lý giá trị NULL: Loại bỏ các hàng thiếu giá trị CLOSE quan trọng
    cleaned_df = df.dropna(subset=['close'])
    
    # 2. Xử lý giá trị ngoại lệ (ví dụ: volume âm hoặc 0)
    cleaned_df = cleaned_df.filter(col('volume') > 0)
    
    # 3. Chuẩn hóa tên cột/định dạng
    cleaned_df = cleaned_df.withColumnRenamed("bank_source", "source")
    
    print(f"   -> Dữ liệu đã làm sạch: {cleaned_df.count()} hàng")
    return cleaned_df