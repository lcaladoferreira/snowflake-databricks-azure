from src.extraction.extractor import Extractor
from jobs.bronze.ingest_raw_to_bronze import ingest_to_bronze
from jobs.silver.transform_bronze_to_silver import transform_to_silver
from jobs.gold.transform_silver_to_gold import transform_to_gold
from src.validation.reconciler import Reconciler
from src.utils.logger import get_logger
import sys

logger = get_logger(__name__)

def main():
    logger.info("Starting Snowflake to Databricks Migration Pipeline...")

    try:
        # 1. Extraction
        logger.info("--- Phase 1: Extraction ---")
        extractor = Extractor()
        extractor.extract_all()

        # 2. Bronze Layer
        logger.info("--- Phase 2: Bronze Layer ---")
        ingest_to_bronze()

        # 3. Silver Layer
        logger.info("--- Phase 3: Silver Layer ---")
        transform_to_silver()

        # 4. Gold Layer
        logger.info("--- Phase 4: Gold Layer ---")
        transform_to_gold()

        # 5. Validation
        logger.info("--- Phase 5: Validation & Reconciliation ---")
        reconciler = Reconciler()
        reconciler.run_reconciliation()

        logger.info("Migration Pipeline completed successfully!")

    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
