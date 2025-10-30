from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_extract, current_timestamp

# ======================
# 1. Khởi tạo SparkSession
# ======================
spark = SparkSession.builder \
    .appName("KafkaToMongoRawIngestion") \
    .config("spark.mongodb.connection.uri", "mongodb://mongodb:27017/") \
    .config("spark.mongodb.write.connection.uri", "mongodb://mongodb:27017/") \
    .config("spark.ui.enabled", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ======================
# 2. Đọc dữ liệu từ Kafka
# ======================
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribePattern", "iot\\..*\\.data") \
    .option("startingOffsets", "earliest") \
    .load()

# ======================
# 3. Tiền xử lý dữ liệu
# ======================
processed_df = df.select(
    col("topic"),
    col("value").cast("string").alias("payload")
).withColumn("processed_at", current_timestamp())

# Trích xuất maphong từ topic: iot.<maphong>.data
final_df = processed_df.withColumn(
    "maphong", regexp_extract(col("topic"), "iot\\.(.*?)\\.data", 1)
)

# ======================
# 4. foreachBatch để ghi Mongo
# ======================
def foreach_batch_function(batch_df, batch_id):
    if batch_df.count() == 0:
        return

    distinct_rooms = [row["maphong"] for row in batch_df.select("maphong").distinct().collect() if row["maphong"]]

    for maphong in distinct_rooms:
        print(f"🚀 Transporting raw data for room: {maphong}")
        room_df = batch_df.filter(col("maphong") == maphong)

        # Ghi MongoDB: mỗi phòng 1 collection
        (room_df.select("payload", "processed_at")
            .write
            .format("mongodb")
            .mode("append")
            .option("database", "iot_db")
            .option("collection", maphong)
            .save()
        )

# ======================
# 5. Khởi chạy streaming
# ======================
query = final_df.writeStream \
    .foreachBatch(foreach_batch_function) \
    .outputMode("append") \
    .start()

query.awaitTermination()
