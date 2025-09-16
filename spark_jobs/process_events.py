from pyspark.sql import SparkSession
from pyspark.sql.functions import col, regexp_extract, current_timestamp

# Khởi tạo SparkSession
spark = SparkSession.builder \
    .appName("KafkaToMongoRawIngestion") \
    .config("spark.mongodb.connection.uri", "mongodb://localhost:27017/") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# --- Không cần định nghĩa schema hay parse JSON nữa ---

# Đọc từ tất cả topic match pattern iot.*.data
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribePattern", "iot\\..*\\.data") \
    .option("startingOffsets", "earliest") \
    .load()

# Chỉ cần lấy topic và nội dung (value)
# Chuyển value (dạng binary) thành chuỗi và đổi tên thành 'payload'
# Thêm một cột timestamp để biết tin nhắn được xử lý lúc nào
processed_df = df.select(
    col("topic"),
    col("value").cast("string").alias("payload") 
).withColumn("processed_at", current_timestamp())

# Tách maphong từ topic: iot.<maphong>.data
final_df = processed_df.withColumn(
    "maphong", regexp_extract(col("topic"), "iot\\.(.*?)\\.data", 1)
)

# Hàm foreachBatch để lưu vào Mongo
def foreach_batch_function(batch_df, batch_id):
    distinct_rooms = [row["maphong"] for row in batch_df.select("maphong").distinct().collect()]
    
    for maphong in distinct_rooms:
        print(f"Transporting raw data for room: {maphong}")
        room_df = batch_df.filter(col("maphong") == maphong)
        
        # Chỉ lưu payload và timestamp, không cần chọn các trường con nữa
        (room_df.select("payload", "processed_at")
            .write
            .format("mongodb")
            .mode("append")
            .option("database", "iot_db")
            .option("collection", maphong)
            .save())

# Streaming query
query = final_df.writeStream \
    .foreachBatch(foreach_batch_function) \
    .outputMode("append") \
    .start()

query.awaitTermination()