from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, DoubleType
from pymongo import MongoClient
import mysql.connector

# ✅ Initialize Spark session
spark = SparkSession.builder \
    .appName("KafkaToMongoMySQL") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# ✅ Define schema with timestamp as DoubleType to accept float
schema = StructType() \
    .add("device_id", StringType()) \
    .add("temperature", DoubleType()) \
    .add("humidity", DoubleType()) \
    .add("timestamp", DoubleType())  # ✅ FIXED: was LongType before

# ✅ Read stream from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "iot-events") \
    .load()

# ✅ Convert Kafka JSON payload to structured columns
json_df = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# ✅ Write to MongoDB
def write_to_mongo(rows):
    try:
        client = MongoClient("mongodb://mongodb:27017")
        db = client.iot
        docs = [row.asDict() for row in rows if row.timestamp is not None]
        if docs:
            db.events.insert_many(docs)
            print(f"✅ Inserted {len(docs)} rows into MongoDB")
        else:
            print("⚠️ No valid rows for MongoDB")
        client.close()
    except Exception as e:
        print(f"❌ MongoDB error: {e}")

# ✅ Write to MySQL
def write_to_mysql(rows):
    try:
        conn = mysql.connector.connect(
            host="mysql",
            user="iot",
            password="iot123",
            database="iot_data"
        )
        cursor = conn.cursor()
        insert_sql = """
            INSERT INTO events (device_id, temperature, humidity, timestamp)
            VALUES (%s, %s, %s, %s)
        """
        values = [
            (row.device_id, row.temperature, row.humidity, row.timestamp)
            for row in rows if row.timestamp is not None
        ]
        if values:
            cursor.executemany(insert_sql, values)
            conn.commit()
            print(f"✅ Inserted {len(values)} rows into MySQL")
        else:
            print("⚠️ No valid rows for MySQL")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ MySQL error: {e}")

# ✅ Process each batch
def foreach_batch_function(df, epoch_id):
    count = df.count()
    print(f"📦 Processing batch {epoch_id} with {count} rows")
    if count == 0:
        return
    try:
        df.persist()
        rows = list(df.toLocalIterator())
        for r in rows:
            print("🔎 Row:", r.asDict())
        write_to_mongo(rows)
        write_to_mysql(rows)
        df.unpersist()
    except Exception as e:
        print(f"❌ Error in batch {epoch_id}: {e}")

# ✅ Start structured streaming query
query = json_df.writeStream \
    .foreachBatch(foreach_batch_function) \
    .outputMode("append") \
    .start()

query.awaitTermination()
