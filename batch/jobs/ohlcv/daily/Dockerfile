FROM apache/spark:3.5.1

WORKDIR /opt/spark/jobs

COPY requirements.txt .

USER root
RUN pip install --no-cache-dir -r requirements.txt \
    && mkdir -p /home/spark/.ivy2 \
    && chown -R spark:spark /home/spark/.ivy2
USER spark

COPY daily_ohlcv.py .

ENTRYPOINT ["spark-submit", \
    "--master", "spark://spark-master:7077", \
    "--packages", "org.elasticsearch:elasticsearch-spark-30_2.12:8.11.0", \
    "--conf", "spark.jars.ivy=/tmp/.ivy2", \
    "daily_ohlcv.py"]

