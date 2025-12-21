import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, from_unixtime, date_format, to_date
from pyspark.sql.types import LongType, TimestampType, DateType

HDFS_PATH = os.getenv("HDFS_PATH", "hdfs://namenode:8020/data/ohlcv")
ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
ES_INDEX = os.getenv("ES_INDEX", "ohlcv_daily_v2")

spark = SparkSession.builder.appName("OHLCV-Daily").getOrCreate()

df = spark.read.parquet(HDFS_PATH)

if 'data' in df.columns:
    df_flat = df.select(
        "symbol",
        "interval",
        "trade_date",
        col("data.open").alias("open"),
        col("data.high").alias("high"),
        col("data.low").alias("low"),
        col("data.close").alias("close"),
        col("data.volume").alias("volume")
    )
else:
    df_flat = df.select(
        "symbol",
        "interval",
        "trade_date",
        "open",
        "high",
        "low",
        "close",
        "volume"
    )

dtype = df_flat.schema["trade_date"].dataType
if isinstance(dtype, (LongType, TimestampType)):
    df_flat = df_flat.withColumn(
        "trade_date",
        date_format(from_unixtime(col("trade_date") / 1000), "yyyy-MM-dd")
    )
elif isinstance(dtype, DateType):
    df_flat = df_flat.withColumn(
        "trade_date",
        date_format(col("trade_date"), "yyyy-MM-dd")
    )
else:
    df_flat = df_flat.withColumn("trade_date", to_date(col("trade_date"), "yyyy-MM-dd"))

df_flat = df_flat.withColumn(
    "es_id",
    concat_ws("_", col("symbol"), col("interval"), col("trade_date"))
)

df_flat.write.format("org.elasticsearch.spark.sql") \
    .option("es.nodes", ES_HOST.replace("http://", "")) \
    .option("es.resource", ES_INDEX) \
    .option("es.mapping.id", "es_id") \
    .mode("append") \
    .save()

spark.stop()
