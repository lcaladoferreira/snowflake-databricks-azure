import os

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import col, row_number, to_timestamp, upper, trim
from pyspark.sql.window import Window

from src.config.config import Config

logger = Config.get_logger(__name__)


class SilverTransformer:
    """Standardizes, cleans, and deduplicates all core entities for the Silver layer."""

    def __init__(self, spark: SparkSession):
        self.spark = spark

    def transform_all(self) -> None:
        """Orchestrates transformation for all entities."""
        self.transform_customers()
        self.transform_products()
        self.transform_orders()
        self.transform_payments()
        self.transform_order_items()

    def transform_customers(self) -> None:
        logger.info("Silver: Processing Customers")
        df = self.spark.read.format("delta").load(Config.get_storage_path("bronze", "customers"))

        cleaned_df = df.select(
            col("customer_id").cast("int"),
            trim(col("first_name")).alias("first_name"),
            trim(col("last_name")).alias("last_name"),
            upper(trim(col("email"))).alias("email"),
            to_timestamp(col("registration_date")).alias("registration_date"),
            col("_ingestion_timestamp").alias("_bronze_at"),
        )
        self._upsert(cleaned_df, "customers", "customer_id")

    def transform_products(self) -> None:
        logger.info("Silver: Processing Products")
        df = self.spark.read.format("delta").load(Config.get_storage_path("bronze", "products"))

        cleaned_df = df.select(
            col("product_id").cast("int"),
            trim(col("product_name")).alias("product_name"),
            upper(col("category")).alias("category"),
            col("price").cast("decimal(10,2)"),
            col("_ingestion_timestamp").alias("_bronze_at"),
        )
        self._upsert(cleaned_df, "products", "product_id")

    def transform_orders(self) -> None:
        logger.info("Silver: Processing Orders")
        df = self.spark.read.format("delta").load(Config.get_storage_path("bronze", "orders"))

        cleaned_df = df.select(
            col("order_id").cast("int"),
            col("customer_id").cast("int"),
            to_timestamp(col("order_date")).alias("order_date"),
            upper(col("status")).alias("status"),
            col("_ingestion_timestamp").alias("_bronze_at"),
        )
        self._upsert(cleaned_df, "orders", "order_id")

    def transform_payments(self) -> None:
        logger.info("Silver: Processing Payments")
        df = self.spark.read.format("delta").load(Config.get_storage_path("bronze", "payments"))

        cleaned_df = df.select(
            col("payment_id").cast("int"),
            col("order_id").cast("int"),
            upper(col("payment_method")).alias("payment_method"),
            col("payment_amount").cast("decimal(10,2)"),
            to_timestamp(col("payment_date")).alias("payment_date"),
            col("_ingestion_timestamp").alias("_bronze_at"),
        )
        self._upsert(cleaned_df, "payments", "payment_id")

    def transform_order_items(self) -> None:
        logger.info("Silver: Processing Order Items")
        df = self.spark.read.format("delta").load(Config.get_storage_path("bronze", "order_items"))

        cleaned_df = df.select(
            col("order_id").cast("int"),
            col("product_id").cast("int"),
            col("quantity").cast("int"),
            col("_ingestion_timestamp").alias("_bronze_at"),
        )
        # Order items usually don't have a single PK, but we deduplicate based on composite
        self._upsert(cleaned_df, "order_items", "order_id, product_id")

    def _upsert(self, df: DataFrame, table_name: str, pk_cols: str) -> None:
        """Idempotent MERGE logic to prevent duplicates and handle updates."""
        target_path = Config.get_storage_path("silver", table_name)

        # Deduplicate source first (keep latest by ingestion)
        pks = [c.strip() for c in pk_cols.split(",")]
        window = Window.partitionBy(*pks).orderBy(col("_bronze_at").desc())
        deduped_df = df.withColumn("rn", row_number().over(window)).filter("rn = 1").drop("rn")

        if not os.path.exists(target_path):
            deduped_df.write.format("delta").mode("overwrite").save(target_path)
        else:
            # Use DeltaTable API for better local/demo compatibility
            from delta.tables import DeltaTable

            target_table = DeltaTable.forPath(self.spark, target_path)

            merge_condition = " AND ".join([f"target.{c} = source.{c}" for c in pks])

            (
                target_table.alias("target")
                .merge(deduped_df.alias("source"), merge_condition)
                .whenMatchedUpdateAll()
                .whenNotMatchedInsertAll()
                .execute()
            )

        logger.info(f"Silver: {table_name} upserted.")
