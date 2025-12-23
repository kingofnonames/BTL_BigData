FROM apache/spark:3.5.1

WORKDIR /opt/spark/jobs
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && mkdir -p /home/spark/.ivy2 \
    && chown -R spark:spark /home/spark/.ivy2

USER spark
COPY ohlcv_speed.py .

ENTRYPOINT ["spark-submit","--master","spark://spark-master:7077","--packages","org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1","--conf","spark.jars.ivy=/tmp/.ivy2","ohlcv_speed.py"]



