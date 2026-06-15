"""Main orchestration module for the Snowflake to Databricks migration pipeline.

This module coordinates the extraction, ingestion, transformation, and validation
phases of the migration process.
"""

import sys
from typing import Any

from jobs.bronze.raw_to_bronze import ingest_raw_to_bronze
from jobs.gold.silver_to_gold import create_gold_marts
from jobs.silver.bronze_to_silver import SilverTransformer
from src.config.config import Config
from src.extraction.demo_extractor import DemoExtractor
from src.extraction.snowflake_extractor import SnowflakeExtractor
from src.utils.spark_utils import get_spark_session
from src.validation.reconciliation_engine import ReconciliationEngine

# Initialize Logger
logger = Config.get_logger(__name__)


def run_pipeline() -> None:
    """Main orchestration function for the Snowflake-to-Databricks migration.

    Coordinates the following phases:
    1. Extraction (Snowflake or Demo)
    2. Bronze Ingestion (Raw to Delta)
    3. Silver Transformation (Clean, Dedupe, Merge)
    4. Gold Processing (Star Schema, Marts)
    5. Validation (Reconciliation Parity Checks)

    Raises:
        Exception: If any phase of the pipeline fails.
    """
    logger.info(
        f"Initiating Migration Pipeline (Mode: {Config.EXECUTION_MODE}, Env: {Config.ENV})"
    )

    try:
        # 1. Extraction Phase
        logger.info("--- Phase 1: Extraction ---")
        extractor: Any
        if Config.EXECUTION_MODE == "demo":
            extractor = DemoExtractor()
            extractor.extract_all()
        else:
            extractor = SnowflakeExtractor()
            tables = ["CUSTOMERS", "PRODUCTS", "ORDERS", "ORDER_ITEMS", "PAYMENTS"]
            for table in tables:
                # Incremental for large tables, full for small
                incremental_col = (
                    "UPDATED_AT" if table in ["ORDERS", "PAYMENTS"] else None
                )
                extractor.extract_table(table, incremental_col=incremental_col)

        # Initialize Spark for Medallion Processing
        spark = get_spark_session(f"MigrationPipeline_{Config.EXECUTION_MODE}")
        batch_id = getattr(extractor, "batch_id", "manual_run")

        # 2. Bronze Phase
        logger.info("--- Phase 2: Bronze Ingestion ---")
        tables_to_ingest = [
            "customers",
            "products",
            "orders",
            "order_items",
            "payments",
        ]
        for table in tables_to_ingest:
            ingest_raw_to_bronze(spark, table, batch_id)

        # 3. Silver Phase
        logger.info("--- Phase 3: Silver Transformation ---")
        transformer = SilverTransformer(spark)
        transformer.transform_all()

        # 4. Gold Phase
        logger.info("--- Phase 4: Gold Processing ---")
        create_gold_marts(spark)

        # 5. Validation Phase
        logger.info("--- Phase 5: Reconciliation & Quality ---")
        reconciler = ReconciliationEngine(spark)
        # Reconcile critical tables
        reconciler.reconcile("fact_orders", ["payment_amount"])
        reconciler.reconcile("dim_customers", [])

        logger.info("Migration Pipeline completed successfully.")

    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()
