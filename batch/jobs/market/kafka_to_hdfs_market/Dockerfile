FROM apache/spark:3.5.1

WORKDIR /opt/spark/jobs

COPY requirements.txt .
USER root
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /home/spark/.ivy2 && chown -R spark:spark /home/spark/.ivy2
USER spark

COPY kafka_to_hdfs_market.py .

ENTRYPOINT ["spark-submit", \
    "--master", "spark://spark-master:7077", \
    "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1", \
    "--conf", "spark.jars.ivy=/tmp/.ivy2", \
    "kafka_to_hdfs_market.py"]
