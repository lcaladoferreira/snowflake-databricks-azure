import json
import os
from datetime import datetime
from typing import Optional, Any
from src.config.config import Config


class MetadataManager:
    """Manages extraction metadata and watermarks."""

    def __init__(self):
        self.metadata_dir = os.path.join(Config.LOCAL_DATA_DIR, "metadata")
        os.makedirs(self.metadata_dir, exist_ok=True)

    def get_last_watermark(self, table_name: str) -> Optional[Any]:
        """Retrieves the last successful watermark for a table."""
        path = os.path.join(self.metadata_dir, f"{table_name}_watermark.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                return data.get("watermark")
        return None

    def log_extraction(
        self,
        batch_id: str,
        table_name: str,
        row_count: int,
        watermark: Optional[Any] = None,
        status: str = "SUCCESS",
        error_message: Optional[str] = None,
    ):
        """Logs the results of an extraction task."""
        log_entry = {
            "batch_id": batch_id,
            "table_name": table_name,
            "row_count": row_count,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "error": error_message,
        }

        # Save historical log
        log_path = os.path.join(self.metadata_dir, "extraction_history.jsonl")
        with open(log_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

        # Update watermark on success
        if status == "SUCCESS" and watermark:
            watermark_path = os.path.join(
                self.metadata_dir, f"{table_name}_watermark.json"
            )
            with open(watermark_path, "w") as f:
                json.dump({"table_name": table_name, "watermark": watermark}, f)
