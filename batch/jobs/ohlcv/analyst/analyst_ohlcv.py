import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, concat_ws, from_unixtime, date_format, to_date
from pyspark.sql.types import LongType, TimestampType, DateType, StructType, StructField, StringType, DoubleType
from datetime import datetime
from elasticsearch import Elasticsearch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OHLCV-MapReduce-Incremental")

HDFS_PATH = os.getenv("HDFS_PATH", "hdfs://namenode:8020/data/ohlcv")
ES_HOST = os.getenv("ES_HOST", "http://elasticsearch:9200")
ES_INDEX = os.getenv("ES_INDEX_BATCH_OHLCV_ANAYLYST", "ohlcv_analysis")

spark = SparkSession.builder.appName("OHLCV-MapReduce-Incremental").getOrCreate()
logger.info(f"{datetime.now()} - Spark session started.")

df = spark.read.parquet(HDFS_PATH)
logger.info(f"{datetime.now()} - Read data from HDFS ({HDFS_PATH}), rows: {df.count()}")

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
    df_flat = df_flat.withColumn("trade_date", date_format(from_unixtime(col("trade_date")/1000), "yyyy-MM-dd"))
elif isinstance(dtype, DateType):
    df_flat = df_flat.withColumn("trade_date", date_format(col("trade_date"), "yyyy-MM-dd"))
else:
    df_flat = df_flat.withColumn("trade_date", to_date(col("trade_date"), "yyyy-MM-dd"))

df_flat = df_flat.withColumn("es_id", concat_ws("_", col("symbol"), col("trade_date")))

es = Elasticsearch([ES_HOST])
latest_dates = {}
for symbol in df_flat.select("symbol").distinct().rdd.flatMap(lambda x:x).collect():
    body = {
        "size": 1,
        "query": {"term": {"symbol": symbol}},
        "sort": [{"trade_date": {"order": "desc"}}]
    }
    res = es.search(index=ES_INDEX, body=body)
    if res['hits']['hits']:
        latest_dates[symbol] = res['hits']['hits'][0]['_source']['trade_date']
    else:
        latest_dates[symbol] = None

df_new = df_flat.rdd.filter(lambda row: latest_dates[row.symbol] is None or row.trade_date > latest_dates[row.symbol])
logger.info(f"{datetime.now()} - Rows to process incrementally: {df_new.count()}")

def safe_float(x):
    return float(x) if x is not None else None

def compute_indicators_incremental(records):
    records = sorted(records, key=lambda x: x["trade_date"])
    closes, volumes, daily_returns, gains, losses = [], [], [], [], []

    for i, r in enumerate(records):
        closes.append(r["close"])
        volumes.append(r["volume"])
        vwap = sum([c*v for c,v in zip(closes, volumes)]) / max(sum(volumes), 1)

        ma7 = sum(closes[-7:])/7 if i+1 >= 7 else None
        ma30 = sum(closes[-30:])/30 if i+1 >= 30 else None

        if i+1 >= 30 and ma30 is not None:
            std30 = (sum([(c-ma30)**2 for c in closes[-30:]])/30)**0.5
            bollinger_upper = ma30 + 2*std30
            bollinger_lower = ma30 - 2*std30
        else:
            bollinger_upper = None
            bollinger_lower = None

        daily_return = 0 if i==0 else (r["close"]-records[i-1]["close"])/records[i-1]["close"]*100
        daily_returns.append(daily_return)
        cum_return = sum(daily_returns)/len(daily_returns)

        change = 0 if i==0 else r["close"]-records[i-1]["close"]
        gain = max(change,0)
        loss = max(-change,0)
        gains.append(gain)
        losses.append(loss)

        if i >= 13:
            avg_gain = sum(gains[-14:])/14
            avg_loss = sum(losses[-14:])/14
            rsi14 = 100 - 100/(1 + avg_gain/max(avg_loss,1e-8))
        else:
            rsi14 = None

        r.update({
            "vwap": safe_float(vwap),
            "ma7": safe_float(ma7),
            "ma30": safe_float(ma30),
            "bollinger_upper": safe_float(bollinger_upper),
            "bollinger_lower": safe_float(bollinger_lower),
            "daily_return": safe_float(daily_return),
            "cumulative_return": safe_float(cum_return),
            "rsi14": safe_float(rsi14)
        })

    return records

result_rdd = df_new.map(lambda row: (row.symbol, {
    "symbol": row.symbol,
    "trade_date": row.trade_date,
    "open": safe_float(row.open),
    "high": safe_float(row.high),
    "low": safe_float(row.low),
    "close": safe_float(row.close),
    "volume": safe_float(row.volume),
    "es_id": row.es_id
})).groupByKey().flatMap(lambda x: compute_indicators_incremental(list(x[1])))

# Schema rõ ràng để tránh lỗi merge type
schema = StructType([
    StructField("symbol", StringType(), True),
    StructField("trade_date", StringType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume", DoubleType(), True),
    StructField("es_id", StringType(), True),
    StructField("vwap", DoubleType(), True),
    StructField("ma7", DoubleType(), True),
    StructField("ma30", DoubleType(), True),
    StructField("bollinger_upper", DoubleType(), True),
    StructField("bollinger_lower", DoubleType(), True),
    StructField("daily_return", DoubleType(), True),
    StructField("cumulative_return", DoubleType(), True),
    StructField("rsi14", DoubleType(), True)
])

result_df = spark.createDataFrame(result_rdd, schema)

logger.info(f"{datetime.now()} - Writing incremental results to Elasticsearch index: {ES_INDEX}")
result_df.write.format("org.elasticsearch.spark.sql") \
         .option("es.nodes", ES_HOST.replace("http://","")) \
         .option("es.resource", ES_INDEX) \
         .option("es.mapping.id", "es_id") \
         .mode("append") \
         .save()

logger.info(f"{datetime.now()} - Finished writing to Elasticsearch. Stopping Spark.")
spark.stop()
