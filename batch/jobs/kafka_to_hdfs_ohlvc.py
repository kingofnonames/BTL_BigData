from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date
from pyspark.sql.types import *

KAFKA_BOOTSTRAP = "kafka:9092"
TOPIC = "stock_ohlcv"
HDFS_PATH = "hdfs://namenode:8020/data/ohlcv"

schema = StructType([
    StructField("symbol", StringType()),
    StructField("interval", StringType()),
    StructField("open", DoubleType()),
    StructField("high", DoubleType()),
    StructField("low", DoubleType()),
    StructField("close", DoubleType()),
    StructField("volume", DoubleType()),
    StructField("timestamp", StringType())
])

spark = SparkSession.builder \
    .appName("KafkaToHDFS-OHLCV") \
    .getOrCreate()

df_raw = spark.read.format("kafka").option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP).option("subscribe", TOPIC).option("startingOffsets", "earliest").load()

df = df_raw.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

df = df.withColumn("trade_date", to_date(col("timestamp")))

df.write.mode("overwrite").partitionBy("symbol", "interval", "trade_date").parquet(HDFS_PATH)

spark.stop()
