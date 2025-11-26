
FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-17-jdk \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*


ENV SPARK_VERSION="3.5.1"
ENV HADOOP_VERSION="3"
ENV SPARK_HOME="/opt/spark"


RUN wget -q "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz" -O /tmp/spark.tgz && \
    tar -xzf /tmp/spark.tgz -C /opt && \
    mv /opt/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} ${SPARK_HOME} && \
    rm /tmp/spark.tgz

ENV PATH="${PATH}:${SPARK_HOME}/bin"


WORKDIR /app/batch


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY src/ src/

CMD ["python", "src/main_batch.py"]


