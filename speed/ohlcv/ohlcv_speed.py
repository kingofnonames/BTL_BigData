import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, current_timestamp,
    to_timestamp, lag
)
from pyspark.sql.types import *
from pyspark.sql.window import Window

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC_SPEED_STOCK", "stock.market.speed.raw")
ES_HOST = os.getenv("ES_HOST", "elasticsearch")
ES_INDEX = os.getenv("ES_INDEX_SPEED_STOCK", "stock_intraday")
EMA_PERIOD = int(os.getenv("EMA_PERIOD", "5"))
CHECKPOINT = "/tmp/checkpoints/ohlcv_speed"
spark = SparkSession.builder \
    .appName("OHLCV-Speed-Streaming") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("time", StringType()),
    StructField("symbol", StringType()),
    StructField("open", DoubleType()),
    StructField("high", DoubleType()),
    StructField("low", DoubleType()),
    StructField("close", DoubleType()),
    StructField("volume", IntegerType())
])

raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

df = (
    raw.select(from_json(col("value").cast("string"), schema).alias("d"))
       .select("d.*")
       .withColumn("time", to_timestamp("time"))
       .withColumn("ingestion_time", current_timestamp())
)

def write_to_es(batch_df, batch_id):
    if batch_df.isEmpty():
        return

    k = 2 / (EMA_PERIOD + 1)

    w = Window.partitionBy("symbol").orderBy("time")

    batch_df = (
        batch_df
        .withColumn("prev_close", lag("close").over(w))
        .withColumn(
            "ema",
            col("close") * k +
            col("prev_close") * (1 - k)
        )
        .drop("prev_close")
        .withColumn(
            "es_id",
            col("symbol") + "_" + col("time").cast("string")
        )
    )

    batch_df.write \
        .format("org.elasticsearch.spark.sql") \
        .mode("append") \
        .option("es.nodes", ES_HOST) \
        .option("es.port", "9200") \
        .option("es.resource", ES_INDEX) \
        .option("es.mapping.id", "es_id") \
        .save()

query = df.writeStream \
    .foreachBatch(write_to_es) \
    .option("checkpointLocation", CHECKPOINT) \
    .trigger(processingTime="10 seconds") \
    .start()

query.awaitTermination()
