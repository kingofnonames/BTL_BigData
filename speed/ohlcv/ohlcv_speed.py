# import os
# from pyspark.sql import SparkSession
# from pyspark.sql.functions import col, from_json, current_timestamp, concat_ws, expr
# from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
# from pyspark.sql.streaming import GroupState, GroupStateTimeout
# from pyspark.sql.functions import struct
# from pyspark.sql import Row

# KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
# KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "stock_ticks")
# ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
# ES_INDEX = os.getenv("ES_INDEX", "stock_intraday")
# CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH", "/tmp/checkpoints/stock_speed")
# EMA_PERIOD = int(os.getenv("EMA_PERIOD", "5"))

# spark = SparkSession.builder \
#     .appName("StockSpeedLayer") \
#     .config(
#         "spark.jars.packages",
#         "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.2,"
#         "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0"
#     ) \
#     .getOrCreate()
# spark.sparkContext.setLogLevel("WARN")

# schema = StructType([
#     StructField("time", StringType(), True),
#     StructField("symbol", StringType(), True),
#     StructField("open", DoubleType(), True),
#     StructField("high", DoubleType(), True),
#     StructField("low", DoubleType(), True),
#     StructField("close", DoubleType(), True),
#     StructField("volume", IntegerType(), True)
# ])

# kafka_df = spark.readStream \
#     .format("kafka") \
#     .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP) \
#     .option("subscribe", KAFKA_TOPIC) \
#     .option("startingOffsets", "latest") \
#     .load()

# parsed_df = kafka_df.select(from_json(col("value").cast("string"), schema).alias("data")).select("data.*")
# parsed_df = parsed_df.withColumn("time", col("time").cast(TimestampType()))
# parsed_df = parsed_df.withColumn("ingestion_time", current_timestamp())

# def ema_update(symbol, rows, state: GroupState):
#     """
#     rows: iterator of rows for a symbol
#     state: previous EMA value
#     """
#     k = 2 / (EMA_PERIOD + 1)
#     result = []

#     prev_ema = state.get("ema") if state.exists else None

#     for row in sorted(rows, key=lambda x: x.time):
#         close = row.close
#         if prev_ema is None:
#             ema = close
#         else:
#             ema = close * k + prev_ema * (1 - k)
#         prev_ema = ema

#         new_row = row.asDict()
#         new_row["ema"] = ema
#         new_row["es_id"] = f"{row.symbol}_{row.time}"
#         result.append(new_row)

#     state.update({"ema": prev_ema})
#     state.setTimeoutDuration("1 hour")
#     return result

# grouped_df = parsed_df.groupBy("symbol").applyInPandasWithState(
#     func=ema_update,
#     outputStructType=StructType([
#         StructField("time", TimestampType()),
#         StructField("symbol", StringType()),
#         StructField("open", DoubleType()),
#         StructField("high", DoubleType()),
#         StructField("low", DoubleType()),
#         StructField("close", DoubleType()),
#         StructField("volume", IntegerType()),
#         StructField("ingestion_time", TimestampType()),
#         StructField("ema", DoubleType()),
#         StructField("es_id", StringType())
#     ]),
#     stateStructType=StructType([
#         StructField("ema", DoubleType())
#     ]),
#     outputMode="update",
#     timeoutConf="ProcessingTimeTimeout"
# )
# query = grouped_df.writeStream \
#     .format("org.elasticsearch.spark.sql") \
#     .option("checkpointLocation", CHECKPOINT_PATH) \
#     .option("es.nodes", ES_HOST.replace("http://", "")) \
#     .option("es.resource", ES_INDEX) \
#     .option("es.mapping.id", "es_id") \
#     .outputMode("update") \
#     .start()

# query.awaitTermination()

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, current_timestamp,
    to_timestamp, lag
)
from pyspark.sql.types import *
from pyspark.sql.window import Window

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "stock_ticks")
ES_HOST = os.getenv("ES_HOST", "elasticsearch")
ES_INDEX = os.getenv("ES_INDEX", "stock_intraday")
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
