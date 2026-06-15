from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, upper, trim, to_timestamp, row_number, expr
from pyspark.sql.window import Window
from src.config.config import Config

logger = Config.get_logger(__name__)

class SilverTransformer:
    """Handles Bronze -> Silver transformations: cleaning, deduplication, and MERGE."""

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def transform_customers(self):
        logger.info("Transforming Customers to Silver...")
        bronze_path = Config.get_storage_path("bronze", "customers")
        silver_path = Config.get_storage_path("silver", "customers")

        df = self.spark.read.format("delta").load(bronze_path)

        # 1. Clean and Standardize
        cleaned_df = df.select(
            col("customer_id").cast("int"),
            trim(col("first_name")).alias("first_name"),
            trim(col("last_name")).alias("last_name"),
            upper(trim(col("email"))).alias("email"),
            to_timestamp(col("registration_date")).alias("registration_date"),
            col("_ingestion_timestamp").alias("_bronze_at")
        )

        # 2. Deduplicate using Window function (keep latest)
        window_spec = Window.partitionBy("customer_id").orderBy(col("_bronze_at").desc())
        deduped_df = cleaned_df.withColumn("rn", row_number().over(window_spec)) \
                               .filter("rn = 1") \
                               .drop("rn")

        # 3. Upsert (Delta Merge) - Pattern for Production
        self._upsert(deduped_df, "customers", "customer_id")

    def _upsert(self, df: DataFrame, table_name: str, pk: str):
        """Idempotent upsert into Silver Delta table."""
        target_path = Config.get_storage_path("silver", table_name)

        if not os.path.exists(target_path) and Config.EXECUTION_MODE == "demo":
             df.write.format("delta").mode("overwrite").save(target_path)
             return

        # In real Databricks, we'd use DeltaTable.forName or alias
        # For simplicity in this template:
        df.createOrReplaceTempView("source")

        merge_sql = f"""
            MERGE INTO delta.`{target_path}` AS target
            USING source
            ON target.{pk} = source.{pk}
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
        """
        self.spark.sql(merge_sql)
        logger.info(f"Upserted {table_name} to Silver.")

import os
if __name__ == "__main__":
    from src.utils.spark_utils import get_spark_session
    s = get_spark_session("SilverTransformation")
    st = SilverTransformer(s)
    st.transform_customers()
    # ... call other transformations
