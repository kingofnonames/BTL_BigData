import os
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_timestamp, window, first, last, max, min, sum, concat_ws, date_format
from pyspark.sql.types import StructType, StringType, DoubleType, LongType

# --- CẤU HÌNH ---
KAFKA_TOPIC = "stock_realtime"
KAFKA_SERVER = "localhost:9092"
ES_INDEX = "stock_ohlcv_realtime" 
ES_HOST = "localhost"
ES_PORT = "9200"

# [QUAN TRỌNG] Đổi đường dẫn này sang thư mục cố định, không dùng /tmp
CHECKPOINT_DIR = "./spark_checkpoints/ohlcv_realtime" 

schema = StructType() \
    .add("ticker", StringType()) \
    .add("timestamp", StringType()) \
    .add("price", DoubleType()) \
    .add("volume", LongType())

def create_spark_session():
    # Giữ nguyên config packages
    packages = [
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0",
        "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.1"
    ]
    os.environ['PYSPARK_SUBMIT_ARGS'] = f'--packages {",".join(packages)} pyspark-shell'
    
    return SparkSession.builder \
        .appName("StockOHLCV_Calculator") \
        .master("local[*]") \
        .config("spark.es.nodes", ES_HOST) \
        .config("spark.es.port", ES_PORT) \
        .config("spark.es.nodes.wan.only", "true") \
        .getOrCreate()

def run_speed_layer():
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")
    
    print("--- [PROCESSING] Đang tính toán OHLCV từ luồng Real-time... ---")

    # 1. READ STREAM
    df_kafka = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_SERVER) \
        .option("subscribe", KAFKA_TOPIC) \
        .option("startingOffsets", "latest") \
        .load()

    # 2. PARSE & CLEAN
    df_clean = df_kafka.select(from_json(col("value").cast("string"), schema).alias("data")) \
                       .select("data.*") \
                       .dropna() \
                       .withColumn("timestamp", to_timestamp(col("timestamp"), "yyyy-MM-dd HH:mm:ss")) \
                       .withWatermark("timestamp", "1 minute") 

    # 3. AGGREGATE
    # Logic này ĐÚNG vì Producer đã gửi delta volume, nên ta dùng SUM là chuẩn.
    df_ohlcv = df_clean.groupBy(
        window(col("timestamp"), "1 minute"), 
        col("ticker")
    ).agg(
        first("price").alias("open"),
        max("price").alias("high"),
        min("price").alias("low"),
        last("price").alias("close"),
        sum("volume").alias("volume") 
    ).select(
        col("window.start").alias("time"),
        col("ticker"),
        col("open"),
        col("high"),
        col("low"),
        col("close"),
        col("volume")
    )

    # [MỚI] Tạo doc_id để tránh trùng lặp trong Elasticsearch
    # ID sẽ có dạng: "FPT_2023-10-27T09:00:00"
    df_final = df_ohlcv.withColumn(
        "doc_id", 
        concat_ws("_", col("ticker"), date_format(col("time"), "yyyy-MM-dd'T'HH:mm:ss"))
    )

    print("--- Schema Final ---")
    df_final.printSchema()

    # 4. WRITE STREAM
    query = df_final.writeStream \
        .format("org.elasticsearch.spark.sql") \
        .option("es.resource", ES_INDEX) \
        .option("checkpointLocation", CHECKPOINT_DIR) \
        .option("es.mapping.id", "doc_id") \
        .option("es.write.operation", "upsert") \
        .outputMode("append") \
        .start()

    print(f">>> [READY] Đang đẩy nến vào Elastic. Checkpoint tại: {CHECKPOINT_DIR}")
    
    query.awaitTermination()

if __name__ == "__main__":
    run_speed_layer()
