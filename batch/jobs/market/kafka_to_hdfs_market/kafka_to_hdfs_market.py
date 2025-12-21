import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, to_date
from pyspark.sql.types import *
KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "stock.market.raw")
HDFS_PATH = os.getenv("HDFS_PATH", "hdfs://namenode:8020/data/market")
PARTITION_COLS = ["index_code", "trade_date"]


schema = StructType([
    StructField("event_type", StringType()),
    StructField("index_code", StringType()),
    StructField("event_date", StringType()),
    StructField("event_time", StringType()),
    StructField("ingest_time", StringType()),
    StructField("source", StringType()),
    StructField("year", IntegerType()),
    StructField("month", IntegerType()),
    StructField("data", StructType([
        StructField("open", DoubleType()),
        StructField("high", DoubleType()),
        StructField("low", DoubleType()),
        StructField("close", DoubleType()),
        StructField("volume", LongType())
    ]))
])
spark = SparkSession.builder \
    .appName(f"BatchKafkaToHDFS-Market-{TOPIC}") \
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
    "parsed.event_type",
    "parsed.index_code",
    "parsed.event_date",
    "parsed.event_time",
    "parsed.ingest_time",
    "parsed.source",
    "parsed.year",
    "parsed.month",
    col("parsed.data.open").alias("open"),
    col("parsed.data.high").alias("high"),
    col("parsed.data.low").alias("low"),
    col("parsed.data.close").alias("close"),
    col("parsed.data.volume").alias("volume")
)
df = df.withColumn("trade_date", to_date(col("event_date")))
df.write.mode("overwrite").partitionBy(*PARTITION_COLS).parquet(HDFS_PATH)
spark.stop()
