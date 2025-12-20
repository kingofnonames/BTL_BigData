from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, to_date
from pyspark.sql.types import *

KAFKA_BOOTSTRAP = "kafka:9092"
TOPIC = "stock_market"
HDFS_PATH = "hdfs://namenode:8020/data/market"

schema = StructType([
    StructField("index", StringType()),
    StructField("open", DoubleType()),
    StructField("high", DoubleType()),
    StructField("low", DoubleType()),
    StructField("close", DoubleType()),
    StructField("volume", DoubleType()),
    StructField("timestamp", StringType())
])

spark = SparkSession.builder.appName("KafkaToHDFS-Market").getOrCreate()
df_raw = spark.read.format("kafka").option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP).option("subscribe", TOPIC).option("startingOffsets", "earliest").load()
df = df_raw.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

df = df.withColumn("trade_date", to_date(col("timestamp")))
df.write.mode("overwrite").partitionBy("index", "trade_date").parquet(HDFS_PATH)

spark.stop()