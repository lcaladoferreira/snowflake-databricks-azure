import os
from datetime import datetime
from typing import Optional

import pandas as pd
import snowflake.connector

from src.config.config import Config
from src.extraction.metadata_manager import MetadataManager

logger = Config.get_logger(__name__)


class SnowflakeExtractor:
    """Enterprise-grade Snowflake extractor with chunking, watermarking, and safety controls.

    This class handles the extraction of data from Snowflake tables into Parquet files,
    supporting both full and incremental loads.
    """

    ALLOWED_TABLES = {"CUSTOMERS", "PRODUCTS", "ORDERS", "ORDER_ITEMS", "PAYMENTS"}

    def __init__(self) -> None:
        """Initializes the extractor with Snowflake configuration and metadata manager."""
        self.config = Config.get_snowflake_config()
        self.metadata_mgr = MetadataManager()
        self.batch_id = datetime.now().strftime("%Y%m%d%H%M%S")

    def _get_connection(self) -> snowflake.connector.SnowflakeConnection:
        """Establishes a secure connection to Snowflake.

        Returns:
            snowflake.connector.SnowflakeConnection: Active Snowflake connection.

        Raises:
            snowflake.connector.Error: If the connection fails.
        """
        try:
            return snowflake.connector.connect(**self.config)
        except snowflake.connector.Error as e:
            logger.error(f"Snowflake Connection Error: {e.msg}")
            raise

    def extract_table(
        self,
        table_name: str,
        incremental_col: Optional[str] = None,
        chunk_size: int = 100000,
    ) -> None:
        """Extracts table data with chunking and watermark management.

        Args:
            table_name: Name of the table to extract.
            incremental_col: Column to use for incremental watermark logic.
            chunk_size: Number of rows per chunk.

        Raises:
            ValueError: If the table name is not in the allowed list.
        """
        if table_name.upper() not in self.ALLOWED_TABLES:
            raise ValueError(f"Table {table_name} is not in the allowed list.")

        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            last_watermark = (
                self.metadata_mgr.get_last_watermark(table_name)
                if incremental_col
                else None
            )

            query = f"SELECT * FROM {table_name.upper()}"
            if last_watermark and incremental_col:
                query += f" WHERE {incremental_col} > %s"
                logger.info(f"Incremental load for {table_name} since {last_watermark}")
                cursor.execute(query, (last_watermark,))
            else:
                logger.info(f"Full load for {table_name}")
                cursor.execute(query)

            chunk_idx = 0
            total_rows = 0
            new_max_watermark = last_watermark

            while True:
                rows = cursor.fetchmany(chunk_size)
                if not rows:
                    break

                df = pd.DataFrame(
                    rows, columns=[col[0].lower() for col in cursor.description]
                )

                if incremental_col:
                    current_max = df[incremental_col.lower()].max()
                    if new_max_watermark is None or current_max > new_max_watermark:
                        new_max_watermark = current_max

                self._write_to_storage(df, table_name.lower(), chunk_idx)

                total_rows += len(df)
                logger.info(
                    f"Extracted chunk {chunk_idx} for {table_name} ({len(df)} rows)"
                )
                chunk_idx += 1

            self.metadata_mgr.log_extraction(
                batch_id=self.batch_id,
                table_name=table_name,
                row_count=total_rows,
                watermark=new_max_watermark,
                status="SUCCESS",
            )

            logger.info(f"Successfully extracted {total_rows} rows from {table_name}.")

        except Exception as e:
            logger.error(f"Critical error extracting {table_name}: {str(e)}")
            self.metadata_mgr.log_extraction(
                batch_id=self.batch_id,
                table_name=table_name,
                row_count=0,
                status="FAILED",
                error_message=str(e),
            )
            raise
        finally:
            cursor.close()
            conn.close()

    def _write_to_storage(
        self, df: pd.DataFrame, table_name: str, chunk_idx: int
    ) -> str:
        """Saves dataframe as a partitioned Parquet file in the landing zone.

        Args:
            df: Dataframe to save.
            table_name: Target table name.
            chunk_idx: Index of the current chunk.

        Returns:
            str: Path to the saved file.
        """
        target_dir = Config.get_storage_path("landing", table_name)
        os.makedirs(target_dir, exist_ok=True)

        filename = f"batch={self.batch_id}/part_{chunk_idx:04d}.parquet"
        file_path = os.path.join(target_dir, filename)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        df.to_parquet(file_path, index=False, engine="pyarrow", compression="snappy")
        return file_path
