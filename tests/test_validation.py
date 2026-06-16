import unittest
from unittest.mock import MagicMock, patch

from src.validation.reconciliation_engine import ReconciliationEngine
from tests.pyspark_test_base import PySparkTestCase


class TestReconciliation(PySparkTestCase):
    def setUp(self):
        self.engine = ReconciliationEngine(self.spark)

    def test_compare_metrics_pass(self):
        source = {"row_count": 100}
        target = {"row_count": 100}

        report = self.engine._compare_metrics("test_table", source, target)

        self.assertEqual(report["status"], "PASSED")
        self.assertEqual(report["table_name"], "test_table")

    def test_compare_metrics_fail(self):
        source = {"row_count": 100}
        target = {"row_count": 90}

        report = self.engine._compare_metrics("test_table", source, target)

        self.assertEqual(report["status"], "FAILED")
        self.assertIn("Count mismatch", report["message"])

    @patch("src.config.config.Config.get_storage_path")
    def test_persist_report(self, mock_path):
        mock_path.return_value = "audit_path"
        mock_report = {
            "table_name": "test",
            "status": "PASSED",
            "source_metrics": "{}",
            "target_metrics": "{}",
            "message": "",
            "reconciled_at": "now",
        }

        # Execution
        # In demo mode it writes to a path, we can't easily mock write without deep patch but we can check if it tries to create df
        with patch.object(
            self.spark, "createDataFrame", wraps=self.spark.createDataFrame
        ) as mock_create:
            self.engine._persist_report(mock_report)
            mock_create.assert_called()

    @patch("snowflake.connector.connect")
    def test_get_source_metrics_calls_snowflake(self, mock_connect):
        # Setup mock connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_conn.__enter__.return_value = mock_conn

        # Mock cursor description and fetchone
        mock_cursor.description = [("ROW_COUNT",)]
        mock_cursor.fetchone.return_value = (500,)

        # Execution
        metrics = self.engine._get_source_metrics("fact_orders", [], None)

        # Assertions
        self.assertEqual(metrics["row_count"], 500)
        mock_cursor.execute.assert_called_once()
        self.assertIn("FROM FACT_ORDERS", mock_cursor.execute.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
