import os
import json
from datetime import datetime
from src.config.config import Config

def capture_metadata(table_name, row_count, status="success"):
    metadata = {
        "table_name": table_name,
        "extraction_timestamp": datetime.now().isoformat(),
        "row_count": row_count,
        "source_system": "snowflake" if Config.EXECUTION_MODE != "demo" else "demo_csv",
        "status": status
    }

    metadata_dir = os.path.join(Config.RAW_DIR, "_metadata")
    os.makedirs(metadata_dir, exist_ok=True)

    with open(os.path.join(metadata_dir, f"{table_name}.json"), "w") as f:
        json.dump(metadata, f, indent=4)
