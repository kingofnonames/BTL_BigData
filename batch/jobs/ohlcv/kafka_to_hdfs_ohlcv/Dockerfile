# FROM apache/spark:3.5.1

# WORKDIR /opt/spark/jobs

# # Cài Python dependencies
# COPY requirements.txt .
# USER root
# RUN pip install --no-cache-dir -r requirements.txt
# USER spark

# # Copy code Spark job
# COPY kafka_to_hdfs_ohlcv.py .

# # Entry point với Kafka connector
# ENTRYPOINT ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1", "--master", "spark://spark-master:7077", "kafka_to_hdfs_ohlcv.py"]


FROM apache/spark:3.5.1

# ------------------------
# Thư mục làm việc
# ------------------------
WORKDIR /opt/spark/jobs

# ------------------------
# Cài Python requirements nếu có
# ------------------------
COPY requirements.txt .
USER root
RUN pip install --no-cache-dir -r requirements.txt

# Tạo thư mục Ivy cache writable cho user spark
RUN mkdir -p /home/spark/.ivy2 && chown -R spark:spark /home/spark/.ivy2
USER spark

# ------------------------
# Copy job script
# ------------------------
COPY kafka_to_hdfs_ohlcv.py .

# ------------------------
# Spark-submit
# Sử dụng --conf spark.jars.ivy để chỉ định thư mục writable cho Ivy cache
# ------------------------
ENTRYPOINT ["spark-submit", \
    "--master", "spark://spark-master:7077", \
    "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1", \
    "--conf", "spark.jars.ivy=/tmp/.ivy2", \
    "kafka_to_hdfs_ohlcv.py"]
