FROM apache/spark:3.5.1

USER root
WORKDIR /opt/spark/work-dir

# Cài đặt curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Tạo thư mục cho user spark và set permissions
RUN mkdir -p /home/spark/.ivy2/local /home/spark/.ivy2/cache && \
    chown -R 185:185 /home/spark && \
    chown -R 185:185 /opt/spark/work-dir

# Download tất cả dependencies cần thiết
RUN curl -L -o /opt/spark/jars/spark-sql-kafka-0-10_2.12-3.5.1.jar \
      https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.1/spark-sql-kafka-0-10_2.12-3.5.1.jar && \
    curl -L -o /opt/spark/jars/kafka-clients-3.4.1.jar \
      https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.4.1/kafka-clients-3.4.1.jar && \
    curl -L -o /opt/spark/jars/spark-token-provider-kafka-0-10_2.12-3.5.1.jar \
      https://repo1.maven.org/maven2/org/apache/spark/spark-token-provider-kafka-0-10_2.12/3.5.1/spark-token-provider-kafka-0-10_2.12-3.5.1.jar && \
    curl -L -o /opt/spark/jars/commons-pool2-2.11.1.jar \
      https://repo1.maven.org/maven2/org/apache/commons/commons-pool2/2.11.1/commons-pool2-2.11.1.jar && \
    curl -L -o /opt/spark/jars/mongo-spark-connector_2.12-10.3.0.jar \
      https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar && \
    curl -L -o /opt/spark/jars/mongodb-driver-sync-5.1.0.jar \
      https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-sync/5.1.0/mongodb-driver-sync-5.1.0.jar && \
    curl -L -o /opt/spark/jars/mongodb-driver-core-5.1.0.jar \
      https://repo1.maven.org/maven2/org/mongodb/mongodb-driver-core/5.1.0/mongodb-driver-core-5.1.0.jar && \
    curl -L -o /opt/spark/jars/bson-5.1.0.jar \
      https://repo1.maven.org/maven2/org/mongodb/bson/5.1.0/bson-5.1.0.jar && \
    curl -L -o /opt/spark/jars/bson-record-codec-5.1.0.jar \
      https://repo1.maven.org/maven2/org/mongodb/bson-record-codec/5.1.0/bson-record-codec-5.1.0.jar

# Copy Python script
COPY process_events.py /opt/spark/work-dir/

# Chuyển sang user spark (185 trong image apache/spark)
USER 185

# CRITICAL: Set HOME environment variable cho user 185
ENV HOME=/home/spark
ENV SPARK_HOME=/opt/spark
ENV PYSPARK_PYTHON=/usr/bin/python3

# Disable Ivy completely bằng cách set ivy settings file không tồn tại
ENV SPARK_SUBMIT_OPTS="-Divy.home=/tmp/ivy"

CMD ["/opt/spark/bin/spark-submit", \
     "--master", "local[*]", \
     "--conf", "spark.jars.ivy=/tmp/ivy", \
     "--conf", "spark.sql.streaming.checkpointLocation=/opt/spark/work-dir/checkpoint", \
     "--conf", "spark.driver.extraJavaOptions=-Duser.home=/home/spark", \
     "--conf", "spark.executor.extraJavaOptions=-Duser.home=/home/spark", \
     "/opt/spark/work-dir/process_events.py"]