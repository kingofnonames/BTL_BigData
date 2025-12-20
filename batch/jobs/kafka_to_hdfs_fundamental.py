from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

KAFKA_BOOTSTRAP = "kafka:9092"
TOPIC = "stock_fundamental"
HDFS_PATH = "hdfs://namenode:8020/data/fundamental"

schema = MapType(StringType(), StringType())

spark = SparkSession.builder.appName("KafkaToHDFS-Fundamental").getOrCreate()

df_raw = spark.read.format("kafka").option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP).option("subscribe", TOPIC).option("startingOffsets", "earliest").load()
df = df_raw.select(
    from_json(col("value").cast("string"), schema).alias("data")
)

df.write.mode("overwrite").parquet(HDFS_PATH)

spark.stop()