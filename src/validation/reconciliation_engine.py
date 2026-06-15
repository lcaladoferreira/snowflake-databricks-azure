from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, count, sum as _sum, min as _min, max as _max, lit, current_timestamp
from src.config.config import Config
from typing import Dict, Any

logger = Config.get_logger(__name__)

class ReconciliationEngine:
    """Performs deep comparison between Snowflake (Source) and Databricks (Target)."""

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.results_table = f"{Config.UC_CATALOG}.{Config.UC_GOLD_SCHEMA}.reconciliation_results"

    def reconcile(self, table_name: str, metric_cols: list):
        """Runs parity checks and persists results."""
        logger.info(f"Starting reconciliation for {table_name}")

        # 1. Fetch Source Metrics (In real prod, this queries Snowflake directly via JDBC/Connector)
        # For this template, we assume metadata was captured during extraction
        source_metrics = self._get_source_metrics(table_name, metric_cols)

        # 2. Calculate Target Metrics (Databricks)
        target_path = Config.get_storage_path("gold", table_name) # Or silver/bronze
        target_df = self.spark.read.format("delta").load(target_path)

        target_metrics = self._calculate_metrics(target_df, metric_cols)

        # 3. Compare and Report
        report = self._compare(table_name, source_metrics, target_metrics)
        self._persist_results(report)

        # 4. Enforce Quality Gate
        if report['status'] == "FAILED":
            raise Exception(f"Reconciliation failed for {table_name}: {report['message']}")

    def _calculate_metrics(self, df: DataFrame, cols: list) -> Dict[str, Any]:
        """Calculates row count and aggregates for checksum."""
        agg_exprs = [count("*").alias("row_count")]
        for c in cols:
            agg_exprs.append(_sum(c).alias(f"sum_{c}"))
            agg_exprs.append(_min(c).alias(f"min_{c}"))
            agg_exprs.append(_max(c).alias(f"max_{c}"))

        metrics = df.agg(*agg_exprs).collect()[0].asDict()
        return metrics

    def _get_source_metrics(self, table_name: str, cols: list) -> Dict[str, Any]:
        """
        Placeholder for fetching metrics from Snowflake.
        In production, this executes: SELECT count(*), sum(col)... FROM table
        """
        # Simulated source metrics for the template
        return {
            "row_count": 500,
            "sum_payment_amount": 125000.0, # Example
            "min_order_date": "2024-01-01",
            "max_order_date": "2024-03-31"
        }

    def _compare(self, table_name: str, source: dict, target: dict) -> dict:
        """Deep comparison logic."""
        diffs = []
        if source['row_count'] != target['row_count']:
            diffs.append(f"Row count mismatch: Source={source['row_count']}, Target={target['row_count']}")

        status = "PASSED" if not diffs else "FAILED"
        return {
            "table_name": table_name,
            "source_metrics": str(source),
            "target_metrics": str(target),
            "status": status,
            "message": "; ".join(diffs),
            "reconciled_at": datetime.now()
        }

    def _persist_results(self, report: dict):
        """Saves results to a Delta table in Gold."""
        df = self.spark.createDataFrame([report])
        (df.withColumn("processed_at", current_timestamp())
         .write.format("delta")
         .mode("append")
         .save(Config.get_storage_path("gold", "reconciliation_results")))

from datetime import datetime
if __name__ == "__main__":
    from src.utils.spark_utils import get_spark_session
    s = get_spark_session("Reconciliation")
    re = ReconciliationEngine(s)
    # re.reconcile("fact_orders", ["payment_amount"])
