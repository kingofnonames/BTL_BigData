import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lead
from pyspark.sql.window import Window
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression, RandomForestRegressor
from pyspark.ml import Pipeline
from pyspark.ml.evaluation import RegressionEvaluator

# --- Spark session ---
spark = SparkSession.builder.appName("OHLCV-FPT-Predict").getOrCreate()

# --- Environment variables ---
HDFS_PATH = os.getenv("HDFS_PATH", "hdfs://namenode:8020/data/ohlcv")
SYMBOL_DEFAULT = os.getenv("SYMBOL_DEFAULT", "FPT")

# --- Load parquet ---
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

df_fpt = df_flat.filter(col("symbol") == SYMBOL_DEFAULT).orderBy("trade_date")

window = Window.orderBy("trade_date")
df_fpt = df_fpt.withColumn("close_next", lead("close", 1).over(window))
df_fpt = df_fpt.na.drop(subset=["close_next"])

feature_cols = ["open", "high", "low", "close", "volume"]
assembler = VectorAssembler(inputCols=feature_cols, outputCol="features")

train_df = df_fpt.filter(col("trade_date") < "2025-12-01")
test_df = df_fpt.filter(col("trade_date") >= "2025-12-01")

lr = LinearRegression(featuresCol="features", labelCol="close_next")
lr_pipeline = Pipeline(stages=[assembler, lr])
lr_model = lr_pipeline.fit(train_df)
pred_lr = lr_model.transform(test_df)

rf = RandomForestRegressor(featuresCol="features", labelCol="close_next", numTrees=100)
rf_pipeline = Pipeline(stages=[assembler, rf])
rf_model = rf_pipeline.fit(train_df)
pred_rf = rf_model.transform(test_df)

evaluator = RegressionEvaluator(labelCol="close_next", predictionCol="prediction", metricName="rmse")
rmse_lr = evaluator.evaluate(pred_lr)
rmse_rf = evaluator.evaluate(pred_rf)

print(f"Linear Regression RMSE: {rmse_lr}")
print(f"Random Forest Regression RMSE: {rmse_rf}")

spark.stop()
