import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date
from pyspark.sql.types import *

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "stock.ohlcv.raw")
HDFS_PATH = os.getenv("HDFS_PATH", "hdfs://namenode:8020/data/ohlcv")
PARTITION_COLS = os.getenv("PARTITION_COLS", "symbol,interval,trade_date").split(",")

schema = StructType([
    StructField("symbol", StringType()),
    StructField("interval", StringType()),
    StructField("event_date", StringType()),
    StructField("event_time", StringType()),
    StructField("source", StringType()),
    StructField("data", StructType([
        StructField("open", DoubleType()),
        StructField("high", DoubleType()),
        StructField("low", DoubleType()),
        StructField("close", DoubleType()),
        StructField("volume", LongType())
    ]))
])


spark = SparkSession.builder \
    .appName(f"BatchKafkaToHDFS-OHLCV-{TOPIC}") \
    .getOrCreate()

df_raw = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("subscribe", TOPIC) \
    .option("startingOffsets", "earliest") \
    .load()

df = df_raw.select(
    from_json(col("value").cast("string"), schema).alias("parsed")
).select(
    "parsed.symbol",
    "parsed.interval",
    "parsed.event_date",
    "parsed.event_time",
    "parsed.source",
    col("parsed.data.open").alias("open"),
    col("parsed.data.high").alias("high"),
    col("parsed.data.low").alias("low"),
    col("parsed.data.close").alias("close"),
    col("parsed.data.volume").alias("volume")
)

df = df.withColumn("trade_date", to_date(col("event_date")))
df.write.mode("append").partitionBy(*PARTITION_COLS).parquet(HDFS_PATH)

spark.stop()
