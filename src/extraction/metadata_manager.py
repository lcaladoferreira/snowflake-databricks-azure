"""Metadata management for the extraction layer.

Handles the persistence and retrieval of extraction logs and high watermarks
for incremental loads.
"""

import json
import os
from datetime import datetime
from typing import Optional, Any
from src.config.config import Config

class MetadataManager:
    """Manages extraction metadata and watermarks.

    Provides methods to get the last watermark for incremental loads and
    log the status of every extraction batch.
    """

    def __init__(self) -> None:
        """Initializes the MetadataManager with a local metadata directory."""
        self.metadata_dir = os.path.join(Config.LOCAL_DATA_DIR, "metadata")
        os.makedirs(self.metadata_dir, exist_ok=True)

    def get_last_watermark(self, table_name: str) -> Optional[Any]:
        """Retrieves the last successful watermark for a table.

        Args:
            table_name (str): Name of the table.

        Returns:
            Optional[Any]: The last recorded watermark value, or None if not found.
        """
        path = os.path.join(self.metadata_dir, f"{table_name}_watermark.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get("watermark")
        return None

    def log_extraction(self,
                       batch_id: str,
                       table_name: str,
                       row_count: int,
                       watermark: Optional[Any] = None,
                       status: str = "SUCCESS",
                       error_message: Optional[str] = None) -> None:
        """Logs the results of an extraction task.

        Args:
            batch_id (str): Unique ID for the extraction batch.
            table_name (str): Name of the table.
            row_count (int): Number of rows extracted.
            watermark (Optional[Any], optional): New watermark value. Defaults to None.
            status (str, optional): Status of the extraction (SUCCESS/FAILED). Defaults to "SUCCESS".
            error_message (Optional[str], optional): Error message if failed. Defaults to None.
        """
        log_entry = {
            "batch_id": batch_id,
            "table_name": table_name,
            "row_count": row_count,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "error": error_message
        }

        # Save historical log
        log_path = os.path.join(self.metadata_dir, "extraction_history.jsonl")
        with open(log_path, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

        # Update watermark on success
        if status == "SUCCESS" and watermark:
            watermark_path = os.path.join(self.metadata_dir, f"{table_name}_watermark.json")
            with open(watermark_path, 'w') as f:
                json.dump({"table_name": table_name, "watermark": watermark}, f)
