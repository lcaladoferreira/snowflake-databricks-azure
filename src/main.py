"""Main orchestration module for the Snowflake to Databricks migration pipeline.

This module coordinates the extraction, ingestion, transformation, and validation
phases of the migration process.
"""

import argparse
import sys
from typing import Any, List, Optional

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


def run_pipeline(
    mode: Optional[str] = None,
    tables: Optional[List[str]] = None,
    skip_validation: bool = False,
) -> None:
    """Main orchestration function for the Snowflake-to-Databricks migration.

    Coordinates the following phases:
    1. Extraction (Snowflake or Demo)
    2. Bronze Ingestion (Raw to Delta)
    3. Silver Transformation (Clean, Dedupe, Merge)
    4. Gold Processing (Star Schema, Marts)
    5. Validation (Reconciliation Parity Checks)

    Args:
        mode: Execution mode ("demo" or "production").
        tables: List of tables to process.
        skip_validation: If True, Phase 5 (Validation) will be skipped.

    Raises:
        Exception: If any phase of the pipeline fails.
    """
    execution_mode = mode or Config.EXECUTION_MODE
    target_tables = tables or [
        "customers",
        "products",
        "orders",
        "order_items",
        "payments",
    ]

    logger.info(
        f"Initiating Migration Pipeline (Mode: {execution_mode}, Env: {Config.ENV})"
    )
    logger.info(f"Target tables: {target_tables}")

    try:
        # 1. Extraction Phase
        logger.info("--- Phase 1: Extraction ---")
        extractor: Any
        if execution_mode == "demo":
            extractor = DemoExtractor()
            extractor.extract_all()
        else:
            extractor = SnowflakeExtractor()
            for table in target_tables:
                # Incremental for large tables, full for small
                sf_table = table.upper()
                incremental_col = (
                    "UPDATED_AT" if sf_table in ["ORDERS", "PAYMENTS"] else None
                )
                extractor.extract_table(sf_table, incremental_col=incremental_col)

        # Initialize Spark for Medallion Processing
        spark = get_spark_session(f"MigrationPipeline_{execution_mode}")
        batch_id = getattr(extractor, "batch_id", "manual_run")

        # 2. Bronze Phase
        logger.info("--- Phase 2: Bronze Ingestion ---")
        for table in target_tables:
            ingest_raw_to_bronze(spark, table.lower(), batch_id)

        # 3. Silver Phase
        logger.info("--- Phase 3: Silver Transformation ---")
        transformer = SilverTransformer(spark)
        # transform_all is used as specified in requirements
        transformer.transform_all()

        # 4. Gold Phase
        logger.info("--- Phase 4: Gold Processing ---")
        create_gold_marts(spark)

        # 5. Validation Phase
        if not skip_validation:
            logger.info("--- Phase 5: Reconciliation & Quality ---")
            reconciler = ReconciliationEngine(spark)
            # Reconcile critical tables
            if "orders" in [t.lower() for t in target_tables]:
                reconciler.reconcile("fact_orders", ["payment_amount"])
            if "customers" in [t.lower() for t in target_tables]:
                reconciler.reconcile("dim_customers", [])
        else:
            logger.info("--- Phase 5: Validation Skipped ---")

        logger.info("Migration Pipeline completed successfully.")

    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}", exc_info=True)
        sys.exit(1)


def main() -> None:
    """CLI entry point for the migration pipeline."""
    parser = argparse.ArgumentParser(
        description="Snowflake to Databricks Migration Pipeline"
    )
    parser.add_argument(
        "--mode",
        choices=["demo", "production"],
        default=Config.EXECUTION_MODE,
        help="Execution mode (default: from Config)",
    )
    parser.add_argument(
        "--tables",
        type=str,
        help="Comma-separated list of tables to process",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip the reconciliation phase",
    )

    args = parser.parse_args()

    table_list = None
    if args.tables:
        table_list = [t.strip() for t in args.tables.split(",")]

    run_pipeline(
        mode=args.mode,
        tables=table_list,
        skip_validation=args.skip_validation,
    )


if __name__ == "__main__":
    main()
