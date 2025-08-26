# Dockerfile: spark_jobs/Dockerfile

FROM bitnami/spark:3.5.0

WORKDIR /app

COPY process_events.py .

USER root
RUN apt-get update && \
    apt-get install -y python3-pip && \
    pip3 install pymongo mysql-connector-python

CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0", "--master", "local[*]", "process_events.py"]
