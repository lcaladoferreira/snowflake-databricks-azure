import snowflake.connector
import pandas as pd
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from src.config.config import Config
from src.extraction.metadata_manager import MetadataManager

logger = Config.get_logger(__name__)

class SnowflakeExtractor:
    """Handles high-performance, chunked extraction from Snowflake to ADLS Gen2."""

    def __init__(self):
        self.config = Config.get_snowflake_config()
        self.metadata_mgr = MetadataManager()
        self.batch_id = datetime.now().strftime("%Y%m%d%H%M%S")

    def _get_connection(self):
        """Creates a Snowflake connection."""
        try:
            return snowflake.connector.connect(
                user=self.config['user'],
                password=self.config['password'],
                account=self.config['account'],
                warehouse=self.config['warehouse'],
                database=self.config['database'],
                schema=self.config['schema'],
                role=self.config['role']
            )
        except Exception as e:
            logger.error(f"Failed to connect to Snowflake: {str(e)}")
            raise

    def extract_table(self,
                      table_name: str,
                      incremental_col: Optional[str] = None,
                      chunk_size: int = 100000):
        """Extracts a table from Snowflake, supporting incremental loads and chunking."""

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            # 1. Determine Watermark
            last_watermark = self.metadata_mgr.get_last_watermark(table_name) if incremental_col else None

            # 2. Build Query
            query = f"SELECT * FROM {table_name}"
            if last_watermark and incremental_col:
                query += f" WHERE {incremental_col} > '{last_watermark}'"

            logger.info(f"Executing extraction query for {table_name}: {query}")
            cursor.execute(query)

            # 3. Chunked Extraction
            chunk_idx = 0
            total_rows = 0
            new_max_watermark = last_watermark

            while True:
                rows = cursor.fetchmany(chunk_size)
                if not rows:
                    break

                df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])

                # Update watermark if applicable
                if incremental_col:
                    current_chunk_max = df[incremental_col].max()
                    if new_max_watermark is None or current_chunk_max > new_max_watermark:
                        new_max_watermark = current_chunk_max

                # Write to ADLS Gen2 (or local for demo)
                output_path = self._write_to_storage(df, table_name, chunk_idx)

                total_rows += len(df)
                logger.info(f"Extracted chunk {chunk_idx} for {table_name} ({len(df)} rows)")
                chunk_idx += 1

            # 4. Finalize Metadata
            self.metadata_mgr.log_extraction(
                batch_id=self.batch_id,
                table_name=table_name,
                row_count=total_rows,
                watermark=new_max_watermark,
                status="SUCCESS"
            )

            logger.info(f"Extraction complete for {table_name}. Total rows: {total_rows}")

        except Exception as e:
            logger.error(f"Extraction failed for {table_name}: {str(e)}")
            self.metadata_mgr.log_extraction(
                batch_id=self.batch_id,
                table_name=table_name,
                row_count=0,
                status="FAILED",
                error_message=str(e)
            )
            raise
        finally:
            cursor.close()
            conn.close()

    def _write_to_storage(self, df: pd.DataFrame, table_name: str, chunk_idx: int) -> str:
        """Writes the dataframe to the landing zone as Parquet."""
        target_dir = Config.get_storage_path("landing", table_name)
        os.makedirs(target_dir, exist_ok=True)

        filename = f"part_{self.batch_id}_{chunk_idx:04d}.parquet"
        file_path = os.path.join(target_dir, filename)

        df.to_parquet(file_path, index=False)
        return file_path

if __name__ == "__main__":
    # Example usage (would be driven by orchestration)
    extractor = SnowflakeExtractor()
    # extractor.extract_table("ORDERS", incremental_col="UPDATED_AT")
