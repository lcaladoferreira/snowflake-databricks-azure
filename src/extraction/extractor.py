import os
import shutil
import pandas as pd
from src.config.config import Config
from src.utils.logger import get_logger
from src.extraction.metadata_collector import capture_metadata

logger = get_logger(__name__)

class Extractor:
    def __init__(self):
        self.mode = Config.EXECUTION_MODE
        self.raw_dir = Config.RAW_DIR
        os.makedirs(self.raw_dir, exist_ok=True)

    def extract_all(self):
        tables = ["customers", "products", "orders", "order_items", "payments"]
        if self.mode == "demo":
            self._extract_demo(tables)
        else:
            self._extract_snowflake(tables)

    def _extract_demo(self, tables):
        logger.info("Running extraction in DEMO mode (local CSV copy)")
        sample_dir = os.path.join(Config.LOCAL_DATA_DIR, "sample")

        for table in tables:
            src = os.path.join(sample_dir, f"{table}.csv")
            dst = os.path.join(self.raw_dir, f"{table}.csv")
            if os.path.exists(src):
                shutil.copy(src, dst)
                df = pd.read_csv(src)
                row_count = len(df)
                capture_metadata(table, row_count)
                logger.info(f"Extracted {table} ({row_count} rows) to {dst}")
            else:
                logger.warning(f"Source file {src} not found!")

    def _extract_snowflake(self, tables):
        logger.info("Running extraction in PRODUCTION mode (Snowflake template)")
        # Placeholder for Snowflake chunked extraction logic
        for table in tables:
            logger.info(f"Initiating chunked extraction for table: {table}")

            # Simulated chunking logic:
            # 1. Fetch total row count
            # 2. Calculate chunk size (e.g., 100,000 rows)
            # 3. Iterate through offsets or partitions
            # 4. Write each chunk to ADLS Gen2 path

            # Example SQL for chunking:
            # SELECT * FROM {table} WHERE _chunk_id BETWEEN {start} AND {end}

            logger.info(f"Table {table}: Metadata captured and data streamed to {Config.get_storage_path('raw', table)}")
            capture_metadata(table, row_count=0, status="template") # row_count unknown in template

if __name__ == "__main__":
    extractor = Extractor()
    extractor.extract_all()
