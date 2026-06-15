import os
from datetime import datetime

import pandas as pd

from src.config.config import Config
from src.extraction.metadata_manager import MetadataManager

logger = Config.get_logger(__name__)


class DemoExtractor:
    """Simulates Snowflake extraction using local CSV files."""

    def __init__(self):
        self.metadata_mgr = MetadataManager()
        self.batch_id = datetime.now().strftime("%Y%m%d%H%M%S")

    def extract_all(self):
        tables = ["customers", "products", "orders", "order_items", "payments"]
        sample_dir = os.path.join(Config.LOCAL_DATA_DIR, "sample")

        for table in tables:
            src = os.path.join(sample_dir, f"{table}.csv")
            if not os.path.exists(src):
                logger.warning(f"Sample file {src} not found.")
                continue

            df = pd.read_csv(src)

            # Simulate landing as Parquet
            target_dir = Config.get_storage_path("landing", table)
            os.makedirs(target_dir, exist_ok=True)
            output_path = os.path.join(target_dir, f"part_{self.batch_id}_0000.parquet")

            df.to_parquet(output_path, index=False)

            self.metadata_mgr.log_extraction(
                batch_id=self.batch_id,
                table_name=table,
                row_count=len(df),
                status="SUCCESS",
            )
            logger.info(f"DEMO: Extracted {table} ({len(df)} rows) to {output_path}")


if __name__ == "__main__":
    DemoExtractor().extract_all()
