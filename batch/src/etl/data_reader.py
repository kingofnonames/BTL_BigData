from pyspark.sql import SparkSession
from pyspark.sql.dataframe import DataFrame

def read_raw_data(spark: SparkSession, path: str) -> DataFrame:
    """
    Đọc dữ liệu thô từ nguồn lưu trữ (ví dụ: Parquet/CSV).

    :param spark: Spark Session hiện tại.
    :param path: Đường dẫn đến dữ liệu thô.
    :return: Spark DataFrame chứa dữ liệu thô.
    """
    print(f"   -> Đọc dữ liệu từ: {path}")
    # Giả sử dữ liệu được lưu dưới dạng Parquet
    df = spark.read.parquet(path)
    
    # Cần phải thêm logic schema khi đọc dữ liệu thực tế
    return df