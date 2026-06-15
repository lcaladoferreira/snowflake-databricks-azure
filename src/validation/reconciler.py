import os
import pandas as pd
from src.config.config import Config
from src.utils.spark_utils import get_spark_session
from src.utils.logger import get_logger
from pyspark.sql.functions import count, when, col

logger = get_logger(__name__)

class Reconciler:
    def __init__(self):
        self.spark = get_spark_session("Reconciliation")
        self.tables = ["customers", "products", "orders", "order_items", "payments"]

    def run_reconciliation(self):
        results = []
        for table in self.tables:
            logger.info(f"Reconciling {table}...")

            # Source metrics (from CSV in demo)
            source_path = os.path.join(Config.LOCAL_DATA_DIR, "sample", f"{table}.csv")
            source_pd = pd.read_csv(source_path)
            source_count = len(source_pd)

            # Target metrics (from Bronze Delta)
            target_path = Config.get_storage_path("bronze", table)
            if os.path.exists(target_path) or self.spark.catalog.tableExists(target_path):
                target_df = self.spark.read.format("delta").load(target_path)
                target_count = target_df.count()

                # Null count check for first column (usually ID)
                id_col = target_df.columns[0]
                target_nulls = target_df.filter(col(id_col).isNull()).count()
                source_nulls = source_pd[source_pd.columns[0]].isna().sum()
            else:
                target_count = -1
                target_nulls = -1
                source_nulls = -1

            status = "PASS" if source_count == target_count and source_nulls == target_nulls else "FAIL"

            results.append({
                "table": table,
                "source_count": source_count,
                "target_count": target_count,
                "source_nulls": int(source_nulls),
                "target_nulls": int(target_nulls),
                "status": status
            })

        report_df = pd.DataFrame(results)
        logger.info("\nReconciliation Report:\n" + report_df.to_string())

        # Save report
        report_path = os.path.join(Config.LOCAL_DATA_DIR, "reconciliation_report.csv")
        report_df.to_csv(report_path, index=False)
        logger.info(f"Report saved to {report_path}")
        return results

if __name__ == "__main__":
    reconciler = Reconciler()
    reconciler.run_reconciliation()
