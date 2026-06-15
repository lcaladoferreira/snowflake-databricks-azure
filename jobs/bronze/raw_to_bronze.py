from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, input_file_name, lit

from src.config.config import Config

logger = Config.get_logger(__name__)


def ingest_raw_to_bronze(spark: SparkSession, table_name: str, batch_id: str) -> None:
    """
    Ingests raw Parquet files from Landing to Bronze Delta tables.
    Uses schema enforcement and adds ingestion metadata.
    """
    logger.info(f"Starting Bronze ingestion for {table_name} (Batch: {batch_id})")

    landing_path = Config.get_storage_path("landing", table_name)
    bronze_path = Config.get_storage_path("bronze", table_name)
    checkpoint_path = (
        f"{Config.ADLS_BASE_PATH}/checkpoints/bronze/{table_name}"
        if Config.EXECUTION_MODE != "demo"
        else None
    )

    # Read from landing
    if (
        Config.EXECUTION_MODE != "demo"
        and spark.conf.get("spark.databricks.service.client.enabled", "false") == "true"
    ):
        # Auto Loader (Production)
        raw_df = (
            spark.readStream.format("cloudFiles")
            .option("cloudFiles.format", "parquet")
            .option("cloudFiles.schemaLocation", f"{bronze_path}/_schema")
            .load(landing_path)
        )
    else:
        # Standard Batch Read (Demo)
        raw_df = spark.read.format("parquet").load(landing_path)

    # Add Ingestion Metadata
    bronze_df = (
        raw_df.withColumn("_ingestion_timestamp", current_timestamp())
        .withColumn("_batch_id", lit(batch_id))
        .withColumn("_source_file", input_file_name())
    )

    # Write to Delta
    if Config.EXECUTION_MODE != "demo" and checkpoint_path:
        (
            bronze_df.writeStream.format("delta")
            .option("checkpointLocation", checkpoint_path)
            .outputMode("append")
            .table(f"{Config.UC_CATALOG}.{Config.UC_BRONZE_SCHEMA}.{table_name}")
        )
    else:
        (bronze_df.write.format("delta").mode("append").save(bronze_path))

    logger.info(f"Successfully ingested {table_name} to Bronze.")


if __name__ == "__main__":
    import sys

    from src.utils.spark_utils import get_spark_session

    table = sys.argv[1] if len(sys.argv) > 1 else "customers"
    batch = sys.argv[2] if len(sys.argv) > 2 else "manual"

    s = get_spark_session("BronzeIngestion")
    ingest_raw_to_bronze(s, table, batch)
