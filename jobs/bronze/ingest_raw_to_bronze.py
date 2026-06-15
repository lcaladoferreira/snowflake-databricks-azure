from pyspark.sql.functions import current_timestamp, lit, input_file_name
from src.utils.spark_utils import get_spark_session
from src.config.config import Config
from src.utils.logger import get_logger
import os

logger = get_logger(__name__)

def ingest_to_bronze():
    spark = get_spark_session("BronzeIngestion")
    tables = ["customers", "products", "orders", "order_items", "payments"]

    for table in tables:
        logger.info(f"Ingesting {table} to Bronze layer...")

        # In demo, raw is a single CSV. In prod, it might be a folder of files.
        raw_path = Config.get_storage_path("raw", f"{table}.csv" if Config.EXECUTION_MODE == "demo" else table)
        bronze_path = Config.get_storage_path("bronze", table)

        df = spark.read.option("header", "true").option("inferSchema", "true").csv(raw_path)

        # Add metadata columns
        df_bronze = df.withColumn("_ingestion_timestamp", current_timestamp()) \
                      .withColumn("_source_system", lit("snowflake" if Config.EXECUTION_MODE != "demo" else "demo_csv")) \
                      .withColumn("_source_file", input_file_name())

        # Write to Delta
        df_bronze.write.format("delta").mode("overwrite").save(bronze_path)
        logger.info(f"Table {table} written to Delta at {bronze_path}")

if __name__ == "__main__":
    ingest_to_bronze()
